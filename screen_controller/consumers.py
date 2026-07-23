from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from .models import Screen


class ScreenConsumer(AsyncWebsocketConsumer):
    connected = {}

    async def connect(self):
        self.role = self.scope["url_route"]["kwargs"]["role"]
        self.connected.setdefault(self.role, set())
        self.connected[self.role].add(self.channel_name)
        # screen_admin or screen_client
        self.group_name = f"screen_{self.role}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        print(f"{self.role} connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

        print(f"{self.role} disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)

        print("Received:", data)
        print(self.connected)

        action = data.get("type")

        # Only admin can change live screen
        if self.role != "admin":
            return

        if action == "set_live_screen":

            screen_id = data.get("screen_id")

            if not screen_id:
                return

            screen = await self.set_live_screen(screen_id)

            # Send only to CLIENTS
            await self.channel_layer.group_send(
                "screen_client",
                {
                    "type": "screen_changed",
                    "screen_id": screen.id,
                    "screen_name": screen.name,
                    "path": screen.path,
                    "thumbnail": (
                        screen.thumbnail.url
                        if screen.thumbnail
                        else None
                    ),
                    "is_live": screen.is_live,
                },
            )

            # Optional: Notify admins too
            await self.channel_layer.group_send(
                "screen_admin",
                {
                    "type": "screen_changed",
                    "screen_id": screen.id,
                    "screen_name": screen.name,
                    "path": screen.path,
                    "thumbnail": (
                        screen.thumbnail.url
                        if screen.thumbnail
                        else None
                    ),
                    "is_live": screen.is_live,
                },
            )

    async def screen_changed(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "screen_changed",
                    "screen_id": event["screen_id"],
                    "screen_name": event["screen_name"],
                    "path": event["path"],
                    "thumbnail": event["thumbnail"],
                    "is_live": event["is_live"],
                }
            )
        )

    @database_sync_to_async
    def set_live_screen(self, screen_id):

        old = Screen.objects.get(is_live=True)
        old.is_live = False
        old.save()


        screen = Screen.objects.get(id=screen_id)

        screen.is_live = True
        screen.save()

        return screen