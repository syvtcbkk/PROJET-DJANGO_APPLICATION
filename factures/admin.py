from django.contrib import admin
from django.utils.html import format_html
from .models import Facture, LigneFacture


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1
    readonly_fields = ('total',)
    fields = ('designation', 'quantite', 'prix_unit', 'total')


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('get_numero', 'client', 'date', 'statut_badge', 'montant_ht', 'montant_total', 'solde_paye')
    list_filter = ('statut', 'date', 'client__nom')
    search_fields = ('client__nom', 'id')
    readonly_fields = ('created_at', 'updated_at', 'montant_tva', 'montant_total')
    date_hierarchy = 'date'
    ordering = ('-date',)
    inlines = [LigneFactureInline]

    fieldsets = (
        ('Informations facture', {
            'fields': ('client', 'date', 'statut')
        }),
        ('Montants', {
            'fields': ('montant_ht', 'taux_tva', 'montant_tva', 'montant_total')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_numero(self, obj):
        return f'FAC-{obj.pk:04d}'
    get_numero.short_description = 'N° Facture'

    def statut_badge(self, obj):
        colors = {
            'brouillon': '#6c757d',
            'envoyee': '#0d6efd',
            'payee': '#198754',
        }
        color = colors.get(obj.statut, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            color, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'

    def montant_ht(self, obj):
        return f'{obj.montant_ht:,.0f} €'
    montant_ht.short_description = 'HT'

    def montant_total(self, obj):
        return f'{obj.montant_total:,.0f} €'
    montant_total.short_description = 'TTC'

    def solde_paye(self, obj):
        total_paye = sum(p.montant for p in obj.paiement_set.all())
        return f'{total_paye:,.0f} €'
    solde_paye.short_description = 'Payé'