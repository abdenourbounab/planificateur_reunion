"""
Service d'envoi d'emails via l'API Gmail (fonctionne même si SMTP est bloqué)
"""
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle


class GmailAPIService:
    """Service pour envoyer des emails via l'API Gmail"""

    # Si vous modifiez ces scopes, supprimez le fichier token.pickle
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self):
        """Initialise le service Gmail API"""
        self.credentials_path = os.path.join(
            os.path.dirname(__file__), '..', 'credentials', 'gmail_credentials.json'
        )
        self.token_path = os.path.join(
            os.path.dirname(__file__), '..', 'credentials', 'gmail_token.pickle'
        )
        self.creds = None

    def _authenticate(self):
        """Authentifie l'utilisateur via OAuth2"""
        # Le token sauvegardé permet d'éviter de se reconnecter à chaque fois
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # Si pas de credentials valides, demander à l'utilisateur de se connecter
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ Fichier credentials manquant: {self.credentials_path}")
                    print("\n📋 Pour configurer Gmail API:")
                    print("1. Allez sur https://console.cloud.google.com/")
                    print("2. Créez un projet ou sélectionnez-en un")
                    print("3. Activez Gmail API")
                    print("4. Créez des credentials OAuth 2.0")
                    print("5. Téléchargez le fichier JSON")
                    print(f"6. Sauvegardez-le comme: {self.credentials_path}")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Sauvegarder le token pour la prochaine fois
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return True

    def send_email(self, to_email: str, subject: str, message: str) -> bool:
        """
        Envoie un email via l'API Gmail

        Args:
            to_email: Email du destinataire
            subject: Objet de l'email
            message: Contenu de l'email

        Returns:
            True si l'envoi a réussi, False sinon
        """
        try:
            # S'authentifier
            if not self._authenticate():
                return False

            # Créer le service Gmail
            service = build('gmail', 'v1', credentials=self.creds)

            # Créer le message
            msg = MIMEMultipart()
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain', 'utf-8'))

            # Encoder le message en base64
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

            # Envoyer via l'API
            message_body = {'raw': raw}
            send_message = service.users().messages().send(
                userId='me', body=message_body
            ).execute()

            print(f"✅ Email envoyé avec succès à {to_email} (ID: {send_message['id']})")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
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

            # Utiliser la première invitation
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
