import asyncio
import json
import websockets

WS_URL = "ws://localhost:8000/ws/power-data"

async def test_websocket():
    try:
        print(f"Connecting to {WS_URL}...")

        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected successfully!")

            # Uncomment if your server expects an initial message
            # await websocket.send(json.dumps({"type": "ping"}))

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30)
                    print("📩 Received:")
                    print(message)

                    # If the server sends JSON
                    try:
                        data = json.loads(message)
                        print("Parsed JSON:")
                        print(json.dumps(data, indent=4))
                    except json.JSONDecodeError:
                        pass

                except asyncio.TimeoutError:
                    print("⏳ No message received in 30 seconds. Sending ping...")
                    pong = await websocket.ping()
                    await pong
                    print("🏓 Ping successful")

    except websockets.exceptions.InvalidStatus as e:
        print(f"❌ Server rejected connection: {e}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())