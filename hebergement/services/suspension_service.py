from datetime import date, timedelta
from ..models import Etudiant, Occupation

def declencher_suspensions(annee_academique_obj):
    """
    Déclenche les suspensions automatiques pour ceux qui n'ont pas déposé de clés.
    """
    date_limite = annee_academique_obj.date_limite_depot_cle
    if date.today() >= date_limite:
        etudiants = Etudiant.objects.filter(
            occupations__cle_deposee=False,
            occupations__annee_academique=annee_academique_obj.id_annee
        ).exclude(
            est_international=True,
            niveau_etudes__in=['TS3', 'ING3', 'MASTER2']
        ).distinct()

        for e in etudiants:
            e.etat_etudiant = 'SUSPENDU'
            e.date_suspension = date.today()
            e.save()
        return len(etudiants)
    return 0

def debloquer_etudiant(etudiant):
    """
    Débloque un étudiant et le rend actif.
    """
    etudiant.etat_etudiant = 'ACTIF'
    etudiant.date_deblocage = None
    etudiant.date_suspension = None
    etudiant.save()
    return etudiant
