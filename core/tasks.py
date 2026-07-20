from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import time
import logging


logger = logging.getLogger(__name__)


@shared_task
def send_data_to_devices(payload):
    """Send `payload` (dict or JSON-serializable) to connected devices group.

    This task runs in the Celery worker process and uses the Channels layer
    to push a message to the `devices` group. Ensure CHANNEL_LAYERS uses Redis
    so the worker can reach the same channel layer as the ASGI server.
    """
    channel_layer = get_channel_layer()
    text = json.dumps(payload)
    async_to_sync(channel_layer.group_send)(
        'devices',
        {
            'type': 'device.message',
            'text': text,
        }
    )


@shared_task
def stream_data_for_duration(payload, duration=5, interval=0.5):
    """Stream `payload` repeatedly to the `devices` group for `duration` seconds.

    - `payload` may be a dict or JSON-serializable value.
    - `duration` is total seconds to stream (default 5s).
    - `interval` is seconds between messages (default 0.5s).
    """
    channel_layer = get_channel_layer()
    end = time.time() + float(duration)
    # Send initial timestamped messages repeatedly until time elapses
    while time.time() < end:
        # Add a timestamp to payload so clients can see progression
        data = {
            'payload': payload,
            'ts': time.time(),
        }
        text = json.dumps(data)
        try:
            async_to_sync(channel_layer.group_send)(
                'devices',
                {
                    'type': 'device.message',
                    'text': text,
                }
            )
        except Exception as exc:
            # Log and continue; if Redis is unavailable, avoid crashing the worker.
            logger.exception('Failed to send group message to "devices": %s', exc)
            # Optional: stop streaming if Redis is unavailable
            break
        time.sleep(float(interval))
