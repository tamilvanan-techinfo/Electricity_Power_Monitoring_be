from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import asyncio
import logging
from services.websocket import ConnectionManager
from services.background_tasks import BackgroundTaskManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Electricity Power Monitoring API",
    description="API for monitoring electricity power consumption",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
ws_manager = ConnectionManager()
bg_task_manager = BackgroundTaskManager(ws_manager)

# ============== Health Check ==============

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "Electricity Power Monitoring API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """API health check"""
    return {"status": "healthy"}

# ============== Startup Events ==============

@app.on_event("startup")
async def startup_event():
    """Start background tasks when server starts"""
    await bg_task_manager.start()
    logger.info("✓ Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks when server shuts down"""
    await bg_task_manager.stop()
    logger.info("✓ Application shutdown complete")

# ============== Task Control Endpoints ==============

@app.post("/tasks/start-power-broadcast")
async def start_power_broadcast():
    """Start broadcasting power data every 5 seconds"""
    try:
        await bg_task_manager.start()
        return {
            "status": "started",
            "message": "Power data broadcast task started",
            "interval": "5 seconds"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/stop-power-broadcast")
async def stop_power_broadcast():
    """Stop broadcasting power data"""
    try:
        await bg_task_manager.stop()
        return {
            "status": "stopped",
            "message": "Power data broadcast task stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/status")
async def task_status():
    """Get status of background tasks"""
    return {
        "power_broadcast": "running" if bg_task_manager.is_running else "stopped",
        "total_connections": ws_manager.get_connection_count(),
        "broadcast_interval": "5 seconds",
        "alert_interval": "10 seconds (random)"
    }

# ============== WebSocket Endpoints ==============

@app.websocket("/ws/power-data")
async def websocket_power_data(websocket: WebSocket):
    """WebSocket endpoint for real-time power data streaming"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast power data to all connected clients
            await ws_manager.broadcast_power_data(data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error in /ws/power-data: {e}")
        ws_manager.disconnect(websocket)


@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket endpoint for system notifications"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            severity = data.get("severity", "info")
            await ws_manager.broadcast_notification(message, severity)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error in /ws/notifications: {e}")
        ws_manager.disconnect(websocket)


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for power alerts and warnings"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.broadcast_alert(data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error in /ws/alerts: {e}")
        ws_manager.disconnect(websocket)


# ============== Power Reading Endpoints ==============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)