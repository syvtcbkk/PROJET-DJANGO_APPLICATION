from django.contrib import admin
from django.urls import path, include
from clients.views import client_list
from django.shortcuts import render
from clients.models import Client
from factures.models import Facture
from paiements.models import Paiement
from django.utils import timezone

def dashboard(request):
    factures = Facture.objects.select_related('client').all()
    paiements = Paiement.objects.all()
    return render(request, 'dashboard.html', {
        'total_facture':      sum(f.montant_total for f in factures),
        'total_paye':         sum(p.montant for p in paiements),
        'total_impaye':       sum(f.solde_restant for f in factures),
        'nb_clients':         Client.objects.count(),
        'dernieres_factures': factures.order_by('-date')[:5],
        'derniers_paiements': paiements.order_by('-date')[:5],
    })

urlpatterns = [
    path('admin/',     admin.site.urls),
    path('',           dashboard,              name='dashboard'),
    path('clients/',   include('clients.urls')),
    path('factures/',  include('factures.urls')),
    path('paiements/', include('paiements.urls')),
]