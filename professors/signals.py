# apps/signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Yangi User yaratilganda, unga bog'liq UserProfile yaratish.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    User ma'lumotlari saqlanganda, profile ham saqlanishini ta'minlash.
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Agar qandaydir sabab bilan profile mavjud bo'lmasa, uni yaratish
        UserProfile.objects.create(user=instance)