from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # En supposant que le rôle est injecté dans request.user par le middleware JWT 
        # ou que request.user est un Gestionnaire
        user = request.user
        if hasattr(user, 'role'):
            return user.role == 'ADMIN'
        return False

class IsGestionnaireDuBatiment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not hasattr(user, 'role'):
            return False
            
        if user.role == 'ADMIN':
            return True
            
        # Logique pour déterminer le bâtiment lié à l'objet (Chambre, Etudiant, etc.)
        from .models import Chambre, Etudiant, Batiment, Occupation
        
        batiment_id = None
        if isinstance(obj, Batiment):
            batiment_id = obj.id_batiment
        elif isinstance(obj, Chambre):
            batiment_id = obj.palier.batiment.id_batiment
        elif isinstance(obj, Etudiant):
            # Un étudiant est lié à un bâtiment via son occupation actuelle
            occ = Occupation.objects.filter(etudiant=obj, date_sortie__isnull=True).first()
            if occ:
                batiment_id = occ.chambre.palier.batiment.id_batiment
        
        # Supposons que user.batiments est une liste d'IDs (via custom token claims)
        # Pour cette implémentation simple, on vérifie si le gestionnaire est assigné au bâtiment
        if batiment_id:
            return Batiment.objects.filter(id_batiment=batiment_id, gestionnaire__email=user.email).exists()
            
        return False
