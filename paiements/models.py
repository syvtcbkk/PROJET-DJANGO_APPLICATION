from django.db import models
from factures.models import Facture

class Paiement(models.Model):
    MODES = [
        ('especes',  'Espèces'),
        ('virement', 'Virement'),
        ('cheque',   'Chèque'),
        ('mobile',   'Mobile Money'),
        ('carte',    'Carte bancaire'),
    ]
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date    = models.DateField()
    mode    = models.CharField(max_length=20, choices=MODES)

    def __str__(self):
        return f"Paiement {self.montant} - FAC-{self.facture.pk:04d}"