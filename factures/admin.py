from django.contrib import admin
from .models import Facture, LigneFacture

class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display  = ('id', 'client', 'date', 'statut', 'montant_total')
    list_filter   = ('statut', 'date')
    search_fields = ('client__nom',)
    inlines       = [LigneFactureInline]