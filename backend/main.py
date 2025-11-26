from fastapi import FastAPI
from routes import meeting_orchestrator

app = FastAPI(
    title="Planificateur de Réunions",
    version="2.0.0",
    description="API de planification de réunions avec agents LLM"
)

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
