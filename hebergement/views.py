from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .serializers import *
from .services import affectation_service, suspension_service, rapport_service
from .permissions import IsAdmin, IsGestionnaireDuBatiment

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            return Response({
                "user_id": request.user.id,
                "email": request.user.email,
                "username": request.user.username,
                "role": getattr(request.user, 'role', 'ADMIN' if request.user.is_superuser else 'GESTIONNAIRE'),
            })
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer
    lookup_field = 'mat_etudiant'

    def get_queryset(self):
        queryset = Etudiant.objects.all()
        sexe = self.request.query_params.get('sexe')
        niveau = self.request.query_params.get('niveau_etudes')
        etat = self.request.query_params.get('etat_etudiant')
        batiment = self.request.query_params.get('batiment')

        if sexe:
            queryset = queryset.filter(sexe=sexe)
        if niveau:
            queryset = queryset.filter(niveau_etudes=niveau)
        if etat:
            queryset = queryset.filter(etat_etudiant=etat)
        if batiment:
            # Filtrer les étudiants qui ont une occupation active dans ce bâtiment
            queryset = queryset.filter(occupations__chambre__palier__batiment_id=batiment, occupations__date_sortie__isnull=True)
            
        return queryset.distinct()

    @action(detail=True, methods=['post'])
    def suspendre(self, request, mat_etudiant=None):
        etudiant = self.get_object()
        etudiant.etat_etudiant = 'SUSPENDU'
        etudiant.save()
        return Response({'status': 'Étudiant suspendu'})

    @action(detail=True, methods=['post'])
    def debloquer(self, request, mat_etudiant=None):
        etudiant = self.get_object()
        suspension_service.debloquer_etudiant(etudiant)
        return Response({'status': 'Étudiant débloqué avec succès'})

class ChambreViewSet(viewsets.ModelViewSet):
    queryset = Chambre.objects.all()
    serializer_class = ChambreSerializer

    @action(detail=False, methods=['get'], url_path='batiment/(?P<bat_id>[^/.]+)')
    def par_batiment(self, request, bat_id=None):
        chambres = Chambre.objects.filter(palier__batiment_id=bat_id)
        serializer = self.get_serializer(chambres, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='palier/(?P<pal_id>[^/.]+)')
    def par_palier(self, request, pal_id=None):
        chambres = Chambre.objects.filter(palier_id=pal_id)
        serializer = self.get_serializer(chambres, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def etat(self, request, pk=None):
        chambre = self.get_object()
        chambre.etat_service = request.data.get('etat_service', chambre.etat_service)
        chambre.save()
        return Response({'status': 'État mis à jour'})

    @action(detail=False, methods=['get'], url_path='disponibles/(?P<mat_etudiant>[^/.]+)')
    def disponibles(self, request, mat_etudiant=None):
        try:
            etudiant = Etudiant.objects.get(mat_etudiant=mat_etudiant)
            chambres = affectation_service.get_chambres_compatibles(etudiant)
            serializer = self.get_serializer(chambres, many=True)
            return Response(serializer.data)
        except Etudiant.DoesNotExist:
            return Response({'error': 'Étudiant non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class AffectationViewSet(viewsets.ModelViewSet):
    queryset = Occupation.objects.all()
    serializer_class = OccupationSerializer

    def create(self, request, *args, **kwargs):
        etudiant = Etudiant.objects.get(mat_etudiant=request.data['etudiant'])
        chambre = Chambre.objects.get(id_chambre=request.data['chambre'])
        
        valide, message = affectation_service.valider_affectation(etudiant, chambre)
        if not valide:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def auto(self, request):
        annee = request.data.get('annee_academique')
        resultats = affectation_service.attribution_automatique(annee)
        return Response(resultats)

class ClesViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='non-deposees')
    def non_deposees(self, request):
        occupations = Occupation.objects.filter(cle_deposee=False, date_sortie__isnull=True)
        serializer = OccupationSerializer(occupations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='suspensions')
    def lancer_suspensions(self, request):
        annee_id = request.data.get('annee_academique')
        annee = AnneeAcademique.objects.get(id_annee=annee_id)
        count = suspension_service.declencher_suspensions(annee)
        return Response({'suspensions_declenchees': count})

class RapportViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        stats = rapport_service.get_dashboard_stats()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def occupation(self, request):
        stats = rapport_service.get_occupation_par_batiment()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def repartition(self, request):
        stats = rapport_service.get_repartition_par_niveau()
        return Response(stats)

