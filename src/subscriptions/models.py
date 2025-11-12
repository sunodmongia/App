from django.db import models
from django.contrib.auth.models import Group, Permission


SUBSCRIPTION_PERMISSIONS = [
    ("starter", "starter perm"),
    ("professional", "professional perm"),
    ("enterprise", "enterprise perm"),
]


class Subscription(models.Model):

    name = models.CharField(max_length=120)
    groups = models.ManyToManyField(Group)
    active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={
            "content_type__app_label": "subscriptions",
            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS],
        },
    )

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
