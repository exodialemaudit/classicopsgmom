# football_debate/preprocessing/data_loader.py

import os
import json
import time
import logging
import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

from football_debate.ai_config import FOOTBALL_API_KEY

# Configuration
BASE_URL = "https://api.football-data.org/v4"
OM_TEAM_ID = 516     # ID OM sur football-data.org
PSG_TEAM_ID = 524    # ID PSG sur football-data.org
HEADERS = {"X-Auth-Token": FOOTBALL_API_KEY}
CACHE_DIR = Path("football_debate/data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Données de fallback (statistiques de base)
FALLBACK_DATA = {
    "OM": {
        "matches_played": 38,
        "wins": 22,
        "draws": 7,
        "losses": 9,
        "goals_for": 67,
        "goals_against": 40,
        "points": 73
    },
    "PSG": {
        "matches_played": 38,
        "wins": 25,
        "draws": 8,
        "losses": 5,
        "goals_for": 89,
        "goals_against": 40,
        "points": 83
    }
}

def _get_cache_path(team_id: int, season: int) -> Path:
    """Génère le chemin du fichier de cache."""
    return CACHE_DIR / f"team_{team_id}_season_{season}.json"

def _load_from_cache(team_id: int, season: int) -> Optional[Dict[str, Any]]:
    """Charge les données depuis le cache si elles existent et sont récentes."""
    cache_path = _get_cache_path(team_id, season)
    if not cache_path.exists():
        return None
    
    # Vérifier si le cache est récent (moins de 24h)
    if time.time() - cache_path.stat().st_mtime > 86400:
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Erreur lecture cache: {e}")
        return None

def _save_to_cache(team_id: int, season: int, data: Dict[str, Any]) -> None:
    """Sauvegarde les données dans le cache."""
    try:
        cache_path = _get_cache_path(team_id, season)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Erreur écriture cache: {e}")

def _fetch_matches(team_id: int, season: int, max_retries: int = 3) -> dict:
    """
    Récupère les matchs avec retry et backoff exponentiel.
    Utilise le cache si disponible.
    """
    # 1. Essayer le cache d'abord
    cached_data = _load_from_cache(team_id, season)
    if cached_data:
        logger.info(f"Données récupérées du cache pour {team_id} saison {season}")
        return cached_data

    # 2. Sinon, appeler l'API avec retry
    url = f"{BASE_URL}/competitions/FL1/matches?season={season}"
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=HEADERS)
            r.raise_for_status()
            data = r.json()
            _save_to_cache(team_id, season, data)
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                wait_time = (2 ** attempt) * 1  # backoff exponentiel
                logger.warning(f"Rate limit atteint, attente de {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except Exception as e:
            logger.error(f"Erreur API: {e}")
            if attempt == max_retries - 1:
                raise

def _load_team_dataframe(raw: dict, team_id: int, team_tag: str) -> pd.DataFrame:
    """Charge les données dans un DataFrame pandas."""
    try:
        rows = []
        for m in raw.get("matches", []):
            home = m["homeTeam"]["id"]
            away = m["awayTeam"]["id"]
            if team_id not in (home, away):
                continue
            hg = m["score"]["fullTime"]["home"]
            ag = m["score"]["fullTime"]["away"]
            if home == team_id:
                result = "win" if hg > ag else "loss" if hg < ag else "draw"
            else:
                result = "win" if ag > hg else "loss" if ag < hg else "draw"
            rows.append({
                "match_id": m["id"],
                "utcDate": m["utcDate"],
                "competition": m["competition"]["code"],
                "team": team_tag,
                "home_goals": hg,
                "away_goals": ag,
                "result": result
            })
        return pd.DataFrame(rows)
    except Exception as e:
        logger.error(f"Erreur traitement données: {e}")
        # Retourner un DataFrame vide avec les bonnes colonnes
        return pd.DataFrame(columns=["match_id", "utcDate", "competition", "team", 
                                   "home_goals", "away_goals", "result"])

def load_team_data(team_id: int, team_tag: str, season: int = 2023) -> pd.DataFrame:
    """
    Charge les données d'une équipe avec fallback.
    """
    try:
        raw = _fetch_matches(team_id, season)
        df = _load_team_dataframe(raw, team_id, team_tag)
        if not df.empty:
            return df
    except Exception as e:
        logger.warning(f"Échec récupération données {team_tag}: {e}")
    
    # Fallback vers les données statiques
    logger.info(f"Utilisation données fallback pour {team_tag}")
    fallback = FALLBACK_DATA[team_tag]
    return pd.DataFrame([{
        "team": team_tag,
        "matches_played": fallback["matches_played"],
        "wins": fallback["wins"],
        "draws": fallback["draws"],
        "losses": fallback["losses"],
        "goals_for": fallback["goals_for"],
        "goals_against": fallback["goals_against"],
        "points": fallback["points"]
    }])

def load_om_data(season: int = 2023) -> pd.DataFrame:
    """Charge les données de l'OM."""
    return load_team_data(OM_TEAM_ID, "OM", season)

def load_psg_data(season: int = 2023) -> pd.DataFrame:
    """Charge les données du PSG."""
    return load_team_data(PSG_TEAM_ID, "PSG", season)