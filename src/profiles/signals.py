from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create or update a UserProfile for every new User.
    Avoid duplicate profile creation (important for django-allauth).
    """
    if created:
        # Only create if not exists
        UserProfile.objects.get_or_create(user=instance)
    else:
        # On update, ensure profile exists and is synced
        UserProfile.objects.get_or_create(user=instance)
        instance.userprofile.save()
