import os
from enum import Enum

class Mode(Enum):
    AGGRESSIVE = "aggressive"
    FACTUAL    = "factual"
    ANALYTICAL = "analytical"

PERSONAS = {
    "OM": {
        "name": "Marseille Fervent",
        "tone": Mode.AGGRESSIVE.value,
    },
    "PSG": {
        "name": "Paris Analyste",
        "tone": Mode.FACTUAL.value,
    },
}

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "debate_engine", "prompt_templates")
TEMPLATES = {
    Mode.AGGRESSIVE.value: "aggressive.j2",
    Mode.FACTUAL.value:    "factual.j2",
    Mode.ANALYTICAL.value: "analytical.j2",
}

OLLAMA_HOST   = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL", "llama3.2-13b-q4_0")
FOOTBALL_API_KEY = "a6da6313243c42d189b3cbd50ebdc219"