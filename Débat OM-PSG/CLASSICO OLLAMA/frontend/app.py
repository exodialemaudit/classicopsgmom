# frontend/app.py
import os
import sys
import streamlit as st
import time

# ——————————————————————————————
# 1) Permettre à Python de trouver ton module football_debate
# ——————————————————————————————
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ——————————————————————————————
# 2) Import de ton service de débat et des personnalités
# ——————————————————————————————
from football_debate.debate_engine.debate_service import process_debate
from football_debate.debate_engine.persona_manager import PERSONALITIES

# ——————————————————————————————
# 3) Configuration de la page et injection CSS
# ——————————————————————————————
st.set_page_config(
    page_title="Football Debate: OM vs PSG",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
/* CONTAINER */
.chat-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 8px;
  animation: fadeInContainer 0.5s ease-out both;
}

/* BULLES */
.chat-bubble {
  position: relative;
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 0.9rem;
  line-height: 1.4;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  margin: 0;
  opacity: 0;
  transform: scale(0.8);
  animation: popIn 0.3s ease-out forwards;
  animation-delay: var(--delay, 0s);
}

/* HOVER EFFECT */
.chat-bubble:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* COLORS */
.chat-om {
  align-self: flex-start;
  background: #F1F0F0;
  color: #000;
}
.chat-psg {
  align-self: flex-end;
  background: #DCF8C6;
  color: #000;
}

/* TRIANGLE TAIL */
.chat-om::after,
.chat-psg::after {
  content: "";
  position: absolute;
  width: 0; height: 0;
  border: 8px solid transparent;
  top: 16px;
}
.chat-om::after { left: -16px; border-right-color: #F1F0F0; }
.chat-psg::after { right: -16px; border-left-color: #DCF8C6; }

/* ICONS */
.chat-bubble .icon {
  position: absolute;
  top: 4px;
  width: 28px; height: 28px;
  border-radius: 50%;
  background-size: cover;
}
.chat-om .icon {
  left: -40px;
  background-image: url("https://crests.football-data.org/516.png");
}
.chat-psg .icon {
  right: -40px;
  background-image: url("https://crests.football-data.org/524.png");
}

/* ANIMATIONS */
@keyframes popIn {
  to { opacity: 1; transform: scale(1); }
}
@keyframes fadeInContainer {
  from { opacity: 0; } to { opacity: 1; }
}

/* TYPING INDICATOR */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}
.typing-indicator span {
  display: block;
  width: 8px; height: 8px;
  background: #ccc;
  border-radius: 50%;
  opacity: 0.4;
  animation: blink 1s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0%, 80%, 100% { opacity: 0.4; }
  40%           { opacity: 1;   }
}
</style>
""", unsafe_allow_html=True)

# ——————————————————————————————
# 4) Définitions des formats de débat (4 formats seulement)
# ——————————————————————————————
FORMATS = {
    "Duel des Géants":  "Rounds punchy chronométrés, allez à l’essentiel.",
    "Choc Ultime":       "Mode clash : provocations cinglantes (sans injures trop fortes).",
    "Analytique 360°":   "Deep-dive factuel et tactique : stats, schémas, jargon spécialisé.",
    "Happy Hour":        "Ton relax, humour et chambrage autour d’une bière virtuelle."
}

# ——————————————————————————————
# 5) Barre latérale : options de débat
# ——————————————————————————————
st.sidebar.title("Configuration du débat")

subject = st.sidebar.text_input(
    "Sujet du débat",
    value="Quel club a le meilleur milieu de terrain ?"
)

debate_format = st.sidebar.selectbox(
    "Format de débat",
    options=list(FORMATS.keys()),
    index=list(FORMATS.keys()).index("Analytique 360°")
)
st.sidebar.caption(FORMATS[debate_format])

turns = st.sidebar.slider(
    "Nombre de tours (OM + PSG)",
    min_value=2, max_value=10, value=4
)

om_personality = st.sidebar.selectbox(
    "Personnalité OM",
    options=list(PERSONALITIES.keys()),
    index=list(PERSONALITIES.keys()).index("Standard")
)
st.sidebar.caption(PERSONALITIES[om_personality])

psg_personality = st.sidebar.selectbox(
    "Personnalité PSG",
    options=list(PERSONALITIES.keys()),
    index=list(PERSONALITIES.keys()).index("Standard")
)
st.sidebar.caption(PERSONALITIES[psg_personality])

st.sidebar.markdown("")  # petit espace
run_button = st.sidebar.button("💬 Lancer le débat")

# ——————————————————————————————
# 6) Titre principal
# ——————————————————————————————
st.title("⚽ Football Debate: OM vs PSG")
st.markdown("## Engagez-vous dans un débat passionné entre deux IA supportant l’OM et le PSG !")

# ——————————————————————————————
# 7) Lancement du débat
# ——————————————————————————————
if run_button:
    # 7.1) Indicateur de frappe
    placeholder = st.empty()
    placeholder.markdown(
        '<div class="typing-indicator">'
        '<span></span><span></span><span></span>'
        '</div>',
        unsafe_allow_html=True
    )

    # 7.2) Appel au moteur de débat
    transcript = process_debate(
        subject,
        debate_format=debate_format,
        max_turns=turns,
        om_personality=om_personality,
        psg_personality=psg_personality
    )

    # 7.3) Effacer le “typing”
    placeholder.empty()

    st.markdown("---")
    st.subheader("Résultats du débat")

    # 8) Affichage dans le conteneur chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, turn in enumerate(transcript):
        speaker = turn["speaker"]
        message = turn["message"]
        cls = "chat-om" if speaker == "OM" else "chat-psg"
        # on décale chaque bulle de 0.1s supplémentaire
        bubble_html = (
            f'<div class="chat-bubble {cls}" style="--delay: {i * 0.1}s;">'
            f'<div class="icon"></div>'
            f'{message}'
            f'</div>'
        )
        st.markdown(bubble_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)