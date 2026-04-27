from django.contrib import admin
from django.utils.html import format_html
from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('get_facture', 'montant_formatted', 'date', 'mode_badge', 'get_client')
    list_filter = ('mode', 'date', 'facture__statut')
    search_fields = ('facture__id', 'facture__client__nom')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)

    def get_facture(self, obj):
        return f'FAC-{obj.facture.pk:04d}'
    get_facture.short_description = 'Facture'

    def montant_formatted(self, obj):
        return f'{obj.montant:,.0f} €'
    montant_formatted.short_description = 'Montant'

    def mode_badge(self, obj):
        return format_html(
            '<span style="background-color:#17a2b8; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            obj.get_mode_display()
        )
    mode_badge.short_description = 'Mode'

    def get_client(self, obj):
        return obj.facture.client.nom
    get_client.short_description = 'Client'