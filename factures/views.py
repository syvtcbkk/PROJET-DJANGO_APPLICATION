from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
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
        facture = Facture.objects.create(
            client_id     = request.POST['client_id'],
            date          = request.POST['date'],
            statut        = request.POST['statut'],
            montant_ht    = request.POST.get('montant_ht', 0) or 0,
            taux_tva      = request.POST.get('taux_tva', 18) or 18,
            montant_tva   = request.POST.get('montant_tva', 0) or 0,
            montant_total = request.POST.get('montant_total', 0) or 0,
        )
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')
        for d, q, p in zip(designations, quantites, prix_units):
            if d.strip():
                LigneFacture.objects.create(
                    facture=facture,
                    designation=d,
                    quantite=q or 0,
                    prix_unit=p or 0,
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
        facture.client_id     = request.POST['client_id']
        facture.date          = request.POST['date']
        facture.statut        = request.POST['statut']
        facture.montant_ht    = request.POST.get('montant_ht', 0) or 0
        facture.taux_tva      = request.POST.get('taux_tva', 18) or 18
        facture.montant_tva   = request.POST.get('montant_tva', 0) or 0
        facture.montant_total = request.POST.get('montant_total', 0) or 0
        facture.save()
        facture.lignefacture_set.all().delete()
        designations = request.POST.getlist('designation[]')
        quantites    = request.POST.getlist('quantite[]')
        prix_units   = request.POST.getlist('prix_unit[]')
        for d, q, p in zip(designations, quantites, prix_units):
            if d.strip():
                LigneFacture.objects.create(
                    facture=facture,
                    designation=d,
                    quantite=q or 0,
                    prix_unit=p or 0,
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