from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("event_types.id"), nullable=False)
    title = Column(String(200))
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    is_all_day = Column(Boolean, default=False)

    # Relations
    user = relationship("User", back_populates="calendar_events")
    event_type = relationship("EventType", back_populates="calendar_events")