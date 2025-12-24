from django.db import models
from django.contrib.auth.models import AbstractUser

# On utilisera un modèle personnalisé pour le Gestionnaire si besoin de l'intégrer à Django Auth
# Mais le prompt demande un modèle GESTIONNAIRE spécifique avec ses champs.

class Gestionnaire(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'ADMIN'),
        ('GESTIONNAIRE', 'GESTIONNAIRE'),
    ]
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=255)  # Hashé bcrypt
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.role})"

class Batiment(models.Model):
    PUBLIC_CHOICES = [
        ('GARCONS', 'GARCONS'),
        ('FILLES', 'FILLES'),
        ('MIXTE', 'MIXTE'),
    ]
    id_batiment = models.CharField(max_length=1, primary_key=True)  # 'A', 'B', etc.
    nom_batiment = models.CharField(max_length=50)
    type_public = models.CharField(max_length=10, choices=PUBLIC_CHOICES)
    niveaux_etudes = models.CharField(max_length=100)  # Ex: 'PREPA1,TS1' ou 'TOUS'
    type_chambre = models.CharField(max_length=10, choices=[('SIMPLE', 'SIMPLE'), ('DOUBLE', 'DOUBLE')])
    nombre_niveaux = models.IntegerField()  # 2 ou 3
    nombre_chambres = models.IntegerField()  # 64 ou 96
    capacite = models.IntegerField()
    gestionnaire = models.ForeignKey(Gestionnaire, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Bâtiment {self.id_batiment} - {self.nom_batiment}"

class Palier(models.Model):
    id_palier = models.CharField(max_length=10, primary_key=True)  # Ex: 'A-R0'
    niveau_palier = models.IntegerField()  # 0, 1, 2
    nbre_chambres = models.IntegerField(default=32)
    batiment = models.ForeignKey(Batiment, on_delete=models.CASCADE, related_name='paliers')

    def __str__(self):
        return self.id_palier

class Chambre(models.Model):
    SERVICE_CHOICES = [
        ('EN_SERVICE', 'EN_SERVICE'),
        ('HORS_SERVICE', 'HORS_SERVICE'),
        ('EN_REPARATION', 'EN_REPARATION'),
    ]
    id_chambre = models.CharField(max_length=10, primary_key=True)  # Ex: 'A-01'
    numero_chambre = models.IntegerField()
    type_chambre = models.CharField(max_length=10, choices=[('SIMPLE', 'SIMPLE'), ('DOUBLE', 'DOUBLE')])
    etat_chambre = models.CharField(max_length=50)
    etat_service = models.CharField(max_length=15, choices=SERVICE_CHOICES, default='EN_SERVICE')
    is_available = models.BooleanField(default=True)
    capacite = models.IntegerField()  # 1 ou 2
    palier = models.ForeignKey(Palier, on_delete=models.CASCADE, related_name='chambres')

    def __str__(self):
        return self.id_chambre

class Etudiant(models.Model):
    SEXE_CHOICES = [('M', 'M'), ('F', 'F')]
    ETAT_CHOICES = [
        ('ACTIF', 'ACTIF'),
        ('SUSPENDU', 'SUSPENDU'),
        ('BLOQUE', 'BLOQUE'),
    ]
    NIVEAU_CHOICES = [
        ('PREPA1','PREPA1'),('PREPA2','PREPA2'),('TS1','TS1'),('TS2','TS2'),('TS3','TS3'),
        ('ING1','ING1'),('ING2','ING2'),('ING3','ING3'),('MASTER1','MASTER1'),('MASTER2','MASTER2')
    ]
    mat_etudiant = models.CharField(max_length=20, primary_key=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    nationalite = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    ecole = models.CharField(max_length=50)
    filiere = models.CharField(max_length=50)
    niveau_etudes = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    est_handicape = models.BooleanField(default=False)
    est_international = models.BooleanField(default=False)
    etat_etudiant = models.CharField(max_length=15, choices=ETAT_CHOICES, default='ACTIF')
    date_suspension = models.DateField(null=True, blank=True)
    date_deblocage = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.mat_etudiant} - {self.nom} {self.prenom}"

class Occupation(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='occupations')
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name='occupations')
    date_entree = models.DateField()
    date_sortie = models.DateField(null=True, blank=True)
    annee_academique = models.CharField(max_length=10)  # Ex: '2024-2025'
    cle_deposee = models.BooleanField(default=False)
    date_depot_cle = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.etudiant} in {self.chambre} ({self.annee_academique})"

class AnneeAcademique(models.Model):
    id_annee = models.CharField(max_length=10, primary_key=True)  # Ex: '2024-2025'
    libelle = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    date_limite_depot_cle = models.DateField()
    est_active = models.BooleanField(default=False)

    def __str__(self):
        return self.id_annee
