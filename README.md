# Electricity Power Monitoring API

A FastAPI server with SQLite database for monitoring electricity power consumption.

## Features

- **Power Readings**: Store and retrieve power readings (voltage, current, power, energy)
- **Device Management**: Create and manage monitoring devices
- **Alerts**: Create and track power anomalies and alerts
- **Statistics**: Get power consumption statistics for devices
- **RESTful API**: Complete REST API with automatic API documentation

## Project Structure

```
├── main.py              # FastAPI application and endpoints
├── database.py          # SQLite database configuration
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic validation schemas
├── crud.py              # Create, Read, Update, Delete operations
├── requirements.txt     # Python dependencies
└── electricity_monitor.db  # SQLite database (auto-created)
```

## Installation

1. **Create and activate virtual environment** (already done):
   ```bash
   python -m venv env
   source env/Scripts/activate  # On Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - API status
- `GET /health` - Health check

### Power Readings
- `POST /api/readings` - Create a new power reading
- `GET /api/readings` - Get power readings (with optional device_id filter)
- `GET /api/readings/{reading_id}` - Get a specific reading
- `GET /api/devices/{device_id}/stats` - Get power statistics (24h default)

### Devices
- `POST /api/devices` - Create a new device
- `GET /api/devices` - List all devices
- `GET /api/devices/{device_id}` - Get device details
- `PUT /api/devices/{device_id}` - Update device
- `DELETE /api/devices/{device_id}` - Delete device

### Alerts
- `POST /api/alerts` - Create a new alert
- `GET /api/alerts` - Get alerts (with filters)
- `PUT /api/alerts/{alert_id}/resolve` - Mark alert as resolved

## Example Requests

### Create a Device
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEVICE001",
    "name": "Main Panel",
    "location": "Electrical Room",
    "is_active": true
  }'
```

### Add a Power Reading
```bash
curl -X POST http://localhost:8000/api/readings \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEVICE001",
    "voltage": 230.5,
    "current": 15.3,
    "power": 3500,
    "energy": 87.5,
    "frequency": 50.0,
    "power_factor": 0.95
  }'
```

### Get Device Statistics
```bash
curl http://localhost:8000/api/devices/DEVICE001/stats?hours=24
```

### Create an Alert
```bash
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEVICE001",
    "alert_type": "overvoltage",
    "message": "Voltage exceeded 250V",
    "severity": "warning"
  }'
```

## Database Schema

### power_readings
- `id`: Unique identifier
- `device_id`: Device identifier
- `voltage`: Voltage in volts
- `current`: Current in amperes
- `power`: Power in watts
- `energy`: Energy in watt-hours
- `frequency`: Frequency in Hz
- `power_factor`: Power factor (0-1)
- `timestamp`: Reading timestamp
- `created_at`: Record creation time

### devices
- `id`: Unique identifier
- `device_id`: Unique device identifier
- `name`: Device name
- `location`: Device location
- `is_active`: Active status
- `created_at`: Creation time
- `updated_at`: Last update time

### alerts
- `id`: Unique identifier
- `device_id`: Device identifier
- `alert_type`: Type of alert
- `message`: Alert message
- `severity`: Severity level (info, warning, critical)
- `is_resolved`: Resolution status
- `created_at`: Creation time

## Configuration

### Database
The SQLite database is stored in `electricity_monitor.db` in the project root. To use a different database, modify the `SQLALCHEMY_DATABASE_URL` in `database.py`.

### CORS
CORS is enabled for all origins. To restrict, modify the CORS middleware in `main.py`.

## Development

### Add a new endpoint
1. Add a new CRUD function in `crud.py`
2. Add request/response schemas in `schemas.py`
3. Add the endpoint in `main.py`

### Add a new model
1. Define the model in `models.py`
2. Create CRUD operations in `crud.py`
3. Add Pydantic schemas in `schemas.py`
4. Add endpoints in `main.py`

## API Response Examples

### Success Response
```json
{
  "id": 1,
  "device_id": "DEVICE001",
  "voltage": 230.5,
  "current": 15.3,
  "power": 3500,
  "energy": 87.5,
  "frequency": 50.0,
  "power_factor": 0.95,
  "timestamp": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00"
}
```

### Error Response
```json
{
  "detail": "Device not found"
}
```

## Troubleshooting

### Port already in use
```bash
python main.py --port 8001
```

### Database locked
Delete `electricity_monitor.db` and restart the server to reinitialize.

### Import errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## License

MIT License
