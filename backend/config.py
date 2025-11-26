# Configuration du projet
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    # Base de données
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/meeting_planner")

    # Configuration Groq API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Modèles LLM (Groq)
    ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "openai/gpt-oss-120b")
    INVITATION_MODEL = os.getenv("INVITATION_MODEL", "openai/gpt-oss-120b")
    
    # Température des modèles
    ORCHESTRATOR_TEMPERATURE = float(os.getenv("ORCHESTRATOR_TEMPERATURE", "0.3"))
    INVITATION_TEMPERATURE = float(os.getenv("INVITATION_TEMPERATURE", "0.7"))

    # Autres configs (ex. : clés API, ports, etc.)
    APP_NAME = "Planificateur de Réunions"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Configuration Email SMTP
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    
    # Signature des emails
    EMAIL_SIGNATURE = os.getenv("EMAIL_SIGNATURE", """Cordialement,
L'équipe du Planificateur de Réunions""")
