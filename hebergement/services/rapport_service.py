from django.db.models import Count, Q
from ..models import Batiment, Etudiant, Occupation, Chambre

def get_dashboard_stats():
    """
    Retourne les statistiques complètes pour le dashboard (formatage pour le front).
    """
    total_etudiants = Etudiant.objects.count()
    total_chambres = Chambre.objects.count()
    total_occupations = Occupation.objects.filter(date_sortie__isnull=True).count()
    
    taux_occupation = (total_occupations / total_chambres * 100) if total_chambres > 0 else 0
    
    # 1. Stats de base
    stats = {
        'tauxOccupation': round(taux_occupation, 1),
        'chambresDispo': total_chambres - total_occupations,
        'etudiantsSuspendus': Etudiant.objects.filter(etat_etudiant='SUSPENDU').count(),
        'clesNonDeposees': Occupation.objects.filter(cle_deposee=False, date_sortie__isnull=False).count(),
    }

    # 2. Répartition Sexe
    repartition_sexe = [
        {'name': 'Garçons', 'value': Etudiant.objects.filter(sexe='M').count()},
        {'name': 'Filles', 'value': Etudiant.objects.filter(sexe='F').count()},
    ]

    # 3. Occupation Bâtiments
    occupation_batiments = get_occupation_par_batiment()
    # On reformate pour Recharts (name, taux)
    occupation_recharts = [
        {'name': b['batiment'], 'taux': b['taux']} for b in occupation_batiments
    ]

    # 4. Alertes (Simulées ou réelles)
    # Pour le moment on peut en simuler quelques-unes basées sur la DB
    alertes = []
    derniers_suspendus = Etudiant.objects.filter(etat_etudiant='SUSPENDU')[:3]
    for e in derniers_suspendus:
        alertes.append({
            'id': f'susp-{e.mat_etudiant}',
            'type': 'suspension',
            'message': f'Étudiant {e.nom} suspendu',
            'time': 'Récent'
        })

    return {
        'stats': stats,
        'repartitionSexe': repartition_sexe,
        'occupationBatiments': occupation_recharts,
        'alertes': alertes
    }

def get_occupation_par_batiment():
    """
    Retourne le taux d'occupation par bâtiment.
    """
    stats = []
    batiments = Batiment.objects.all()
    for bat in batiments:
        occupees = Occupation.objects.filter(
            chambre__palier__batiment=bat, 
            date_sortie__isnull=True
        ).count()
        capacite = bat.capacite
        stats.append({
            'batiment': bat.id_batiment,
            'nom': bat.nom_batiment,
            'occupees': occupees,
            'capacite': capacite,
            'taux': round((occupees / capacite * 100), 2) if capacite > 0 else 0
        })
    return stats

def get_repartition_par_niveau():
    """
    Retourne la répartition des étudiants par niveau d'études.
    """
    return Etudiant.objects.values('niveau_etudes').annotate(count=Count('mat_etudiant')).order_by('niveau_etudes')
