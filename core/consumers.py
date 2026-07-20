from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging


logger = logging.getLogger(__name__)


class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Try to add this connection to the 'devices' group.
        # If Redis is down or slow, don't let the exception bubble up
        # and crash the consumer; log and accept the connection anyway.
        try:
            await self.channel_layer.group_add('devices', self.channel_name)
        except Exception as exc:  # defensive: catch redis timeout/connection errors
            logger.exception('Failed to add channel to group "devices": %s', exc)

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            await self.send(text_data=f"ECHO: {text_data}")
        elif bytes_data is not None:
            await self.send(bytes_data=bytes_data)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard('devices', self.channel_name)
        except Exception as exc:
            logger.exception('Failed to discard channel from group "devices": %s', exc)

    async def device_message(self, event):
        # Handler for messages sent by Celery task via group_send
        text = event.get('text')
        if text is not None:
            try:
                await self.send(text_data=text)
            except Exception as exc:
                logger.exception('Failed to send websocket message to client: %s', exc)

