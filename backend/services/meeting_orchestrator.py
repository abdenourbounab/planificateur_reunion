"""
Orchestrateur de réunions
LLM principal qui coordonne la planification de réunions multi-participants
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from services.availability_service import AvailabilityService
from services.invitation_agent import InvitationAgent
from services.calendar_event_service import CalendarEventService
from services.user_service import UserService
from services.gmail_api_service import GmailAPIService
from services.google_calendar_service import GoogleCalendarService
from config import Config
from dateutil import parser as date_parser
import json
import os


class MeetingOrchestrator:
    """Orchestrateur principal qui coordonne la planification de réunions"""
    
    def __init__(self):
        """Initialise l'orchestrateur avec le modèle LLM"""
        self.llm = ChatGroq(
            model=Config.ORCHESTRATOR_MODEL,
            temperature=Config.ORCHESTRATOR_TEMPERATURE,
            api_key=Config.GROQ_API_KEY
        )
        
        self.invitation_agent = InvitationAgent()
        self.gmail_service = GmailAPIService()
        self.google_calendar_service = GoogleCalendarService()
        
        # Charger les templates depuis les fichiers
        self.slot_selection_template = self._load_slot_selection_template()
        self.parsing_template = self._load_parsing_template()
        self.natural_response_template = self._load_natural_response_template()
        
        self.json_parser = JsonOutputParser()
        self.selection_chain = self.slot_selection_template | self.llm | self.json_parser
        self.parsing_chain = self.parsing_template | self.llm | self.json_parser
        self.natural_response_chain = self.natural_response_template | self.llm | StrOutputParser()
    
    def _generate_natural_response(
        self,
        subject: str,
        selected_slot: Dict,
        participants: List[Dict],
        email_results: Dict,
        google_calendar_event: Optional[Dict],
        reasoning: str
    ) -> str:
        """
        Génère une réponse en langage naturel pour confirmer la planification
        
        Args:
            subject: Sujet de la réunion
            selected_slot: Créneau sélectionné
            participants: Liste des participants
            email_results: Résultats d'envoi des emails
            google_calendar_event: Événement Google Calendar créé
            reasoning: Raisonnement du choix du créneau
            
        Returns:
            Message en langage naturel
        """
        # Formater les données pour le LLM
        start_datetime = selected_slot["start"]
        end_datetime = selected_slot["end"]
        
        datetime_range = f"{start_datetime.strftime('%A %d %B %Y')} de {start_datetime.strftime('%H:%M')} à {end_datetime.strftime('%H:%M')}"
        
        participant_names = ", ".join([p["name"] for p in participants])
        
        # Statut Google Calendar
        if google_calendar_event:
            google_calendar_status = "Créé avec succès"
        else:
            google_calendar_status = "Non synchronisé"
        
        # Statut des emails
        emails_sent = sum(1 for result in email_results.values() if result.get("sent", False))
        total_emails = len(email_results)
        if emails_sent == total_emails:
            email_status = f"Toutes les invitations envoyées avec succès ({emails_sent}/{total_emails})"
        elif emails_sent > 0:
            failed_participants = [
                email_results[pid]["user_name"] 
                for pid in email_results 
                if not email_results[pid].get("sent", False)
            ]
            email_status = f"{emails_sent}/{total_emails} invitations envoyées, échec pour : {', '.join(failed_participants)}"
        else:
            email_status = "Aucune invitation n'a pu être envoyée"
        
        # Générer la réponse avec le LLM
        return self.natural_response_chain.invoke({
            "subject": subject,
            "datetime_range": datetime_range,
            "participant_names": participant_names,
            "reasoning": reasoning or "Créneau optimal sélectionné",
            "google_calendar_status": google_calendar_status,
            "email_status": email_status
        })
    
    def _load_slot_selection_template(self):
        """Charge le template de sélection de créneau depuis les fichiers"""
        prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        
        with open(os.path.join(prompts_dir, 'slot_selection_system.txt'), 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
        
        with open(os.path.join(prompts_dir, 'slot_selection_human.txt'), 'r', encoding='utf-8') as f:
            human_prompt = f.read().strip()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
    
    def _load_parsing_template(self):
        """Charge le template d'extraction de requête depuis les fichiers"""
        prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        
        with open(os.path.join(prompts_dir, 'request_parsing_system.txt'), 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
        
        with open(os.path.join(prompts_dir, 'request_parsing_human.txt'), 'r', encoding='utf-8') as f:
            human_prompt = f.read().strip()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        self.parsing_chain = self.parsing_template | self.llm | self.json_parser
    
    def _load_natural_response_template(self):
        """Charge le template de génération de réponse naturelle depuis les fichiers"""
        prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        
        with open(os.path.join(prompts_dir, 'natural_response_system.txt'), 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
        
        with open(os.path.join(prompts_dir, 'natural_response_human.txt'), 'r', encoding='utf-8') as f:
            human_prompt = f.read().strip()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
    
    def parse_request(self, request_text: str) -> Dict:
        """
        Parse une demande de réunion en langage naturel
        
        Args:
            request_text: Le texte de la demande
            
        Returns:
            Dictionnaire avec les informations extraites
        """
        try:
            parsed = self.parsing_chain.invoke({"request_text": request_text})
            return parsed
        except Exception as e:
            # Fallback avec valeurs par défaut
            return {
                "subject": "Réunion",
                "objective": request_text,
                "participant_names": [],
                "preferred_start_date": datetime.now().isoformat(),
                "preferred_end_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "duration_minutes": 60,
                "preferences": {}
            }
    
    def plan_meeting(
        self,
        db: Session,
        request_text: str
    ) -> Dict:
        """
        Planifie une réunion en analysant une demande en langage naturel
        
        Args:
            db: Session de base de données
            request_text: Texte de la demande de réunion
            
        Returns:
            Dictionnaire avec les détails de la réunion planifiée
        """
        # Étape 1: Analyser la demande avec le LLM
        parsed_request = self.parse_request(request_text)
        
        subject = parsed_request.get("subject", "Réunion")
        objective = parsed_request.get("objective", request_text)
        participant_names = parsed_request.get("participant_names", [])
        preferred_start_date = date_parser.parse(parsed_request.get("preferred_start_date", datetime.now().isoformat()))
        preferred_end_date = date_parser.parse(parsed_request.get("preferred_end_date", (datetime.now() + timedelta(days=7)).isoformat()))
        duration_minutes = parsed_request.get("duration_minutes", 60)
        preferences = parsed_request.get("preferences", {})
        
        # Étape 2: Convertir les noms des participants en IDs
        participant_ids = []
        for name in participant_names:
            # Recherche par nom (approximative)
            user = UserService.get_user_by_name(db, name)
            if user:
                participant_ids.append(user.id)
        
        if not participant_ids:
            return {
                "success": False,
                "error": "Aucun participant valide trouvé dans la demande"
            }
        
        # Étape 3: Récupérer les informations des participants
        participants = AvailabilityService.get_participants_info(db, participant_ids)
        
        if not participants:
            return {
                "success": False,
                "error": "Aucun participant valide trouvé"
            }
        
        # Étape 4: Trouver les créneaux disponibles
        available_slots = AvailabilityService.get_available_slots(
            db=db,
            participant_ids=participant_ids,
            start_date=preferred_start_date,
            end_date=preferred_end_date,
            meeting_duration_minutes=duration_minutes
        )
        
        if not available_slots:
            return {
                "success": False,
                "error": "Aucun créneau disponible pour tous les participants",
                "participants": participants,
                "searched_period": {
                    "start": preferred_start_date.isoformat(),
                    "end": preferred_end_date.isoformat()
                }
            }
        
        # Étape 5: Le LLM choisit le meilleur créneau
        try:
            slots_formatted = AvailabilityService.format_slots_for_llm(available_slots)
            
            selection_result = self.selection_chain.invoke({
                "available_slots": slots_formatted,
                "subject": subject,
                "duration": duration_minutes,
                "participant_count": len(participants),
                "preferences": json.dumps(preferences or {}, ensure_ascii=False)
            })
            
            # Récupérer le créneau sélectionné
            selected_index = selection_result.get("slot_index", 0)
            selected_slot = available_slots[selected_index]
            reasoning = selection_result.get("reasoning", "Meilleur créneau disponible")
            alternative_indices = selection_result.get("alternative_slots", [])
            
        except Exception as e:
            # Fallback: prendre le premier créneau
            selected_slot = available_slots[0]
            reasoning = "Créneau sélectionné automatiquement (erreur LLM)"
            alternative_indices = [1, 2] if len(available_slots) > 2 else []
            selection_result = {"error": str(e)}
        
        # Étape 6: Générer l'invitation avec l'agent de rédaction
        invitation = self.invitation_agent.generate_invitation(
            subject=subject,
            participants=participants,
            start_datetime=selected_slot["start"],
            end_datetime=selected_slot["end"],
            objective=objective
        )
        
        # Étape 7: Créer l'événement dans Google Calendar pour tous les participants
        google_calendar_event = None
        attendee_emails = [p.get("email") for p in participants if p.get("email")]
        
        try:
            google_calendar_event = self.google_calendar_service.create_event(
                summary=subject,
                start_datetime=selected_slot["start"],
                end_datetime=selected_slot["end"],
                description=f"{objective}\n\nParticipants: {', '.join([p['name'] for p in participants])}",
                attendees=attendee_emails,
                location=""
            )
            if google_calendar_event:
                print(f"✅ Événement synchronisé avec Google Calendar: {google_calendar_event.get('htmlLink')}")
        except Exception as e:
            print(f"⚠️ Impossible de synchroniser avec Google Calendar: {str(e)}")
            print("   L'événement sera quand même créé en base de données locale")
        
        # Étape 8: Créer les événements dans le calendrier local pour chaque participant
        created_events = []
        for participant in participants:
            try:
                event = CalendarEventService.create_event(
                    db=db,
                    user_id=participant["id"],
                    type_id=1,  # Type par défaut, à ajuster selon vos besoins
                    title=subject,
                    start_datetime=selected_slot["start"],
                    end_datetime=selected_slot["end"],
                    is_all_day=False
                )
                created_events.append({
                    "user_id": participant["id"],
                    "event_id": event.id,
                    "user_name": participant["name"],
                    "google_calendar_link": google_calendar_event.get('htmlLink') if google_calendar_event else None
                })
            except Exception as e:
                created_events.append({
                    "user_id": participant["id"],
                    "error": str(e),
                    "user_name": participant["name"]
                })
        
        # Étape 9: Envoyer les invitations personnalisées par email
        email_results = {}
        for participant in participants:
            email = participant.get("email")
            if email:
                try:
                    # Générer une invitation personnalisée pour ce participant
                    personalized_invitation = self.invitation_agent.generate_personalized_invitation(
                        recipient=participant,
                        subject=subject,
                        all_participants=participants,
                        start_datetime=selected_slot["start"],
                        end_datetime=selected_slot["end"],
                        objective=objective
                    )
                    
                    # Envoyer l'email personnalisé via Gmail API
                    success = self.gmail_service.send_email(
                        to_email=email,
                        subject=personalized_invitation["subject"],
                        message=personalized_invitation["message"]
                    )
                    email_results[participant["id"]] = {
                        "sent": success,
                        "email": email,
                        "user_name": participant["name"]
                    }
                except Exception as e:
                    print(f"❌ Erreur lors de l'envoi à {participant['name']}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    email_results[participant["id"]] = {
                        "sent": False,
                        "error": str(e),
                        "email": email,
                        "user_name": participant["name"]
                    }
            else:
                email_results[participant["id"]] = {
                    "sent": False,
                    "error": "Email manquant",
                    "user_name": participant["name"]
                }
        
        # Préparer les créneaux alternatifs
        alternatives = []
        for idx in alternative_indices:
            if 0 <= idx < len(available_slots):
                alt_slot = available_slots[idx]
                alternatives.append({
                    "start": alt_slot["start"].isoformat(),
                    "end": alt_slot["end"].isoformat(),
                    "score": alt_slot["score"]
                })
        
        # Générer une réponse en langage naturel
        natural_response = self._generate_natural_response(
            subject=subject,
            selected_slot=selected_slot,
            participants=participants,
            email_results=email_results,
            google_calendar_event=google_calendar_event,
            reasoning=reasoning
        )
        
        # Retourner le résultat avec la réponse naturelle
        return {
            "success": True,
            "message": natural_response,
            "details": {
                "meeting": {
                    "subject": subject,
                    "objective": objective,
                    "selected_slot": {
                        "start": selected_slot["start"].isoformat(),
                        "end": selected_slot["end"].isoformat(),
                        "score": selected_slot["score"]
                    },
                    "reasoning": reasoning,
                    "alternative_slots": alternatives
                },
                "participants": participants,
                "invitation": invitation,
                "google_calendar_event": google_calendar_event,
                "created_events": created_events,
                "email_notifications": email_results,
                "total_slots_found": len(available_slots),
                "llm_selection": selection_result
            }
        }