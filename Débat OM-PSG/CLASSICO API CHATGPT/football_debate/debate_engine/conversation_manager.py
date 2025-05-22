#!/usr/bin/env python3
"""
Module: conversation_manager.py
Description: Orchestre un débat entre deux IA (OM vs PSG) avec :
  - contextes factuels enrichis (API-Football v4 + Wikipédia)
  - prompts persona ultra-complets (argot, fautes, interjections, émoticônes)
  - formats de débat clairs et distincts
  - directives strictes anti-confusion d'équipe et anti-redite
  - injection systématique de la dernière réplique adverse
  - post-processing pour détecter et corriger d'éventuelles confusions de joueurs
  - suivi pas à pas et journaux détaillés
"""

import os
import sys
import time
import logging
import re

# ——————————————————————————————————————————————
# 1) Configuration du chemin pour modules internes
# ——————————————————————————————————————————————
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, "..")
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# ——————————————————————————————————————————————
# 2) Imports
# ——————————————————————————————————————————————
from football_debate.llm_interface.openai_interface import generate_response
from football_debate.debate_engine.persona_manager import get_persona_prompt
from football_debate.debate_engine.knowledge_retriever import (
    get_om_enhanced_context,
    get_psg_enhanced_context,
    get_om_wiki_context,
    get_psg_wiki_context,
    _fetch_official_squad,
    OM_TEAM_ID,
    PSG_TEAM_ID,
)

# ——————————————————————————————————————————————
# 3) Logging
# ——————————————————————————————————————————————
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ——————————————————————————————————————————————
# 4) Helper: nettoyage et vérification post-génération
# ——————————————————————————————————————————————
def sanitize_response(speaker: str, text: str, previous: str | None = None) -> str:
    """
    Nettoie et sécurise la réponse d'une IA :
      1) Supprime balises []{}… et placeholders.
      2) Enlève les labels 'Réponse OM :' ou 'Réponse PSG :'.
      3) Évite la confusion des joueurs en supprimant tout nom hors équipe.
      4) Supprime les redondances avec la réplique précédente.
      5) Uniformise les sauts de ligne.
    """
    # 4.1) Supprimer les placeholders et crochets
    text = re.sub(r"[\[\]\{\}…]", "", text)

    # 4.2) Supprimer les labels de prompt
    text = re.sub(r"\bRéponse\s+(OM|PSG)\s*:", "", text, flags=re.IGNORECASE)

    # 4.3) Filtrer noms d'équipe adverse dynamiquement
    if speaker == "OM":
        forbidden = _fetch_official_squad(PSG_TEAM_ID)
    else:
        forbidden = _fetch_official_squad(OM_TEAM_ID)
    for name in forbidden:
        # ne laisser passer que dans un contexte de comparaison explicite ("plus fort que X")
        pattern = rf"\b{name}\b(?!.*plus fort|.*meilleur)"
        text = re.sub(pattern, "[...]".replace("...", ""), text, flags=re.IGNORECASE)

    # 4.4) Éviter la redite brute de la précédente réplique
    if previous:
        # si le texte commence par la même phrase
        prev_snip = previous.strip().split("\n")[0][:60]
        if text.startswith(prev_snip):
            text = text[len(prev_snip):].lstrip()

    # 4.5) Uniformiser sauts de ligne
    text = re.sub(r"\n{2,}", "\n\n", text).strip()

    return text

# ——————————————————————————————————————————————
# 5) Fonction principale
# ——————————————————————————————————————————————
def start_debate(
    initial_question: str,
    debate_format: str = "Analytique 360°",
    max_turns: int = 4,
    om_personality: str = "Standard",
    psg_personality: str = "Standard",
    model: str = "gpt-4-turbo-preview"
) -> list[dict]:
    """
    Lance un débat structuré, tour par tour, entre IA OM et IA PSG.
    """
    transcript: list[dict] = []
    logger.info(
        "DÉBUT DÉBAT — Format:%s — Tours:%d — OM Persona:%s — PSG Persona:%s — Model:%s",
        debate_format, max_turns, om_personality, psg_personality, model
    )

    # A) Contexte factuel enrichi
    ctx_om = (
        "=== Contexte OM (API & Wiki) ===\n"
        f"{get_om_enhanced_context()}\n"
        f"Wikipedia : {get_om_wiki_context()}\n"
        "================================\n"
    )
    ctx_psg = (
        "=== Contexte PSG (API & Wiki) ===\n"
        f"{get_psg_enhanced_context()}\n"
        f"Wikipedia : {get_psg_wiki_context()}\n"
        "=================================\n"
    )

    # B) Blocs persona détaillés
    persona_om  = get_persona_prompt("OM", om_personality, debate_format)
    persona_psg = get_persona_prompt("PSG", psg_personality, debate_format)

    # C) Directives strictes anti-confusion et anti-redite
    def build_directives(team_label: str, persona: str) -> str:
        lines = []
        if persona.lower() != "footix":
            lines.append(f"- Reste factuel et cite **seulement** les joueurs de {team_label}.")
        lines.append("- Intègre toujours la dernière réplique adverse pour rebondir.")
        lines.append("- Ne répète **jamais** tes propres phrases textuellement.")
        lines.append("- Sois concis et humain, comme dans une vraie discussion.")
        return "\n".join(lines)

    directives_om  = build_directives("l'OM", om_personality)
    directives_psg = build_directives("le PSG", psg_personality)

    # D) Prompt et tour #1 pour l'OM
    prompt_om = (
        f"{ctx_om}"
        "CI-DESSOUS : point de vue de l'OM\n"
        f"{persona_om}\n"
        f"Format : {debate_format}\n"
        f"{directives_om}\n"
        f"Question : {initial_question}\n"
        "Réponse OM :"
    )
    logger.info("Prompt OM initial prêt")
    raw_om = generate_response(prompt_om, model=model)
    om_resp = sanitize_response("OM", raw_om)
    transcript.append({"speaker": "OM", "message": om_resp})
    time.sleep(1)

    # E) Prompt et tour #1 pour le PSG
    prompt_psg = (
        f"{ctx_psg}"
        "CI-DESSOUS : point de vue du PSG\n"
        f"{persona_psg}\n"
        f"Format : {debate_format}\n"
        f"{directives_psg}\n"
        f"Réponse OM précédente : {om_resp}\n"
        f"Question : {initial_question}\n"
        "Réponse PSG :"
    )
    logger.info("Prompt PSG initial prêt")
    raw_psg = generate_response(prompt_psg, model=model)
    psg_resp = sanitize_response("PSG", raw_psg, previous=om_resp)
    transcript.append({"speaker": "PSG", "message": psg_resp})
    time.sleep(1)

    # F) Tours suivants (alternance OM ↔ PSG)
    turn = 2
    while turn < max_turns:
        # OM
        prompt_om_follow = (
            f"{ctx_om}"
            "CI-DESSOUS : point de vue de l'OM\n"
            f"{persona_om}\n"
            f"Format : {debate_format}\n"
            f"{directives_om}\n"
            f"Réponse PSG précédente : {psg_resp}\n"
            f"Question : {initial_question}\n"
            "Réponse OM :"
        )
        logger.info("Prompt OM (tour %d) prêt", turn + 1)
        raw_om = generate_response(prompt_om_follow, model=model)
        om_resp = sanitize_response("OM", raw_om, previous=psg_resp)
        transcript.append({"speaker": "OM", "message": om_resp})
        turn += 1
        time.sleep(1)
        if turn >= max_turns:
            break

        # PSG
        prompt_psg_follow = (
            f"{ctx_psg}"
            "CI-DESSOUS : point de vue du PSG\n"
            f"{persona_psg}\n"
            f"Format : {debate_format}\n"
            f"{directives_psg}\n"
            f"Réponse OM précédente : {om_resp}\n"
            f"Question : {initial_question}\n"
            "Réponse PSG :"
        )
        logger.info("Prompt PSG (tour %d) prêt", turn + 1)
        raw_psg = generate_response(prompt_psg_follow, model=model)
        psg_resp = sanitize_response("PSG", raw_psg, previous=om_resp)
        transcript.append({"speaker": "PSG", "message": psg_resp})
        turn += 1
        time.sleep(1)

    logger.info("FIN DEBATS — %d échanges générés", len(transcript))
    return transcript

# ——————————————————————————————————————————————
# CLI de test rapide
# ——————————————————————————————————————————————
if __name__ == "__main__":
    print("=== TEST DEBATS CLI ===")
    result = start_debate(
        initial_question="Quel club a le meilleur milieu de terrain ?",
        debate_format="Choc Ultime",
        max_turns=4,
        om_personality="Ultra",
        psg_personality="Ancien Joueur",
    )
    for msg in result:
        print(f"{msg['speaker']} :\n{msg['message']}\n{'-'*40}")