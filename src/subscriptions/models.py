from django.db import models
from django.contrib.auth.models import Group

class Subscription(models.Model):
    name = models.CharField(max_length=120)
    groups = models.ManyToManyField(Group)

    class Meta:
        permissions = [
            ("starter", "starter perm"),
            ("professional", "professional perm"),
            ("enterprise", "enterprise perm"),
        ]
