"""
Routes pour l'orchestration de réunions avec agents LLM
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from models.database import get_db
from services.meeting_orchestrator import MeetingOrchestrator
from services.s2t import s2t
from pydantic import BaseModel
from typing import List
from datetime import datetime
from dateutil import parser as date_parser
import os
import uuid
import io
import soundfile as sf
import numpy as np

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


@router.post("/meeting/text")
def meeting_from_text(
    request: MeetingPlanRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour traiter une requête texte directement.
    Appelle l'orchestrateur avec le texte brut.
    
    Args:
        request: Contient le texte de la demande de réunion
        db: Session de base de données
        
    Returns:
        Résultat de la planification avec texte et audio
    """
    try:
        orchestrator = MeetingOrchestrator()
        
        # Planifier la réunion avec le texte
        result = orchestrator.plan_meeting(
            db=db,
            request_text=request.text
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur de planification"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")


@router.post("/meeting/audio")
async def meeting_from_audio(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint pour traiter une requête audio.
    Convertit l'audio en texte avec s2t, puis appelle l'orchestrateur.
    
    Args:
        audio: Fichier audio uploadé
        db: Session de base de données
        
    Returns:
        Résultat de la planification avec texte et audio
    """
    try:
        # Créer un répertoire temporaire pour l'audio
        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_audio')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Lire le contenu du fichier audio
        content = await audio.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Fichier audio vide")
        
        # Convertir l'audio en WAV avec soundfile
        # Charger l'audio depuis les bytes
        audio_io = io.BytesIO(content)
        try:
            # Essayer de lire l'audio avec soundfile
            data, samplerate = sf.read(audio_io)
        except Exception:
            # Si soundfile ne peut pas lire, essayer avec scipy pour WAV
            from scipy.io import wavfile
            audio_io.seek(0)
            samplerate, data = wavfile.read(audio_io)
            # Normaliser si nécessaire
            if data.dtype != np.float32:
                data = data.astype(np.float32) / np.iinfo(data.dtype).max
        
        # Sauvegarder en WAV
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(temp_dir, audio_filename)
        sf.write(audio_path, data, samplerate, format='WAV')
        
        # Convertir l'audio en texte avec s2t
        transcribed_text = s2t(audio_path)
        
        # Nettoyer les guillemets JSON si présents
        if transcribed_text.startswith('"') and transcribed_text.endswith('"'):
            transcribed_text = transcribed_text[1:-1]
        
        # Supprimer le fichier temporaire
        try:
            os.remove(audio_path)
        except:
            pass
        
        # Planifier la réunion avec le texte transcrit
        orchestrator = MeetingOrchestrator()
        result = orchestrator.plan_meeting(
            db=db,
            request_text=transcribed_text
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur de planification"))
        
        # Ajouter le texte transcrit dans la réponse
        result["transcribed_text"] = transcribed_text
        
        return result
        
    except Exception as e:
        # Nettoyer le fichier en cas d'erreur
        try:
            if 'audio_path' in locals():
                os.remove(audio_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement audio: {str(e)}")