from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django import forms
from decimal import Decimal
from .models import Facture, LigneFacture
from clients.models import Client

def facture_list(request):
    factures = Facture.objects.select_related('client').all()
    if request.GET.get('statut'):
        factures = factures.filter(statut=request.GET['statut'])
    if request.GET.get('date_debut'):
        factures = factures.filter(date__gte=request.GET['date_debut'])
    if request.GET.get('date_fin'):
        factures = factures.filter(date__lte=request.GET['date_fin'])
    return render(request, 'factures/facture_list.html', {'factures': factures})

def facture_detail(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'factures/facture_detail.html', {'facture': facture})

def facture_create(request):
    clients = Client.objects.all()
    if request.method == 'POST':
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')
        
        # Calculer le montant HT à partir des lignes
        montant_ht = sum(Decimal(q) * Decimal(p) for q, p in zip(quantites, prix_units) if q.strip() and p.strip())
        taux_tva = Decimal(request.POST.get('taux_tva', 18))
        
        facture = Facture.objects.create(
            client_id   = request.POST['client_id'],
            date        = request.POST['date'],
            statut      = request.POST['statut'],
            montant_ht  = montant_ht,
            taux_tva    = taux_tva,
        )
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')
        for d, q, p in zip(designations, quantites, prix_units):
            if d.strip():
                LigneFacture.objects.create(
                    facture=facture, designation=d, 
                    quantite=Decimal(q), prix_unit=Decimal(p)
                )
        return redirect('facture_detail', pk=facture.pk)
    return render(request, 'factures/facture_form.html', {
        'clients': clients,
        'lignes': [],
        'today': timezone.now().date(),
    })

def facture_edit(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    clients = Client.objects.all()
    if request.method == 'POST':
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')
        
        # Calculer le montant HT à partir des lignes
        montant_ht = sum(Decimal(q) * Decimal(p) for q, p in zip(quantites, prix_units) if q.strip() and p.strip())
        taux_tva = Decimal(request.POST.get('taux_tva', 18))
        
        facture.client_id    = request.POST['client_id']
        facture.date         = request.POST['date']
        facture.statut       = request.POST['statut']
        facture.montant_ht   = montant_ht
        facture.taux_tva     = taux_tva
        facture.save()
        facture.lignefacture_set.all().delete()
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')
        for d, q, p in zip(designations, quantites, prix_units):
            if d.strip():
                LigneFacture.objects.create(
                    facture=facture, designation=d, 
                    quantite=Decimal(q), prix_unit=Decimal(p)
                )
        return redirect('facture_detail', pk=facture.pk)
    return render(request, 'factures/facture_form.html', {
        'facture': facture,
        'clients': clients,
        'lignes': facture.lignefacture_set.all(),
        'today': timezone.now().date(),
    })

def facture_send(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    facture.statut = 'envoyee'
    facture.save()
    return redirect('facture_detail', pk=pk)

def facture_delete(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        facture.delete()
        return redirect('facture_list')
    return render(request, 'confirm_delete.html', {'object': facture, 'cancel_url': '/factures/'})

def facture_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'factures/facture_pdf.html', {'facture': facture})