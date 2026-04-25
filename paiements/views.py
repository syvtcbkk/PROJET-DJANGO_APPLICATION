from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Paiement
from factures.models import Facture

@login_required
def paiement_list(request):
    paiements = Paiement.objects.select_related('facture__client').all()
    total = sum(p.montant for p in paiements)
    aujourd_hui = timezone.now().date()
    paiements_mois = sum(
        p.montant for p in paiements
        if p.date.month == aujourd_hui.month and p.date.year == aujourd_hui.year
    )
    return render(request, 'paiements/paiement_list.html', {
        'paiements': paiements,
        'total_paiements': total,
        'paiements_mois': paiements_mois,
    })

@login_required
def paiement_create(request):
    factures = Facture.objects.exclude(statut='payee').select_related('client')
    if request.method == 'POST':
        facture = get_object_or_404(Facture, pk=request.POST['facture_id'])
        Paiement.objects.create(
            facture=facture,
            montant=request.POST['montant'],
            date=request.POST['date'],
            mode=request.POST['mode'],
        )
        if facture.solde_restant <= 0:
            facture.statut = 'payee'
            facture.save()
        return redirect('paiement_list')
    return render(request, 'paiements/paiement_form.html', {
        'factures': factures,
        'today': timezone.now().date(),
    })

@login_required
def paiement_delete(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    if request.method == 'POST':
        paiement.delete()
        return redirect('paiement_list')
    return render(request, 'confirm_delete.html', {'object': paiement, 'cancel_url': '/paiements/'})