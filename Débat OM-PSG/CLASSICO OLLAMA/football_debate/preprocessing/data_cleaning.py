# football_debate/preprocessing/data_cleaning.py

def clean_team_info(info_dict):
    """
    Prend en entrée le dict 'info' renvoyé par l'API-Football pour une équipe.
    Retourne un dict minimal avec le nom de l'équipe et, si besoin, d'autres champs.
    """
    return {
        "team":   info_dict.get("name", ""),
        "venue":  info_dict.get("venue", ""),
        "founded": info_dict.get("founded", None),
        # ajoute d’autres champs si nécessaire
    }

def clean_team_stats(df):
    """
    Prend en entrée un DataFrame contenant une colonne 'result' avec valeurs 'win', 'draw', 'loss'.
    Retourne un dict{"wins":…, "draws":…, "losses":…}.
    """
    counts = df["result"].value_counts().to_dict()
    return {
        "wins":   int(counts.get("win",   0)),
        "draws":  int(counts.get("draw",  0)),
        "losses": int(counts.get("loss",  0)),
    }