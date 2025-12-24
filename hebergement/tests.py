from django.test import TestCase
from .models import Batiment, Palier, Chambre, Etudiant, Occupation
from .services import affectation_service

class AffectationServiceTest(TestCase):
    def setUp(self):
        # Création d'un bâtiment
        self.batiment = Batiment.objects.create(
            id_batiment='A',
            nom_batiment='Bâtiment A',
            type_public='GARCONS',
            niveaux_etudes='TOUS',
            type_chambre='SIMPLE',
            nombre_niveaux=3,
            nombre_chambres=96,
            capacite=96
        )
        # Création d'un palier
        self.palier = Palier.objects.create(
            id_palier='A-R0',
            niveau_palier=0,
            nbre_chambres=32,
            batiment=self.batiment
        )
        # Création d'une chambre
        self.chambre = Chambre.objects.create(
            id_chambre='A-01',
            numero_chambre=1,
            type_chambre='SIMPLE',
            etat_chambre='BONNE',
            etat_service='EN_SERVICE',
            is_available=True,
            capacite=1,
            palier=self.palier
        )
        # Création d'un étudiant
        self.etudiant = Etudiant.objects.create(
            mat_etudiant='24INP00001',
            nom='Koffi',
            prenom='Jean',
            sexe='M',
            nationalite='Ivoirienne',
            telephone='07070707',
            email='jean.koffi@inphb.ci',
            ecole='ESIE',
            filiere='Informatique',
            niveau_etudes='ING1',
            est_handicape=False,
            etat_etudiant='ACTIF'
        )

    def test_validation_nominale(self):
        """Test une affectation valide simple."""
        valide, message = affectation_service.valider_affectation(self.etudiant, self.chambre)
        self.assertTrue(valide)
        self.assertEqual(message, "Validé")

    def test_validation_sexe_invalide(self):
        """Test l'affectation d'une fille dans un bâtiment garçons."""
        fille = Etudiant.objects.create(
            mat_etudiant='24INP00002',
            nom='Bamba',
            prenom='Awa',
            sexe='F',
            nationalite='Ivoirienne',
            email='awa.bamba@inphb.ci',
            niveau_etudes='ING1',
            etat_etudiant='ACTIF'
        )
        valide, message = affectation_service.valider_affectation(fille, self.chambre)
        self.assertFalse(valide)
        self.assertIn("réservé aux GARCONS", message)

    def test_validation_handicap_etage(self):
        """Test qu'un handicapé ne peut pas être à l'étage."""
        palier_r1 = Palier.objects.create(
            id_palier='A-R1',
            niveau_palier=1,
            batiment=self.batiment
        )
        chambre_r1 = Chambre.objects.create(
            id_chambre='A-33',
            numero_chambre=33,
            type_chambre='SIMPLE',
            etat_service='EN_SERVICE',
            capacite=1,
            palier=palier_r1
        )
        self.etudiant.est_handicape = True
        self.etudiant.save()
        
        valide, message = affectation_service.valider_affectation(self.etudiant, chambre_r1)
        self.assertFalse(valide)
        self.assertIn("handicapés doivent être au RDC", message)
