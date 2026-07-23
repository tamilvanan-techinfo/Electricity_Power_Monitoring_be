from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio
import json
import time
import logging

from .models import ParticipentCycle,Grouping


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

        # Kick off this connection's own 5-second send loop. Each client
        # gets an independent timer starting the moment it connects, rather
        # than a schedule shared across all clients.
        self.send_loop_task = asyncio.ensure_future(self._send_every_5_seconds())

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            await self.send(text_data=f"ECHO: {text_data}")
        elif bytes_data is not None:
            await self.send(bytes_data=bytes_data)

    async def disconnect(self, close_code):
        # Stop this connection's loop first so it can't fire against a
        # socket that's already going away.
        task = getattr(self, 'send_loop_task', None)
        if task is not None:
            task.cancel()

        try:
            await self.channel_layer.group_discard('devices', self.channel_name)
        except Exception as exc:
            logger.exception('Failed to discard channel from group "devices": %s', exc)

    async def device_message(self, event):
        # Handler for messages sent by a Celery task via group_send — still
        # supported for the on-demand /api/stream/ burst, independent of the
        # per-connection loop below.
        text = event.get('text')
        if text is not None:
            try:
                await self.send(text_data=text)
            except Exception as exc:
                logger.exception('Failed to send websocket message to client: %s', exc)

    async def _send_every_5_seconds(self):
        """Runs for the lifetime of this connection.

        Sends a fresh data snapshot to this client only, every 5 seconds,
        starting 5 seconds after connect. Cancelled from disconnect().
        """
        try:
            while True:
                await asyncio.sleep(5)
                
                data = await self._group_build_payload()
                await self.send(text_data=json.dumps(data))
        except asyncio.CancelledError:
            # Normal shutdown path when the client disconnects.
            raise
        except Exception as exc:
            logger.exception('Per-connection 5s send loop failed: %s', exc)

    @staticmethod
    def _profile_image_url(participent):
        """Return the participant's profile image path, or None.

        `profile` is blank/null-able, and calling .url on an empty
        ImageFieldFile raises ValueError — this keeps that off the hot path
        of every heartbeat tick.
        """
        if not participent.profile:
            return None
        try:
            return participent.profile.url
        except ValueError:
            return None

    def _build_absolute_uri(self, path):
        """Turn a MEDIA_URL-relative path (e.g. /media/x.jpg) into a full
        URL using this connection's own scope, since a consumer has no HTTP
        request to build one from the way a view does.
        """
        if not path:
            return None

        scheme = 'https' if self.scope.get('scheme') == 'wss' else 'http'

        headers = dict(self.scope.get('headers') or [])
        host_header = headers.get(b'host')
        if host_header:
            host = host_header.decode('latin-1')
        else:
            server_host, server_port = self.scope.get('server') or (None, None)
            host = server_host or 'localhost'
            if server_port:
                host = f'{host}:{server_port}'

        return f'{scheme}://{host}{path}'

    @database_sync_to_async
    def _build_payload(self):
        # .only() trims the columns pulled off each joined table to just
        # what this payload uses, instead of loading full Participent/Cycle
        # rows every 5 seconds for every connected client.
        allocations = (
            ParticipentCycle.objects
            .select_related('participent', 'cycle')
            .only(
                'voltage', 'amperage', 'power',
                'participent__name', 'participent__profile',
                'cycle__cycle_no',
            )
            .order_by('-power')  # Highest power first
        )

        return {
            'type': 'heartbeat',
            
            'ts': time.time(),
            'allocations': [
                {
                    'rank': rank,
                    'participent': allocation.participent.name,
                    'profile_image': self._build_absolute_uri(
                        self._profile_image_url(allocation.participent)
                    ),
                    'cycle': allocation.cycle.cycle_no,
                    'voltage': allocation.voltage,
                    'amperage': allocation.amperage,
                    'power': allocation.power,
                }
                for rank, allocation in enumerate(allocations, start=1)
            ],
        }
    
    @database_sync_to_async
    def _group_build_payload(self):
        # .only() trims the columns pulled off each joined table to just
        # what this payload uses, instead of loading full Participent/Cycle
        # rows every 5 seconds for every connected client.
        allocations = (
            ParticipentCycle.objects
            .select_related('participent', 'cycle')
            .only(
                'voltage', 'amperage', 'power',
                'participent__name', 'participent__profile',
                'cycle__cycle_no',
            )
            .order_by('-power')  # Highest power first
        )

        grouped_allocations = {}
        for allocation in allocations:
            
            cycle_no = allocation.cycle.cycle_no
            if cycle_no not in grouped_allocations:
                grouped_allocations[cycle_no] = {
                    'cycle': cycle_no,
                    'total_voltage': 0.0,
                    'total_amperage': 0.0,
                    'total_power': 0.0,
                    'participants': []
                }
            grouped_allocations[cycle_no]['total_voltage'] += allocation.voltage
            grouped_allocations[cycle_no]['total_amperage'] += allocation.amperage
            grouped_allocations[cycle_no]['total_power'] += allocation.power
            grouped_allocations[cycle_no]['participants'].append({
                'name': allocation.participent.name,
                'profile_image': self._build_absolute_uri(
                    self._profile_image_url(allocation.participent)
                ),
                'voltage': allocation.voltage,
                'amperage': allocation.amperage,
                'power': allocation.power,
            })

        return {
            'type': 'heartbeat',
            'ts': time.time(),
            'grouped_allocations': list(grouped_allocations.values()),
        }

