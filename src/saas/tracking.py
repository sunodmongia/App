from .models import Usage, Event
from saas.consumers import *


def record_api_call(org):
    usage = Usage.objects.get(org=org)
    usage.api_calls += 1
    usage.save()

    Event.objects.create(
        org=org,
        type="api_call",
        data={"count": usage.api_calls}
    )
def api_call(org):
    usage = Usage.objects.get(org=org)
    usage.api_calls += 1
    usage.save()

    Event.objects.create(org=org, type="api_call")

    broadcast(org, {
        "api_calls": usage.api_calls,
        "storage": usage.storage_gb,
        "revenue": float(usage.revenue),
        "users": usage.active_users,
        "event": "API call made"
    })
