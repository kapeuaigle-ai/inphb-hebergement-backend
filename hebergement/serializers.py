from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Gestionnaire, Batiment, Palier, Chambre, Etudiant, Occupation, AnneeAcademique

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = getattr(user, 'role', 'ADMIN' if user.is_superuser else 'GESTIONNAIRE')
        token['nom'] = f"{user.last_name} {user.first_name}" if user.last_name else user.username
        # Add batiments if relevant
        return token

class GestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gestionnaire
        fields = '__all__'
        extra_kwargs = {'mot_de_passe': {'write_only': True}}

class BatimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batiment
        fields = '__all__'

class PalierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Palier
        fields = '__all__'

class ChambreSerializer(serializers.ModelSerializer):
    occupants = serializers.SerializerMethodField()
    
    class Meta:
        model = Chambre
        fields = '__all__'

    def get_occupants(self, obj):
        # Récupérer les occupations actives (sans date de sortie)
        active_occupations = obj.occupations.filter(date_sortie__isnull=True)
        return [{"nom": f"{occ.etudiant.nom} {occ.etudiant.prenom}", "mat_etudiant": occ.etudiant.mat_etudiant} for occ in active_occupations]

class EtudiantSerializer(serializers.ModelSerializer):
    chambre = serializers.SerializerMethodField()

    class Meta:
        model = Etudiant
        fields = '__all__'

    def get_chambre(self, obj):
        # Récupérer l'occupation active (sans date de sortie)
        occupation = obj.occupations.filter(date_sortie__isnull=True).first()
        return occupation.chambre.id_chambre if occupation else None

class OccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = '__all__'

class AnneeAcademiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnneeAcademique
        fields = '__all__'
