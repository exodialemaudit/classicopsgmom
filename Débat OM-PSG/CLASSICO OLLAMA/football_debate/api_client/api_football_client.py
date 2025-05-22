#!/usr/bin/env python3
"""
Module: api_football_client.py
Description: Ce module interroge l'API-Football de football-data.org pour
récupérer les informations et les matchs d'une équipe.
"""

import requests
from football_debate.ai_config import FOOTBALL_API_KEY

# Base URL et en-têtes pour football-data.org v4
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": FOOTBALL_API_KEY
}


def get_team_info(team_id: int) -> dict:
    """
    Récupère les informations détaillées d'une équipe via son ID.

    Args:
        team_id (int): Identifiant de l'équipe sur football-data.org

    Returns:
        dict: Données JSON de l'équipe
    """
    url = f"{BASE_URL}/teams/{team_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_team_matches(team_id: int, season: int) -> dict:
    """
    Récupère la liste des matchs joués par une équipe sur une saison donnée.

    Args:
        team_id (int): Identifiant de l'équipe
        season  (int): Année de la saison (ex.: 2023)

    Returns:
        dict: Données JSON contenant les matchs
    """
    url = f"{BASE_URL}/teams/{team_id}/matches"
    params = {"season": season}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()


def get_team_data(team_id: int, season: int = 2023) -> dict:
    """
    Combine info de base et matchs pour une équipe donnée.
    """
    info = get_team_info(team_id)
    matches = get_team_matches(team_id, season)
    return {"info": info, "matches": matches}


def get_om_data(season: int = 2023) -> dict:
    """
    Récupère les données complètes de l'OM pour la saison spécifiée.
    """
    team_id_om = 516   # ← Remplacez par l’ID exact de l’OM sur football-data.org
    return get_team_data(team_id_om, season)


def get_psg_data(season: int = 2023) -> dict:
    """
    Récupère les données complètes du PSG pour la saison spécifiée.
    """
    team_id_psg = 524  # ← Remplacez par l’ID exact du PSG sur football-data.org
    return get_team_data(team_id_psg, season)


if __name__ == "__main__":
    # Test rapide depuis la ligne de commande
    print("OM:", get_om_data())
    print("PSG:", get_psg_data())