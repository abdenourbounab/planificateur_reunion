"""
Service de disponibilités
Récupère les disponibilités des participants via les endpoints existants
"""
from sqlalchemy.orm import Session
from services.calendar_event_service import CalendarEventService
from services.user_service import UserService
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class AvailabilityService:
    """Service pour gérer les disponibilités des participants"""
    
    @staticmethod
    def get_user_events_in_range(
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List:
        """
        Récupère tous les événements d'un utilisateur dans une période donnée
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements du calendrier
        """
        events = CalendarEventService.get_events_by_user(db, user_id)
        
        # Filtrer les événements dans la période
        filtered_events = [
            event for event in events
            if event.start_datetime >= start_date and event.end_datetime <= end_date
        ]
        
        return filtered_events
    
    @staticmethod
    def get_available_slots(
        db: Session,
        participant_ids: List[int],
        start_date: datetime,
        end_date: datetime,
        meeting_duration_minutes: int = 60,
        work_hours: Tuple[int, int] = (9, 18)  # 9h-18h par défaut
    ) -> List[Dict]:
        """
        Trouve les créneaux disponibles pour tous les participants
        
        Args:
            db: Session de base de données
            participant_ids: Liste des IDs des participants
            start_date: Date de début de recherche
            end_date: Date de fin de recherche
            meeting_duration_minutes: Durée de la réunion en minutes
            work_hours: Tuple (heure_debut, heure_fin) des heures de travail
            
        Returns:
            Liste des créneaux disponibles avec score de disponibilité
        """
        # Récupérer tous les événements de tous les participants
        all_busy_slots = []
        
        for user_id in participant_ids:
            user_events = AvailabilityService.get_user_events_in_range(
                db, user_id, start_date, end_date
            )
            all_busy_slots.extend([
                (event.start_datetime, event.end_datetime) 
                for event in user_events
            ])
        
        # Générer les créneaux possibles
        available_slots = []
        current_date = start_date.replace(hour=work_hours[0], minute=0, second=0, microsecond=0)
        meeting_duration = timedelta(minutes=meeting_duration_minutes)
        
        while current_date < end_date:
            # Ignorer les week-ends
            if current_date.weekday() >= 5:  # 5 = Samedi, 6 = Dimanche
                current_date += timedelta(days=1)
                current_date = current_date.replace(hour=work_hours[0], minute=0)
                continue
            
            # Vérifier si on est dans les heures de travail
            if current_date.hour >= work_hours[1]:
                current_date += timedelta(days=1)
                current_date = current_date.replace(hour=work_hours[0], minute=0)
                continue
            
            slot_end = current_date + meeting_duration
            
            # Vérifier si le créneau ne dépasse pas les heures de travail
            if slot_end.hour > work_hours[1] or (slot_end.hour == work_hours[1] and slot_end.minute > 0):
                current_date += timedelta(days=1)
                current_date = current_date.replace(hour=work_hours[0], minute=0)
                continue
            
            # Vérifier si le créneau est libre pour tous
            is_free = True
            conflicts = 0
            
            for busy_start, busy_end in all_busy_slots:
                # Vérifier chevauchement
                if not (slot_end <= busy_start or current_date >= busy_end):
                    is_free = False
                    conflicts += 1
            
            if is_free:
                available_slots.append({
                    "start": current_date,
                    "end": slot_end,
                    "conflicts": 0,
                    "score": 100  # Score de 100 si aucun conflit
                })
            
            # Avancer de 30 minutes
            current_date += timedelta(minutes=30)
        
        return available_slots
    
    @staticmethod
    def format_slots_for_llm(slots: List[Dict]) -> str:
        """
        Formate les créneaux disponibles pour le LLM
        
        Args:
            slots: Liste des créneaux disponibles
            
        Returns:
            String formaté pour le LLM
        """
        if not slots:
            return "Aucun créneau disponible trouvé."
        
        formatted = "Créneaux disponibles:\n\n"
        for i, slot in enumerate(slots[:10], 1):  # Limiter à 10 créneaux
            formatted += f"{i}. {slot['start'].strftime('%Y-%m-%d %H:%M')} - "
            formatted += f"{slot['end'].strftime('%H:%M')} "
            formatted += f"(Score: {slot['score']})\n"
        
        return formatted
    
    @staticmethod
    def get_participants_info(db: Session, participant_ids: List[int]) -> List[Dict]:
        """
        Récupère les informations des participants
        
        Args:
            db: Session de base de données
            participant_ids: Liste des IDs des participants
            
        Returns:
            Liste des informations des participants
        """
        participants = []
        for user_id in participant_ids:
            user = UserService.get_user_by_id(db, user_id)
            if user:
                participants.append({
                    "id": user.id,
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or f"User {user.id}",
                    "email": user.email
                })
        
        return participants
