from .models import Event

def log_event(org, type, **data):
    Event.objects.create(
        org=org,
        type=type,
        data=data
    )
