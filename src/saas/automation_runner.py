from saas.telemetry import Telemetry

def execute_action(automation):
    print(f"Executing automation: {automation.name}")

def run_automation(automation):
    if not automation.enabled:
        return

    execute_action(automation)
    Telemetry.automation_run(automation.org, automation.id)
