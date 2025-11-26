# Backend - Planificateur de Réunions

API REST FastAPI pour un système de planification de réunions avec gestion des utilisateurs, types d'événements et événements calendrier.

## Architecture

Le backend suit une architecture modulaire avec séparation claire des responsabilités :

```
backend/
├── main.py                 # Point d'entrée FastAPI
├── config.py               # Configuration centralisée
├── models/                 # Modèles de données SQLAlchemy
│   ├── database.py         # Configuration base de données
│   ├── user.py             # Modèle User
│   ├── event_type.py       # Modèle EventType
│   └── calendar_event.py   # Modèle CalendarEvent
├── services/               # Logique métier
│   ├── user_service.py     # Service utilisateurs
│   ├── event_type_service.py # Service types d'événements
│   └── calendar_event_service.py # Service événements calendrier
└── routes/                 # Routes API
    ├── users.py            # Endpoints utilisateurs
    ├── event_types.py      # Endpoints types d'événements
    └── calendar_events.py  # Endpoints événements calendrier
```

### Technologies utilisées
- **FastAPI** : Framework web asynchrone
- **SQLAlchemy** : ORM pour la base de données
- **PyMySQL** : Pilote MySQL
- **python-dotenv** : Gestion des variables d'environnement

## Installation et Configuration

### Prérequis
- Python 3.8+
- MySQL Server
- Base de données MySQL créée et remplie

### 1. Créer l'environnement virtuel

```bash
# Depuis le dossier racine du projet
python -m venv planif_venv
```

### 2. Activer l'environnement virtuel

**Windows (PowerShell) :**
```bash
planif_venv\Scripts\activate
```

**Linux/Mac :**
```bash
source planif_venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Éditez le fichier `.env` à la racine du projet :

```env
DATABASE_URL=mysql+pymysql://user:votre_mot_de_passe@localhost/meeting_planner
DEBUG=True
```

Remplacez `user` par votre utilisateur et `votre_mot_de_passe` par votre mot de passe MySQL.

## Lancement du serveur

### Mode développement (avec rechargement automatique)

```bash
uvicorn main:app --reload
```

Le serveur sera accessible sur : http://127.0.0.1:8000

### Documentation API

Une fois le serveur lancé, accédez à la documentation interactive :
- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

## Endpoints API

### Utilisateurs
- `GET /api/users/` - Liste tous les utilisateurs
- `GET /api/users/{id}` - Détails d'un utilisateur

### Types d'événements
- `GET /api/event-types/` - Liste tous les types
- `GET /api/event-types/{id}` - Détails d'un type

### Événements calendrier
- `GET /api/calendar-events/` - Liste tous les événements
- `GET /api/calendar-events/{id}` - Détails d'un événement
- `POST /api/calendar-events/` - Créer un événement
- `PUT /api/calendar-events/{id}` - Modifier un événement
- `DELETE /api/calendar-events/{id}` - Supprimer un événement
- `GET /api/users/{user_id}/calendar-events/` - Événements d'un utilisateur
- `GET /api/event-types/{type_id}/calendar-events/` - Événements d'un type

## Développement

### Ajouter une nouvelle entité
1. Créer le modèle dans `models/`
2. Créer le service dans `services/`
3. Créer les routes dans `routes/`
4. Importer et enregistrer dans `main.py`