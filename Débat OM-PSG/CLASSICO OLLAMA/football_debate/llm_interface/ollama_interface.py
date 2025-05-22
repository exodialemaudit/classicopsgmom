#!/usr/bin/env python3
"""
Interface pour appeler Llama via l'outil de commande Ollama.
Plutôt que d'utiliser l'API HTTP, on invoque directement le binaire 'ollama run'.
"""

import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generate_response(prompt: str, model: str = "llama3.2") -> str:
    """
    Envoie un prompt au modèle via la commande Ollama et renvoie la réponse générée.

    Args:
        prompt (str): Le texte à envoyer au modèle.
        model  (str): Le nom du modèle à invoquer (par défaut "llama3.2").

    Returns:
        str: La réponse du modèle, ou chaîne vide en cas d'erreur.
    """
    cmd = ["ollama", "run", model, prompt]
    logging.info("Exécution de la commande : %s", " ".join(cmd))
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error("Erreur Ollama (subprocess) : %s", e)
        return ""
    except FileNotFoundError:
        logging.error("Command 'ollama' introuvable : avez-vous installé Ollama ?")
        return ""