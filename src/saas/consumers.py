import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class DashboardConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            self.close()
            return

        self.org_group = f"org_{user.organization.id}"

        async_to_sync(self.channel_layer.group_add)(self.org_group, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.org_group, self.channel_name
        )

    def send_update(self, event):
        self.send(text_data=json.dumps(event["data"]))


def broadcast(org, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"org_{org.id}",
        {
            "type": "send_update",
            "data": payload,
        },
    )
