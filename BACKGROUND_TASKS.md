# Electricity Power Monitoring - Background Tasks Setup

## Overview
The system now includes automatic background tasks that broadcast power data to all connected WebSocket clients every 5 seconds.

## Architecture

### Background Task Manager
- **File**: `services/background_tasks.py`
- **Type**: Async-based (no external dependencies like Redis/Celery)
- **Broadcast Interval**: 5 seconds
- **Alert Generation**: Random alerts every ~10 seconds

### Key Features
✅ Automatic power data generation and broadcasting  
✅ Real-time WebSocket updates to all connected clients  
✅ Random alert generation for anomalies  
✅ No Redis/Celery dependencies required  
✅ Simple start/stop control via REST endpoints  

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python main.py
```

The server will:
- Start on `http://localhost:8000`
- Automatically start background power data broadcasting
- Send data to all connected WebSocket clients every 5 seconds

## API Endpoints

### WebSocket Endpoints
1. **Power Data Stream**
   ```
   ws://localhost:8000/ws/power-data
   ```
   Receives real-time power readings every 5 seconds

2. **Notifications**
   ```
   ws://localhost:8000/ws/notifications
   ```
   Receives system notifications

3. **Alerts**
   ```
   ws://localhost:8000/ws/alerts
   ```
   Receives power anomaly alerts

### REST Endpoints for Task Control

**Get Task Status**
```bash
curl http://localhost:8000/tasks/status
```
Response:
```json
{
  "power_broadcast": "running",
  "total_connections": 2,
  "broadcast_interval": "5 seconds",
  "alert_interval": "10 seconds (random)"
}
```

**Start Power Broadcast**
```bash
curl -X POST http://localhost:8000/tasks/start-power-broadcast
```

**Stop Power Broadcast**
```bash
curl -X POST http://localhost:8000/tasks/stop-power-broadcast
```

## Testing

### 1. Test with Python Client
```bash
python test_websocket.py
```

### 2. Test with JavaScript (Browser Console)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/power-data');

ws.onopen = () => {
  console.log('Connected to power data stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Power Data:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### 3. Test with Postman
1. Open Postman Desktop (Web version has limitations)
2. Create WebSocket request: `ws://localhost:8000/ws/power-data`
3. Click Connect
4. Monitor incoming messages

## Sample Data Format

### Power Data (sent every 5 seconds)
```json
{
  "type": "power_data",
  "data": {
    "device_id": "sensor_001",
    "voltage": 242.56,
    "current": 18.75,
    "power": 4568.50,
    "frequency": 50.02,
    "power_factor": 0.95
  },
  "timestamp": "2026-07-20T12:34:56.789012"
}
```

### Alert (sent randomly)
```json
{
  "type": "alert",
  "data": {
    "alert_type": "overvoltage",
    "device_id": "sensor_002",
    "value": 250.5,
    "severity": "critical",
    "message": "Power anomaly detected"
  },
  "timestamp": "2026-07-20T12:34:56.789012"
}
```

## Project Structure

```
.
├── main.py                          # FastAPI application
├── services/
│   ├── websocket.py                 # WebSocket connection manager
│   └── background_tasks.py          # Background task manager
├── database.py                      # Database configuration
├── test_websocket.py               # WebSocket test client
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Configuration

### Broadcast Interval
To change the 5-second interval, edit `services/background_tasks.py`:
```python
await asyncio.sleep(5)  # Change 5 to desired seconds
```

### Power Data Range
To adjust generated power data ranges, edit `_send_power_data()`:
```python
"voltage": round(random.uniform(220, 250), 2),  # Adjust range
"current": round(random.uniform(5, 30), 2),     # Adjust range
```

## Monitoring

### Check Running Tasks
```bash
curl http://localhost:8000/tasks/status
```

### View Active WebSocket Connections
The `/tasks/status` endpoint shows `total_connections` count

### Logs
The server logs all broadcasting activity:
```
✓ Power data sent: {...}
⚠ Alert sent: overvoltage
```

## Troubleshooting

### No data being received?
1. Check if server is running: `curl http://localhost:8000/health`
2. Verify WebSocket connection is established
3. Check browser console for errors
4. Ensure background tasks are running: `curl http://localhost:8000/tasks/status`

### WebSocket connection fails?
1. For Codespace: Use `wss://` with your Codespace URL
2. For Local: Use `ws://localhost:8000`
3. Check CORS middleware is enabled (it is by default)

### High CPU usage?
- Reduce broadcast frequency by increasing `asyncio.sleep()` interval
- Reduce number of concurrent connections
- Monitor with: `top` or `htop`

## Production Deployment

For production with heavy loads, consider:
1. **Redis + Celery**: Replace `BackgroundTaskManager` with Celery tasks
2. **Multiple Workers**: Deploy with multiple worker processes
3. **Load Balancing**: Use nginx for load balancing across instances
4. **Database Integration**: Store power data in database for historical analysis

## Next Steps

1. ✅ Background power data broadcasting (DONE)
2. Connect to real power monitoring sensors
3. Add database persistence for power readings
4. Create data visualization dashboard
5. Implement alert rules and thresholds
6. Add authentication and user management

---

**Status**: ✓ Fully Functional  
**Last Updated**: 2026-07-20  
**Version**: 1.0.0
