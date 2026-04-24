from django.db import models
from clients.models import Client

class Facture(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('envoyee',   'Envoyée'),
        ('payee',     'Payée'),
    ]
    client        = models.ForeignKey(Client, on_delete=models.CASCADE)
    date          = models.DateField()
    statut        = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    montant_ht    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taux_tva      = models.DecimalField(max_digits=5,  decimal_places=2, default=18)
    montant_tva   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"FAC-{self.pk:04d} - {self.client.nom}"

    def save(self, *args, **kwargs):
        # Calculer le montant TVA et total
        self.montant_tva = self.montant_ht * self.taux_tva / 100
        self.montant_total = self.montant_ht + self.montant_tva
        super().save(*args, **kwargs)


class LigneFacture(models.Model):
    facture     = models.ForeignKey(Facture, on_delete=models.CASCADE)
    designation = models.CharField(max_length=300)
    quantite    = models.DecimalField(max_digits=10, decimal_places=2)
    prix_unit   = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def calcul_total(self):
        total = sum(l.quantite*l.prix_unit for l in self.facture.lignefacture_set.all())
        return total

    @property
    def solde_restant(self):
        paye = sum(p.montant for p in self.paiement_set.all())
        return self.montant_total - paye