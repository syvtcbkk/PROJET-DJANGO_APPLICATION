from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un Profile lors de la création d'un utilisateur.
    """
    if created:
        default_role = 'admin' if instance.is_staff else 'client'
        Profile.objects.create(user=instance, role=default_role)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarde le Profile existant lors de la mise à jour de l'utilisateur.
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        default_role = 'admin' if instance.is_staff else 'client'
        Profile.objects.create(user=instance, role=default_role)