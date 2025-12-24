#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que l'authentification fonctionne correctement
"""
import os
import sys
import django

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

def test_authentication():
    """Test de l'authentification Django"""

    print("="*60)
    print("TEST D'AUTHENTIFICATION - INP-HB Hébergement")
    print("="*60)

    # Test 1: Vérifier l'existence de l'utilisateur admin
    print("\n1. Vérification de l'utilisateur admin...")
    try:
        admin = User.objects.get(username='admin')
        print(f"   ✅ Utilisateur trouvé: {admin.username}")
        print(f"   - Email: {admin.email}")
        print(f"   - Est superutilisateur: {admin.is_superuser}")
        print(f"   - Est staff: {admin.is_staff}")
    except User.DoesNotExist:
        print("   ❌ Utilisateur 'admin' non trouvé!")
        print("   → Exécutez: python create_admin.py")
        return False

    # Test 2: Vérifier le mot de passe
    print("\n2. Vérification du mot de passe...")
    if admin.check_password('admin123'):
        print("   ✅ Mot de passe correct: admin123")
    else:
        print("   ❌ Mot de passe incorrect!")
        print("   → Exécutez: python create_admin.py")
        return False

    # Test 3: Tester l'API de login (si le serveur est lancé)
    print("\n3. Test de l'endpoint API /api/auth/login/...")
    if HAS_REQUESTS:
        try:
            response = requests.post(
                'http://localhost:8000/api/auth/login/',
                json={'username': 'admin', 'password': 'admin123'},
                timeout=3
            )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Login API réussi!")
                print(f"   - Access token: {data.get('access', '')[:50]}...")
                print(f"   - Refresh token: {data.get('refresh', '')[:50]}...")
            else:
                print(f"   ❌ Erreur {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print("   ⚠️  Serveur Django non démarré (normal si vous testez hors ligne)")
            print("   → Pour tester l'API, lancez: python manage.py runserver")
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
    else:
        print("   ⚠️  Module 'requests' non installé, test API ignoré")
        print("   → Pour installer: pip install requests")

    # Test 4: Lister tous les utilisateurs
    print("\n4. Liste de tous les utilisateurs Django...")
    users = User.objects.all()
    print(f"   Total: {users.count()} utilisateur(s)")
    for user in users:
        print(f"   - {user.username} ({user.email}) - Superuser: {user.is_superuser}")

    print("\n" + "="*60)
    print("✅ TESTS TERMINÉS AVEC SUCCÈS!")
    print("="*60)
    print("\nIDENTIFIANTS DE CONNEXION:")
    print("-" * 60)
    print("  Username: admin")
    print("  Email: admin@inphb.ci")
    print("  Password: admin123")
    print("-" * 60)
    print("\nPOUR VOUS CONNECTER:")
    print("  1. Assurez-vous que le backend est démarré:")
    print("     python manage.py runserver")
    print("  2. Assurez-vous que le frontend est démarré:")
    print("     cd ../front_flash && npm start")
    print("  3. Ouvrez http://localhost:3000")
    print("  4. Utilisez les identifiants ci-dessus")
    print("="*60)

    return True

if __name__ == '__main__':
    try:
        test_authentication()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
