# Frontend (Application Web)

## Rôle
Interface utilisateur pour interagir avec le système de planification de réunions.

## Responsabilités
- Afficher un formulaire pour saisir une demande de réunion
- Saisie des participants (Paul, Sarah, Lisa, etc.)
- Choix de la période (semaine prochaine, dates spécifiques)
- Options : générer rapport, créer présentation
- Afficher les créneaux proposés et la confirmation
- Visualiser les calendriers et les disponibilités

## Technologies suggérées
- React / Vue.js / Angular
- Appels REST vers `backend/routes/`

## Flux
1. L'utilisateur saisit : "Planifie une réunion avec Paul, Sarah et Lisa la semaine prochaine"
2. Frontend appelle `POST /api/meetings` (backend)
3. Affiche la progression et les résultats retournés par le backend

## Fichiers à créer (plus tard)
- `src/components/MeetingForm.jsx`
- `src/components/Calendar.jsx`
- `src/services/api.js`
- `public/index.html`
