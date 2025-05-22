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
  - configuration du niveau d'argot
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
    "Standard":               "Le voisin sympa qui s'y connaît un peu, mais sans folie.",
    "Ultra":                  "Le fan hardcore qui refuse toute critique et vit le foot comme une religion.",
    "Hooligan":              "Le supporter radical, prêt à en découdre verbalement, très agressif.",
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
            # Expressions marseillaises authentiques avec accent
            "tié fada", "oh fan de chichoune", "boulegan", "peuchère", "péguer",
            "pitchoun", "chépa", "tchatche", "gavé", "oulà", "nique ta mère",
            "va te faire enculer", "sale merde", "fils de pute", "ta gueule",
            "oh la vache", "oh putain", "oh bordel", "oh merde", "oh fan de chichoune",
            "t'as vu", "t'as capté", "t'as compris", "t'as pigé", "t'as saisi",
            "c'est clair", "c'est sûr", "c'est certain", "c'est évident", "c'est logique",
            "j'ai dit", "j'ai dit quoi", "j'ai dit ce que j'ai dit", "j'ai dit ce que je pense",
            "j'ai dit ce que je crois", "j'ai dit ce que je sais", "j'ai dit ce que je vois",
            "j'ai dit ce que j'entends", "j'ai dit ce que je sens", "j'ai dit ce que je ressens",
            "j'ai dit ce que je vis", "j'ai dit ce que je subis", "j'ai dit ce que je supporte",
            "j'ai dit ce que je tolère", "j'ai dit ce que j'accepte", "j'ai dit ce que je refuse",
            "j'ai dit ce que je veux", "j'ai dit ce que je peux", "j'ai dit ce que je dois",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas", "j'ai dit ce que je ferai",
            "j'ai dit ce que je ferai pas", "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas",
            "j'ai dit ce que je ferai", "j'ai dit ce que je ferai pas",
            "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire"
        ],
        "interjections": [
            # Interjections marseillaises avec accent
            "allez l'OM !", "oulà", "éh bé", "tu vois", "quoi", "putain",
            "merde", "bordel", "nique", "ta gueule", "ferme ta gueule",
            "oh la vache", "oh putain", "oh bordel", "oh merde", "oh fan de chichoune",
            "t'as vu", "t'as capté", "t'as compris", "t'as pigé", "t'as saisi",
            "c'est clair", "c'est sûr", "c'est certain", "c'est évident", "c'est logique",
            "j'ai dit", "j'ai dit quoi", "j'ai dit ce que j'ai dit", "j'ai dit ce que je pense",
            "j'ai dit ce que je crois", "j'ai dit ce que je sais", "j'ai dit ce que je vois",
            "j'ai dit ce que j'entends", "j'ai dit ce que je sens", "j'ai dit ce que je ressens",
            "j'ai dit ce que je vis", "j'ai dit ce que je subis", "j'ai dit ce que je supporte",
            "j'ai dit ce que je tolère", "j'ai dit ce que j'accepte", "j'ai dit ce que je refuse",
            "j'ai dit ce que je veux", "j'ai dit ce que je peux", "j'ai dit ce que je dois",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas", "j'ai dit ce que je ferai",
            "j'ai dit ce que je ferai pas", "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas",
            "j'ai dit ce que je ferai", "j'ai dit ce que je ferai pas",
            "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire"
        ],
        "emoticons": ["🔵", "💙", "⚽️", "🤟", "👊", "💪", "😤", "😡", "🔥", "💯", "💥", "⚡️", "🌊", "🌞", "🏆"]
    },
    "PSG": {
        "colloquial": [
            # Expressions parisiennes/banlieue
            "wesh mon reuf", "chelou", "paname", "chanmé", "money",
            "poto", "dégaine", "sape", "chiller", "la mif", "nique ta race",
            "va te faire foutre", "sale merde", "fils de pute", "ta gueule",
            "wesh", "frère", "mon gars", "mon pote", "mon reuf",
            "wesh", "frère", "mon gars", "mon pote", "mon reuf",
            "t'as vu", "t'as capté", "t'as compris", "t'as pigé", "t'as saisi",
            "c'est clair", "c'est sûr", "c'est certain", "c'est évident", "c'est logique",
            "j'ai dit", "j'ai dit quoi", "j'ai dit ce que j'ai dit", "j'ai dit ce que je pense",
            "j'ai dit ce que je crois", "j'ai dit ce que je sais", "j'ai dit ce que je vois",
            "j'ai dit ce que j'entends", "j'ai dit ce que je sens", "j'ai dit ce que je ressens",
            "j'ai dit ce que je vis", "j'ai dit ce que je subis", "j'ai dit ce que je supporte",
            "j'ai dit ce que je tolère", "j'ai dit ce que j'accepte", "j'ai dit ce que je refuse",
            "j'ai dit ce que je veux", "j'ai dit ce que je peux", "j'ai dit ce que je dois",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas", "j'ai dit ce que je ferai",
            "j'ai dit ce que je ferai pas", "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas",
            "j'ai dit ce que je ferai", "j'ai dit ce que je ferai pas",
            "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire"
        ],
        "interjections": [
            # Interjections parisiennes
            "allez Paris !", "oh la la", "mdr", "grave", "t'as capté", "putain",
            "merde", "bordel", "nique", "ta gueule", "ferme ta gueule",
            "wesh", "frère", "mon gars", "mon pote", "mon reuf",
            "wesh", "frère", "mon gars", "mon pote", "mon reuf",
            "t'as vu", "t'as capté", "t'as compris", "t'as pigé", "t'as saisi",
            "c'est clair", "c'est sûr", "c'est certain", "c'est évident", "c'est logique",
            "j'ai dit", "j'ai dit quoi", "j'ai dit ce que j'ai dit", "j'ai dit ce que je pense",
            "j'ai dit ce que je crois", "j'ai dit ce que je sais", "j'ai dit ce que je vois",
            "j'ai dit ce que j'entends", "j'ai dit ce que je sens", "j'ai dit ce que je ressens",
            "j'ai dit ce que je vis", "j'ai dit ce que je subis", "j'ai dit ce que je supporte",
            "j'ai dit ce que je tolère", "j'ai dit ce que j'accepte", "j'ai dit ce que je refuse",
            "j'ai dit ce que je veux", "j'ai dit ce que je peux", "j'ai dit ce que je dois",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas", "j'ai dit ce que je ferai",
            "j'ai dit ce que je ferai pas", "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire",
            "j'ai dit ce que je fais", "j'ai dit ce que je fais pas",
            "j'ai dit ce que je ferai", "j'ai dit ce que je ferai pas",
            "j'ai dit ce que j'ai fait", "j'ai dit ce que j'ai pas fait",
            "j'ai dit ce que je vais faire", "j'ai dit ce que je vais pas faire",
            "j'ai dit ce que je peux faire", "j'ai dit ce que je peux pas faire",
            "j'ai dit ce que je dois faire", "j'ai dit ce que je dois pas faire",
            "j'ai dit ce que je veux faire", "j'ai dit ce que je veux pas faire"
        ],
        "emoticons": ["🔴", "⭐️", "🏆", "✌️", "👊", "💪", "😤", "😡", "🔥", "💯", "💥", "⚡️", "🌊", "🌞", "🏆"]
    }
}

# ——————————————————————————————————————————————
# 3) Blocs d'exemples illustratifs
# ——————————————————————————————————————————————
EXAMPLES = {
    "Standard": [
        "J'aime notre collectif, on reste soudés jusqu'au bout.",
        "Il faut garder la tête froide et jouer simple.",
        "Notre force, c'est la solidarité sur le terrain."
    ],
    "Ultra": [
        "ALLEZ L'OM, ON LÂCHE RIEN!!! NIQUE TA MÈRE LE PSG!!! ON EST LES ROIS DE LA MÉDITERRANÉE!!! LE VÉLODROME VA TREMBLER!!!",
        "C'EST NOTRE MATCH, PAS DE PITIÉ!!! ON VA VOUS DÉMONTER!!! LE VÉLODROME VA TREMBLER!!! ON EST LES ROIS DU SUD!!!",
        "ON EST LES MEILLEURS, POINT FINAL!!! FERME TA GUEULE!!! ON EST LES ROIS!!! LE SUD EST À NOUS!!!"
    ],
    "Hooligan": [
        "TA GUEULE SALE MERDE!!! ON VA TE DÉMONTER!!! LE VÉLODROME EST À NOUS!!! ON EST LES ROIS DE MARSEILLE!!!",
        "NIQUE TA RACE!!! T'AS RIEN À FOUTRE ICI!!! ON EST LES ROIS DE MARSEILLE!!! LE SUD EST À NOUS!!!",
        "FERME TA GUEULE!!! ON EST LES ROIS!!! LE SUD EST À NOUS!!! ON VA VOUS DÉMONTER!!!"
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
        "Le 4-3-3 fluidifie la circulation ballon-attaquant, mon gars, faut être plus agressif.",
        "Bloc bas risqué : attention aux transversales, faut être plus agressif, faut être plus direct.",
        "Optimiser la largeur pour écarter la défense, c'est la clé du match, faut être plus agressif."
    ],
    "Footix": [
        "wé trop bo match lol, on va les défoncer, on est les meilleurs",
        "jai pa capté, mais c cool je crois, on gagne, on est les meilleurs",
        "on gagne tro fassile, c ouf, on est les meilleurs, on va les défoncer"
    ],
    "Journaliste Free-Lance": [
        "Breaking : transfert choc imminent… Le club est en ébullition ! Les supporters s'impatientent !",
        "Selon nos infos, le coach vacille… La pression monte ! Les supporters s'impatientent !",
        "Un scandale couve en coulisses… Les supporters s'impatientent ! Le club est en ébullition !"
    ],
    "Supporter « Mémé »": [
        "À mon temps, on gagnait tout avec Papin ! C'était le bon vieux temps ! On était les meilleurs !",
        "Je vous prépare une tarte après le match, comme dans le temps ! On était les meilleurs !",
        "Mon jardin fleurit quand l'OM gagne, c'est comme ça depuis 50 ans ! On était les meilleurs !"
    ]
}

# ——————————————————————————————————————————————
# 4) Mots-clés pour validation interne
# ——————————————————————————————————————————————
KEYWORDS = {
    "Standard": [],
    "Ultra": ["!!!", "aucune critique", "ALLEZ", "NIQUE"],
    "Hooligan": ["TA GUEULE", "SALE MERDE", "NIQUE", "FERME"],
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
        blocks.append("• Aucune critique tolérée, passion extrême, agressivité verbale.")
        blocks.append("• Insultes et provocations autorisées, mais pas de violence physique.")
        blocks.append("• Style très direct et brutal, pas de diplomatie.")
        blocks.append("• Utilise beaucoup d'expressions régionales et d'argot.")
        blocks.append("• Accent marseillais prononcé pour l'OM, accent parisien pour le PSG.")
        blocks.append("• Répète souvent les mêmes phrases pour insister.")
        blocks.append("• Utilise beaucoup de points d'exclamation et de majuscules.")
    elif personality == "Hooligan":
        blocks.append(f"• Hooligan de {team} : langage très agressif, insultes ({sample_colo}), provocations ({sample_inter}).")
        blocks.append("• Menaces verbales, intimidation, domination psychologique.")
        blocks.append("• Style très direct et brutal, pas de diplomatie.")
        blocks.append("• Utilise beaucoup d'expressions régionales et d'argot.")
        blocks.append("• Menace souvent de violence mais reste verbal.")
        blocks.append("• Accent marseillais prononcé pour l'OM, accent parisien pour le PSG.")
        blocks.append("• Répète souvent les mêmes phrases pour insister.")
        blocks.append("• Utilise beaucoup de points d'exclamation et de majuscules.")
    elif personality == "Commentateur":
        blocks.append("• Commentateur pro : stats en direct, vocabulaire technique, structure live TV.")
    elif personality == "Ancien Joueur":
        blocks.append("• Ancien joueur : anecdotes de vestiaire, émotions, camaraderie.")
    elif personality == "Expert Tactique":
        blocks.append("• Expert tactique : schémas, transitions, bloc haut/bas, passes clés.")
        blocks.append("• Utilise un langage technique mais accessible.")
        blocks.append("• Reste factuel et analytique.")
        blocks.append("• Accent marseillais léger pour l'OM, accent parisien léger pour le PSG.")
        blocks.append("• Utilise des expressions techniques mais compréhensibles.")
    elif personality == "Footix":
        blocks.append("• Footix : mal informé, fautes volontaires ('wé', 'trop bo'), vannes loufoques.")
        blocks.append("• Style très familier et décontracté.")
        blocks.append("• Utilise beaucoup d'expressions de la rue.")
        blocks.append("• Accent marseillais prononcé pour l'OM, accent parisien prononcé pour le PSG.")
        blocks.append("• Fait beaucoup de fautes d'orthographe volontaires.")
    elif personality == "Journaliste Free-Lance":
        blocks.append("• Journaliste sensationaliste : titres chocs, scoops, teasers.")
        blocks.append("• Style dramatique et exagéré.")
        blocks.append("• Utilise beaucoup de points d'exclamation.")
        blocks.append("• Accent neutre, style journalistique.")
        blocks.append("• Utilise beaucoup de formules chocs.")
    elif personality == "Supporter « Mémé »":
        blocks.append("• Mémé nostalgique : souvenirs, jardin, madeleines, affectueux.")
        blocks.append("• Style très affectueux et nostalgique.")
        blocks.append("• Utilise beaucoup d'expressions d'époque.")
        blocks.append("• Accent marseillais très prononcé pour l'OM, accent parisien très prononcé pour le PSG.")
        blocks.append("• Parle beaucoup du passé et des anciens joueurs.")

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
      - l'équipe (OM ou PSG)
      - le persona (style, argot, exemples…)
      - le format de débat
      - le niveau d'argot
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