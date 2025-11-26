# Database Configuration

"""
Configuration de la connexion à la base de données MySQL.
Utilise SQLAlchemy pour l'ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

DATABASE_URL = Config.DATABASE_URL

engine = create_engine(DATABASE_URL, echo=Config.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency pour FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Importer les modèles pour qu'ils soient enregistrés avec Base
from . import user, event_type, calendar_event
