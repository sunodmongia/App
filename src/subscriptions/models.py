from django.db import models


class Subscription(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        permissions = [
            ("starter", "starter perm"),
            ("professional", "professional perm"),
            ("enterprise", "enterprise perm"),
        ]
