from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    Décorateur pour restreindre l'accès selon le rôle.
    
    Usage:
        @role_required('admin', 'comptable')
        def ma_vue(request):
            ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Vérifier si l'utilisateur a un profil
            try:
                profile = request.user.profile
                user_role = profile.role
            except:
                # Par défaut: staff = admin, sinon = client
                user_role = 'admin' if request.user.is_staff else 'client'
            
            if user_role not in allowed_roles:
                raise PermissionDenied("Vous n'avez pas l'autorisation d'accéder à cette page.")
            
            return view_func(request, *args, **kwargs)
        
        return login_required(wrapper)
    return decorator


# Décorateurs pratiques
admin_required = role_required('admin')
comptable_required = role_required('admin', 'comptable')
commercial_required = role_required('admin', 'comptable', 'commercial')
client_required = role_required('client')