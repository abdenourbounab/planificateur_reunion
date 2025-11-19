# Backend Models

## Rôle
Définir les modèles de données pour la base de données (SQLAlchemy) et la validation API (Pydantic).
Contient aussi la configuration de connexion à la base de données.

## Fichiers

### `database.py`
Configuration SQLAlchemy pour la connexion PostgreSQL :
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost:5432/reunions_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `meeting.py`
Modèles SQLAlchemy :
```python
class Meeting(Base):
    __tablename__ = "meetings"
    id: UUID
    created_at: datetime
    participants: JSON
    period: str
    status: str  # "processing", "completed", "failed"
    selected_slot: JSON
    invitation: JSON
```

### `calendar.py`
```python
class User(Base):
    __tablename__ = "users"
    id: UUID
    name: str
    email: str

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id: UUID
    user_id: UUID
    start: datetime
    end: datetime
    title: str
    type: str  # "meeting", "busy", "available"
```

### `schemas.py`
Schémas Pydantic (validation API) :
```python
class MeetingRequest(BaseModel):
    participants: List[str]
    period: str
    options: dict

class MeetingResponse(BaseModel):
    meeting_id: UUID
    status: str
    slot: Optional[dict]
    invitation: Optional[dict]
```

## Implémentation (à venir)
Fichiers à créer dans ce dossier.
