from django.db import models
from django.conf import settings
import helper.billing

from allauth.account.signals import (
    user_signed_up as allauth_user_signed_up,
    email_confirmed as allauth_email_confirmation,
)


User = settings.AUTH_USER_MODEL


class Customers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    init_email = models.EmailField(blank=True, null=True)
    init_email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            if self.init_email_confirmed and self.init_email:
                email = self.init_email
                if email != "" or email is not None:
                    stripe_id = helper.billing.Create_Customer(
                        email=email,
                        metadata={
                            "user_id": self.user.id,
                            "username": self.user.username,
                        },
                        raw=False,
                    )
                    self.stripe_id = stripe_id
        super().save(*args, **kwargs)


def allauth_user_signed_up_handler(request, user, *args, **kwargs):
    email = user.email
    Customers.objects.create(
        user=user,
        init_email=email,
        init_email_confirmed=False,
    )


allauth_user_signed_up.connect(allauth_user_signed_up_handler)


def allauth_email_confirmed_handler(request, email_address, *args, **kwargs):
    queryset = Customers.objects.filter(
        init_email=email_address,
        init_email_confirmed=False,
    )
    for obj in queryset:
        obj.init_email_confirmed = True
        obj.save()


allauth_email_confirmation.connect(allauth_email_confirmed_handler)
