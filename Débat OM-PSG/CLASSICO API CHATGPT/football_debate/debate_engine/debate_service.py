#!/usr/bin/env python3
"""
Module: debate_service.py
Description:
    Orchestre un débat entre deux IA (OM vs PSG) sur un sujet donné, en utilisant
    le Conversation Manager pour gérer les tours de parole et l'LLM Interface
    pour générer les réponses.
    Fournit également :
      - validation des entrées (formats et personas)
      - génération d'un ID unique de débat
      - mesure des durées de génération
      - export optionnel du transcript en JSON
      - CLI avancé avec options de logging et sortie
"""

import logging
import uuid
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

from football_debate.debate_engine.conversation_manager import start_debate
from football_debate.debate_engine.persona_manager import PERSONALITIES

# Formats valides (doivent correspondre à ceux exposés dans l'UI)
VALID_FORMATS = [
    "Duel des Géants",
    "Choc Ultime",
    "Analytique 360°",
    "Happy Hour"
]

# Logger global
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def validate_args(
    topic: str,
    debate_format: str,
    max_turns: int,
    om_personality: str,
    psg_personality: str
) -> None:
    """
    Vérifie que les arguments fournis sont cohérents.
    Lève ValueError si invalide.
    """
    if not topic.strip():
        raise ValueError("Le sujet du débat ne peut pas être vide.")
    if debate_format not in VALID_FORMATS:
        raise ValueError(f"Format inconnu : '{debate_format}'. Formats valides : {VALID_FORMATS}")
    if max_turns < 2 or max_turns % 1 != 0:
        raise ValueError("Le nombre de tours doit être un entier >= 2.")
    if om_personality not in PERSONALITIES:
        raise ValueError(f"Persona OM inconnu : '{om_personality}'. Personas valides : {list(PERSONALITIES.keys())}")
    if psg_personality not in PERSONALITIES:
        raise ValueError(f"Persona PSG inconnu : '{psg_personality}'. Personas valides : {list(PERSONALITIES.keys())}")


def process_debate(
    topic: str,
    debate_format: str = "Analytique 360°",
    max_turns: int = 4,
    om_personality: str = "Standard",
    psg_personality: str = "Standard",
    output_file: Optional[str] = None,
    log_level: str = "INFO",
    model: str = "gpt-4-turbo-preview"
) -> List[Dict[str, Any]]:
    """
    Lance un débat structuré et retourne la liste des messages avec métadonnées.

    Args:
        topic           (str): Sujet du débat
        debate_format   (str): Format du débat
        max_turns       (int): Nombre total de tours (OM+PSG)
        om_personality  (str): Persona pour OM
        psg_personality (str): Persona pour PSG
        output_file     (str): Chemin du fichier JSON pour sauvegarder le transcript
        log_level       (str): Niveau de log (DEBUG, INFO, WARNING, ERROR)
        model          (str): Modèle OpenAI à utiliser

    Returns:
        List[dict]: Chaque dict contient :
            - debate_id       : identifiant unique
            - timestamp       : ISO du début de génération
            - speaker         : 'OM' ou 'PSG'
            - message         : texte généré (post-sanitization)
            - generation_time : durée (en secondes) de l'appel LLM
    """
    # Configurer le level de log
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Validation des arguments
    validate_args(topic, debate_format, max_turns, om_personality, psg_personality)

    debate_id = str(uuid.uuid4())
    logger.info(
        "Démarrage débat %s - Sujet: '%s', Format: '%s', Tours: %d, OM: '%s', PSG: '%s', Model: '%s'",
        debate_id, topic, debate_format, max_turns, om_personality, psg_personality, model
    )

    # Lancer la conversation
    start_time = datetime.utcnow()
    raw_transcript = start_debate(
        initial_question=topic,
        debate_format=debate_format,
        max_turns=max_turns,
        om_personality=om_personality,
        psg_personality=psg_personality,
        model=model
    )
    end_time = datetime.utcnow()
    total_duration = (end_time - start_time).total_seconds()

    # Enrichir le transcript avec métadonnées
    enriched: List[Dict[str, Any]] = []
    for idx, entry in enumerate(raw_transcript, start=1):
        enriched.append({
            "debate_id": debate_id,
            "timestamp": datetime.utcnow().isoformat(),
            "turn": idx,
            "speaker": entry["speaker"],
            "message": entry["message"],
            "generation_time": None  # disponible si on mesure individuellement
        })

    logger.info(
        "Débat %s terminé en %.2f s, %d messages générés",
        debate_id, total_duration, len(enriched)
    )

    # Sauvegarde optionnelle
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "debate_id": debate_id,
                        "topic": topic,
                        "format": debate_format,
                        "max_turns": max_turns,
                        "om_personality": om_personality,
                        "psg_personality": psg_personality,
                        "started_at": start_time.isoformat(),
                        "ended_at": end_time.isoformat(),
                        "duration_s": total_duration
                    },
                    "messages": enriched
                }, f, ensure_ascii=False, indent=2)
            logger.info("Transcript enregistré dans '%s'", output_file)
        except Exception as e:
            logger.error("Erreur sauvegarde transcript: %s", e)

    return enriched


if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description="Lancer un débat OM vs PSG")
    parser.add_argument("topic", help="Sujet du débat")
    parser.add_argument(
        "--debate-format", dest="debate_format",
        choices=VALID_FORMATS, default="Analytique 360°",
        help="Format du débat"
    )
    parser.add_argument(
        "--max-turns", dest="max_turns", type=int,
        default=4, help="Nombre de tours (OM + PSG)"
    )
    parser.add_argument(
        "--om-personality", dest="om_personality",
        choices=list(PERSONALITIES.keys()), default="Standard",
        help="Personnalité de l'OM"
    )
    parser.add_argument(
        "--psg-personality", dest="psg_personality",
        choices=list(PERSONALITIES.keys()), default="Standard",
        help="Personnalité du PSG"
    )
    parser.add_argument(
        "--output-file", dest="output_file",
        help="Chemin pour sauvegarder le transcript au format JSON"
    )
    parser.add_argument(
        "--log-level", dest="log_level",
        choices=["DEBUG","INFO","WARNING","ERROR"], default="INFO",
        help="Niveau de log"
    )
    args = parser.parse_args()

    debate = process_debate(
        topic=args.topic,
        debate_format=args.debate_format,
        max_turns=args.max_turns,
        om_personality=args.om_personality,
        psg_personality=args.psg_personality,
        output_file=args.output_file,
        log_level=args.log_level
    )
    for msg in debate:
        print(f"[{msg['turn']:02d}] {msg['speaker']}: {msg['message']}")
