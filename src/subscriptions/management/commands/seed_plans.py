from django.core.management.base import BaseCommand
from django.db import transaction
from subscriptions.models import Subscription, PlanLimit
from subscriptions.services import sync_subscription_permissions

class Command(BaseCommand):
    help = 'Seeds the database with four standard industrial subscription plans'

    def handle(self, *args, **options):
        self.stdout.write('Seeding industrial subscription plans...')
        
        plans_data = [
            {
                'name': 'Free',
                'description': 'Ideal for hobbyists and early-stage telemetry projects.',
                'monthly_price': 0,
                'annual_price': 0,
                'is_default': True,
                'display_order': 1,
                'features': ['1,000 API Calls/mo', '100 MB Storage', '1 Team Member', 'Basic Analytics'],
                'limits': {
                    'api_calls': 1000,
                    'storage_mb': 10000,
                    'automations': 5,
                    'team_members': 1
                }
            },
            {
                'name': 'Starter',
                'description': 'Perfect for emerging teams scaling their industrial footprint.',
                'monthly_price': 2499,
                'annual_price': 24990,
                'is_featured': True,
                'display_order': 2,
                'features': ['50,000 API Calls/mo', '50 GB Storage', '5 Team Members', 'Standard Automations'],
                'limits': {
                    'api_calls': 50000,
                    'storage_mb': 51200, # 50 GB
                    'automations': 25,
                    'team_members': 5
                }
            },
            {
                'name': 'Professional',
                'description': 'The standard for high-growth organizations and data-heavy fleets.',
                'monthly_price': 999,
                'annual_price': 9990,
                'display_order': 3,
                'features': ['500,000 API Calls/mo', '500 GB Storage', '25 Team Members', 'Priority Support'],
                'limits': {
                    'api_calls': 500000,
                    'storage_mb': 51200, # 500 GB
                    'automations': 100,
                    'team_members': 25
                }
            },
            {
                'name': 'Enterprise',
                'description': 'Industrial-grade infrastructure with maximum resource quotas.',
                'monthly_price': 2499,
                'annual_price': 24990,
                'display_order': 4,
                'features': ['Unlimited API Calls', '10 TB Storage', 'Unlimited Team Members', 'Dedicated Infrastructure'],
                'limits': {
                    'api_calls': 1000000000, # Treat as unlimited
                    'storage_mb': 10485760, # 10 TB
                    'automations': 1000,
                    'team_members': 1000
                }
            }
        ]

        with transaction.atomic():
            for plan in plans_data:
                limits_data = plan.pop('limits')
                obj, created = Subscription.objects.update_or_create(
                    name=plan['name'],
                    defaults=plan
                )
                
                PlanLimit.objects.update_or_create(
                    subscription=obj,
                    defaults=limits_data
                )
                
                status = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(f'{status} plan: {obj.name}'))

        sync_subscription_permissions()
        self.stdout.write(self.style.SUCCESS('Seeding complete. Industrial billing engine is ready.'))
