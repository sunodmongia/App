from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce

from .models import Event


def get_usage(start_date=None):
    qs = Event.objects.all()

    if start_date:
        qs = qs.filter(created_at__gte=start_date)

    return qs.aggregate(
        api_calls=Count("id", filter=Q(type="api_call")),
        automations=Count("id", filter=Q(type="automation_run")),
        reports=Count("id", filter=Q(type="report_generated")),
        revenue=Coalesce(Sum("data__amount", filter=Q(type="revenue")), 0),
        storage=Coalesce(Sum("data__mb", filter=Q(type="storage_added")), 0),
    )
