from sqlalchemy.orm import Session
from models.event_type import EventType

class EventTypeService:
    @staticmethod
    def get_all_event_types(db: Session):
        return db.query(EventType).all()

    @staticmethod
    def get_event_type_by_id(db: Session, event_type_id: int):
        return db.query(EventType).filter(EventType.id == event_type_id).first()