# Credentials Google API

Ce dossier contient les fichiers d'authentification pour les APIs Google (Calendar et Gmail).

## ⚠️ IMPORTANT - Sécurité

**Ne commitez JAMAIS ces fichiers dans Git !**
Les fichiers `.json` et `.pickle` de ce dossier sont automatiquement ignorés par `.gitignore`.

## 📋 Fichiers requis

### À créer manuellement :
1. **`calendar_credentials.json`** - Credentials OAuth2 pour Google Calendar API
2. **`gmail_credentials.json`** - Credentials OAuth2 pour Gmail API

### Générés automatiquement au premier lancement :
3. **`calendar_token.pickle`** - Token d'authentification Calendar (auto-généré)
4. **`gmail_token.pickle`** - Token d'authentification Gmail (auto-généré)

## 🔧 Configuration

### 1. Obtenir les credentials OAuth2

1. Allez sur https://console.cloud.google.com/
2. Créez ou sélectionnez un projet
3. Activez les APIs :
   - Google Calendar API
   - Gmail API
4. Créez des credentials OAuth 2.0 (type: Desktop app)
5. Téléchargez le fichier JSON

### 2. Placer les credentials

```bash
# Depuis le dossier racine du projet
cp ~/Downloads/client_secret_*.json backend/credentials/calendar_credentials.json
cp backend/credentials/calendar_credentials.json backend/credentials/gmail_credentials.json
```

**Note** : Vous pouvez utiliser le même fichier credentials pour les deux services.

### 3. Première authentification

Au premier lancement de l'application :
1. Une fenêtre de navigateur s'ouvrira automatiquement
2. Connectez-vous avec votre compte Google
3. Autorisez l'accès aux APIs
4. Les tokens seront automatiquement sauvegardés

## 📁 Structure finale

```
credentials/
├── .gitkeep                    # Garde le dossier dans Git
├── README.md                   # Ce fichier
├── calendar_credentials.json   # À créer (OAuth credentials)
├── calendar_token.pickle       # Auto-généré
├── gmail_credentials.json      # À créer (OAuth credentials)
└── gmail_token.pickle         # Auto-généré
```

## 🔄 Renouvellement des tokens

Les tokens sont automatiquement renouvelés par l'application. Si vous rencontrez des problèmes :

```bash
# Supprimez les tokens pour forcer une nouvelle authentification
cd backend/credentials
rm calendar_token.pickle gmail_token.pickle
```

Relancez l'application et réauthentifiez-vous.

## 📖 Documentation

Pour plus d'informations, consultez :
- [Google Calendar API](https://developers.google.com/calendar/api)
- [Gmail API](https://developers.google.com/gmail/api)
- [OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
