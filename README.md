# Planificateur de Réunions - Système Multi-Agent

## 📋 Description
Système intelligent de planification de réunions utilisant une architecture multi-agent. L'application trouve automatiquement le meilleur créneau en analysant les calendriers des participants et génère les invitations.

## 🏗️ Architecture

Le projet utilise une architecture en 4 couches :

### 1. **Frontend** (`frontend/`)
Application web permettant aux utilisateurs de :
- Saisir une demande de réunion
- Spécifier les participants et la période
- Visualiser les créneaux proposés
- Consulter l'invitation générée

### 2. **Backend API** (`backend/`)
API REST FastAPI organisant la logique métier :
- **Routes** : endpoints HTTP (`/api/meetings`, `/api/calendars`, `/api/health`)
- **Services** : orchestration des agents et gestion des calendriers
- **Models** : modèles de données (SQLAlchemy + Pydantic) + configuration DB
- **Agents** : modules Python (fichiers `.py`) :
  - `agent_interface.py` : point d'entrée
  - `agent_planner.py` : calcul des créneaux optimaux
  - `agent_executor.py` : génération des invitations
  - `agent_report.py` : création de rapports (optionnel)
  - `agent_presentation.py` : génération de présentations PowerPoint (optionnel)

### 3. **Base de données** (PostgreSQL)
Configuration dans `backend/models/database.py` (SQLAlchemy).
Stocke :
- Utilisateurs et leurs calendriers
- Événements calendaires
- Historique des réunions planifiées

## 🔄 Flux simplifié

```
Utilisateur → Frontend → Backend API (Routes)
                              ↓
                         Services (Orchestrateur)
                              ↓
                    ┌─────────┴─────────┐
                    ▼                   ▼
              Agents (Python)    Database (PostgreSQL)
              • interface              ⇅
              • planner          Models (SQLAlchemy)
              • executor
              • report
              • presentation
```

## 📁 Structure du projet

```
planificateur_reunion/
├── frontend/              # Application web (React/Vue)
│   └── src/
│
├── backend/               # API FastAPI + Agents + Models
│   ├── routes/           # Endpoints HTTP
│   ├── services/         # Logique métier + orchestrateur
│   ├── models/           # Modèles SQLAlchemy + database.py
│   ├── agents/           # Fichiers Python des agents
│   │   ├── agent_interface.py
│   │   ├── agent_planner.py
│   │   ├── agent_executor.py
│   │   ├── agent_report.py
│   │   └── agent_presentation.py
│   └── main.py           # Point d'entrée FastAPI
│
├── ARCHITECTURE.md       # Documentation détaillée de l'architecture
└── README.md            # Ce fichier
```

## 📖 Documentation

- **ARCHITECTURE.md** : documentation complète de l'architecture (diagrammes, flux)
- **backend/README.md** : détails sur l'API FastAPI
- **backend/agents/README.md** : fonctionnement du système multi-agent
- Chaque sous-dossier contient son propre README

## 🚀 Démarrage rapide

### Prérequis
- Python 3.10+
- Node.js 16+ (pour le frontend)
- PostgreSQL 13+

### Installation (à venir)
Les scripts d'installation et de déploiement seront ajoutés dans les prochaines étapes.

## 🎯 Objectifs du projet

Ce projet fait partie d'un hackathon sur les systèmes multi-agents et vise à :
- Démontrer la coopération entre agents spécialisés (modules Python)
- Utiliser FastAPI pour l'API REST
- Intégrer des LLMs pour l'optimisation contextuelle (optionnel)
- Créer une architecture simple, robuste et extensible

## 📝 État actuel

✅ Architecture définie  
✅ Structure de dossiers créée  
✅ Documentation de l'architecture  
⏳ Implémentation du backend API  
⏳ Implémentation des agents  
⏳ Développement du frontend  
⏳ Scripts de base de données  

## 👥 Équipe

Projet réalisé dans le cadre du M2 Data & IA (groupes de 4)