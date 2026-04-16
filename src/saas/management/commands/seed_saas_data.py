import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from saas.models import Organization, Event, Usage, TeamMember, Automation

User = get_user_model()

class Command(BaseCommand):
    help = "Seed the database with realistic SaaS data for a Cloud Service Provider."

    def handle(self, *args, **options):
        self.stdout.write("Seeding SaaS data...")

        # Get or create a default user
        user, _ = User.objects.get_or_create(username="sunodmongia", email="sunodmongia2003@gmail.com")
        if _:
            user.set_password("mongi@kum@r")
            user.save()

        org_names = ["CloudScale Systems", "NitroHost", "SkyNet Infrastructure", "Quantum Storage", "Vector API"]

        for name in org_names:
            org, _ = Organization.objects.get_or_create(name=name, owner=user)
            
            # Create team members
            TeamMember.objects.get_or_create(org=org, user=user, role="Owner")
            
            # Create automations
            automations = [
                ("Auto-Scale Workers", "cpu_load > 80%", "spin_up_instance"),
                ("Daily Data Backup", "schedule:daily", "backup_storage"),
                ("Security Audit", "event:login_failure", "notify_admin"),
            ]
            for a_name, trigger, action in automations:
                Automation.objects.get_or_create(org=org, name=a_name, trigger=trigger, action=action, enabled=random.choice([True, True, False]))

            # Create Usage
            usage, _ = Usage.objects.get_or_create(user=user)
            usage.api_calls += random.randint(1000, 5000)
            usage.storage_mb += random.randint(500, 2000)
            usage.revenue += random.randint(50, 200)
            usage.save()

            # Create 90 days of events
            start_date = now() - timedelta(days=90)
            for i in range(90):
                curr_date = start_date + timedelta(days=i)
                
                # Multiple events per day
                for _ in range(random.randint(2, 8)):
                    e_type = random.choice(["revenue", "api_call", "api_call", "report_generated", "automation_run"])
                    data = {}
                    if e_type == "revenue":
                        data = {"amount": random.randint(10, 50)}
                    elif e_type == "api_call":
                        data = {"endpoint": random.choice(["/v1/compute", "/v1/storage", "/v1/auth"])}
                    
                    event = Event.objects.create(org=org, type=e_type, data=data)
                    event.created_at = curr_date
                    event.save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded SaaS data!"))
