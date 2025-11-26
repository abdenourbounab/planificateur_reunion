import streamlit as st
import uuid
import os
from datetime import datetime
from gtts import gTTS
from agent_api import send_to_agents_audio, send_to_agents_text

# -----------------------------------------
# CONFIG DEMO / BACKEND
# -----------------------------------------
USE_FAKE = False   # ← mettre False quand ton équipe backend sera prête

# -----------------------------------------
# STREAMLIT CONFIG
# -----------------------------------------
st.set_page_config(page_title="Planificateur Intelligent", layout="wide")

# -----------------------------------------
# SESSION STATE INIT
# -----------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# -----------------------------------------
# MODE SOMBRE / CLAIR
# -----------------------------------------
mode = st.sidebar.radio("🎨 Mode", ["Clair", "Sombre"])

if mode == "Sombre":
    st.session_state.dark_mode = True
else:
    st.session_state.dark_mode = False

# THEME COLORS
if st.session_state.dark_mode:
    background = "#1e1e1e"
    text_color = "white"
    card_bg = "#2c2c2c"
    bubble_vocal = "#c62828"
    bubble_text = "#1565c0"
    history_bg = "#2c2c2c"
else:
    background = "linear-gradient(135deg, #d0e8ff, #bbdefb)"
    text_color = "black"
    card_bg = "white"
    bubble_vocal = "#e53935"
    bubble_text = "#1e88e5"
    history_bg = "white"

# -----------------------------------------
# CSS
# -----------------------------------------
st.markdown(f"""
<style>
body {{
    background: {background};
    color: {text_color};
}}
.card {{
    background:{card_bg};
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
    box-shadow:0px 6px 18px rgba(0,0,0,0.12);
}}
.section-title {{ font-size:22px; font-weight:700; }}
.result-item {{
    margin-bottom:8px;
    padding:10px;
    background:#eef4ff;
    border-left:5px solid #1565c0;
    border-radius:10px;
}}
.agent-log {{
    padding:15px;
    background:#f5f5f5;
    border-radius:10px;
    border-left: 5px solid #90caf9;
    margin-bottom:10px;
}}
.message-bubble {{
    padding: 12px 15px;
    border-radius: 15px;
    margin-bottom: 8px;
    color: white;
    max-width: 90%;
}}
.vocal {{ background-color: {bubble_vocal}; }}
.textmsg {{ background-color: {bubble_text}; }}
.timestamp {{
    font-size: 12px;
    color: #bbb;
}}
.history-box {{
    background: {history_bg};
    padding: 15px;
    border-radius: 15px;
    height: 88vh;
    overflow-y: scroll;
    display: flex;
    flex-direction: column-reverse;
}}
.separator {{
    border-left: 2px solid #cccccc;
    height: 88vh;
    margin: auto;
}}
.stButton>button {{
    background:linear-gradient(90deg, #1e88e5,#1565c0);
    color:white;
    border:none;
    padding:12px 20px;
    border-radius:10px;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# LAYOUT
# -----------------------------------------
col_history, col_sep, col_main = st.columns([1.2, 0.05, 3])

# -----------------------------------------
# HISTORIQUE
# -----------------------------------------
with col_history:

    st.markdown("### 📜 Historique")

    if st.button("🗑️ Effacer l'historique"):
        st.session_state.history = []
        st.rerun()

    st.markdown("<div class='history-box'>", unsafe_allow_html=True)

    for entry in st.session_state.history:
        bubble_class = "vocal" if entry["type"] == "vocal" else "textmsg"
        st.markdown(
            f"<div class='message-bubble {bubble_class}'>{entry['content']}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='timestamp'>🕒 {entry['time']}</div>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------
# SÉPARATEUR
# -----------------------------------------
with col_sep:
    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# -----------------------------------------
# INTERFACE PRINCIPALE
# -----------------------------------------
with col_main:

    st.title("Planificateur de Réunion Multi-Agents")
    st.write("Laissez une note vocale ou saisissez un texte, puis laissez les agents travailler !")

    # --- CARD AUDIO + TEXTE ---
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col_audio, col_text = st.columns(2)

    with col_audio:
        audio = st.audio_input("🎙️ Enregistrer une note vocale")

    with col_text:
        user_text = st.text_area("✏️ Saisir un texte", placeholder="Décrivez la réunion...")

    st.markdown("</div>", unsafe_allow_html=True)

    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = None

    # AUDIO
    if audio:
        audio_path = f"{temp_dir}/{uuid.uuid4()}.wav"
        with open(audio_path, "wb") as f:
            f.write(audio.getvalue())

        st.session_state.history.insert(0, {
            "type": "vocal",
            "content": "🎤 Note vocale envoyée",
            "time": datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        })

        st.success("Audio bien enregistré !")
        st.audio(audio)

    # TEXTE
    if user_text.strip():
        st.session_state.history.insert(0, {
            "type": "text",
            "content": user_text,
            "time": datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        })

    # -----------------------------------------
    # BOUTON LANCER AGENTS
    # -----------------------------------------
    if st.button("Lancer les Agents"):

        # MODE DÉMO — AUCUN BACKEND NÉCESSAIRE
        if USE_FAKE:
            response = {
                "participants": ["Karim", "Fatou", "Alice"],
                "subject": "Réunion de coordination du projet",
                "possible_dates": ["2025-11-29", "2025-11-30"],
                "validated_slot": "2025-11-30 14:00",
                "invitation_message": "Bonjour, la réunion est programmée le 30 novembre à 14h.",
                "logs": {
                    "agent1": "Extraction réussie.",
                    "agent2": "Disponibilités validées.",
                    "agent3": "Message final généré."
                }
            }
        else:
            # MODE BACKEND RÉEL
            if audio_path:
                response = send_to_agents_audio(audio_path)
            else:
                response = send_to_agents_text(user_text)

        # -------------------------------------
        # AFFICHAGE DES RÉSULTATS
        # -------------------------------------
        st.subheader("Résultat du Travail des Agents")

        # Agent 1
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Extraction des informations</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='result-item'><b>Participants :</b> {', '.join(response['participants'])}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='result-item'><b>Objet :</b> {response['subject']}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='result-item'><b>Dates possibles :</b> {', '.join(response['possible_dates'])}</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Agent 2
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Vérification de disponibilité</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='result-item'><b>Créneau validé :</b> {response['validated_slot']}</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Agent 3
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Message d'invitation</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='result-item'>{response['invitation_message']}</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # TTS
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Synthèse vocale (TTS)</div>", unsafe_allow_html=True)
        tts_path = f"{temp_dir}/tts_{uuid.uuid4()}.mp3"
        tts = gTTS(text=response["invitation_message"], lang="fr")
        tts.save(tts_path)
        st.success("La réponse a été convertie en audio !")
        st.audio(tts_path)
        st.markdown("</div>", unsafe_allow_html=True)

       
