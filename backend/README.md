# Backend API (FastAPI)

<<<<<<< Updated upstream
## Rôle
API REST qui gère la logique métier et orchestre la communication entre le frontend, la base de données et les agents.
=======
API REST FastAPI pour un système de planification de réunions intelligent avec agents LLM. Le système utilise LangChain et Groq pour orchestrer la planification de réunions multi-participants avec vérification des disponibilités et génération automatique d'invitations.

## Architecture

Le backend suit une architecture modulaire avec séparation claire des responsabilités et intégration d'agents IA :
>>>>>>> Stashed changes

## Structure
```
backend/
<<<<<<< Updated upstream
├── routes/       → Définition des endpoints HTTP
├── services/     → Logique métier (orchestration des agents)
├── models/       → Modèles de données (SQLAlchemy, Pydantic)
└── main.py       → Point d'entrée FastAPI
```

## Responsabilités
=======
├── main.py                          # Point d'entrée FastAPI
├── config.py                        # Configuration centralisée (API keys, modèles)
├── prompts/                         # Templates de prompts pour les LLM
│   ├── slot_selection_system.txt    # Prompt système sélection créneau
│   ├── slot_selection_human.txt     # Prompt utilisateur sélection créneau
│   ├── invitation_system.txt        # Prompt système génération invitation
│   ├── invitation_human.txt         # Prompt utilisateur génération invitation
│   ├── request_parsing_system.txt   # Prompt système extraction requête
│   └── request_parsing_human.txt    # Prompt utilisateur extraction requête
├── models/                          # Modèles de données SQLAlchemy
│   ├── database.py                  # Configuration base de données
│   ├── user.py                      # Modèle User
│   ├── event_type.py                # Modèle EventType
│   └── calendar_event.py            # Modèle CalendarEvent
├── services/                        # Logique métier et agents IA
│   ├── user_service.py              # Service utilisateurs
│   ├── calendar_event_service.py    # Service événements calendrier
│   ├── availability_service.py      # Service vérification disponibilités
│   ├── invitation_agent.py          # Agent génération invitations (LLM)
│   └── meeting_orchestrator.py      # Orchestrateur principal (LLM)
└── routes/                          # Routes API
    └── meeting_orchestrator.py      # Endpoints orchestration réunions
```

### Technologies utilisées
- **FastAPI** : Framework web asynchrone
- **SQLAlchemy** : ORM pour la base de données
- **LangChain** : Framework pour les applications LLM
- **Groq** : API d'inférence LLM rapide
- **PyMySQL** : Pilote MySQL
- **python-dotenv** : Gestion des variables d'environnement
- **dateutil** : Parsing flexible des dates
>>>>>>> Stashed changes

### Routes (`routes/`)
Endpoints HTTP exposés au frontend :
- `POST /api/meetings` : créer une demande de réunion
- `GET /api/meetings/{id}` : récupérer l'état d'une réunion
- `GET /api/calendars/{user}` : récupérer le calendrier d'un utilisateur
- `GET /api/health` : état de santé du backend

### Services (`services/`)
Logique métier et orchestration :
- `meeting_service.py` : coordonne les agents pour planifier la réunion
- `calendar_service.py` : lit/écrit les calendriers depuis la DB
- `agent_orchestrator.py` : envoie des messages MCP aux agents et collecte les réponses

### Models (`models/`)
Modèles de données pour la DB et validation :
- `meeting.py` : Meeting, Participant
- `calendar.py` : CalendarEvent, Availability
- `schemas.py` : Pydantic schemas pour validation API

<<<<<<< Updated upstream
## Flux typique
1. Frontend → `POST /api/meetings` avec participants et période
2. Route → appelle `meeting_service.create_meeting()`
3. Service → récupère calendriers depuis DB via `calendar_service`
4. Service → appelle `agent_orchestrator` pour communiquer avec agents
5. Agents → calculent créneau optimal, génèrent invitation
6. Service → sauvegarde résultat en DB
7. Route → renvoie réponse au frontend
=======
```bash
# Depuis le dossier racine du projet
python -m venv planif_venv
```

### 2. Activer l'environnement virtuel

**Windows (PowerShell) :**
```bash
planif_venv\Scripts\activate
```

**Linux/Mac :**
```bash
source planif_venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Éditez le fichier `.env` à la racine du projet :

```env
# Base de données
DATABASE_URL=mysql+pymysql://user:votre_mot_de_passe@localhost/meeting_planner

# Configuration générale
DEBUG=True

# API Groq pour les LLM
GROQ_API_KEY=votre_cle_api_groq

# Modèles LLM utilisés
ORCHESTRATOR_MODEL=openai/gpt-oss-120b
ORCHESTRATOR_TEMPERATURE=0.1
INVITATION_MODEL=openai/gpt-oss-120b
INVITATION_TEMPERATURE=0.3
```

Remplacez `user` par votre utilisateur MySQL, `votre_mot_de_passe` par votre mot de passe MySQL, et `votre_cle_api_groq` par votre clé API Groq (obtenue sur https://console.groq.com/).

## Lancement du serveur

### Mode développement (avec rechargement automatique)

```bash
uvicorn main:app --reload
```

Le serveur sera accessible sur : http://127.0.0.1:8000

### Documentation API

Une fois le serveur lancé, accédez à la documentation interactive :
- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

## Endpoints API

### Utilisateurs
- `GET /api/users/` - Liste tous les utilisateurs
- `GET /api/users/{id}` - Détails d'un utilisateur

### Types d'événements
- `GET /api/event-types/` - Liste tous les types
- `GET /api/event-types/{id}` - Détails d'un type

### Événements calendrier
- `GET /api/calendar-events/` - Liste tous les événements
- `GET /api/calendar-events/{id}` - Détails d'un événement
- `POST /api/calendar-events/` - Créer un événement
- `PUT /api/calendar-events/{id}` - Modifier un événement
- `DELETE /api/calendar-events/{id}` - Supprimer un événement

### Orchestration de réunions (IA)
- `POST /api/orchestrator/plan-meeting` - Planifier une réunion via texte naturel
  - Analyse les disponibilités de tous les participants
  - Sélectionne le meilleur créneau disponible
  - Génère et envoie des invitations personnalisées
  - Crée automatiquement les événements dans le calendrier
- `GET /api/orchestrator/available-slots` - Consulter les créneaux disponibles pour un groupe

## Développement

### Architecture des agents IA

Le système utilise une architecture multi-agent pour la planification intelligente :

1. **MeetingOrchestrator** : Agent principal qui coordonne le processus
   - Analyse la requête en langage naturel
   - Récupère les disponibilités via AvailabilityService
   - Utilise LLM pour sélectionner le meilleur créneau (prompts dans `prompts/slot_selection_*.txt`)
   - Déclenche InvitationAgent pour générer les invitations
   - Crée les événements calendrier

2. **InvitationAgent** : Spécialisé dans la génération d'invitations
   - Utilise LLM pour créer des messages personnalisés (prompts dans `prompts/invitation_*.txt`)
   - Supporte le format Google Calendar
   - Gère les fallback en cas d'erreur

3. **AvailabilityService** : Logique métier pour les disponibilités
   - Récupère les événements existants
   - Calcule les créneaux libres
   - Filtre par durée et participants

### Ajouter une nouvelle fonctionnalité
1. **Pour une entité CRUD** :
   - Créer le modèle dans `models/`
   - Créer le service dans `services/`
   - Créer les routes dans `routes/`
   - Importer et enregistrer dans `main.py`

2. **Pour un nouvel agent IA** :
   - Créer une classe dans `services/` héritant des patterns existants
   - Configurer le modèle et température dans `config.py`
   - Intégrer dans MeetingOrchestrator ou créer de nouvelles routes
   - Ajouter les variables d'environnement nécessaires

### Configuration des modèles LLM

Les modèles sont configurés dans `config.py` :
- **Orchestrateur** : Modèle puissant (70B) pour la logique complexe
- **Invitations** : Modèle plus léger (8B) pour la génération de texte

Ajustez les températures selon vos besoins :
- `0.0-0.3` : Réponses déterministes et précises
- `0.7-1.0` : Réponses plus créatives

## Personnalisation des prompts

Les prompts des agents IA sont stockés dans le dossier `prompts/` pour faciliter la maintenance et la personnalisation :

- `slot_selection_system.txt` & `slot_selection_human.txt` : Prompts pour la sélection intelligente de créneaux
- `invitation_system.txt` & `invitation_human.txt` : Prompts pour la génération d'invitations

Vous pouvez modifier ces fichiers pour :
- Changer le ton des réponses (plus formel, plus décontracté)
- Ajouter des critères spécifiques de sélection
- Supporter d'autres langues
- Adapter aux besoins métier spécifiques

Les modifications sont prises en compte au redémarrage du serveur.

## Utilisation de l'orchestrateur IA

### Planification automatique de réunion

Envoyez une requête POST à `/api/orchestrator/plan-meeting` avec un JSON contenant le champ `text` décrivant la réunion en langage naturel :

```json
{
  "text": "Planifie une réunion avec Alice, Bob et Charlie pour discuter du projet X demain après-midi pendant 1 heure"
}
```

L'orchestrateur va :
1. **Parser la requête** : Extraire participants, sujet, contraintes temporelles
2. **Vérifier disponibilités** : Consulter les calendriers de tous les participants
3. **Sélectionner créneau** : Utiliser IA pour choisir le meilleur slot disponible
4. **Générer invitations** : Créer des messages personnalisés pour chaque participant
5. **Créer événements** : Ajouter automatiquement au calendrier

### Formats de requête supportés

L'orchestrateur comprend diverses formulations :
- "Réunion avec Alice et Bob demain 14h-15h pour le projet Y"
- "Planifie un meeting équipe dev vendredi matin 2h"
- "RDV avec le client Dupont la semaine prochaine"

### Consultation des disponibilités

Pour voir les créneaux disponibles sans planifier :

```
GET /api/orchestrator/available-slots?participant_ids=1,2,3&start_date=2025-11-25&end_date=2025-11-26&duration_minutes=60
```

Retourne une liste de créneaux avec scores de préférence.
>>>>>>> Stashed changes
