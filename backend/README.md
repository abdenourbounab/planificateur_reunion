# Backend - Planificateur de Réunions

API REST développée avec FastAPI pour la planification intelligente de réunions via agents LLM.

## Architecture

### Structure du projet

```
backend/
├── main.py                 # Point d'entrée de l'application FastAPI
├── config.py              # Configuration (base de données, API keys, modèles LLM)
├── models/                # Modèles SQLAlchemy
│   ├── database.py        # Configuration de la base de données
│   ├── user.py            # Modèle User
│   ├── calendar_event.py  # Modèle CalendarEvent
│   └── event_type.py      # Modèle EventType
├── routes/                # Endpoints API
│   └── meeting_orchestrator.py  # Routes de planification
├── services/              # Logique métier
│   ├── meeting_orchestrator.py  # Orchestration multi-agent LangChain
│   ├── invitation_agent.py      # Génération d'invitations
│   ├── availability_service.py  # Gestion des disponibilités
│   ├── user_service.py          # Gestion des utilisateurs
│   ├── calendar_event_service.py # Gestion des événements
│   ├── google_calendar_service.py # Intégration Google Calendar
│   ├── gmail_api_service.py     # Envoi d'emails via Gmail
│   ├── s2t.py                   # Speech-to-Text (Groq Whisper)
│   └── t2s.py                   # Text-to-Speech (Google TTS)
├── prompts/               # Templates de prompts LLM
│   ├── request_parsing_system.txt
│   ├── request_parsing_human.txt
│   ├── slot_selection_system.txt
│   ├── slot_selection_human.txt
│   ├── invitation_system.txt
│   ├── invitation_human.txt
│   ├── natural_response_system.txt
│   └── natural_response_human.txt
└── credentials/           # Fichiers d'authentification Google
```

### Technologies

- **FastAPI** : Framework web moderne et rapide
- **SQLAlchemy** : ORM pour MySQL
- **LangChain** : Framework pour agents LLM
- **Groq API** : Modèles LLM (Whisper, GPT)
- **Google APIs** : Calendar et Gmail
- **Pydantic** : Validation des données

## Fonctionnalités

### 1. Orchestration Multi-Agent
L'orchestrateur coordonne plusieurs agents LLM pour traiter les demandes de réunion :
- **Agent de parsing** : Analyse la demande en langage naturel
- **Agent de sélection** : Choisit le meilleur créneau disponible
- **Agent d'invitation** : Génère des invitations personnalisées
- **Agent de réponse** : Formule une réponse naturelle à l'utilisateur

### 2. Entrées multiples
- Requête textuelle
- Requête vocale (audio → transcription → traitement)

### 3. Gestion des disponibilités
- Recherche de créneaux libres pour tous les participants
- Respect des préférences horaires et de durée
- Détection automatique des conflits d'agenda

### 4. Intégration Google
- Synchronisation avec Google Calendar
- Envoi d'invitations par Gmail

## API Endpoints

### POST `/api/orchestrator/meeting/text`
Planifie une réunion à partir d'une requête textuelle.

**Body:**
```json
{
  "request_text": "Je voudrais une réunion avec Jean Dupont la semaine prochaine"
}
```

### POST `/api/orchestrator/meeting/audio`
Planifie une réunion à partir d'un fichier audio.

**Form Data:**
- `audio`: fichier audio (format: WAV, MP3, etc.)

**Réponse:**
```json
{
  "success": true,
  "transcribed_text": "Je voudrais une réunion...",
  "meeting": {
    "subject": "Réunion",
    "start_time": "2025-12-01T14:00:00",
    "end_time": "2025-12-01T15:00:00",
    "participants": [...]
  },
  "invitation": {
    "subject": "Invitation: Réunion",
    "body": "Bonjour...",
    "sent": true
  }
}
```

## Configuration

### Variables d'environnement (.env)

```bash
# Base de données MySQL
DATABASE_URL=mysql+pymysql://root:password@localhost/meeting_planner

# API Groq (pour LLM et Whisper)
GROQ_API_KEY=your_groq_api_key

# Modèles LLM
ORCHESTRATOR_MODEL=openai/gpt-oss-120b
INVITATION_MODEL=openai/gpt-oss-120b

# Températures
ORCHESTRATOR_TEMPERATURE=0.3
INVITATION_TEMPERATURE=0.7

# Debug
DEBUG=True
```

### Base de données

Le projet utilise MySQL. Les tables sont créées automatiquement au démarrage via SQLAlchemy.

**Tables principales :**
- `users` : Utilisateurs
- `calendar_events` : Événements de calendrier
- `event_types` : Types d'événements

## Démarrage

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Lancer le serveur
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

L'API sera accessible sur `http://127.0.0.1:8000`

Documentation interactive : `http://127.0.0.1:8000/docs`
