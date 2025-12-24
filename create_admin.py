#!/usr/bin/env python
"""
Script pour créer un utilisateur admin pour l'application INP-HB Hébergement
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    """Créer un superutilisateur admin"""
    username = 'admin'
    email = 'admin@inphb.ci'
    password = 'admin123'

    if User.objects.filter(username=username).exists():
        print(f"L'utilisateur '{username}' existe déjà.")
        # Mettre à jour le mot de passe si l'utilisateur existe
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Mot de passe mis à jour pour l'utilisateur '{username}'")
    else:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='INP-HB'
        )
        print(f"Superutilisateur '{username}' créé avec succès!")

    print("\n" + "="*50)
    print("IDENTIFIANTS DE CONNEXION:")
    print("="*50)
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print("="*50)

if __name__ == '__main__':
    create_admin()
