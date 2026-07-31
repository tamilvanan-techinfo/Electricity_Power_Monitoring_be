from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from core.models import *
from .models import *
from .serializer import *
CAMEL_TO_SNAKE_FIELD_MAP = {
        "x": "x",
        "y": "y",
        "width": "width",
        "height": "height",
        "fullscreen": "fullscreen",
        "alwaysOnTop": "always_on_top",
        "resizable": "resizable",
        "movable": "movable",
        "minimizable": "minimizable",
        "maximizable": "maximizable",
        "visible": "visible",
        "menuBarVisible": "menu_bar_visible",
        "autoHideMenuBar": "auto_hide_menu_bar",
        "opacity": "opacity",
        "kiosk": "kiosk",
        "title": "title",
        "skipTaskbar": "skip_taskbar",
        "closable": "closable",
        "minimized": "minimized",
        "maximized": "maximized",
        "focus": "focus",
    }
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

            if screen.id == 5:
                init_data = await self.getInitialData()
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
                                    "init_data":init_data
                                },
                            )

            else:
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

        elif action == "window_update":
            try:
                properties = data.get("properties", {})

                await self.getScreenProps(1,properties)

                screen = await self.getScreenProps(1)

                await self.channel_layer.group_send(
                    "screen_client",
                    {
                        "type": "window_update",
                        "properties": screen,
                    },
                )

            except Exception as e:
                print(e)

    async def screen_changed(self, event):
        data={
            "type": "screen_changed",
            "screen_id": event["screen_id"],
            "screen_name": event["screen_name"],
            "path": event["path"],
            "thumbnail": event["thumbnail"],
            "is_live": event["is_live"],
            
        }
        if event.get("init_data"):
            data["init_data"] = event["init_data"]
        print(event)
        await self.send(
            text_data=json.dumps(
                data
            )
        )
    async def window_update(self,event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "window_update",
                    "properties": event["properties"],
                    
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

    @database_sync_to_async
    def getInitialData(self):
        data = ActiveParticipent.objects.get(id=1)

        # Convert HH:MM:SS to total minutes
        duration_minutes = (
            data.time_duration.hour * 60
            + data.time_duration.minute
            + data.time_duration.second // 60
        )

        response = {
            "duration": duration_minutes,
            "cycles": list(data.cycle.values_list("cycle_no", flat=True))
        }

        return response

    
    @database_sync_to_async
    def getScreenProps(self, screen_id, properties=None):
        screen = ScreenPosition.objects.get(id=screen_id)

        if properties:
            for field, value in properties.items():
                model_field = CAMEL_TO_SNAKE_FIELD_MAP.get(field, field)
                if hasattr(screen, model_field):
                    setattr(screen, model_field, value)
                else:
                    print(f"⚠ Unknown screen property received: {field} (mapped to {model_field})")

            screen.save()

        response = {
            "height": 0,
            "width": 0,
            "x": screen.x,
            "y": screen.y,
            "fullscreen": screen.fullscreen,
            "alwaysOnTop": screen.always_on_top,
            "resizable": screen.resizable,
            "movable": screen.movable,
            "minimizable": screen.minimizable,
            "maximizable": screen.maximizable,
            "visible": screen.visible,
            "menuBarVisible": screen.menu_bar_visible,
            "autoHideMenuBar": screen.auto_hide_menu_bar,
            "opacity": screen.opacity,
        }

        if not screen.fullscreen:
            response["width"] = screen.width
            response["height"] = screen.height

        return response