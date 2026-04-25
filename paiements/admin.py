from django.contrib import admin
from .models import Paiement

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('facture', 'montant', 'date', 'mode')
    list_filter  = ('mode', 'date')