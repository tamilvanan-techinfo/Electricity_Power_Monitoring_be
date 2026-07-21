from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
import json

from .models import Screen


class ScreenConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.role = self.scope["url_route"]["kwargs"]["role"]
        self.group_name = f"screen_{self.role}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        action = data.get("action")

        if action == "set_live":
            screen_id = data.get("screen_id")

            screen = await self.set_live_screen(screen_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "screen_changed",
                    "screen_id": screen.id,
                    "screen_name": screen.name,
                },
            )

    async def screen_changed(self, event):
        await self.send(text_data=json.dumps({
            "type": "screen_changed",
            "screen_id": event["screen_id"],
            "screen_name": event["screen_name"],
        }))

    @database_sync_to_async
    def set_live_screen(self, screen_id):
        Screen.objects.update(is_live=False)

        screen = Screen.objects.get(pk=screen_id)
        screen.is_live = True
        screen.save()

        return screen