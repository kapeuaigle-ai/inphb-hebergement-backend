from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

router = DefaultRouter()
router.register(r'etudiants', EtudiantViewSet)
router.register(r'chambres', ChambreViewSet)
router.register(r'affectations', AffectationViewSet)
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'rapports', RapportViewSet, basename='rapports')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('cles/non-deposees/', ClesViewSet.as_view({'get': 'non_deposees'})),
    path('cles/suspensions/', ClesViewSet.as_view({'post': 'lancer_suspensions'})),
]
