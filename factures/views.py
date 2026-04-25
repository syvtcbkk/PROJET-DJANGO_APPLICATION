from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import Facture, LigneFacture
from clients.models import Client
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import EmailMessage
import io

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

def facture_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="facture_{pk}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Titre
    elements.append(Paragraph(f"FACTURE N° FAC-{pk:04d}", styles['Title']))
    elements.append(Spacer(1, 20))

    # Infos client
    elements.append(Paragraph(f"<b>Client :</b> {facture.client.nom}", styles['Normal']))
    elements.append(Paragraph(f"<b>Email :</b> {facture.client.email}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date :</b> {facture.date}", styles['Normal']))
    elements.append(Paragraph(f"<b>Statut :</b> {facture.get_statut_display()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Tableau des lignes
    data = [['Désignation', 'Quantité', 'Prix Unit.', 'Sous-total']]
    for ligne in facture.lignefacture_set.all():
        data.append([
            ligne.designation,
            str(ligne.quantite),
            f"{ligne.prix_unit} FCFA",
            f"{ligne.total} FCFA",
        ])

    # Totaux
    data.append(['', '', 'Montant HT', f"{facture.montant_ht} FCFA"])
    data.append(['', '', f"TVA ({facture.taux_tva}%)", f"{facture.montant_tva} FCFA"])
    data.append(['', '', 'TOTAL TTC', f"{facture.montant_total} FCFA"])

    table = Table(data, colWidths=[250, 70, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN',      (1,0), (-1,-1), 'CENTER'),
        ('GRID',       (0,0), (-1,-2), 0.5, colors.grey),
        ('FONTNAME',   (0,-3), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#27ae60')),
        ('TEXTCOLOR',  (0,-1), (-1,-1), colors.white),
    ]))
    elements.append(table)
    doc.build(elements)
    return response
   
def facture_email(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    
    # Générer le PDF en mémoire
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"FACTURE N° FAC-{pk:04d}", styles['Title']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Client :</b> {facture.client.nom}", styles['Normal']))
    elements.append(Paragraph(f"<b>Email :</b> {facture.client.email}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date :</b> {facture.date}", styles['Normal']))
    elements.append(Paragraph(f"<b>Statut :</b> {facture.get_statut_display()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [['Désignation', 'Quantité', 'Prix Unit.', 'Sous-total']]
    for ligne in facture.lignefacture_set.all():
        data.append([ligne.designation, str(ligne.quantite), f"{ligne.prix_unit} FCFA", f"{ligne.total} FCFA"])
    data.append(['', '', 'Montant HT', f"{facture.montant_ht} FCFA"])
    data.append(['', '', f"TVA ({facture.taux_tva}%)", f"{facture.montant_tva} FCFA"])
    data.append(['', '', 'TOTAL TTC', f"{facture.montant_total} FCFA"])

    table = Table(data, colWidths=[250, 70, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN',      (1,0), (-1,-1), 'CENTER'),
        ('GRID',       (0,0), (-1,-2), 0.5, colors.grey),
        ('FONTNAME',   (0,-3), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#27ae60')),
        ('TEXTCOLOR',  (0,-1), (-1,-1), colors.white),
    ]))
    elements.append(table)
    doc.build(elements)

    # Envoyer l'email avec PDF en pièce jointe
    pdf = buffer.getvalue()
    email = EmailMessage(
        subject=f"Facture N° FAC-{pk:04d}",
        body=f"Bonjour {facture.client.nom},\n\nVeuillez trouver ci-joint votre facture.\n\nCordialement.",
        to=[facture.client.email],
    )
    email.attach(f"facture_{pk}.pdf", pdf, 'application/pdf')
    email.send()

    from django.contrib import messages
    messages.success(request, f"Facture envoyée à {facture.client.email} ✅")
    return redirect('facture_detail', pk=pk)