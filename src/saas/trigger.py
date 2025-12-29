from .models import Automation
from .automation_runner import run_automation

def handle_event(org, event_type):
    automations = Automation.objects.filter(
        org=org,
        trigger=event_type,
        enabled=True
    )

    for automation in automations:
        run_automation(automation)
