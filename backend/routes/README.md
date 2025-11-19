# Backend Routes

## Rôle
Définir les endpoints HTTP (FastAPI) exposés au frontend.

## Endpoints suggérés

### Meetings
- `POST /api/meetings` : créer une demande de réunion
  - Body : `{ "participants": ["Paul", "Sarah", "Lisa"], "period": "next_week", "options": {...} }`
  - Retourne : `{ "meeting_id": "uuid", "status": "processing" }`

- `GET /api/meetings/{meeting_id}` : récupérer l'état d'une réunion
  - Retourne : `{ "meeting_id": "uuid", "status": "completed", "slot": {...}, "invitation": {...} }`

### Calendars
- `GET /api/calendars/{user_id}` : récupérer le calendrier d'un utilisateur
  - Retourne : `{ "user_id": "Paul", "events": [...] }`

### Health
- `GET /api/health` : état de santé du backend
  - Retourne : `{ "status": "ok" }`

## Implémentation (à venir)
- Fichiers : `meetings.py`, `calendars.py`, `health.py`
