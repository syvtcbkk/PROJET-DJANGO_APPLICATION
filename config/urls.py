from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from clients.models import Client
from factures.models import Facture
from paiements.models import Paiement
from config.forms import PasswordResetForm
from clients.models import Profile 

class EmailPasswordResetView(PasswordResetView):
    """Vue de réinitialisation de mot de passe par email"""
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Trouver l'utilisateur par email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Pour des raisons de sécurité, ne pas révéler si l'email existe
            # Toujours afficher la page de succès
            return super().form_valid(form)
        
        # Générer le token manuellement
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Construire le lien
        domain = self.request.get_host()
        protocol = 'https' if self.request.is_secure() else 'http'
        reset_link = f"{protocol}://{domain}/reset/{uid}/{token}/"
        
        # Envoyer l'email
        subject = 'Réinitialisation de votre mot de passe'
        message = render_to_string('registration/password_reset_email.html', {
            'domain': domain,
            'uid': uid,
            'token': token,
            'protocol': protocol,
            'user': user,
        })
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")
        
        # Toujours rediriger vers la page de succès
        return super().form_valid(form)

@login_required
def dashboard(request):
    factures  = Facture.objects.select_related('client').all()
    paiements = Paiement.objects.all()
    
    total_facture = sum(f.montant_total for f in factures)
    total_paye = sum(p.montant for p in paiements)
    total_impaye = sum(f.solde_restant for f in factures)
    
    # Calcul du taux de paiement
    taux_paiement = 0
    if total_facture > 0:
        taux_paiement = (total_paye / total_facture) * 100
    
    return render(request, 'dashboard.html', {
        'total_facture':      total_facture,
        'total_paye':         total_paye,
        'total_impaye':       total_impaye,
        'taux_paiement':      taux_paiement,
        'nb_clients':         Client.objects.count(),
        'dernieres_factures': factures.order_by('-date')[:5],
        'derniers_paiements': paiements.order_by('-date')[:5],
    })

urlpatterns = [
    path('admin/',     admin.site.urls),
    path('login/',     auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view( next_page='/login/'), name='logout'),
    path('password_reset/', EmailPasswordResetView.as_view(template_name='registration/password_reset_form.html',success_url='/password_reset/done/'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),  name='password_reset_done'),
    path('reset/<uidb64>/<token>/',  auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', success_url='/reset/done/'),  name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html' ),  name='password_reset_complete'),
    path('',           dashboard,                       name='dashboard'),
    path('admin-dashboard/', dashboard, name='admin_dashboard'),
    path('clients/',   include('clients.urls')),
    path('factures/',  include('factures.urls')),
    path('paiements/', include('paiements.urls')),
]

@login_required
def dashboard(request):
    try:
        profile = request.user.profile
        role = profile.role
    except:
        role = 'comptable' if request.user.is_staff else 'client'

    factures  = Facture.objects.select_related('client').all()
    paiements = Paiement.objects.all()

    if role == 'client':
        # Le client voit seulement ses propres factures
        try:
            client = request.user.profile.client
            mes_factures = Facture.objects.filter(client=client)
        except:
            mes_factures = Facture.objects.none()
        return render(request, 'dashboard_client.html', {
            'factures':      mes_factures,
            'nb_factures':   mes_factures.count(),
            'total_paye':    sum(p.montant for f in mes_factures for p in f.paiements.all()),
            'total_impaye':  sum(f.solde_restant for f in mes_factures),
        })

    elif role == 'commercial':
        return render(request, 'dashboard_commercial.html', {
            'nb_clients':        Client.objects.count(),
            'nb_factures':       factures.count(),
            'nb_brouillon':      factures.filter(statut='brouillon').count(),
            'nb_envoyee':        factures.filter(statut='envoyee').count(),
            'dernieres_factures': factures.order_by('-date')[:5],
        })

    else:  # comptable ou staff
        return render(request, 'dashboard_comptable.html', {
            'total_facture':      sum(f.montant_total for f in factures),
            'total_paye':         sum(p.montant for p in paiements),
            'total_impaye':       sum(f.solde_restant for f in factures),
            'nb_clients':         Client.objects.count(),
            'dernieres_factures': factures.order_by('-date')[:5],
            'derniers_paiements': paiements.order_by('-date')[:5],
            'nb_brouillon':       factures.filter(statut='brouillon').count(),
            'nb_envoyee':         factures.filter(statut='envoyee').count(),
            'nb_payee':           factures.filter(statut='payee').count(),
        })