# football_debate/preprocessing/data_loader.py

import os
import requests
import pandas as pd

from football_debate.ai_config import FOOTBALL_API_KEY

BASE_URL = "https://api.football-data.org/v4"
OM_TEAM_ID = 516     # ID OM sur football-data.org
PSG_TEAM_ID = 524    # ID PSG sur football-data.org
HEADERS = {"X-Auth-Token": FOOTBALL_API_KEY}


def _fetch_matches(team_id: int, season: int) -> dict:
    url = f"{BASE_URL}/competitions/FL1/matches?season={season}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def _load_team_dataframe(raw: dict, team_id: int, team_tag: str) -> pd.DataFrame:
    rows = []
    for m in raw.get("matches", []):
        home = m["homeTeam"]["id"]
        away = m["awayTeam"]["id"]
        # ne garder que les matchs impliquant notre équipe
        if team_id not in (home, away):
            continue
        hg = m["score"]["fullTime"]["home"]
        ag = m["score"]["fullTime"]["away"]
        # définir le résultat du point de vue de team_id
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
    df = pd.DataFrame(rows)
    return df


def load_om_data(season: int = 2023) -> pd.DataFrame:
    raw = _fetch_matches(OM_TEAM_ID, season)
    return _load_team_dataframe(raw, OM_TEAM_ID, "OM")


def load_psg_data(season: int = 2023) -> pd.DataFrame:
    raw = _fetch_matches(PSG_TEAM_ID, season)
    return _load_team_dataframe(raw, PSG_TEAM_ID, "PSG")