from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from services.event_type_service import EventTypeService

router = APIRouter()

@router.get("/event-types/")
def read_event_types(db: Session = Depends(get_db)):
    try:
        event_types = EventTypeService.get_all_event_types(db)
        return {"event_types": event_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/event-types/{event_type_id}")
def read_event_type(event_type_id: int, db: Session = Depends(get_db)):
    event_type = EventTypeService.get_event_type_by_id(db, event_type_id)
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")
    return {"event_type": event_type}