from .models import Event

class Telemetry:
    @staticmethod
    def api_call(org):
        Event.objects.create(org=org, type="api_call")

    @staticmethod
    def automation_run(org, automation_id=None):
        Event.objects.create(
            org=org,
            type="automation_run",
            data={"automation_id": automation_id} if automation_id else {},
        )
    @staticmethod
    def revenue(org, amount, source="stripe"):
        Event.objects.create(
            org=org,
            type="revenue",
            data={"amount": float(amount), "source": source},
        )