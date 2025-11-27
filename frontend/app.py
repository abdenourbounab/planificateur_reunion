import streamlit as st
import uuid
import os
import requests
from datetime import datetime
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
# THEME COLORS (MODE SOMBRE)
# -----------------------------------------
background = "#1e1e1e"
text_color = "white"
card_bg = "#2c2c2c"
bubble_vocal = "#c62828"
bubble_text = "#1565c0"

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
    background:{card_bg};
    border-left:5px solid #1565c0;
    border-radius:10px;
    color: {text_color};
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
    max-width: 100%;
}}
.vocal {{ background-color: {bubble_vocal}; }}
.textmsg {{ background-color: {bubble_text}; }}
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
# INTERFACE PRINCIPALE
# -----------------------------------------
st.title("Planificateur de Réunion Multi-Agents")
st.write("Laissez une note vocale ou saisissez un texte, puis laissez les agents travailler !")

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

    st.success("Audio bien enregistré !")
    st.audio(audio)

# -----------------------------------------
# BOUTON LANCER AGENTS
# -----------------------------------------
if st.button("Lancer les Agents"):
    
    # Afficher le message utilisateur
    if audio:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 👤 Votre demande")
        st.markdown(
            f"<div class='message-bubble vocal'>🎤 Note vocale envoyée</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
    elif user_text.strip():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 👤 Votre demande")
        st.markdown(
            f"<div class='message-bubble textmsg'>{user_text}</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # MODE DÉMO — AUCUN BACKEND NÉCESSAIRE
    if USE_FAKE:
        response = {
            "success": True,
            "message": "Bonjour, la réunion est programmée le 30 novembre à 14h.",
            "participants": ["Karim", "Fatou", "Alice"],
            "subject": "Réunion de coordination du projet",
            "possible_dates": ["2025-11-29", "2025-11-30"],
            "validated_slot": "2025-11-30 14:00",
            "invitation_message": "Bonjour, la réunion est programmée le 30 novembre à 14h.",
            "audio_path": None,
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
        elif user_text.strip():
            response = send_to_agents_text(user_text)
        else:
            st.error("❌ Veuillez fournir un audio ou un texte")
            response = None

    # -------------------------------------
    # AFFICHAGE DES RÉSULTATS
    # -------------------------------------
    if response and response.get("success"):
        st.markdown("---")
        st.markdown("### 🤖 Réponse de l'assistant")
        
        # Afficher le message de réponse
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='message-bubble' style='background-color: #4caf50; color: white;'>{response.get('message', 'Réunion planifiée avec succès')}</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Afficher l'audio si disponible
        if response.get("audio_path"):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🔊 Synthèse vocale</div>", unsafe_allow_html=True)
            
            # Construire l'URL de l'audio
            audio_filename = os.path.basename(response["audio_path"])
            audio_url = f"http://localhost:8000/audio/{audio_filename}"
            
            try:
                # Télécharger l'audio depuis le backend
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    # Sauvegarder localement pour streamlit
                    local_audio_path = f"{temp_dir}/response_{uuid.uuid4()}.wav"
                    with open(local_audio_path, "wb") as f:
                        f.write(audio_response.content)
                    st.audio(local_audio_path)
                else:
                    st.warning("⚠️ Audio non disponible")
            except Exception as e:
                st.warning(f"⚠️ Impossible de charger l'audio: {str(e)}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Afficher les détails si disponibles
        if response.get("details"):
            details = response["details"]
            
            # Informations sur la réunion
            if details.get("meeting"):
                meeting = details["meeting"]
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>📅 Détails de la réunion</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='result-item'><b>Sujet :</b> {meeting.get('subject', 'N/A')}</div>",
                    unsafe_allow_html=True
                )
                if meeting.get("selected_slot"):
                    slot = meeting["selected_slot"]
                    st.markdown(
                        f"<div class='result-item'><b>Créneau :</b> {slot.get('start', 'N/A')} - {slot.get('end', 'N/A')}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Participants
            if details.get("participants"):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>👥 Participants</div>", unsafe_allow_html=True)
                participant_names = [p.get('name', 'N/A') for p in details["participants"]]
                st.markdown(
                    f"<div class='result-item'>{', '.join(participant_names)}</div>",
                    unsafe_allow_html=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
        
    elif response:
        # Afficher l'erreur
        st.error(f"❌ Erreur: {response.get('error', 'Erreur inconnue')}")

       
