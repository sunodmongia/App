from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import os


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_constraint=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# Create or update profile when a User is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Only update the profile, no weird save loops
        instance.userprofile.save()


# Delete profile image when profile is deleted (BUT DO NOT delete the user)
@receiver(pre_delete, sender=UserProfile)
def delete_profile_image(sender, instance, **kwargs):
    if instance.profile_image and instance.profile_image.path:
        if os.path.isfile(instance.profile_image.path):
            os.remove(instance.profile_image.path)
