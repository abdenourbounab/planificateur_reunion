"""
Service pour gérer Google Calendar API
Permet de créer, modifier et supprimer des événements dans Google Agenda
"""
import os
import pickle
from datetime import datetime
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarService:
    """Service pour interagir avec Google Calendar API"""

    # Scopes nécessaires pour lire et écrire dans le calendrier
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]

    def __init__(self):
        """Initialise le service Google Calendar API"""
        self.credentials_path = os.path.join(
            os.path.dirname(__file__), '..', 'credentials', 'calendar_credentials.json'
        )
        self.token_path = os.path.join(
            os.path.dirname(__file__), '..', 'credentials', 'calendar_token.pickle'
        )
        self.creds = None
        self.service = None

    def _authenticate(self) -> bool:
        """
        Authentifie l'utilisateur via OAuth2
        
        Returns:
            True si l'authentification a réussi, False sinon
        """
        # Charger le token sauvegardé s'il existe
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # Si pas de credentials valides, demander l'authentification
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Erreur lors du refresh du token: {str(e)}")
                    # Supprimer le token invalide
                    if os.path.exists(self.token_path):
                        os.remove(self.token_path)
                    return False
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ Fichier credentials manquant: {self.credentials_path}")
                    print("\n📋 Pour configurer Google Calendar API:")
                    print("1. Allez sur https://console.cloud.google.com/")
                    print("2. Sélectionnez votre projet (ou créez-en un)")
                    print("3. Activez Google Calendar API")
                    print("4. Créez des credentials OAuth 2.0")
                    print("5. Téléchargez le fichier JSON")
                    print(f"6. Sauvegardez-le comme: {self.credentials_path}")
                    print("\nNote: Vous pouvez utiliser le même credentials.json que Gmail")
                    print("      en le copiant et renommant en calendar_credentials.json")
                    return False

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"❌ Erreur lors de l'authentification: {str(e)}")
                    return False

            # Sauvegarder le token pour la prochaine fois
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return True

    def _get_service(self):
        """Obtient le service Google Calendar API"""
        if not self.service:
            if not self._authenticate():
                return None
            self.service = build('calendar', 'v3', credentials=self.creds)
        return self.service

    def create_event(
        self,
        summary: str,
        start_datetime: datetime,
        end_datetime: datetime,
        description: str = "",
        attendees: List[str] = None,
        location: str = "",
        calendar_id: str = 'primary'
    ) -> Optional[Dict]:
        """
        Crée un événement dans Google Calendar
        
        Args:
            summary: Titre de l'événement
            start_datetime: Date et heure de début
            end_datetime: Date et heure de fin
            description: Description de l'événement
            attendees: Liste des emails des participants
            location: Lieu de la réunion
            calendar_id: ID du calendrier ('primary' par défaut)
            
        Returns:
            Dictionnaire avec les détails de l'événement créé ou None si erreur
        """
        try:
            service = self._get_service()
            if not service:
                return None

            # Construire l'événement
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',  # Ajustez selon votre timezone
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
            }

            # Ajouter les participants si fournis
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
                # Envoyer des notifications aux participants
                event['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 jour avant
                        {'method': 'popup', 'minutes': 30},  # 30 minutes avant
                    ],
                }

            # Créer l'événement
            created_event = service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'  # Envoie des invitations aux participants
            ).execute()

            print(f"✅ Événement créé dans Google Calendar: {created_event.get('htmlLink')}")
            
            return {
                'id': created_event['id'],
                'htmlLink': created_event['htmlLink'],
                'summary': created_event['summary'],
                'start': created_event['start'],
                'end': created_event['end']
            }

        except HttpError as error:
            print(f"❌ Erreur HTTP lors de la création de l'événement: {error}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'événement dans Google Calendar: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def update_event(
        self,
        event_id: str,
        summary: str = None,
        start_datetime: datetime = None,
        end_datetime: datetime = None,
        description: str = None,
        attendees: List[str] = None,
        location: str = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict]:
        """
        Met à jour un événement existant dans Google Calendar
        
        Args:
            event_id: ID de l'événement à modifier
            summary: Nouveau titre (optionnel)
            start_datetime: Nouvelle date de début (optionnel)
            end_datetime: Nouvelle date de fin (optionnel)
            description: Nouvelle description (optionnel)
            attendees: Nouvelle liste de participants (optionnel)
            location: Nouveau lieu (optionnel)
            calendar_id: ID du calendrier
            
        Returns:
            Dictionnaire avec les détails de l'événement modifié ou None si erreur
        """
        try:
            service = self._get_service()
            if not service:
                return None

            # Récupérer l'événement existant
            event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

            # Mettre à jour les champs fournis
            if summary is not None:
                event['summary'] = summary
            if location is not None:
                event['location'] = location
            if description is not None:
                event['description'] = description
            if start_datetime is not None:
                event['start'] = {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                }
            if end_datetime is not None:
                event['end'] = {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                }
            if attendees is not None:
                event['attendees'] = [{'email': email} for email in attendees]

            # Sauvegarder les modifications
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            print(f"✅ Événement mis à jour dans Google Calendar: {updated_event.get('htmlLink')}")
            
            return {
                'id': updated_event['id'],
                'htmlLink': updated_event['htmlLink'],
                'summary': updated_event['summary'],
                'start': updated_event['start'],
                'end': updated_event['end']
            }

        except HttpError as error:
            print(f"❌ Erreur HTTP lors de la modification de l'événement: {error}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la modification de l'événement: {str(e)}")
            return None

    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """
        Supprime un événement de Google Calendar
        
        Args:
            event_id: ID de l'événement à supprimer
            calendar_id: ID du calendrier
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            service = self._get_service()
            if not service:
                return False

            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            print(f"✅ Événement supprimé de Google Calendar")
            return True

        except HttpError as error:
            print(f"❌ Erreur HTTP lors de la suppression de l'événement: {error}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de l'événement: {str(e)}")
            return False

    def get_event(self, event_id: str, calendar_id: str = 'primary') -> Optional[Dict]:
        """
        Récupère les détails d'un événement
        
        Args:
            event_id: ID de l'événement
            calendar_id: ID du calendrier
            
        Returns:
            Dictionnaire avec les détails de l'événement ou None si erreur
        """
        try:
            service = self._get_service()
            if not service:
                return None

            event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            
            return {
                'id': event['id'],
                'htmlLink': event['htmlLink'],
                'summary': event.get('summary', ''),
                'start': event['start'],
                'end': event['end'],
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'attendees': event.get('attendees', [])
            }

        except HttpError as error:
            print(f"❌ Erreur HTTP lors de la récupération de l'événement: {error}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'événement: {str(e)}")
            return None

    def list_upcoming_events(self, max_results: int = 10, calendar_id: str = 'primary') -> List[Dict]:
        """
        Liste les événements à venir
        
        Args:
            max_results: Nombre maximum d'événements à retourner
            calendar_id: ID du calendrier
            
        Returns:
            Liste des événements à venir
        """
        try:
            service = self._get_service()
            if not service:
                return []

            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indique UTC
            
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [{
                'id': event['id'],
                'summary': event.get('summary', 'Sans titre'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'htmlLink': event['htmlLink']
            } for event in events]

        except HttpError as error:
            print(f"❌ Erreur HTTP lors de la récupération des événements: {error}")
            return []
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des événements: {str(e)}")
            return []
