from typing import Any
from django.core.management.base import BaseCommand
from subscriptions.models import Subscription


class Command(BaseCommand):
     def handle(self, *args: Any, **options:Any):
          qs = Subscription.objects.filter(active=True)
          for obj in qs:
               print(obj.groups.all())
               for group in obj.groups.all():
                    for per in obj.permissions.all():
                         group.permissions.add(per)
               print(obj.permission.all())