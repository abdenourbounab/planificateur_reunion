# Backend - Planificateur de Réunions Intelligent

API REST FastAPI avec agents IA pour la planification automatique de réunions multi-participants. Le système utilise **LangChain** et **Groq** pour orchestrer intelligemment la sélection de créneaux, la génération d'invitations personnalisées et la synchronisation avec **Google Calendar** et **Gmail**.

## 🚀 Fonctionnalités principales

- ✅ **Planification intelligente** avec agents LLM (analyse en langage naturel)
- 📅 **Synchronisation Google Calendar** automatique
- 📧 **Envoi d'invitations** personnalisées via Gmail API
- 🤖 **Génération de réponses** en langage naturel
- 🎯 **Sélection optimale** de créneaux basée sur l'IA
- 👥 **Gestion multi-participants** avec vérification des disponibilités
- 🔄 **Base de données locale** pour historique et backup

## 🏗️ Architecture

```
backend/
├── main.py                          # Point d'entrée FastAPI
├── config.py                        # Configuration (API keys, modèles LLM)
├── init_db.py                       # Script d'initialisation de la DB
│
├── credentials/                     # Credentials Google API (non versionné)
│   ├── .gitkeep
│   ├── README.md                    # Instructions de configuration
│   ├── calendar_credentials.json   # OAuth2 Calendar (à créer)
│   ├── gmail_credentials.json      # OAuth2 Gmail (à créer)
│   └── *.pickle                    # Tokens auto-générés
│
├── prompts/                         # Templates de prompts LLM
│   ├── slot_selection_system.txt   # Sélection de créneau
│   ├── slot_selection_human.txt
│   ├── invitation_system.txt       # Génération d'invitations
│   ├── invitation_human.txt
│   ├── request_parsing_system.txt  # Parsing de requêtes
│   └── request_parsing_human.txt
│
├── models/                          # Modèles SQLAlchemy
│   ├── database.py                 # Configuration DB
│   ├── user.py                     # Utilisateurs
│   ├── event_type.py               # Types d'événements
│   └── calendar_event.py           # Événements calendrier
│
├── services/                        # Logique métier et agents IA
│   ├── meeting_orchestrator.py     # 🎯 Orchestrateur principal
│   ├── invitation_agent.py         # 📝 Agent génération invitations
│   ├── availability_service.py     # Calcul disponibilités
│   ├── google_calendar_service.py  # API Google Calendar
│   ├── gmail_api_service.py        # API Gmail
│   ├── calendar_event_service.py   # CRUD événements locaux
│   ├── user_service.py             # CRUD utilisateurs
│   └── event_type_service.py       # CRUD types d'événements
│
└── routes/                          # Routes API
    └── meeting_orchestrator.py     # Endpoints orchestration
```

## 🛠️ Technologies

- **FastAPI** - Framework web moderne et rapide
- **SQLAlchemy** - ORM pour MySQL
- **LangChain** - Framework pour applications LLM
- **Groq** - API d'inférence LLM ultra-rapide
- **Google Calendar API** - Synchronisation des événements
- **Gmail API** - Envoi d'invitations
- **PyMySQL** - Driver MySQL
- **python-dotenv** - Gestion de configuration
- **dateutil** - Parsing flexible des dates

## 📋 Installation

### Prérequis
- Python 3.11+
- MySQL Server 8.0+
- Compte Google Cloud Platform (pour Calendar & Gmail API)
- Clé API Groq (gratuite sur [console.groq.com](https://console.groq.com/))

### 1. Créer l'environnement virtuel

```bash
# Depuis la racine du projet
python -m venv planif_venv
```

### 2. Activer l'environnement

**Windows (PowerShell):**
```powershell
.\planif_venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source planif_venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créez/éditez `.env` à la racine du projet :

```env
# Base de données
DATABASE_URL=mysql+pymysql://user:password@localhost/meeting_planner

# API Groq (LLM)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# Modèles LLM
ORCHESTRATOR_MODEL=llama-3.3-70b-versatile
ORCHESTRATOR_TEMPERATURE=0.1
INVITATION_MODEL=llama-3.1-8b-instant
INVITATION_TEMPERATURE=0.3

# Signature email
EMAIL_SIGNATURE=Cordialement,\nL'équipe du Planificateur de Réunions

# Environnement
DEBUG=True
```

### 5. Configurer Google Calendar et Gmail API

**Étapes détaillées dans `backend/credentials/README.md`**

Résumé :
1. Créez un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activez **Google Calendar API** et **Gmail API**
3. Créez des credentials OAuth 2.0 (type: Desktop app)
4. Téléchargez le JSON et placez-le :
   ```bash
   cp ~/Downloads/client_secret_*.json backend/credentials/calendar_credentials.json
   cp backend/credentials/calendar_credentials.json backend/credentials/gmail_credentials.json
   ```
5. Au premier lancement, authentifiez-vous dans le navigateur

### 6. Initialiser la base de données

```bash
cd backend
python init_db.py
```

## 🚀 Lancement

### Mode développement

```bash
cd backend
uvicorn main:app --reload
```

Le serveur démarre sur **http://127.0.0.1:8000**

### Documentation interactive

- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

## 📡 API Endpoints

### 🤖 Orchestration IA

#### `POST /api/orchestrator/plan-meeting`
Planifie une réunion en langage naturel.

**Request:**
```json
{
  "text": "Planifie une réunion avec Alice, Bob et Charlie demain à 14h pour discuter du projet X"
}
```

**Response:**
```json
{
  "success": true,
  "message": "✅ **Réunion planifiée avec succès !**\n\n**Sujet :** Projet X\n**Date :** Mercredi 27 Novembre 2025\n**Horaire :** 14:00 - 15:00\n\n**Participants (3) :** Alice, Bob, Charlie\n\n**Pourquoi ce créneau ?** Tous les participants sont disponibles et l'horaire correspond à la demande.\n\n📅 **Google Calendar :** Événement créé avec succès\n📧 **Invitations :** Toutes les invitations ont été envoyées avec succès (3/3)",
  "details": {
    "meeting": { ... },
    "participants": [ ... ],
    "google_calendar_event": { ... },
    "email_notifications": { ... }
  }
}
```

**Fonctionnalités :**
- ✅ Parse la requête en langage naturel
- ✅ Vérifie les disponibilités de tous les participants
- ✅ Sélectionne le meilleur créneau avec IA
- ✅ Crée l'événement dans Google Calendar
- ✅ Envoie des invitations personnalisées par email
- ✅ Sauvegarde en base de données locale
- ✅ Retourne une réponse en langage naturel

#### `GET /api/orchestrator/available-slots`
Consulte les créneaux disponibles sans planifier.

**Query params:**
- `participant_ids`: IDs séparés par des virgules
- `start_date`: Date de début (ISO format)
- `end_date`: Date de fin (ISO format)
- `duration_minutes`: Durée en minutes

### 👥 Utilisateurs

- `GET /api/users/` - Liste tous les utilisateurs
- `GET /api/users/{id}` - Détails d'un utilisateur

### 📋 Types d'événements

- `GET /api/event-types/` - Liste tous les types
- `GET /api/event-types/{id}` - Détails d'un type

### 📅 Événements calendrier

- `GET /api/calendar-events/` - Liste tous les événements
- `GET /api/calendar-events/{id}` - Détails d'un événement
- `POST /api/calendar-events/` - Créer un événement
- `PUT /api/calendar-events/{id}` - Modifier un événement
- `DELETE /api/calendar-events/{id}` - Supprimer un événement

## 🎯 Architecture des Agents IA

### 1. **MeetingOrchestrator** (Agent Principal)
Coordonne tout le processus de planification.

**Responsabilités :**
- Parse les requêtes en langage naturel
- Récupère les disponibilités via `AvailabilityService`
- Utilise LLM pour sélectionner le meilleur créneau
- Synchronise avec Google Calendar
- Génère et envoie les invitations
- Produit une réponse en langage naturel

**Configuration :**
- Modèle : `llama-3.3-70b-versatile` (puissant pour la logique complexe)
- Température : `0.1` (déterministe)

### 2. **InvitationAgent** (Agent de Rédaction)
Spécialisé dans la génération d'invitations personnalisées.

**Responsabilités :**
- Génère des messages d'invitation avec LLM
- Personnalise pour chaque participant
- Gère les fallbacks en cas d'erreur

**Configuration :**
- Modèle : `llama-3.1-8b-instant` (rapide pour génération de texte)
- Température : `0.3` (légèrement créatif)

### 3. **AvailabilityService** (Logique Métier)
Calcul des disponibilités sans IA.

**Responsabilités :**
- Récupère les événements existants
- Calcule les créneaux libres
- Filtre par durée et participants
- Formate pour le LLM

### 4. **GoogleCalendarService**
Synchronisation avec Google Calendar.

**Responsabilités :**
- Authentification OAuth2
- Création/modification/suppression d'événements
- Gestion des participants et notifications

### 5. **GmailAPIService**
Envoi d'emails via Gmail API.

**Responsabilités :**
- Authentification OAuth2
- Envoi d'invitations personnalisées
- Contournement des restrictions SMTP

## 🎨 Personnalisation

### Modifier les prompts LLM

Les prompts sont dans `backend/prompts/`. Modifiez-les pour :
- Changer le ton (formel, décontracté)
- Ajouter des critères de sélection
- Supporter d'autres langues
- Adapter aux besoins métier

**Exemple - Sélection de créneaux :**
```
prompts/
├── slot_selection_system.txt   # Instructions système
└── slot_selection_human.txt    # Template de requête
```

Redémarrez le serveur après modification.

### Changer les modèles LLM

Dans `.env` :
```env
# Modèles disponibles sur Groq
ORCHESTRATOR_MODEL=llama-3.3-70b-versatile    # Meilleur pour logique
ORCHESTRATOR_MODEL=mixtral-8x7b-32768         # Alternative rapide

INVITATION_MODEL=llama-3.1-8b-instant         # Rapide pour texte
INVITATION_MODEL=gemma2-9b-it                 # Alternative créative
```

### Ajuster les températures

```env
# 0.0-0.3 : Déterministe (pour logique, calculs)
ORCHESTRATOR_TEMPERATURE=0.1

# 0.3-0.7 : Équilibré (pour rédaction)
INVITATION_TEMPERATURE=0.3

# 0.7-1.0 : Créatif (pour brainstorming)
```

## 🔧 Développement

### Ajouter une nouvelle fonctionnalité

1. **Service CRUD simple :**
   ```python
   # 1. Créer le modèle : models/my_model.py
   # 2. Créer le service : services/my_service.py
   # 3. Créer les routes : routes/my_routes.py
   # 4. Enregistrer dans main.py
   ```

2. **Nouvel agent IA :**
   ```python
   # 1. Créer l'agent : services/my_agent.py
   # 2. Créer les prompts : prompts/my_agent_*.txt
   # 3. Configurer dans config.py
   # 4. Intégrer dans MeetingOrchestrator
   ```

### Tests

```bash
# Tester l'import des services
python -c "from services.meeting_orchestrator import MeetingOrchestrator; print('✅ OK')"

# Tester la connexion DB
python -c "from models.database import engine; engine.connect(); print('✅ DB OK')"
```

### Debugging

Activez les logs SQLAlchemy dans `models/database.py` :
```python
engine = create_engine(DATABASE_URL, echo=True)  # Affiche toutes les requêtes SQL
```

## 🔒 Sécurité

### Fichiers sensibles (jamais commiter)

Le `.gitignore` exclut automatiquement :
- `.env` - Variables d'environnement
- `credentials/*.json` - Credentials Google
- `credentials/*.pickle` - Tokens d'authentification
- `__pycache__/` - Cache Python

### Rotation des tokens

Si vous rencontrez des problèmes d'authentification :
```bash
cd backend/credentials
rm calendar_token.pickle gmail_token.pickle
# Relancez l'app pour ré-authentifier
```

## 📊 Base de données

### Structure

- **users** - Utilisateurs du système
- **event_types** - Types d'événements (réunion, pause, etc.)
- **calendar_events** - Événements calendrier

### Schéma

```sql
users (id, name, email, created_at)
event_types (id, name, color, created_at)
calendar_events (id, user_id, type_id, title, start_datetime, end_datetime, is_all_day)
```

## 🐛 Troubleshooting

### Erreur "No module named 'services'"
```bash
# Vérifiez que vous êtes dans backend/
cd backend
python main.py
```

### Erreur OAuth Google
```bash
# Supprimez les tokens et réauthentifiez
rm credentials/*.pickle
# Relancez l'app
```

### Erreur Groq API
```bash
# Vérifiez votre clé API dans .env
echo $GROQ_API_KEY  # Linux/Mac
echo $env:GROQ_API_KEY  # Windows PowerShell
```

### Erreur de connexion MySQL
```bash
# Testez la connexion
mysql -u user -p meeting_planner
# Vérifiez DATABASE_URL dans .env
```

## 📚 Documentation

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [Groq](https://console.groq.com/docs)
- [Google Calendar API](https://developers.google.com/calendar/api)
- [Gmail API](https://developers.google.com/gmail/api)
- [SQLAlchemy](https://www.sqlalchemy.org/)

## 📄 Licence

Ce projet est développé dans un cadre éducatif.

## 👥 Équipe

Projet Planificateur de Réunions - 2025
