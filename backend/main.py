from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import meeting_orchestrator
import os

app = FastAPI(
    title="Planificateur de Réunions",
    version="2.0.0",
    description="API de planification de réunions avec agents LLM"
)

# Créer le répertoire temp_audio s'il n'existe pas
temp_audio_dir = os.path.join(os.path.dirname(__file__), 'temp_audio')
os.makedirs(temp_audio_dir, exist_ok=True)

# Servir les fichiers audio statiques
app.mount("/audio", StaticFiles(directory=temp_audio_dir), name="audio")

# Inclure les nouvelles routes pour l'orchestration multi-agent
app.include_router(meeting_orchestrator.router, prefix="/api/orchestrator", tags=["orchestrator"])

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue dans le Planificateur de Réunions",
        "version": "2.0.0",
        "features": [
            "Gestion des utilisateurs",
            "Gestion des événements",
            "Orchestration multi-agent avec LangChain",
            "Génération automatique d'invitations",
            "Sélection intelligente de créneaux"
        ]
    }
