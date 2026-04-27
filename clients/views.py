from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.contrib import messages
from .forms import RegistrationForm
from .models import Profile

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
        messages.success(request, "Client modifié avec succès ✅")
        return redirect('client_list')
    return render(request, 'clients/client_form.html', {'form': client, 'client': client})

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client supprimé avec succès ✅")
        return redirect('client_list')
    return render(request, 'confirm_delete.html', {'object': client, 'cancel_url': '/clients/'})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Créer le profil associé avec le rôle client par défaut
            Profile.objects.create(user=user, role='client')
            
            messages.success(request, f"Compte créé pour {user.username} ! Vous pouvez vous connecter.")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})