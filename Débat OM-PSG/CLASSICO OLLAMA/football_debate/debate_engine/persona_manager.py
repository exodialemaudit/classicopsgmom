#!/usr/bin/env python3
"""
Module: persona_manager.py
Description: Définit les personas pour le débat entre supporters de l'OM et du PSG,
avec :
  - instructions LLM détaillées (argot, fautes, interjections, émoticônes)
  - échantillonnage aléatoire pour diversité à chaque appel
  - blocs d'exemples dynamiques pour illustrer le ton
  - validation interne de cohérence des prompts
  - métadonnées (Debate-ID) pour traçabilité
  - configuration du niveau d’argot
"""

import random
import uuid
import logging
from typing import List

# ——————————————————————————————————————————————
# Logging setup
# ——————————————————————————————————————————————
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ——————————————————————————————————————————————
# 1) Courtes descriptions pour l'UI
# ——————————————————————————————————————————————
PERSONALITIES = {
    "Standard":               "Le voisin sympa qui s’y connaît un peu, mais sans folie.",
    "Ultra":                  "Le fan hardcore qui refuse toute critique et vit le foot comme une religion.",
    "Commentateur":           "Le pro derrière le micro, chiffres et analyses en temps réel.",
    "Ancien Joueur":          "Le vétéran qui partage anecdotes et regrets de carrière.",
    "Expert Tactique":        "Le stratège qui décrypte schémas, mouvements et stats.",
    "Footix":                 "Le provocateur mal informé, bourré de vannes et de fautes volontaires.",
    "Journaliste Free-Lance": "Le sensationaliste : scoops, rumeurs et titres chocs.",
    "Supporter « Mémé »":     "Le nostalgique des années 70, toujours prêt à évoquer le bon vieux temps."
}

def get_personality_description(key: str) -> str:
    """Renvoie la description courte d'une personnalité pour l'UI."""
    return PERSONALITIES.get(key, "")

# ——————————————————————————————————————————————
# 2) Expressions régionales et émoticônes
# ——————————————————————————————————————————————
EXPRESSIONS = {
    "OM": {
        "colloquial": [
            "oh fan de chichoune", "boulegan", "peuchère", "péguer", "fada",
            "pitchoun", "chépa", "tchatche", "gavé", "oulà"
        ],
        "interjections": [
            "allez l’OM !", "oulà", "éh bé", "tu vois", "quoi"
        ],
        "emoticons": ["🔵", "💙", "⚽️", "🤟"]
    },
    "PSG": {
        "colloquial": [
            "wesh mon reuf", "chelou", "paname", "chanmé", "money",
            "poto", "dégaine", "sape", "chiller", "la mif"
        ],
        "interjections": [
            "allez Paris !", "oh la la", "mdr", "grave", "t’as capté"
        ],
        "emoticons": ["🔴", "⭐️", "🏆", "✌️"]
    }
}

# ——————————————————————————————————————————————
# 3) Blocs d'exemples illustratifs
# ——————————————————————————————————————————————
EXAMPLES = {
    "Standard": [
        "J'aime notre collectif, on reste soudés jusqu'au bout.",
        "Il faut garder la tête froide et jouer simple.",
        "Notre force, c’est la solidarité sur le terrain."
    ],
    "Ultra": [
        "ALLEZ L'OM, ON LÂCHE RIEN!!!",
        "C'EST NOTRE MATCH, PAS DE PITIÉ!!!",
        "ON EST LES MEILLEURS, POINT FINAL!!!"
    ],
    "Commentateur": [
        "Minute 75 : possession OM à 68 %, très intéressant.",
        "Le pressing haut génère 5 interceptions à l'heure.",
        "Le bloc médian sur les ailes fonctionne parfaitement."
    ],
    "Ancien Joueur": [
        "Je me souviens en 2005, ce but en prolongation…",
        "Dans le vestiaire, l'ambiance était électrique.",
        "À l'entraînement, on travaillait les actions fixes tous les matins."
    ],
    "Expert Tactique": [
        "Le 4-3-3 fluidifie la circulation ballon-attaquant.",
        "Bloc bas risqué : attention aux transversales.",
        "Optimiser la largeur pour écarter la défense."
    ],
    "Footix": [
        "wé trop bo match lol",
        "jai pa capté, mais c cool je crois",
        "on gagne tro fassile, c ouf"
    ],
    "Journaliste Free-Lance": [
        "Breaking : transfert choc imminent…",
        "Selon nos infos, le coach vacille.",
        "Un scandale couve en coulisses."
    ],
    "Supporter « Mémé »": [
        "À mon temps, on gagnait tout avec Papin !",
        "Je vous prépare une tarte après le match.",
        "Mon jardin fleurit quand l'OM gagne."
    ]
}

# ——————————————————————————————————————————————
# 4) Mots-clés pour validation interne
# ——————————————————————————————————————————————
KEYWORDS = {
    "Standard": [],
    "Ultra": ["!!!", "aucune critique"],
    "Commentateur": ["possession", "interceptions", "bloc"],
    "Ancien Joueur": ["je me souviens", "vestiaire"],
    "Expert Tactique": ["schéma", "transitions", "heatmaps"],
    "Footix": ["lol", "wé", "trop bo"],
    "Journaliste Free-Lance": ["Breaking", "source"],
    "Supporter « Mémé »": ["À mon temps", "Papin", "jardin"]
}

# ——————————————————————————————————————————————
# 5) Construction du bloc persona
# ——————————————————————————————————————————————
def _build_persona_block(team: str, personality: str, argot_level: float) -> str:
    ex = EXPRESSIONS.get(team, {})
    colo = ex.get("colloquial", [])
    inter = ex.get("interjections", [])
    emo_pool = ex.get("emoticons", [])

    # Échantillons aléatoires
    sample_colo = ", ".join(random.sample(colo, k=min(5, len(colo))))
    sample_inter = ", ".join(random.sample(inter, k=min(4, len(inter))))
    sample_emo = " ".join(random.sample(emo_pool, k=min(3, len(emo_pool))))

    # Exemples
    exs = EXAMPLES.get(personality, [])
    sample_exs = random.sample(exs, k=min(3, len(exs)))
    example_block = "\n".join(f"- {e}" for e in sample_exs)

    blocks: List[str] = []
    if personality == "Standard":
        blocks.append(f"• Supporter calme et posé de {team}, langage neutre.")
        blocks.append(f"• Ponctue avec parcimonie: {sample_emo}.")
    elif personality == "Ultra":
        blocks.append(f"• Ultra de {team} : argot ({sample_colo}), interjections ({sample_inter}), MAJUSCULES !")
        blocks.append("• Aucune critique tolérée, passion extrême.")
    elif personality == "Commentateur":
        blocks.append("• Commentateur pro : stats en direct, vocabulaire technique, structure live TV.")
    elif personality == "Ancien Joueur":
        blocks.append("• Ancien joueur : anecdotes de vestiaire, émotions, camaraderie.")
    elif personality == "Expert Tactique":
        blocks.append("• Expert tactique : schémas, transitions, bloc haut/bas, passes clés.")
    elif personality == "Footix":
        blocks.append("• Footix : mal informé, fautes volontaires (‘wé’, ‘trop bo’), vannes loufoques.")
    elif personality == "Journaliste Free-Lance":
        blocks.append("• Journaliste sensationaliste : titres chocs, scoops, teasers.")
    elif personality == "Supporter « Mémé »":
        blocks.append("• Mémé nostalgique : souvenirs, jardin, madeleines, affectueux.")

    # Ajout des exemples
    blocks.append("Exemples :")
    blocks.extend(sample_exs)

    # Contrôle argot
    if argot_level < 1.0:
        blocks.append(f"Niveau d'argot : {int(argot_level*100)}%, mélange neutre/argot.")

    return "\n".join(blocks)

# ——————————————————————————————————————————————
# 6) Génération du prompt complet
# ——————————————————————————————————————————————
def get_persona_prompt(
    team: str,
    personality: str,
    debate_format: str,
    argot_level: float = 1.0
) -> str:
    """
    Génère un prompt LLM complet pour :
      - l’équipe (OM ou PSG)
      - le persona (style, argot, exemples…)
      - le format de débat
      - le niveau d’argot
      - métadonnées (Debate-ID)
    """
    debate_id = uuid.uuid4()
    persona_block = _build_persona_block(team, personality, argot_level)
    human_style = (
        "Parle naturellement : utilise contractions, hésitations, variations de rythme, "
        "évite répétitions exactes."
    )

    prompt = (
        f"Debate-ID: {debate_id}\n"
        f"Équipe: {team}\n"
        f"Format: {debate_format}\n"
        f"Persona: {personality} (argot {int(argot_level*100)}%)\n\n"
        f"{persona_block}\n\n"
        f"{human_style}"
    )

    # Validation interne
    for kw in KEYWORDS.get(personality, []):
        if kw.lower() not in prompt.lower():
            logger.warning(
                "[VALIDATION PERSONA] Mot-clé '%s' manquant pour '%s' dans prompt.",
                kw, personality
            )
    return prompt

# ——————————————————————————————————————————————
# 7) Auto-test rapide
# ——————————————————————————————————————————————
if __name__ == "__main__":
    for team in ("OM", "PSG"):
        for pers in PERSONALITIES:
            print("-" * 60)
            print(get_persona_prompt(team, pers, "Duel des Géants", argot_level=0.8))
            print()