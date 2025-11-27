# Frontend - Planificateur de Réunions

Interface utilisateur développée avec Streamlit pour interagir avec le système de planification de réunions.

## Architecture

### Structure du projet

```
frontend/
├── app.py              # Application Streamlit principale
├── agent_api.py        # Client API pour communiquer avec le backend
└── temp_audio/         # Stockage temporaire des enregistrements audio
```

### Technologies

- **Streamlit** : Framework pour applications web en Python
- **Requests** : Client HTTP pour appeler l'API backend
- **Audio Recording** : Enregistrement vocal intégré

## Fonctionnalités

### 1. Interface en mode sombre
Interface moderne avec thème sombre pour un confort visuel optimal.

### 2. Deux modes de saisie

#### Mode Textuel
- Zone de texte pour saisir une demande de réunion
- Exemples de requêtes suggérés
- Soumission instantanée

#### Mode Vocal
- Enregistrement audio en temps réel
- Indicateur visuel pendant l'enregistrement
- Conversion automatique en texte (Speech-to-Text)

### 3. Affichage des résultats

L'application affiche de manière claire :
- Le texte transcrit (en mode vocal)
- Le sujet de la réunion
- La date et l'heure proposées
- La liste des participants
- Le statut de l'invitation (envoyée ou non)
- Les messages d'erreur détaillés si nécessaire

### 4. Gestion des erreurs

Messages d'erreur explicites en cas de :
- Problème de connexion au backend
- Participant non trouvé dans la base de données
- Aucun créneau disponible
- Erreur de transcription audio

## Configuration

### Connexion au backend

Le fichier `agent_api.py` configure l'URL du backend :

```python
API_BASE_URL = "http://localhost:8000/api/orchestrator"
```

Modifiez cette URL si votre backend est déployé sur un autre serveur/port.

## Interface utilisateur

### En-tête
- Titre de l'application
- Instructions pour l'utilisateur

### Section de saisie
- **Onglet Texte** : Zone de texte multiligne
- **Onglet Audio** : Bouton d'enregistrement avec minuteur

### Section de résultats
Affichage dynamique des informations de la réunion planifiée :
- Carte avec fond sombre
- Bordure bleue pour une meilleure visibilité
- Icônes et formatage pour chaque information

## Démarrage

```bash
# Installer les dépendances
pip install streamlit requests

# Lancer l'application
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## Exemples de requêtes

### Texte
```
Je voudrais une réunion avec Jean Dupont la semaine prochaine
Planifie un meeting avec Marie Martin et Paul Durand demain à 14h
Organise une réunion de 2 heures avec l'équipe projet pour discuter du budget
```

### Audio
Cliquez sur "🎤 Enregistrer une note vocale" et énoncez clairement votre demande, par exemple :
- "Je voudrais organiser une réunion avec Jean Dupont pour la semaine prochaine"
- "Planifie un rendez-vous avec Marie Martin demain après-midi"

## Personnalisation

### Layout
Ajustez la configuration de la page dans `app.py` :
```python
st.set_page_config(page_title="Planificateur Intelligent", layout="wide")
```
