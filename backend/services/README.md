# Backend Services

## Rôle
Logique métier et orchestration des agents.

## Services suggérés

### `meeting_service.py`
- `create_meeting(participants, period, options)` : coordonne les agents pour planifier
- `get_meeting_status(meeting_id)` : récupère l'état d'une réunion depuis DB
- Appelle `calendar_service` pour récupérer les disponibilités
- Appelle `agent_orchestrator` pour communiquer avec les agents

### `calendar_service.py`
- `get_user_calendar(user_id)` : lit le calendrier depuis la DB
- `get_availabilities(user_ids, period)` : calcule les disponibilités
- `create_event(user_id, event)` : ajoute un événement au calendrier

### `agent_orchestrator.py`
- `orchestrate_meeting(data)` : flux complet :
  1. Importe les agents depuis `backend.agents`
  2. Appelle `agent_planner.find_best_slots()`
  3. Appelle `agent_executor.generate_invitation()`
  4. Optionnellement appelle `agent_report` et `agent_presentation`
- Gère les erreurs avec try/except
- Exemple :
```python
from backend.agents import agent_planner, agent_executor

def orchestrate_meeting(calendars, period, duration, participants):
    try:
        slots = agent_planner.find_best_slots(calendars, period, duration)
        invitation = agent_executor.generate_invitation(slots[0], participants)
        return {"status": "success", "invitation": invitation}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## Flux
Service reçoit requête → récupère données DB → appelle agents → sauvegarde résultat → retourne réponse
