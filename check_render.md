# ✅ Checklist de Vérification Render

## Avant le Déploiement

- [ ] Les fichiers modifiés sont commités dans Git :
  - [ ] `seed_db.py` (modifié)
  - [ ] `render.yaml` (modifié)
  - [ ] `create_admin.py` (nouveau)
  - [ ] `test_login.py` (nouveau)
  - [ ] `DEPLOYMENT.md` (nouveau)

- [ ] Le code est poussé sur le repository distant :
  ```bash
  git push origin main
  ```

## Pendant le Déploiement Render

Dans les logs, vérifiez que vous voyez :

- [ ] ✅ `Running build command './build.sh'...`
- [ ] ✅ `pip install -r requirements.txt`
- [ ] ✅ `python manage.py collectstatic --no-input`
- [ ] ✅ `python manage.py migrate`
- [ ] ✅ `Seeding database...`
- [ ] ✅ `Superutilisateur créé: admin` ou `Superutilisateur 'admin' existe déjà`
- [ ] ✅ `Creating occupations...`
- [ ] ✅ `Success: Database seeded.`
- [ ] ✅ `Build successful`
- [ ] ✅ Service démarré avec succès

## Après le Déploiement

### Test 1 : Vérifier que le Backend est Accessible

Ouvrez dans votre navigateur :
```
https://inphb-hebergement-backend.onrender.com/swagger/
```

- [ ] ✅ La page Swagger UI s'affiche correctement

### Test 2 : Tester l'Endpoint de Login

Dans Swagger UI, testez `/api/auth/login/` :

1. Cliquez sur `POST /api/auth/login/`
2. Cliquez sur "Try it out"
3. Entrez :
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. Cliquez sur "Execute"

- [ ] ✅ Réponse 200 OK
- [ ] ✅ Vous recevez `access` et `refresh` tokens

### Test 3 : Tester depuis le Frontend

1. Ouvrez votre application frontend
2. Entrez les identifiants :
   - Username: `admin`
   - Password: `admin123`

- [ ] ✅ Connexion réussie
- [ ] ✅ Redirection vers le dashboard
- [ ] ✅ Données chargées (bâtiments, chambres, étudiants)

## En Cas de Problème

### Problème : "Identifiants incorrects"

**Solution** :
1. Allez dans Shell de Render
2. Exécutez :
   ```bash
   python create_admin.py
   ```
3. Réessayez

### Problème : Erreur 500

**Vérifications** :
- [ ] Variables d'environnement configurées dans Render
- [ ] `SECRET_KEY` est définie
- [ ] Migrations appliquées
- [ ] Consultez les logs pour plus de détails

### Problème : Base de données vide

**Solution** :
```bash
# Dans Render Shell
python seed_db.py
```

### Problème : CORS Error

**Vérification** :
- [ ] `CORS_ALLOW_ALL_ORIGINS = True` dans `settings.py`
- [ ] Ou `CORS_ALLOWED_ORIGINS` configuré avec l'URL du frontend

## Commandes Utiles Render Shell

### Créer/Réinitialiser l'admin
```bash
python create_admin.py
```

### Initialiser la base de données
```bash
python seed_db.py
```

### Vérifier les utilisateurs
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all().values('username', 'email', 'is_superuser')
>>> exit()
```

### Appliquer les migrations
```bash
python manage.py migrate
```

### Collecter les fichiers statiques
```bash
python manage.py collectstatic --no-input
```

## Configuration Frontend

Vérifiez que le fichier `.env.production` pointe vers le bon backend :

```env
REACT_APP_API_URL=https://inphb-hebergement-backend.onrender.com/api
```

- [ ] ✅ URL correcte dans `.env.production`
- [ ] ✅ Build du frontend avec la bonne variable d'environnement

## Documentation API Disponible

Une fois déployé, accédez à :

- **Swagger UI** : https://inphb-hebergement-backend.onrender.com/swagger/
- **ReDoc** : https://inphb-hebergement-backend.onrender.com/redoc/
- **Admin Django** : https://inphb-hebergement-backend.onrender.com/admin/

## Identifiants de Connexion

```
Username: admin
Email: admin@inphb.ci
Password: admin123
```

⚠️ **N'oubliez pas de changer le mot de passe après la première connexion !**

---

**Dernière mise à jour** : 2025-12-24
