from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    nom        = models.CharField(max_length=200)
    email      = models.EmailField(unique=True)
    telephone  = models.CharField(max_length=20, blank=True)
    adresse    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ('-created_at',)


class Profile(models.Model):
    ROLE_CHOICES = [
        ('comptable',  'Comptable'),
        ('commercial', 'Commercial'),
        ('client',     'Client'),
    ]
    user   = models.OneToOneField(User, on_delete=models.CASCADE)
    role   = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"