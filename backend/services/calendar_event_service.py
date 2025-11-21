from sqlalchemy.orm import Session
from models.calendar_event import CalendarEvent
from datetime import datetime

class CalendarEventService:
    @staticmethod
    def get_all_events(db: Session):
        return db.query(CalendarEvent).all()

    @staticmethod
    def get_event_by_id(db: Session, event_id: int):
        return db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()

    @staticmethod
    def create_event(db: Session, user_id: int, type_id: int, title: str, start_datetime: datetime, end_datetime: datetime, is_all_day: bool = False):
        new_event = CalendarEvent(
            user_id=user_id,
            type_id=type_id,
            title=title,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            is_all_day=is_all_day
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return new_event

    @staticmethod
    def update_event(db: Session, event_id: int, **kwargs):
        event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
        if event:
            for key, value in kwargs.items():
                if hasattr(event, key):
                    setattr(event, key, value)
            db.commit()
            db.refresh(event)
        return event

    @staticmethod
    def delete_event(db: Session, event_id: int):
        event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
        if event:
            db.delete(event)
            db.commit()
            return True
        return False

    @staticmethod
    def get_events_by_user(db: Session, user_id: int):
        return db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id).all()

    @staticmethod
    def get_events_by_type(db: Session, type_id: int):
        return db.query(CalendarEvent).filter(CalendarEvent.type_id == type_id).all()