from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import Facture, LigneFacture
from clients.models import Client

@login_required
def facture_list(request):
    factures = Facture.objects.select_related('client').all()
    if request.GET.get('statut'):
        factures = factures.filter(statut=request.GET['statut'])
    if request.GET.get('date_debut'):
        factures = factures.filter(date__gte=request.GET['date_debut'])
    if request.GET.get('date_fin'):
        factures = factures.filter(date__lte=request.GET['date_fin'])
    return render(request, 'factures/facture_list.html', {'factures': factures})

@login_required
def facture_detail(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'factures/facture_detail.html', {'facture': facture})

@login_required
def facture_create(request):
    clients = Client.objects.all()
    if request.method == 'POST':
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')
        
        montant_ht = sum(
            Decimal(q or 0) * Decimal(p or 0) 
            for q, p in zip(quantites, prix_units) if q and p
        )
        taux_tva    = Decimal(request.POST.get('taux_tva', 18) or 18)
        montant_tva = montant_ht * (taux_tva / 100)
        montant_total = montant_ht + montant_tva

        facture = Facture.objects.create(
            client_id=request.POST['client_id'],
            date=request.POST['date'],
            statut=request.POST['statut'],
            montant_ht=montant_ht,
            taux_tva=taux_tva,
            montant_tva=montant_tva,
            montant_total=montant_total
        )
        for d, q, p in zip(designations, quantites, prix_units):
            if d.strip():
                LigneFacture.objects.create(
                    facture=facture,
                    designation=d,
                    quantite=Decimal(q or 0),
                    prix_unit=Decimal(p or 0)
                )
        return redirect('facture_detail', pk=facture.pk)

    return render(request, 'factures/facture_form.html', {
        'clients': clients,
        'lignes': [],
        'today': timezone.now().date(),
    })

@login_required
def facture_edit(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    clients = Client.objects.all()
    
    if request.method == 'POST':
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')

        montant_ht  = sum(
            Decimal(q or 0) * Decimal(p or 0) 
            for q, p in zip(quantites, prix_units) if q and p
        )
        taux_tva = Decimal(request.POST.get('taux_tva', 18) or 18)
        
        facture.client_id   = request.POST['client_id']
        facture.date        = request.POST['date']
        facture.statut      = request.POST['statut']
        facture.montant_ht  = montant_ht
        facture.taux_tva    = taux_tva
        facture.montant_tva = montant_ht * (taux_tva / 100)
        facture.montant_total = montant_ht + facture.montant_tva
        facture.save()

        facture.lignefacture_set.all().delete()
        for d, q, p in zip(designations, quantites, prix_units):
            if d.strip():
                LigneFacture.objects.create(
                    facture=facture,
                    designation=d,
                    quantite=Decimal(q or 0),
                    prix_unit=Decimal(p or 0)
                )
        return redirect('facture_detail', pk=facture.pk)

    return render(request, 'factures/facture_form.html', {
        'facture': facture,
        'clients': clients,
        'lignes': facture.lignefacture_set.all(),
        'today': timezone.now().date(),
    })

@login_required
def facture_send(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    facture.statut = 'envoyee'
    facture.save()
    return redirect('facture_detail', pk=pk)

@login_required
def facture_delete(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        facture.delete()
        return redirect('facture_list')
    return render(request, 'confirm_delete.html', {'object': facture, 'cancel_url': '/factures/'})

@login_required
def facture_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'factures/facture_pdf.html', {'facture': facture})