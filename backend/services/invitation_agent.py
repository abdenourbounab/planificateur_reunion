"""
Agent de rédaction d'invitation
Utilise LangChain pour générer des messages d'invitation personnalisés
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, List
from datetime import datetime
from config import Config
import os


class InvitationAgent:
    """Agent LLM pour rédiger les invitations de réunion"""
    
    def __init__(self):
        """Initialise l'agent avec le modèle LLM"""
        self.llm = ChatGroq(
            model=Config.INVITATION_MODEL,
            temperature=Config.INVITATION_TEMPERATURE,
            api_key=Config.GROQ_API_KEY
        )
        
        # Charger le template depuis les fichiers
        self.invitation_template = self._load_invitation_template()
        
        self.chain = self.invitation_template | self.llm | StrOutputParser()
    
    def _load_invitation_template(self):
        """Charge le template d'invitation depuis les fichiers"""
        prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        
        with open(os.path.join(prompts_dir, 'invitation_system.txt'), 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
        
        with open(os.path.join(prompts_dir, 'invitation_human.txt'), 'r', encoding='utf-8') as f:
            human_prompt = f.read().strip()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
    
    def generate_invitation(
        self,
        subject: str,
        participants: List[Dict],
        start_datetime: datetime,
        end_datetime: datetime,
        objective: str
    ) -> Dict[str, str]:
        """
        Génère une invitation de réunion (version générique pour tous)
        
        Args:
            subject: Objet de la réunion
            participants: Liste des participants avec leurs informations
            start_datetime: Date et heure de début
            end_datetime: Date et heure de fin
            objective: Objectif de la réunion
            
        Returns:
            Dictionnaire contenant l'objet et le message de l'invitation
        """
        # Formater les participants
        participant_names = ", ".join([p.get("name", f"User {p['id']}") for p in participants])
        
        # Formater les dates
        date_str = start_datetime.strftime("%A %d %B %Y")
        start_time_str = start_datetime.strftime("%H:%M")
        end_time_str = end_datetime.strftime("%H:%M")
        
        try:
            # Générer le message avec le LLM
            invitation_message = self.chain.invoke({
                "subject": subject,
                "participants": participant_names,
                "date": date_str,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "objective": objective
            })
            
            return {
                "subject": f"Invitation: {subject}",
                "message": invitation_message,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            # Fallback en cas d'erreur
            return {
                "subject": f"Invitation: {subject}",
                "message": self._generate_fallback_invitation(
                    subject, participant_names, date_str, start_time_str, end_time_str, objective
                ),
                "generated_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def generate_personalized_invitation(
        self,
        recipient: Dict,
        subject: str,
        all_participants: List[Dict],
        start_datetime: datetime,
        end_datetime: datetime,
        objective: str
    ) -> Dict[str, str]:
        """
        Génère une invitation personnalisée pour un participant spécifique
        
        Args:
            recipient: Le participant qui recevra l'email
            subject: Objet de la réunion
            all_participants: Liste de TOUS les participants (pour info dans l'email)
            start_datetime: Date et heure de début
            end_datetime: Date et heure de fin
            objective: Objectif de la réunion
            
        Returns:
            Dictionnaire contenant l'objet et le message personnalisé
        """
        # Nom du destinataire uniquement pour le "Bonjour"
        recipient_name = recipient.get("name", "")
        recipient_first_name = recipient_name.split()[0] if recipient_name else "Cher participant"
        
        # Liste complète des participants pour l'info
        all_participant_names = ", ".join([p.get("name", f"User {p['id']}") for p in all_participants])
        
        # Formater les dates
        date_str = start_datetime.strftime("%A %d %B %Y")
        start_time_str = start_datetime.strftime("%H:%M")
        end_time_str = end_datetime.strftime("%H:%M")
        
        # Créer un prompt personnalisé pour ce destinataire
        personalized_prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un assistant professionnel qui rédiges des invitations de réunion claires et engageantes.
Tu dois créer une invitation formelle mais chaleureuse, en français.

IMPORTANT: Dans la salutation, utilise UNIQUEMENT le prénom du destinataire (pas tous les participants).
Par exemple: "Bonjour {recipient_name}," et NON "Bonjour X, Y, Z,"

L'invitation doit contenir:
- Un message d'accueil personnalisé avec le prénom du destinataire UNIQUEMENT
- Les détails de la réunion (date, heure, durée)
- La liste de TOUS les participants (dans la section Participants)
- L'objectif de la réunion
- Une formule de politesse suivie de la signature fournie

NE PAS INCLURE de ligne "**Objet :**" ou "**Objet : XXX**" dans le message, car l'objet est déjà dans le sujet de l'email.

Sois concis mais professionnel."""),
            ("human", """Crée une invitation personnalisée pour {recipient_name} concernant:

Sujet de la réunion: {subject}
Tous les participants: {participants}
Date: {date}
Heure de début: {start_time}
Heure de fin: {end_time}
Objectif: {objective}

Termine l'email avec cette signature exactement:
{signature}

RAPPEL: 
- Commence par "Bonjour {recipient_name}," (pas les autres participants)
- NE PAS mettre de ligne "**Objet :**" dans le message""")
        ])
        
        personalized_chain = personalized_prompt | self.llm | StrOutputParser()
        
        try:
            # Générer le message personnalisé
            invitation_message = personalized_chain.invoke({
                "recipient_name": recipient_first_name,
                "subject": subject,
                "participants": all_participant_names,
                "date": date_str,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "objective": objective,
                "signature": Config.EMAIL_SIGNATURE
            })
            
            return {
                "subject": f"Invitation: {subject}",
                "message": invitation_message,
                "generated_at": datetime.now().isoformat(),
                "recipient": recipient_name
            }
        except Exception as e:
            # Fallback en cas d'erreur
            return {
                "subject": f"Invitation: {subject}",
                "message": self._generate_fallback_personalized_invitation(
                    recipient_first_name, subject, all_participant_names, 
                    date_str, start_time_str, end_time_str, objective
                ),
                "generated_at": datetime.now().isoformat(),
                "recipient": recipient_name,
                "error": str(e)
            }
    
    def _generate_fallback_invitation(
        self,
        subject: str,
        participants: str,
        date: str,
        start_time: str,
        end_time: str,
        objective: str
    ) -> str:
        """
        Génère une invitation de secours si le LLM échoue
        
        Args:
            subject: Objet de la réunion
            participants: Noms des participants
            date: Date formatée
            start_time: Heure de début
            end_time: Heure de fin
            objective: Objectif de la réunion
            
        Returns:
            Message d'invitation formaté
        """
        return f"""Bonjour,

Vous êtes invité(e) à la réunion suivante:

Objet: {subject}
Date: {date}
Horaire: {start_time} - {end_time}
Participants: {participants}

Objectif de la réunion:
{objective}

Nous vous remercions de confirmer votre présence.

Cordialement,
Planificateur de Réunions
"""
    
    def _generate_fallback_personalized_invitation(
        self,
        recipient_first_name: str,
        subject: str,
        participants: str,
        date: str,
        start_time: str,
        end_time: str,
        objective: str
    ) -> str:
        """
        Génère une invitation personnalisée de secours si le LLM échoue
        
        Args:
            recipient_first_name: Prénom du destinataire
            subject: Objet de la réunion
            participants: Noms de tous les participants
            date: Date formatée
            start_time: Heure de début
            end_time: Heure de fin
            objective: Objectif de la réunion
            
        Returns:
            Message d'invitation personnalisé
        """
        return f"""Bonjour {recipient_first_name},

Vous êtes invité(e) à la réunion suivante:

Objet: {subject}
Date: {date}
Horaire: {start_time} - {end_time}
Participants: {participants}

Objectif de la réunion:
{objective}

Nous vous remercions de confirmer votre présence.

Cordialement,
Planificateur de Réunions
"""
