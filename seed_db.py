import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from hebergement.models import Gestionnaire, Batiment, Palier, Chambre, Etudiant, Occupation, AnneeAcademique
from django.contrib.auth.models import User

def seed_data():
    print("Seeding database...")

    # 0. Créer un superutilisateur Django pour la connexion
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@inphb.ci',
            password='admin123',
            first_name='Admin',
            last_name='INP-HB'
        )
        print(f"Superutilisateur créé: {admin_user.username}")
    else:
        print("Superutilisateur 'admin' existe déjà")

    # 1. Annee Academique
    annee, _ = AnneeAcademique.objects.get_or_create(
        id_annee='2024-2025',
        defaults={
            'libelle': 'Année Académique 2024-2025',
            'date_debut': date(2024, 9, 1),
            'date_fin': date(2025, 7, 31),
            'date_limite_depot_cle': date(2025, 8, 5),
            'est_active': True
        }
    )

    # 2. Gestionnaire
    gest, _ = Gestionnaire.objects.get_or_create(
        email='gestionnaire@inphb.ci',
        defaults={
            'nom': 'Soro',
            'prenom': 'Moussa',
            'contact': '0102030405',
            'mot_de_passe': 'pbkdf2_sha256$...', # Simulated hash
            'role': 'GESTIONNAIRE'
        }
    )

    # 3. Batiments, Paliers, Chambres
    # Tous les bâtiments sauf I et O (15 bâtiments au total)
    batiments_config = {
        'A': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'B': {'public': 'FILLES', 'niveaux': 2, 'chambres': 64},
        'C': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'D': {'public': 'FILLES', 'niveaux': 3, 'chambres': 96},
        'E': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'F': {'public': 'FILLES', 'niveaux': 3, 'chambres': 96},
        'G': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'H': {'public': 'FILLES', 'niveaux': 3, 'chambres': 96},
        'J': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'K': {'public': 'FILLES', 'niveaux': 3, 'chambres': 96},
        'L': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'M': {'public': 'FILLES', 'niveaux': 3, 'chambres': 96},
        'N': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'P': {'public': 'FILLES', 'niveaux': 3, 'chambres': 96},
        'T': {'public': 'GARCONS', 'niveaux': 3, 'chambres': 96},
        'R': {'public': 'FILLES', 'niveaux': 3, 'chambres': 96},
    }

    # Liste des statuts possibles avec leur probabilité
    service_statuses = ['EN_SERVICE', 'EN_SERVICE', 'EN_SERVICE', 'EN_REPARATION', 'HORS_SERVICE']

    for char, config in batiments_config.items():
        bat, _ = Batiment.objects.get_or_create(
            id_batiment=char,
            defaults={
                'nom_batiment': f'Bâtiment {char}',
                'type_public': config['public'],
                'niveaux_etudes': 'TOUS',
                'type_chambre': 'DOUBLE',
                'nombre_niveaux': config['niveaux'],
                'nombre_chambres': config['chambres'],
                'capacite': config['chambres'] * 2,
                'gestionnaire': gest
            }
        )

        # Créer les paliers
        for niv in range(config['niveaux']):
            pal_id = f"{char}-R{niv}"
            pal, _ = Palier.objects.get_or_create(
                id_palier=pal_id,
                defaults={
                    'niveau_palier': niv,
                    'nbre_chambres': 32,
                    'batiment': bat
                }
            )

            # Créer 32 chambres par palier
            for c in range(1, 33):
                # Numérotation: 1-32 (R0), 33-64 (R1), 65-96 (R2)
                chambre_num = niv * 32 + c
                ch_id = f"{char}-{chambre_num}"
                # Assigner un statut aléatoire pour avoir une distribution variée
                etat_service = random.choice(service_statuses)

                Chambre.objects.get_or_create(
                    id_chambre=ch_id,
                    defaults={
                        'numero_chambre': chambre_num,
                        'type_chambre': 'DOUBLE',
                        'etat_chambre': 'BON ETAT' if etat_service == 'EN_SERVICE' else 'NECESSITA REPARATION',
                        'etat_service': etat_service,
                        'is_available': etat_service == 'EN_SERVICE',
                        'capacite': 2,
                        'palier': pal
                    }
                )

    # 4. Etudiants - Créer plusieurs étudiants pour avoir des chambres occupées
    noms_garcons = ['KOUADIO', 'TRAORE', 'KONE', 'DIALLO', 'OUATTARA', 'KONAN', 'BAMBA', 'YAO', 'N\'GUESSAN', 'SORO']
    prenoms_garcons = ['Jean', 'Bakary', 'Moussa', 'Amadou', 'Ibrahim', 'Yao', 'Kouassi', 'Kofi', 'Koffi', 'Drissa']
    noms_filles = ['DIARRA', 'N\'GORAN', 'BAMBA', 'KOFFI', 'COULIBALY', 'TOURE', 'ADJOUA', 'AYA', 'AFFOUE', 'AMENAN']
    prenoms_filles = ['Fatou', 'Awa', 'Mariam', 'Aissata', 'Aminata', 'Adjoua', 'Aya', 'Affoue', 'Amenan', 'Marie']
    niveaux = ['PREPA1', 'PREPA2', 'TS1', 'TS2', 'TS3', 'ING1', 'ING2', 'ING3']

    etudiants_created = []

    # Créer 50 étudiants garçons
    for i in range(50):
        mat = f'24INP{str(i+1).zfill(3)}'
        nom = random.choice(noms_garcons)
        prenom = random.choice(prenoms_garcons)
        niveau = random.choice(niveaux)

        etud, created = Etudiant.objects.get_or_create(
            mat_etudiant=mat,
            defaults={
                'nom': nom,
                'prenom': prenom,
                'sexe': 'M',
                'nationalite': random.choice(['Ivoirienne', 'Malienne', 'Burkinabé', 'Sénégalaise']),
                'telephone': f'07{random.randint(10000000, 99999999)}',
                'email': f'{prenom.lower()}.{nom.lower()}{i}@inphb.ci',
                'ecole': 'ESI' if 'ING' in niveau else 'ESTP',
                'filiere': random.choice(['Informatique', 'Génie Civil', 'Génie Electrique']),
                'niveau_etudes': niveau,
                'etat_etudiant': 'ACTIF'
            }
        )
        etudiants_created.append(etud)

    # Créer 50 étudiantes filles
    for i in range(50, 100):
        mat = f'24INP{str(i+1).zfill(3)}'
        nom = random.choice(noms_filles)
        prenom = random.choice(prenoms_filles)
        niveau = random.choice(niveaux)

        etud, created = Etudiant.objects.get_or_create(
            mat_etudiant=mat,
            defaults={
                'nom': nom,
                'prenom': prenom,
                'sexe': 'F',
                'nationalite': random.choice(['Ivoirienne', 'Malienne', 'Burkinabé', 'Sénégalaise']),
                'telephone': f'07{random.randint(10000000, 99999999)}',
                'email': f'{prenom.lower()}.{nom.lower()}{i}@inphb.ci',
                'ecole': 'ESI' if 'ING' in niveau else 'ESTP',
                'filiere': random.choice(['Informatique', 'Génie Civil', 'Génie Electrique']),
                'niveau_etudes': niveau,
                'etat_etudiant': 'ACTIF'
            }
        )
        etudiants_created.append(etud)

    # 5. Occupations - Occuper aléatoirement des chambres en service
    print("Creating occupations...")
    chambres_garcons = list(Chambre.objects.filter(
        etat_service='EN_SERVICE',
        palier__batiment__type_public='GARCONS'
    ).order_by('?')[:60])  # 60 chambres garçons

    chambres_filles = list(Chambre.objects.filter(
        etat_service='EN_SERVICE',
        palier__batiment__type_public='FILLES'
    ).order_by('?')[:60])  # 60 chambres filles

    etud_idx_garcons = 0
    etud_idx_filles = 50

    # Occuper les chambres garçons (1 ou 2 étudiants par chambre)
    for chambre in chambres_garcons[:40]:
        nb_occupants = random.randint(1, 2)  # 1 ou 2 occupants
        for _ in range(nb_occupants):
            if etud_idx_garcons < 50:
                etud = etudiants_created[etud_idx_garcons]
                Occupation.objects.get_or_create(
                    etudiant=etud,
                    chambre=chambre,
                    annee_academique='2024-2025',
                    defaults={
                        'date_entree': date(2024, 9, random.randint(1, 30)),
                        'cle_deposee': False
                    }
                )
                etud_idx_garcons += 1

    # Occuper les chambres filles (1 ou 2 étudiants par chambre)
    for chambre in chambres_filles[:40]:
        nb_occupants = random.randint(1, 2)  # 1 ou 2 occupants
        for _ in range(nb_occupants):
            if etud_idx_filles < 100:
                etud = etudiants_created[etud_idx_filles]
                Occupation.objects.get_or_create(
                    etudiant=etud,
                    chambre=chambre,
                    annee_academique='2024-2025',
                    defaults={
                        'date_entree': date(2024, 9, random.randint(1, 30)),
                        'cle_deposee': False
                    }
                )
                etud_idx_filles += 1

    print("Success: Database seeded.")

if __name__ == '__main__':
    seed_data()
