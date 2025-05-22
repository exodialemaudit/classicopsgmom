#!/usr/bin/env python3
"""
Module: knowledge_retriever.py
Description: Extrait et assemble toutes les données fiables sur l'OM et le PSG :
  - Stats officielles (position, points, W/D/L) via API-Football v4
  - Effectif complet via API-Football v4
  - Fallback local sur DataLoader
  - Infobox Wikipédia (fondation, stade)
  - Résumé Wikipédia
  - Validation basique (W+D+L vs nombre de matches)
"""

import os
import re
import requests
import logging
import pandas as pd

from football_debate.preprocessing.data_loader import load_om_data, load_psg_data
from football_debate.preprocessing.data_cleaning import clean_team_stats

# ——————————————————————————————————————————————
# 1) CONFIGURATION GLOBALE
# ——————————————————————————————————————————————
FOOTBALL_API_KEY      = "a6da6313243c42d189b3cbd50ebdc219"
FOOTBALL_STANDINGS_URL = "https://api.football-data.org/v4/competitions/FL1/standings"
FOOTBALL_TEAM_URL      = "https://api.football-data.org/v4/teams/{team_id}"
WIKI_API_SUMMARY       = "https://fr.wikipedia.org/api/rest_v1/page/summary/"
WIKI_PAGE_URL          = "https://fr.wikipedia.org/wiki/"

OM_TEAM_ID  = 516
PSG_TEAM_ID = 524

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ——————————————————————————————————————————————
# 2) UTILITAIRES WIKIPÉDIA
# ——————————————————————————————————————————————

def _fetch_wiki_infobox(title: str) -> dict:
    """Extrait l'année de fondation et le stade depuis l'infobox HTML."""
    try:
        resp = requests.get(WIKI_PAGE_URL + title, timeout=5)
        resp.raise_for_status()
        html = resp.text
        founded = re.search(r'Fondé en\s*</th>\s*<td[^>]*>(\d{4})', html)
        venue   = re.search(r'Stade\s*</th>\s*<td[^>]*>([^<]+)', html)
        return {
            "founded": founded.group(1) if founded else None,
            "venue":   venue.group(1).strip() if venue else None
        }
    except Exception as e:
        logger.warning(f"[WIKI INFOBOX] échec infobox '{title}': {e}")
        return {}

def _fetch_wiki_summary(title: str) -> str:
    """Récupère le premier paragraphe via l'API REST de Wikipédia."""
    try:
        url = WIKI_API_SUMMARY + requests.utils.quote(title)
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("extract", "").split("\n")[0]
    except Exception as e:
        logger.warning(f"[WIKI SUMMARY] échec résumé '{title}': {e}")
        return ""


# ——————————————————————————————————————————————
# 3) EFFECTIF via API-FOOTBALL v4
# ——————————————————————————————————————————————

def _fetch_official_squad(team_id: int) -> list[str]:
    """
    Récupère la liste complète des joueurs du club via l'endpoint /teams/{team_id}.
    """
    try:
        resp = requests.get(
            FOOTBALL_TEAM_URL.format(team_id=team_id),
            headers={"X-Auth-Token": FOOTBALL_API_KEY},
            timeout=5
        )
        resp.raise_for_status()
        squad = resp.json().get("squad", [])
        return [p["name"] for p in squad]
    except Exception as e:
        logger.warning(f"[SQUAD] échec récupération effectif {team_id}: {e}")
        return []


# ——————————————————————————————————————————————
# 4) STANDINGS via API-FOOTBALL v4
# ——————————————————————————————————————————————

def _fetch_team_stats_from_api(team_id: int) -> dict:
    """
    Récupère position, points, wins/draws/losses via endpoint standings.
    """
    resp = requests.get(
        FOOTBALL_STANDINGS_URL,
        headers={"X-Auth-Token": FOOTBALL_API_KEY},
        timeout=5
    )
    resp.raise_for_status()
    data = resp.json()
    overall = next(g for g in data["standings"] if g["type"] == "TOTAL")["table"]
    row = next(r for r in overall if r["team"]["id"] == team_id)
    return {
        "position": row["position"],
        "points":   row["points"],
        "wins":     row["won"],
        "draws":    row["draw"],
        "losses":   row["lost"]
    }


def _validate_stats(df: pd.DataFrame, stats: dict) -> bool:
    """
    Compare le nombre de matches (df) et la somme W+D+L dans un ±1 match.
    """
    total = df.shape[0]
    s = stats["wins"] + stats["draws"] + stats["losses"]
    if abs(total - s) <= 1:
        return True
    logger.warning(f"[VALIDATION] total matches {total} vs stats sum {s}")
    return False


# ——————————————————————————————————————————————
# 5) ASSEMBLAGE DU CONTEXTE
# ——————————————————————————————————————————————

def _build_context(team_name: str, team_id: int, loader_fn, season: int) -> str:
    """
    Construit le contexte factuel pour une équipe :
      A) Stats officielles v4
      B) Fallback local si échec ou stats non valides
      C) Infobox Wikipédia (fondé / stade)
      D) Résumé Wikipédia
      E) Effectif (jusqu'à 15 joueurs)
    """
    # A) STATS OFFICIELLES
    try:
        stats = _fetch_team_stats_from_api(team_id)
        df    = loader_fn(season)
        if not _validate_stats(df, stats):
            raise ValueError("Stats invalides")
        src = "[OFFICIEL]"
    except Exception as e:
        logger.warning(f"[OFFICIEL] échec stats '{team_name}': {e}")
        df    = loader_fn(season)
        stats = clean_team_stats(df)
        src   = "[LOCAL]"
        logger.info(f"{src} stats fallback pour {team_name}: {stats}")

    # B) INFOBOX WIKIPÉDIA
    wikibox = _fetch_wiki_infobox(team_name.replace(" ", "_"))
    founded = wikibox.get("founded") or (
        "1898" if "Marseille" in team_name else "1970"
    )
    venue   = wikibox.get("venue") or (
        "Orange Vélodrome" if "Marseille" in team_name else "Parc des Princes"
    )

    # C) RÉSUMÉ WIKIPÉDIA
    summary = _fetch_wiki_summary(team_name.replace(" ", "_"))

    # D) EFFECTIF
    squad = _fetch_official_squad(team_id)
    if squad:
        lineup    = squad[:15]
        squad_txt = "Effectif (15) : " + ", ".join(lineup) + "."
    else:
        squad_txt = "Effectif indisponible."

    # E) ASSEMBLAGE FINAL
    ctx = (
        f"{team_name} en {season}/{season+1} {src} :\n"
        f"- Position : {stats.get('position', '?')}ᵉ (Points : {stats.get('points', '?')})\n"
        f"- Résultats : {stats['wins']}V / {stats['draws']}N / {stats['losses']}D\n"
        f"- Fondé en {founded} | Stade : {venue}\n"
    )
    if summary:
        ctx += f"Wikipedia résumé : {summary}\n"
    ctx += squad_txt
    return ctx


def get_om_enhanced_context(season: int = 2023) -> str:
    """Contexte complet pour l’OM."""
    return _build_context("Olympique de Marseille", OM_TEAM_ID, load_om_data, season)


def get_psg_enhanced_context(season: int = 2023) -> str:
    """Contexte complet pour le PSG."""
    return _build_context("Paris Saint-Germain", PSG_TEAM_ID, load_psg_data, season)


# ——————————————————————————————————————————————
# 6) EXTRACTEURS DIRECTS WIKIPÉDIA (résumés seuls)
# ——————————————————————————————————————————————

def get_om_wiki_context() -> str:
    return _fetch_wiki_summary("Olympique_de_Marseille")

def get_psg_wiki_context() -> str:
    return _fetch_wiki_summary("Paris_Saint-Germain_FC")


# ——————————————————————————————————————————————
# 7) CLI DE TEST
# ——————————————————————————————————————————————
if __name__ == "__main__":
    print("=== OM Contexte ===")
    print(get_om_enhanced_context())
    print("\n=== PSG Contexte ===")
    print(get_psg_enhanced_context())
    print("\n=== OM Wiki résumé ===")
    print(get_om_wiki_context())
    print("\n=== PSG Wiki résumé ===")
    print(get_psg_wiki_context())