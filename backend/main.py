from fastapi import FastAPI
from routes import users, event_types, calendar_events

app = FastAPI(title="Planificateur de Réunions", version="1.0.0")

# Inclure les routes
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(event_types.router, prefix="/api", tags=["event-types"])
app.include_router(calendar_events.router, prefix="/api", tags=["calendar-events"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue dans le Planificateur de Réunions"}