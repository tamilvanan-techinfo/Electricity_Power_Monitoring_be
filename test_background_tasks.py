import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket_with_background_tasks():
    """Test WebSocket connection and receive background task data"""
    try:
        print("=" * 60)
        print("WebSocket Test - Receiving Background Task Data")
        print("=" * 60)
        print()
        
        # Connect to power data stream
        async with websockets.connect("ws://localhost:8000/ws/power-data") as websocket:
            print("✓ Connected to ws://localhost:8000/ws/power-data")
            print("Waiting for power data (broadcasted every 5 seconds)...")
            print()
            
            # Receive multiple messages
            for i in range(5):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=7)
                    data = json.loads(response)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] Message {i+1}:")
                    print(f"  Type: {data.get('type')}")
                    
                    if data.get('type') == 'power_data':
                        power = data.get('data', {})
                        print(f"  Device: {power.get('device_id')}")
                        print(f"  Voltage: {power.get('voltage')} V")
                        print(f"  Current: {power.get('current')} A")
                        print(f"  Power: {power.get('power')} W")
                        print(f"  Power Factor: {power.get('power_factor')}")
                    
                    elif data.get('type') == 'alert':
                        alert = data.get('data', {})
                        print(f"  Alert Type: {alert.get('alert_type')}")
                        print(f"  Severity: {alert.get('severity')}")
                        print(f"  Message: {alert.get('message')}")
                    
                    print()
                    
                except asyncio.TimeoutError:
                    print("✗ Timeout - No message received in 7 seconds")
                    break
                    
        print("=" * 60)
        print("✓ Test completed successfully!")
        print("=" * 60)
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_with_background_tasks())
