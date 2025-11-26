# Configuration du projet
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    # Base de données
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/meeting_planner")

    # Autres configs (ex. : clés API, ports, etc.)
    APP_NAME = "Planificateur de Réunions"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"