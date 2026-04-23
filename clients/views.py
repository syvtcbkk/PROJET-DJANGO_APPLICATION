from django.shortcuts import render, get_object_or_404, redirect
from .models import Client

def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    factures = client.facture_set.all()
    return render(request, 'clients/client_detail.html', {'client': client, 'factures': factures})

def client_create(request):
    if request.method == 'POST':
        Client.objects.create(
            nom=request.POST['nom'],
            email=request.POST['email'],
            telephone=request.POST.get('telephone', ''),
            adresse=request.POST.get('adresse', ''),
        )
        return redirect('client_list')
    return render(request, 'clients/client_form.html', {'form': {}})

def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.nom       = request.POST['nom']
        client.email     = request.POST['email']
        client.telephone = request.POST.get('telephone', '')
        client.adresse   = request.POST.get('adresse', '')
        client.save()
        return redirect('client_list')
    return render(request, 'clients/client_form.html', {'form': client, 'client': client})

def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render(request, 'confirm_delete.html', {'object': client, 'cancel_url': '/clients/'})