from django.db import models
from django.utils import timezone
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
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"FAC-{self.pk:04d} - {self.client.nom}"

    def save(self, *args, **kwargs):
        # On s'assure que montant_ht et taux_tva ne sont pas None
        ht = self.montant_ht or 0
        taux = self.taux_tva or 0
        
        self.montant_tva = ht * taux / 100
        self.montant_total = ht + self.montant_tva
        super().save(*args, **kwargs)

    @property
    def solde_restant(self):
        total_paye = sum(p.montant for p in self.paiement_set.all())
        return self.montant_total - total_paye

    class Meta:
        ordering = ('-date',)


class LigneFacture(models.Model):
    facture     = models.ForeignKey(Facture, on_delete=models.CASCADE)
    designation = models.CharField(max_length=300)
    # Ajout de default=0 pour éviter les valeurs None
    quantite    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prix_unit   = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def total(self):
        # Sécurité : si l'un des deux est None, on retourne 0
        if self.quantite is None or self.prix_unit is None:
            return 0
        return self.quantite * self.prix_unit