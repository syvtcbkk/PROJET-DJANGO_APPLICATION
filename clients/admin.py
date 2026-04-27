from django.contrib import admin
from django.utils.html import format_html
from .models import Client
from .models import Client, Profile

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'facture_count', 'total_ca', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nom', 'email', 'telephone')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'email', 'telephone')
        }),
        ('Adresse', {
            'fields': ('adresse',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def facture_count(self, obj):
        count = obj.facture_set.count()
        return format_html('<strong>{}</strong>', count)
    facture_count.short_description = 'Factures'

    def total_ca(self, obj):
        total = sum(f.montant_total for f in obj.facture_set.all())
        return f'{total:,.0f} €'
    total_ca.short_description = 'CA Total'

    @admin.register(Profile)
    class ProfileAdmin(admin.ModelAdmin):
     list_display = ('user', 'role', 'client')