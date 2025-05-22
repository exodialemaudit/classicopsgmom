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

OPENAI_API_KEY="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"
FOOTBALL_API_KEY = "a6da6313243c42d189b3cbd50ebdc219"