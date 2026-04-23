# FacturePro — Application de facturation Django

Projet 6 : Application complète de facturation en ligne.

## Installation

```bash
# 1. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 2. Installer les dépendances
pip install django

# 3. Appliquer les migrations
python manage.py migrate

# 4. Créer un superutilisateur (admin)
python manage.py createsuperuser

# 5. Lancer le serveur
python manage.py runserver
```

Accéder à l'application : http://127.0.0.1:8000/
Interface admin : http://127.0.0.1:8000/admin/

## Structure du projet

```
facturation/
├── config/              # Configuration Django
│   ├── settings.py
│   └── urls.py
├── factures/            # Application principale
│   ├── models.py        # Client, Facture, LigneFacture, Paiement
│   ├── views.py         # Toutes les vues (CRUD + API JSON)
│   ├── forms.py         # Formulaires Django
│   ├── urls.py          # Routes URL
│   ├── admin.py         # Interface d'administration
│   └── templates/
│       └── factures/    # Templates HTML
└── manage.py
```

## Fonctionnalités

- **CRUD Clients** : création, consultation, modification, suppression
- **CRUD Factures** : avec numérotation automatique (FAC-2024-XXXX)
- **Lignes de facturation dynamiques** : ajout/suppression en JS
- **Calcul automatique** : totaux HT, TVA, TTC en temps réel
- **Suivi des statuts** : brouillon → envoyée → payée / annulée
- **Paiements** : enregistrement multiple, solde restant calculé
- **Recherche & filtres** : par client, statut, plage de dates
- **Dashboard** : KPIs, factures récentes, répartition des statuts
- **Admin Django** : interface complète pour tous les modèles

## Modèles de données

| Modèle | Champs |
|--------|--------|
| Client | id, nom, email, telephone, adresse |
| Facture | id, client_id, numero, date, statut, taux_tva, montant_ht, montant_tva, montant_total |
| LigneFacture | id, facture_id, designation, quantite, prix_unit |
| Paiement | id, facture_id, montant, date, mode, reference |
