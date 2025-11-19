# Architecture: Assistant interne pour planification de réunions

## Objectif
Trouver le meilleur créneau de réunion pour une liste de participants en utilisant une architecture multi-couches (frontend, backend API, base de données, agents).

---

## 🏗️ Vue d'ensemble de l'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  Interface utilisateur (React/Vue) - Formulaire de réunion      │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────┐      │
│  │   Routes     │→ │   Services    │→ │    Models      │      │
│  │ /api/meetings│  │ meeting_svc   │  │ Meeting, User  │      │
│  │ /api/calendar│  │ calendar_svc  │  │ CalendarEvent  │      │
│  │ /api/health  │  │ agent_orch    │  │ database.py    │      │
│  └──────────────┘  └───────┬───────┘  └────────┬───────┘      │
│                            │                    │               │
│                            ▼                    │ SQLAlchemy    │
│                    ┌───────────────┐           │               │
│                    │    Agents     │           ▼               │
│                    │ (Python files)│    ┌──────────────┐       │
│                    │ • interface   │    │  PostgreSQL  │       │
│                    │ • planner     │    │  Database    │       │
│                    │ • executor    │    │              │       │
│                    │ • report      │    └──────────────┘       │
│                    │ • presentation│                            │
│                    └───────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Structure des dossiers

```
planificateur_reunion/
├── frontend/                    # Application web (React/Vue)
│   ├── src/
│   │   ├── components/         # Composants UI
│   │   └── services/           # Appels API
│   └── README.md
│
├── backend/                     # API FastAPI + Agents + Models
│   ├── routes/                 # Endpoints HTTP
│   │   ├── meetings.py         # POST /api/meetings, GET /api/meetings/{id}
│   │   ├── calendars.py        # GET /api/calendars/{user}
│   │   └── health.py           # GET /api/health
│   ├── services/               # Logique métier
│   │   ├── meeting_service.py  # Orchestration de la planification
│   │   ├── calendar_service.py # Gestion des calendriers
│   │   └── agent_orchestrator.py # Communication avec les agents
│   ├── models/                 # Modèles de données + DB
│   │   ├── database.py         # Configuration SQLAlchemy
│   │   ├── meeting.py          # Meeting, Participant
│   │   ├── calendar.py         # CalendarEvent, User
│   │   └── schemas.py          # Pydantic schemas
│   ├── agents/                 # Système multi-agent
│   │   ├── agent_interface.py  # Point d'entrée agents
│   │   ├── agent_planner.py    # Calcul des créneaux
│   │   ├── agent_executor.py   # Génération invitation
│   │   ├── agent_report.py     # Génération rapport (optionnel)
│   │   ├── agent_presentation.py # Génération PPTX (optionnel)
│   │   └── README.md
│   ├── main.py                 # Point d'entrée FastAPI
│   └── README.md
│
├── ARCHITECTURE.md              # Ce fichier
└── README.md                    # Documentation projet
```

---

## 🔄 Flux de données détaillé

### 1. Requête utilisateur
```
Utilisateur → Frontend → POST /api/meetings
```
**Payload** :
```json
{
  "participants": ["Paul", "Sarah", "Lisa"],
  "period": "next_week",
  "duration": 60,
  "options": {
    "generate_report": true,
    "generate_presentation": false
  }
}
```

### 2. Backend traite la requête
```
Route → Service → DB + Agents
```
- **Route** (`meetings.py`) : reçoit la requête, valide avec Pydantic
- **Service** (`meeting_service.py`) :
  1. Crée une entrée `Meeting` en DB (status: "processing")
  2. Récupère calendriers via `calendar_service.get_availabilities()`
  3. Appelle `agent_orchestrator.orchestrate_meeting()`

### 3. Orchestration des agents
```
Backend Services → agent_interface.py → agent_planner.py → agent_executor.py → [agent_report.py] → [agent_presentation.py]
```

**Les agents sont des modules Python** (pas de HTTP, appels de fonctions directs) :

#### `agent_interface.py`
- Reçoit la demande depuis `agent_orchestrator`
- Valide et route vers `agent_planner`

#### `agent_planner.py`
- Fonction : `find_best_slots(calendars, period, duration) -> List[TimeSlot]`
- Calcule l'intersection des disponibilités
- Retourne 1 à 3 créneaux optimaux

#### `agent_executor.py`
- Fonction : `generate_invitation(meeting_slot, participants) -> dict`
- Génère invitation (iCal) + email simulé
- Retourne confirmation

#### `agent_report.py` (optionnel)
- Fonction : `generate_report(meeting_context) -> str`
- Génère un rapport Markdown avec ordre du jour

#### `agent_presentation.py` (optionnel)
- Fonction : `generate_presentation(meeting_context) -> bytes`
- Génère un PPTX avec les slides de la réunion

### 4. Sauvegarde et réponse
```
Agents → Backend → DB (update) → Frontend
```
- Backend met à jour `Meeting` (status: "completed", slot, invitation)
- Retourne la réponse au frontend

**Réponse** :
```json
{
  "meeting_id": "uuid-123",
  "status": "completed",
  "slot": {
    "start": "2025-11-26T10:00:00",
    "end": "2025-11-26T11:00:00"
  },
  "invitation": { /* contenu iCal */ },
  "report_url": "/api/reports/uuid-123",
  "presentation_url": null
}
```

---

## 🔌 Communication entre agents

**Les agents sont des modules Python** appelés directement par l'orchestrateur (pas de HTTP).

**Flux simplifié** :
```python
from backend.agents import agent_interface, agent_planner, agent_executor

# Orchestrateur appelle les agents
slots = agent_planner.find_best_slots(calendars, period, duration)
invitation = agent_executor.generate_invitation(slots[0], participants)
```

**Gestion d'erreurs** :
- Try/except autour des appels d'agents
- Logs structurés
- Fallback : retour d'erreur au frontend

---

## 🗄️ Base de données

**Configuration** : `backend/models/database.py` (SQLAlchemy)

### Tables principales

**users**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(255) UNIQUE
);
```

**calendar_events**
```sql
CREATE TABLE calendar_events (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  start TIMESTAMP,
  end TIMESTAMP,
  title VARCHAR(255),
  type VARCHAR(50) -- 'meeting', 'busy', 'available'
);
```

**meetings**
```sql
CREATE TABLE meetings (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW(),
  participants JSON,
  period VARCHAR(100),
  status VARCHAR(50), -- 'processing', 'completed', 'failed'
  selected_slot JSON,
  invitation JSON
);
```

**Scripts d'initialisation** : à créer dans `backend/scripts/`
- `init_db.py` : création des tables via SQLAlchemy
- `seed_data.py` : données de test

---

## 🚀 Prochaines étapes

1. **Backend API** : implémenter `main.py` + routes + services + models
2. **Database** : configurer `database.py` + créer modèles SQLAlchemy
3. **Agents** : implémenter les fonctions dans chaque fichier agent (`.py`)
4. **Frontend** : créer formulaire de saisie + affichage des résultats
5. **Tests** : scripts d'intégration simulant le flux complet
6. **Docker** : `docker-compose.yml` pour orchestrer frontend + backend + PostgreSQL
