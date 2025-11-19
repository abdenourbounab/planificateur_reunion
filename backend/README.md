# Backend API (FastAPI)

## Rôle
API REST qui gère la logique métier et orchestre la communication entre le frontend, la base de données et les agents.

## Structure
```
backend/
├── routes/       → Définition des endpoints HTTP
├── services/     → Logique métier (orchestration des agents)
├── models/       → Modèles de données (SQLAlchemy, Pydantic)
└── main.py       → Point d'entrée FastAPI
```

## Responsabilités

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

## Flux typique
1. Frontend → `POST /api/meetings` avec participants et période
2. Route → appelle `meeting_service.create_meeting()`
3. Service → récupère calendriers depuis DB via `calendar_service`
4. Service → appelle `agent_orchestrator` pour communiquer avec agents
5. Agents → calculent créneau optimal, génèrent invitation
6. Service → sauvegarde résultat en DB
7. Route → renvoie réponse au frontend
