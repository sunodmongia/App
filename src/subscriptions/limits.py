from django.utils.timezone import now
from datetime import timedelta
from saas.models import Event

def api_calls_last_30_days(org):
    since = now() - timedelta(days=30)
    return Event.objects.filter(
        org=org,
        type="api_call",
        created_at__gte=since
    ).count()
