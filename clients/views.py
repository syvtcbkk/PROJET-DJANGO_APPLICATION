from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.contrib import messages
from .models import Profile
from .decorators import comptable_required, client_required # Importe tes outils

@comptable_required # Seuls Bob et le Directeur peuvent voir tous les clients
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})

@client_required # Seuls les clients peuvent accéder à cette logique spécifique
def mon_espace_perso(request):
    profile = request.user.profile
    if profile.client:
        factures = profile.client.facture_set.all()
        return render(request, 'clients/mon_espace_perso.html', {
            'client': profile.client,
            'factures': factures
        })
    else:
        messages.error(request, "Votre compte n'est lié à aucun client.")
        return redirect('login')
@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})

@login_required
def client_detail(request, pk):
    client  = get_object_or_404(Client, pk=pk)
    factures = client.facture_set.all()
    return render(request, 'clients/client_detail.html', {'client': client, 'factures': factures})

@login_required
def client_create(request):
    if request.method == 'POST':
        Client.objects.create(
            nom=request.POST['nom'],
            email=request.POST['email'],
            telephone=request.POST.get('telephone', ''),
            adresse=request.POST.get('adresse', ''),
        )
        messages.success(request, 'Client créé avec succès.')
        return redirect('client_list')
    return render(request, 'clients/client_form.html', {'form': {}})

@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.nom       = request.POST['nom']
        client.email     = request.POST['email']
        client.telephone = request.POST.get('telephone', '')
        client.adresse   = request.POST.get('adresse', '')
        client.save()
        messages.success(request, "Client modifié avec succès")
        return redirect('client_list')
    return render(request, 'clients/client_form.html', {'form': client, 'client': client})

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client supprimé avec succès")
        return redirect('client_list')
    return render(request, 'confirm_delete.html', {'object': client, 'cancel_url': '/clients/'})


@login_required
def dashboard(request):
    profile = request.user.profile 
    
    if profile.role in ['admin']:
        return render(request, 'dashadmin.html')
    
    elif profile.role == 'comptable':
        return render(request, 'dashcomptable.html')
    
    # Si c'est un client (Yannick)
    else:
        if profile.client:
            # On récupère UNIQUEMENT les factures de CE client
            factures = profile.client.facture_set.all()
            return render(request, 'dashclient.html', {
                'client': profile.client,
                'factures': factures
            })
        else:
            messages.error(request, "Votre compte n'est lié à aucun client.")
            return redirect('login')
        
@login_required
def home_redirect(request):
    profile = request.user.profile
    
    if profile.role in ['admin']:
        return redirect('dashadmin')
    
    elif profile.role == 'comptable':
        return redirect('dashcomptable') # Redirige vers la vue comptable
    
    # Si c'est Yannick (Client)
    else:
        if profile.client:
            # On récupère ses factures via la relation ForeignKey
            factures = profile.client.facture_set.all()
            return render(request, 'dashclient.html', {
                'client': profile.client,
                'factures': factures
            })
        else:
            return render(request, 'clients/no_client_assigned.html')