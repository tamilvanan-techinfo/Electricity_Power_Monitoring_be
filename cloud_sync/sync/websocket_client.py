import asyncio
import json
import websockets

from .services import save_monitor_data

CLOUD_WS = "ws://192.168.1.46:8000/ws/local-server?client_id=django_local"


class CloudSocketClient:

    async def connect(self):

        while True:

            try:

                print("Connecting to Cloud...")

                async with websockets.connect(
                    CLOUD_WS,
                    ping_interval=20,
                    ping_timeout=20
                ) as websocket:

                    print("Connected")

                    async for message in websocket:

                        data = json.loads(message)
                        print(f"Received data: {data}") 
                        await save_monitor_data(data)

            except Exception as e:

                print(f"Disconnected : {e}")

                await asyncio.sleep(5)