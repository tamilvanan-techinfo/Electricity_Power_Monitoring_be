from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from core.models import *
from .models import *
from .serializer import *
from admin_panel.models import FreeText
import base64
from django.core.files.base import ContentFile

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

        # Send the current active theme immediately on connect so the
        # screen/admin doesn't have to wait for the next theme_updated
        # broadcast to render the right colors (matches what
        # /api/get_active_theme/ would return on a page refresh).
        theme_payload = await self.getActiveThemePayload()
        if theme_payload is not None:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "theme_updated",
                        "data": theme_payload,
                    }
                )
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        self.connected.get(self.role, set()).discard(self.channel_name)

        print(f"{self.role} disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)

        print("Received:", data)
        print(self.connected)

        action = data.get("type")

        # Only admin can change live screen / trigger these actions
        if self.role != "admin":
            return

        if action == "set_live_screen":
            await self.handle_set_live_screen(data)

        elif action == "window_update":
            await self.handle_window_update(data)

        elif action == "send_free_text":
            await self.handle_send_free_text(data)



        elif action == "update_theme":
            print("updating")
            await self.handle_update_theme(data)

        elif action == "get_active_theme":
            # Lets an admin client explicitly re-request the current
            # theme (e.g. after opening a settings panel) without
            # waiting for the next broadcast.
            theme_payload = await self.getActiveThemePayload()
            if theme_payload is not None:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "theme_updated",
                            "data": theme_payload,
                        }
                    )
                )

    # ------------------------------------------------------------
    # Action handlers (kept separate from receive() for readability)
    # ------------------------------------------------------------
    async def handle_set_live_screen(self, data):
        screen_id = data.get("screen_id")

        if not screen_id:
            return

        screen = await self.set_live_screen(screen_id)
        if screen is None:
            return

        base_payload = {
            "type": "screen_changed",
            "screen_id": screen.id,
            "screen_name": screen.name,
            "path": screen.path,
            "thumbnail": screen.thumbnail.url if screen.thumbnail else None,
            "is_live": screen.is_live,
        }

        client_payload = dict(base_payload)
        if screen.id == 5:
            client_payload["init_data"] = await self.getInitialData()
        elif screen.id == 8:
            client_payload["init_data"] = await self.getFreeText()

        await self.channel_layer.group_send("screen_client", client_payload)

        # Notify admins too (no init_data needed there)
        await self.channel_layer.group_send("screen_admin", base_payload)

    async def handle_window_update(self, data):
        try:
            properties = data.get("properties", {})

            await self.getScreenProps(1, properties)

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

    async def handle_send_free_text(self, data):
        try:
            print("Received free text:", data)
            saved = await self.saveFreeText(data)

            await self.channel_layer.group_send(
                "screen_client",
                {
                    "type": "free_text_updated",
                    "content": saved.text,
                    "bg_image_url": saved.bg_image.url if saved.bg_image else None,
                    "style": saved.style,
                },
            )
        except Exception as e:
            print(e)

    async def handle_update_theme(self, data):
        """
        Saves the AppTheme with the colors/theme dict sent by
        AppSettings.jsx, then pushes the fresh payload straight to
        screen_client (the group the actual display screens are in)
        and echoes it back to screen_admin so every open admin panel
        stays in sync. Sent directly here instead of relying solely on
        AppTheme's post_save signal, since that signal broadcasts to
        a "screen" group this consumer's clients never join.
        """
        try:
            payload = await self.updateActiveTheme(data.get("colors", {}), data.get("theme", {}))
        except Exception as e:
            print(f"⚠ handle_update_theme failed: {e}")
            return

        message = {
            "type": "theme_updated",
            "data": payload,
        }

        await self.channel_layer.group_send(
            "screen_client",
            {"type": "theme_update", "message": message},
        )
  

    # ------------------------------------------------------------
    # Group-send handlers (dispatched by channel_layer.group_send's
    # "type" key — method name must match exactly)
    # ------------------------------------------------------------
    async def screen_changed(self, event):
        data = {
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
        await self.send(text_data=json.dumps(data))

    async def window_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "window_update",
                    "properties": event["properties"],
                }
            )
        )

    async def free_text_updated(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "free_text_updated",
                    "data": event,
                }
            )
        )

    async def theme_update(self, event):
        """
        Handler for the "screen" group broadcast sent by
        broadcast_theme_update() in core/models.py (AppTheme's
        post_save signal). event["message"] is already the exact
        {"type": "theme_updated", "data": {...}} shape the frontend's
        SocketContext.jsx expects, so just forward it as-is.
        """
        await self.send(text_data=json.dumps(event["message"]))

    # ------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------
    @database_sync_to_async
    def set_live_screen(self, screen_id):
        try:
            screen = Screen.objects.get(id=screen_id)
        except Screen.DoesNotExist:
            print(f"⚠ set_live_screen: no Screen with id={screen_id}")
            return None

        # Deactivate whichever screen(s) were previously live. Using
        # filter().update() instead of get() avoids a crash if zero or
        # more than one screen is currently marked live.
        Screen.objects.filter(is_live=True).exclude(pk=screen.pk).update(is_live=False)

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
            "cycles": list(data.cycle.values_list("cycle_no", flat=True)),
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

    @database_sync_to_async
    def getFreeText(self):
        free_text = FreeText.objects.last()
        return free_text.text if free_text else ""

    @database_sync_to_async
    def saveFreeText(self, data):
        free_text = FreeText.objects.create(
            text=data.get("text", ""),
            style=data.get("style", {}),
        )

        bg_image = data.get("bgImage")
        if bg_image and bg_image.get("data"):
            decoded = base64.b64decode(bg_image["data"])
            free_text.bg_image.save(
                bg_image.get("name", "background.jpg"),
                ContentFile(decoded),
                save=True,
            )

        return free_text

    # camelCase (frontend / to_payload()) -> AppTheme field name
    THEME_COLORS_FIELD_MAP = {
        "backgroundGradient": "colors_background_gradient",
        "headerBorder": "colors_header_border",
        "headerBorderShadow": "colors_header_border_shadow",
        "white": "colors_white",
        "green": "colors_green",
        "gold": "colors_gold",
        "highlightBorder": "colors_highlight_border",
        "highlightShadow": "colors_highlight_shadow",
        "normalRowBorder": "colors_normal_row_border",
        "circleBg": "colors_circle_bg",
        "circleHighlightBorder": "colors_circle_highlight_border",
        "circleHighlightShadow": "colors_circle_highlight_shadow",
    }
    THEME_THEME_FIELD_MAP = {
        "bg": "theme_bg",
        "bgGradient": "theme_bg_gradient",
        "panel": "theme_panel",
        "panelBorder": "theme_panel_border",
        "panelGlow": "theme_panel_glow",
        "neon": "theme_neon",
        "neonSoft": "theme_neon_soft",
        "gold": "theme_gold",
        "text": "theme_text",
        "subtext": "theme_subtext",
        "muted": "theme_muted",
        "divider": "theme_divider",
    }

    @database_sync_to_async
    def updateActiveTheme(self, colors, theme):
        """
        Applies partial colors/theme dicts (camelCase keys, as sent by
        AppSettings.jsx) onto the active AppTheme row and saves it.
        Unknown keys are ignored; missing keys keep their current
        value. Returns the saved to_payload() dict so callers (e.g.
        handle_update_theme) have data to broadcast — this is easy to
        miss since Python silently returns None otherwise, which is
        exactly what was causing the {"data": null} you saw over the
        socket.
        """
        from core.models import AppTheme  # adjust import path if AppTheme lives elsewhere

        active = AppTheme.get_active()

        for key, value in (colors or {}).items():
            field = self.THEME_COLORS_FIELD_MAP.get(key)
            if field:
                setattr(active, field, value)
            else:
                print(f"⚠ Unknown theme color key received: {key}")

        for key, value in (theme or {}).items():
            field = self.THEME_THEME_FIELD_MAP.get(key)
            if field:
                setattr(active, field, value)
            else:
                print(f"⚠ Unknown theme key received: {key}")

        active.is_active = True
        active.full_clean(exclude=["created_at", "updated_at"])  # runs the color validators
        active.save()

        return active.to_payload()

    @database_sync_to_async
    def getActiveThemePayload(self):
        """
        Wraps AppTheme.get_active().to_payload() for use inside this
        consumer. Returns None (instead of raising) if the AppTheme
        model isn't importable/migrated yet, so connect() never fails
        because of the theme feature.
        """
        try:
            from core.models import AppTheme  # adjust import path if AppTheme lives elsewhere
            return AppTheme.get_active().to_payload()
        except Exception as e:
            print(f"⚠ getActiveThemePayload failed: {e}")
            return None