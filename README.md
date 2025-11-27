# 🗓️ Planificateur de Réunions Intelligent

Système de planification de réunions basé sur des agents LLM, capable de comprendre des demandes en langage naturel (texte ou audio), de trouver automatiquement les créneaux disponibles et de générer des invitations personnalisées.

## 🎯 Fonctionnalités principales

- ✅ **Compréhension du langage naturel** : Saisie de demandes en français naturel
- 🎤 **Entrée vocale** : Enregistrement audio avec transcription automatique (Whisper)
- 🤖 **Orchestration multi-agent** : Agents LLM spécialisés coordonnés par LangChain
- 📅 **Gestion des disponibilités** : Recherche automatique de créneaux libres
- 📧 **Invitations automatiques** : Génération et envoi d'emails via Gmail
- 🔗 **Intégration Google Calendar** : Synchronisation des événements

## 🏗️ Architecture du projet

```
planificateur_reunion/
├── backend/                 # API FastAPI
│   ├── main.py             # Point d'entrée
│   ├── config.py           # Configuration
│   ├── models/             # Modèles de données (SQLAlchemy)
│   ├── routes/             # Endpoints API
│   ├── services/           # Logique métier et agents LLM
│   ├── prompts/            # Templates de prompts
│   └── credentials/        # Authentification Google
├── frontend/               # Interface Streamlit
│   ├── app.py             # Application principale
│   └── agent_api.py       # Client API
└── requirements.txt        # Dépendances Python
```

### Technologies utilisées

**Backend :**
- FastAPI (API REST)
- SQLAlchemy + MySQL (Base de données)
- LangChain (Framework agents LLM)
- Groq API (Modèles LLM + Whisper)
- Google APIs (Calendar & Gmail)

**Frontend :**
- Streamlit (Interface web)
- Requests (Client HTTP)

## 🚀 Installation et démarrage

### Prérequis

- Python 3.11+
- MySQL
- Compte Groq (pour API LLM)
- Compte Google (pour Calendar et Gmail)

### 1. Cloner le projet

```bash
git clone https://github.com/abdenourbounab/planificateur_reunion.git
cd planificateur_reunion
```

### 2. Créer un environnement virtuel

```bash
python -m venv planif_venv
planif_venv\Scripts\activate  # Windows
# source planif_venv/bin/activate  # Linux/Mac
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Créez une base de données MySQL :

```sql
CREATE DATABASE meeting_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurer les variables d'environnement

Créez un fichier `.env` dans le dossier `backend/` :

```bash
cd backend
cp .env.example .env
```

Éditez `.env` avec vos configurations :

```bash
# Base de données
DATABASE_URL=mysql+pymysql://root:votre_mot_de_passe@localhost/meeting_planner

# API Groq
GROQ_API_KEY=votre_cle_groq

# Modèles LLM
ORCHESTRATOR_MODEL=
INVITATION_MODEL=openai/gpt-oss-120b

# Températures
ORCHESTRATOR_TEMPERATURE=0.3
INVITATION_TEMPERATURE=0.7

# Debug
DEBUG=True
```

### 6. Configurer Google APIs

Pour l'intégration Google Calendar et Gmail :

1. Créez un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activez les APIs Calendar et Gmail
3. Créez des identifiants OAuth 2.0
4. Téléchargez le fichier JSON et placez-le dans `backend/credentials/`
5. Renommez-le en `client_secret_[...].json`

### 7. Lancer le backend

```bash
cd backend
uvicorn main:app --reload
```

Le backend sera accessible sur `http://127.0.0.1:8000`

Documentation API : `http://127.0.0.1:8000/docs`

### 8. Lancer le frontend

Dans un nouveau terminal :

```bash
cd frontend
streamlit run app.py
```

L'interface sera accessible sur `http://localhost:8501`

## 📖 Utilisation

### Mode Texte

1. Ouvrez l'interface Streamlit
2. Cliquez sur l'onglet **"✍️ Saisir du texte"**
3. Entrez votre demande, par exemple :
   ```
   Je voudrais une réunion avec Jean Dupont la semaine prochaine
   ```
4. Cliquez sur **"Envoyer"**

### Mode Vocal

1. Cliquez sur l'onglet **"🎤 Enregistrer une note vocale"**
2. Cliquez sur **"🎤 Enregistrer une note vocale"**
3. Énoncez votre demande clairement
4. Cliquez à nouveau pour arrêter l'enregistrement
5. L'audio est automatiquement transcrit et traité

### Résultats

Le système affichera :
- ✅ Le sujet de la réunion
- 📅 La date et l'heure proposées
- 👥 La liste des participants
- 📧 Le statut de l'invitation (envoyée ou non)

## 🔧 Configuration avancée

### Modifier les modèles LLM

Dans `backend/config.py`, ajustez les paramètres :

```python
ORCHESTRATOR_MODEL = "openai/gpt-oss-120b"  # Modèle pour l'orchestration
INVITATION_MODEL = "openai/gpt-oss-120b"    # Modèle pour les invitations
ORCHESTRATOR_TEMPERATURE = 0.3               # Créativité (0-1)
INVITATION_TEMPERATURE = 0.7                 # Créativité (0-1)
```

### Personnaliser les prompts

Modifiez les templates dans `backend/prompts/` pour adapter le comportement des agents.

## 📚 Documentation détaillée

- [Backend README](backend/README.md) - Architecture et API du backend
- [Frontend README](frontend/README.md) - Interface utilisateur

## 🔗 Liens utiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Groq API](https://console.groq.com/)
