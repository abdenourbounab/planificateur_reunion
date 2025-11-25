"""
Service d'envoi d'emails et création d'événements Google Calendar
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os
from config import Config
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle


class NotificationService:
    """Service pour envoyer des emails et créer des événements Google Calendar"""

    def __init__(self):
        """Initialise le service de notifications"""
        self.smtp_server = Config.SMTP_SERVER if hasattr(Config, 'SMTP_SERVER') else "smtp.gmail.com"
        self.smtp_port = Config.SMTP_PORT if hasattr(Config, 'SMTP_PORT') else 587
        self.sender_email = Config.SENDER_EMAIL if hasattr(Config, 'SENDER_EMAIL') else None
        self.sender_password = Config.SENDER_PASSWORD if hasattr(Config, 'SENDER_PASSWORD') else None

        # Configuration Google Calendar
        self.google_credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'google_credentials.json')
        self.google_token_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'token.pickle')

    def send_email(self, to_email: str, subject: str, message: str) -> bool:
        """
        Envoie un email

        Args:
            to_email: Email du destinataire
            subject: Objet de l'email
            message: Contenu de l'email

        Returns:
            True si l'envoi a réussi, False sinon
        """
        if not self.sender_email or not self.sender_password:
            print("Configuration email manquante. Veuillez définir SENDER_EMAIL et SENDER_PASSWORD dans config.py")
            return False

        try:
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Ajouter le corps du message
            msg.attach(MIMEText(message, 'plain', 'utf-8'))

            # Connexion au serveur SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            # Envoyer l'email
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()

            print(f"Email envoyé avec succès à {to_email}")
            return True

        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
            return False

    def send_meeting_invitations(self, invitations: List[Dict], participants: List[Dict]) -> Dict[str, bool]:
        """
        Envoie les invitations par email à tous les participants

        Args:
            invitations: Liste des invitations générées
            participants: Liste des participants avec leurs emails

        Returns:
            Dictionnaire avec le statut d'envoi pour chaque participant
        """
        results = {}

        for participant in participants:
            email = participant.get('email')
            if not email:
                print(f"Pas d'email pour le participant {participant.get('name', participant['id'])}")
                results[participant['id']] = False
                continue

            # Utiliser la première invitation (elles sont identiques pour tous)
            invitation = invitations[0] if invitations else None
            if not invitation:
                print(f"Pas d'invitation disponible pour {email}")
                results[participant['id']] = False
                continue

            success = self.send_email(
                to_email=email,
                subject=invitation['subject'],
                message=invitation['message']
            )

            results[participant['id']] = success

        return results

    def create_google_calendar_event(self, event_data: Dict) -> str:
        """
        Crée un événement dans Google Calendar

        Args:
            event_data: Données de l'événement au format Google Calendar

        Returns:
            ID de l'événement créé ou None si erreur
        """
        try:
            # Charger les credentials
            creds = self._get_google_credentials()
            if not creds:
                print("Impossible de charger les credentials Google")
                return None

            # Créer le service Google Calendar
            service = build('calendar', 'v3', credentials=creds)

            # Créer l'événement
            event = service.events().insert(calendarId='primary', body=event_data).execute()

            print(f"Événement Google Calendar créé: {event.get('htmlLink')}")
            return event.get('id')

        except Exception as e:
            print(f"Erreur lors de la création de l'événement Google Calendar: {str(e)}")
            return None

    def _get_google_credentials(self):
        """
        Récupère les credentials Google Calendar

        Returns:
            Credentials Google ou None
        """
        creds = None

        # Charger le token sauvegardé
        if os.path.exists(self.google_token_path):
            with open(self.google_token_path, 'rb') as token:
                creds = pickle.load(token)

        # Si les credentials ne sont pas valides ou n'existent pas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("Token Google manquant. Veuillez suivre les instructions de configuration Google Calendar API")
                return None

            # Sauvegarder le token pour la prochaine fois
            with open(self.google_token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds