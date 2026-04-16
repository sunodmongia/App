from .models import Event
from .consumers import broadcast

def log_event(org, type, **data):
    event = Event.objects.create(
        org=org,
        type=type,
        data=data
    )
    # Broadcast the event data in real-time
    broadcast(org, {
        "event_id": event.id,
        "type": type,
        "data": data,
        "created_at": event.created_at.isoformat()
    })
