"""
Routes pour l'orchestration de réunions avec agents LLM
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from services.meeting_orchestrator import MeetingOrchestrator
from pydantic import BaseModel
from typing import List
from datetime import datetime
from dateutil import parser as date_parser

router = APIRouter()


def parse_flexible_date(date_string: str) -> datetime:
    """
    Parse une date depuis différents formats possibles
    
    Formats acceptés:
    - ISO: 2025-12-15T10:00:00 ou 2025-12-15
    - Français: 15/12/2025
    - Autres formats courants
    
    Args:
        date_string: La date sous forme de string
        
    Returns:
        datetime object
        
    Raises:
        ValueError: Si le format n'est pas reconnu
    """
    try:
        # Essayer d'abord le format ISO
        return datetime.fromisoformat(date_string)
    except ValueError:
        pass
    
    try:
        # Essayer avec dateutil qui supporte beaucoup de formats
        # dayfirst=True pour privilégier le format européen (jour/mois/année)
        return date_parser.parse(date_string, dayfirst=True)
    except Exception as e:
        raise ValueError(f"Format de date non reconnu: '{date_string}'. "
                        f"Formats acceptés: ISO (2025-12-15T10:00:00), "
                        f"Français (15/12/2025), etc.")


class MeetingPlanRequest(BaseModel):
    """Modèle de requête pour planifier une réunion via texte naturel"""
    text: str


class MeetingRescheduleRequest(BaseModel):
    """Modèle de requête pour replanifier une réunion"""
    event_id: int
    new_preferred_dates: List[str]  # ISO format
    reason: str = ""


@router.post("/plan-meeting")
def plan_meeting(
    request: MeetingPlanRequest,
    db: Session = Depends(get_db)
):
    """
    Planifie une réunion en utilisant l'orchestrateur multi-agent
    
    L'orchestrateur va:
    1. Récupérer les disponibilités via les endpoints existants
    2. Utiliser le LLM pour choisir le meilleur créneau
    3. Utiliser l'agent de rédaction pour créer l'invitation
    4. Créer les événements dans le calendrier
    
    Args:
        request: Détails de la réunion à planifier
        db: Session de base de données
        
    Returns:
        Détails complets de la réunion planifiée avec invitation
    """
    try:
        # Initialiser l'orchestrateur
        orchestrator = MeetingOrchestrator()
        
        # Planifier la réunion
        result = orchestrator.plan_meeting(
            db=db,
            request_text=request.text
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur de planification"))
        
        # Retourner directement le résultat de l'orchestrateur
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Format de date invalide: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la planification: {str(e)}")