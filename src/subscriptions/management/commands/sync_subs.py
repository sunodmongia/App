from typing import Any
from django.core.management.base import BaseCommand
from subscriptions.services import ensure_default_subscriptions, sync_subscription_permissions


class Command(BaseCommand):
     help = "Ensure default subscriptions exist and sync their permissions to linked groups."

     def handle(self, *args: Any, **options:Any):
          ensure_default_subscriptions()
          sync_subscription_permissions()
          self.stdout.write(self.style.SUCCESS("Subscriptions synced successfully."))
