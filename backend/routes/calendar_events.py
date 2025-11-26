from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from services.calendar_event_service import CalendarEventService
from datetime import datetime

router = APIRouter()

@router.get("/calendar-events/")
def read_calendar_events(db: Session = Depends(get_db)):
    try:
        events = CalendarEventService.get_all_events(db)
        return {"calendar_events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar-events/{event_id}")
def read_calendar_event(event_id: int, db: Session = Depends(get_db)):
    event = CalendarEventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return {"calendar_event": event}

@router.post("/calendar-events/")
def create_calendar_event(
    user_id: int,
    type_id: int,
    title: str,
    start_datetime: str,
    end_datetime: str,
    is_all_day: bool = False,
    db: Session = Depends(get_db)
):
    try:
        start_dt = datetime.fromisoformat(start_datetime)
        end_dt = datetime.fromisoformat(end_datetime)
        event = CalendarEventService.create_event(db, user_id, type_id, title, start_dt, end_dt, is_all_day)
        return {"calendar_event": event}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/calendar-events/{event_id}")
def update_calendar_event(event_id: int, title: str = None, db: Session = Depends(get_db)):
    event = CalendarEventService.update_event(db, event_id, title=title)
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return {"calendar_event": event}

@router.delete("/calendar-events/{event_id}")
def delete_calendar_event(event_id: int, db: Session = Depends(get_db)):
    success = CalendarEventService.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return {"message": "Calendar event deleted"}

@router.get("/users/{user_id}/calendar-events/")
def read_user_calendar_events(user_id: int, db: Session = Depends(get_db)):
    try:
        events = CalendarEventService.get_events_by_user(db, user_id)
        return {"calendar_events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/event-types/{type_id}/calendar-events/")
def read_event_type_calendar_events(type_id: int, db: Session = Depends(get_db)):
    try:
        events = CalendarEventService.get_events_by_type(db, type_id)
        return {"calendar_events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))