from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import time
import logging

from .models import ParticipentCycle


logger = logging.getLogger(__name__)


def _broadcast(text):
    """Push a pre-serialized text payload to all clients in the 'devices' group.

    Shared by every task that needs to talk to the websocket layer so the
    error handling (Redis down/slow) lives in exactly one place.
    """
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            'devices',
            {
                'type': 'device.message',
                'text': text,
            }
        )
    except Exception as exc:
        # Log and swallow; a missing/slow Redis shouldn't crash the worker
        # or the beat schedule.
        logger.exception('Failed to send group message to "devices": %s', exc)


@shared_task
def send_data_to_devices(payload):
    """Send `payload` (dict or JSON-serializable) to connected devices group.

    This task runs in the Celery worker process and uses the Channels layer
    to push a message to the `devices` group. Ensure CHANNEL_LAYERS uses Redis
    so the worker can reach the same channel layer as the ASGI server.
    """
    _broadcast(json.dumps(payload))


@shared_task
def heartbeat():
    """Periodic task, fired every 5 seconds by Celery Beat.

    Builds a fresh snapshot of current cycle allocations and pushes it to
    every connected websocket client. This is what keeps the dashboard's
    live readings up to date without the client having to poll.

    Registered in settings.py under CELERY_BEAT_SCHEDULE — requires a
    `celery ... beat` process running alongside the worker (see notes below).
    """
    allocations = ParticipentCycle.objects.select_related('participent', 'cycle').all()

    data = {
        'type': 'heartbeat',
        'ts': time.time(),
        'allocations': [
            {
                'participent': a.participent.name,
                'cycle': a.cycle.cycle_no,
                'voltage': a.voltage,
                'amperage': a.amperage,
                'power': a.power,
            }
            for a in allocations
        ],
    }
    _broadcast(json.dumps(data))


@shared_task
def stream_data_for_duration(payload, duration=5, interval=0.5):
    """Stream `payload` repeatedly to the `devices` group for `duration` seconds.

    Kept for on-demand bursts triggered via /api/stream/ — independent of the
    always-on `heartbeat` task above. Note this blocks the worker for the
    full duration, so keep `duration` short or give it a dedicated queue if
    you use it alongside the heartbeat under real load.

    - `payload` may be a dict or JSON-serializable value.
    - `duration` is total seconds to stream (default 5s).
    - `interval` is seconds between messages (default 0.5s).
    """
    end = time.time() + float(duration)
    while time.time() < end:
        data = {
            'payload': payload,
            'ts': time.time(),
        }
        _broadcast(json.dumps(data))
        time.sleep(float(interval))