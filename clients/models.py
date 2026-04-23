from django import forms
from django.db import models


class Client(models.Model):
    nom       = models.CharField(max_length=200)
    email     = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse   = models.TextField(blank=True)

    def __str__(self):
        return self.nom

class ClientForm(forms.ModelForm): 
    class Meta:
        model = Client
        fields = '__all__' 