import random
from datetime import date, timedelta
from django.db.models import Q, Count
from ..models import Etudiant, Chambre, Occupation, Batiment, Palier

ORDRE_NIVEAUX = {
    'ING3': 1, 'MASTER2': 1, 'TS3': 1,
    'ING2': 2, 'MASTER1': 2, 'TS2': 2,
    'ING1': 3, 'TS1': 3,
    'PREPA2': 4,
    'PREPA1': 5
}

def valider_affectation(etudiant, chambre):
    """
    Valide si un étudiant peut être affecté à une chambre selon les règles métier.
    """
    # 1. Chambre EN_SERVICE et disponible
    if chambre.etat_service != 'EN_SERVICE':
        return False, "La chambre n'est pas en service."
    
    if not chambre.is_available:
        return False, "La chambre n'est pas disponible."

    # 2. Compatibilité sexe
    batiment = chambre.palier.batiment
    sexe_map = {'M': 'GARCONS', 'F': 'FILLES'}
    if batiment.type_public != sexe_map.get(etudiant.sexe) and batiment.type_public != 'MIXTE':
        return False, f"Le bâtiment {batiment.id_batiment} est réservé aux {batiment.type_public}."

    # 3. Compatibilité niveau
    niveaux_autorises = batiment.niveaux_etudes.split(',')
    if etudiant.niveau_etudes not in niveaux_autorises and batiment.niveaux_etudes != 'TOUS':
        return False, f"Niveau {etudiant.niveau_etudes} non autorisé dans ce bâtiment."

    # 4. Handicapé → RDC obligatoire
    if etudiant.est_handicape:
        if chambre.palier.niveau_palier != 0:
            return False, "Les étudiants handicapés doivent être au RDC."

    # 5. Bâtiment MIXTE : règles étage
    if batiment.type_public == 'MIXTE':
        fin_cycle = etudiant.niveau_etudes in ['TS3', 'ING3', 'MASTER2']
        if etudiant.sexe == 'F':
            if fin_cycle:
                if chambre.palier.niveau_palier != 2:
                    return False, "Filles en fin de cycle (MIXTE) -> R2 obligatoire."
            else:
                if chambre.palier.niveau_palier != 1:
                    return False, "Filles (MIXTE) -> R1 obligatoire."

    # 6. Chambre double : vérifier place restante
    if chambre.type_chambre == 'DOUBLE':
        nb_occupants = Occupation.objects.filter(chambre=chambre, date_sortie__isnull=True).count()
        if nb_occupants >= 2:
            return False, "La chambre double est déjà complète."
    elif chambre.type_chambre == 'SIMPLE':
        nb_occupants = Occupation.objects.filter(chambre=chambre, date_sortie__isnull=True).count()
        if nb_occupants >= 1:
            return False, "La chambre simple est déjà occupée."

    return True, "Validé"

def attribution_automatique(annee_academique):
    """
    Algorithme d'attribution automatique en masse.
    """
    # 1. Récupérer étudiants sans affectation pour l'année donnée
    etudiants_affectes = Occupation.objects.filter(annee_academique=annee_academique).values_list('etudiant_id', flat=True)
    etudiants = Etudiant.objects.exclude(mat_etudiant__in=etudiants_affectes).filter(etat_etudiant='ACTIF')
    
    # 2. Trier par priorité
    # Handicapés > Fin de cycle > Niveau (décroissant)
    etudiants_list = list(etudiants)
    etudiants_list.sort(key=lambda e: (
        not e.est_handicape,
        e.niveau_etudes not in ['TS3', 'ING3', 'MASTER2'],
        ORDRE_NIVEAUX.get(e.niveau_etudes, 99)
    ))
    
    resultats = {'succes': 0, 'echecs': []}
    
    for etudiant in etudiants_list:
        chambres = get_chambres_compatibles(etudiant)
        
        if chambres.exists():
            chambre = random.choice(list(chambres))
            
            # Créer occupation
            Occupation.objects.create(
                etudiant=etudiant,
                chambre=chambre,
                date_entree=date.today(),
                annee_academique=annee_academique
            )
            
            # Mettre à jour disponibilité de la chambre
            update_disponibilite(chambre)
            
            resultats['succes'] += 1
        else:
            resultats['echecs'].append(etudiant.mat_etudiant)
    
    return resultats

def get_chambres_compatibles(etudiant):
    """
    Retourne les chambres compatibles avec l'étudiant selon toutes les règles métier.
    """
    # 1. Filtrer les bâtiments par sexe
    sexe_long = 'GARCONS' if etudiant.sexe == 'M' else 'FILLES'
    batiments_sexe = Batiment.objects.filter(
        Q(type_public=sexe_long) | Q(type_public='MIXTE')
    )
    
    # 2. Filtrer les bâtiments par niveau et filière
    batiments_compatibles_ids = []
    for bat in batiments_sexe:
        if bat.niveaux_etudes == 'TOUS':
            batiments_compatibles_ids.append(bat.id_batiment)
            continue
            
        levels_str = bat.niveaux_etudes
        
        # Cas spécial : Fin de cycle
        if levels_str == 'FIN_DE_CYCLE':
            if etudiant.niveau_etudes in ['ING3', 'TS3', 'MASTER2']:
                batiments_compatibles_ids.append(bat.id_batiment)
            continue
            
        # Cas spécial : Filière (ex: FILIERE:Data Science,Mécatronique)
        if levels_str.startswith('FILIERE:'):
            filieres = [f.strip().lower() for f in levels_str.replace('FILIERE:', '').split(',')]
            if etudiant.filiere and etudiant.filiere.lower() in filieres:
                batiments_compatibles_ids.append(bat.id_batiment)
            continue
            
        # Filtrage standard par liste CSV
        niveaux = [n.strip() for n in levels_str.split(',')]
        if etudiant.niveau_etudes in niveaux:
            batiments_compatibles_ids.append(bat.id_batiment)
    
    paliers = Palier.objects.filter(batiment_id__in=batiments_compatibles_ids)
    
    # 3. Contrainte Handicapé → RDC
    if etudiant.est_handicape:
        paliers = paliers.filter(niveau_palier=0)
    
    return Chambre.objects.filter(
        palier__in=paliers,
        etat_service='EN_SERVICE',
        is_available=True
    )

def update_disponibilite(chambre):
    nb_occupants = Occupation.objects.filter(chambre=chambre, date_sortie__isnull=True).count()
    if chambre.type_chambre == 'SIMPLE':
        chambre.is_available = (nb_occupants == 0)
    else:
        chambre.is_available = (nb_occupants < 2)
    chambre.save()
