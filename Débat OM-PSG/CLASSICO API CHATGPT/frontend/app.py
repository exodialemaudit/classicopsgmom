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

# Liste des modèles OpenAI disponibles
OPENAI_MODELS = [
    "gpt-4-turbo-preview",
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k"
]

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
  gap: 24px;
  padding: 24px 16px;
  animation: fadeInContainer 0.5s ease-out both;
  max-width: 800px;
  margin: 0 auto;
}

/* BULLES */
.chat-bubble {
  position: relative;
  max-width: 75%;
  padding: 16px 20px;
  border-radius: 20px;
  font-size: 1rem;
  line-height: 1.5;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin: 0;
  opacity: 0;
  transform: translateY(20px);
  animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  animation-delay: var(--delay, 0s);
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

/* HOVER EFFECT */
.chat-bubble:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

/* COLORS */
.chat-om {
  align-self: flex-start;
  background: linear-gradient(135deg, #F1F0F0 0%, #E8E8E8 100%);
  color: #000;
  margin-left: 48px;
  border: 1px solid rgba(0,0,0,0.05);
}
.chat-psg {
  align-self: flex-end;
  background: linear-gradient(135deg, #DCF8C6 0%, #C8E6B5 100%);
  color: #000;
  margin-right: 48px;
  border: 1px solid rgba(0,0,0,0.05);
}

/* TRIANGLE TAIL */
.chat-om::before,
.chat-psg::before {
  content: "";
  position: absolute;
  width: 0; height: 0;
  border: 12px solid transparent;
  top: 16px;
  filter: drop-shadow(-2px 2px 2px rgba(0,0,0,0.1));
}
.chat-om::before { 
  left: -24px; 
  border-right-color: #E8E8E8;
}
.chat-psg::before { 
  right: -24px; 
  border-left-color: #C8E6B5;
}

/* ICONS */
.chat-bubble .icon {
  position: absolute;
  top: 4px;
  width: 36px; height: 36px;
  border-radius: 50%;
  background-size: cover;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  border: 2px solid white;
  transition: transform 0.3s ease;
}
.chat-om .icon {
  left: -52px;
  background-image: url("https://crests.football-data.org/516.png");
}
.chat-psg .icon {
  right: -52px;
  background-image: url("https://crests.football-data.org/524.png");
}

.chat-bubble:hover .icon {
  transform: scale(1.1) rotate(5deg);
}

/* ANIMATIONS */
@keyframes slideIn {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInContainer {
  from { 
    opacity: 0;
    transform: translateY(10px);
  } 
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* TYPING INDICATOR */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  padding: 12px 20px;
  background: rgba(240, 240, 240, 0.9);
  border-radius: 20px;
  width: fit-content;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease-out;
}

.typing-indicator span {
  display: block;
  width: 10px; height: 10px;
  background: #666;
  border-radius: 50%;
  opacity: 0.4;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% { 
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Responsive Design */
@media (max-width: 768px) {
  .chat-bubble {
    max-width: 85%;
    font-size: 0.95rem;
  }
  .chat-container {
    padding: 16px 8px;
  }
}
</style>
""", unsafe_allow_html=True)


# ——————————————————————————————
# 4) Définitions des formats de débat
# ——————————————————————————————
FORMATS = {
    "Duel des Géants":  "Rounds punchy chronométrés, allez à l'essentiel.",
    "Choc Ultime":       "Mode clash : provocations cinglantes (sans injures trop fortes).",
    "Analytique 360°":   "Deep-dive factuel et tactique : stats, schémas, jargon spécialisé.",
    "Happy Hour":        "Ton relax, humour et chambrage autour d'une bière virtuelle."
}

# ——————————————————————————————
# 5) Barre latérale : options de débat
# ——————————————————————————————
st.sidebar.title('Configuration du débat')

# Sélection du modèle OpenAI
openai_model = st.sidebar.selectbox(
    'Modèle OpenAI',
    options=OPENAI_MODELS,
    index=0,
    help="Choisissez le modèle OpenAI à utiliser pour le débat"
)

subject = st.sidebar.text_input(
    'Sujet du débat',
    value="Quel club a le meilleur milieu de terrain ?"
)

debate_format = st.sidebar.selectbox(
    'Format de débat',
    options=list(FORMATS.keys()),
    index=list(FORMATS.keys()).index("Analytique 360°")
)
st.sidebar.caption(FORMATS[debate_format])

turns = st.sidebar.slider(
    'Nombre de tours (OM + PSG)',
    min_value=2, max_value=10, value=4
)

om_personality = st.sidebar.selectbox(
    'Personnalité OM',
    options=list(PERSONALITIES.keys()),
    index=list(PERSONALITIES.keys()).index("Standard")
)
st.sidebar.caption(PERSONALITIES[om_personality])

psg_personality = st.sidebar.selectbox(
    'Personnalité PSG',
    options=list(PERSONALITIES.keys()),
    index=list(PERSONALITIES.keys()).index("Standard")
)
st.sidebar.caption(PERSONALITIES[psg_personality])

st.sidebar.markdown("")  # petit espace
run_button = st.sidebar.button('Lancer le débat')

# ——————————————————————————————
# 6) Titre principal
# ——————————————————————————————
st.title('Football Debate: OM vs PSG')
st.markdown("## Engagez-vous dans un débat passionné entre deux IA supportant l'OM et le PSG !")

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
        psg_personality=psg_personality,
        model=openai_model
    )

    # 7.3) Effacer le "typing"
    placeholder.empty()

    st.markdown("---")
    st.subheader('Résultats du débat')

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