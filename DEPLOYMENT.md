# Déploiement et Configuration - INP-HB Hébergement

## Déploiement sur Render

### 1. Configuration automatique

Le déploiement sur Render est automatisé via le fichier `build.sh` qui :
- Installe les dépendances
- Collecte les fichiers statiques
- Effectue les migrations de base de données
- Initialise la base de données avec des données de test
- Crée automatiquement un superutilisateur

### 2. Identifiants de connexion par défaut

Après le déploiement, vous pouvez vous connecter avec :

```
Username: admin
Email: admin@inphb.ci
Password: admin123
```

⚠️ **IMPORTANT**: Changez ce mot de passe en production !

### 3. Scripts disponibles

#### Créer/Réinitialiser l'utilisateur admin
```bash
python create_admin.py
```

#### Initialiser la base de données
```bash
python seed_db.py
```

#### Créer un nouveau superutilisateur manuellement
```bash
python manage.py createsuperuser
```

## Configuration locale

### Installation
```bash
pip install -r requirements.txt
```

### Migrations
```bash
python manage.py migrate
```

### Initialiser les données
```bash
python seed_db.py
```

### Lancer le serveur
```bash
python manage.py runserver
```

## Endpoints API

### Authentification
- `POST /api/auth/login/` - Connexion (retourne access et refresh tokens)
- `POST /api/auth/token/refresh/` - Rafraîchir le token
- `GET /api/auth/me/` - Obtenir les infos de l'utilisateur connecté

### Ressources principales
- `/api/etudiants/` - Gestion des étudiants
- `/api/chambres/` - Gestion des chambres
- `/api/affectations/` - Gestion des affectations
- `/api/rapports/` - Rapports et statistiques

### Documentation API
- `/swagger/` - Documentation interactive Swagger UI
- `/redoc/` - Documentation ReDoc

## Connexion à l'application frontend

L'application frontend doit envoyer les identifiants à l'endpoint `/api/auth/login/` :

```javascript
POST /api/auth/login/
{
  "username": "admin",
  "password": "admin123"
}

// Réponse
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Ensuite, utilisez le token d'accès dans l'en-tête Authorization :
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Résolution des problèmes

### Impossible de se connecter
1. Vérifiez que le service backend est bien démarré sur Render
2. Réexécutez `python create_admin.py` dans la console Render
3. Vérifiez les logs de Render pour les erreurs

### Base de données vide
1. Exécutez `python seed_db.py` dans la console Render
2. Vérifiez que les migrations sont bien appliquées : `python manage.py migrate`

### Erreur 500 sur Render
1. Vérifiez les variables d'environnement (SECRET_KEY, etc.)
2. Consultez les logs de Render
3. Vérifiez que toutes les dépendances sont dans `requirements.txt`
