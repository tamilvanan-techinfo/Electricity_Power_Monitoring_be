from fastapi import WebSocket
from typing import Set
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time power monitoring"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: dict = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        if client_id:
            self.connection_metadata[id(websocket)] = {"client_id": client_id}
        print(f"✓ Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        if id(websocket) in self.connection_metadata:
            del self.connection_metadata[id(websocket)]
        print(f"✗ Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict, exclude_sender: WebSocket = None):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            # Skip sender if specified
            if exclude_sender and connection == exclude_sender:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending message: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast_power_data(self, power_data: dict):
        """Broadcast real-time power data to all clients"""
        message = {
            "type": "power_data",
            "data": power_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_notification(self, notification: str, severity: str = "info"):
        """Broadcast system notification to all clients"""
        message = {
            "type": "notification",
            "message": notification,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_alert(self, alert_data: dict):
        """Broadcast alert/warning to all clients"""
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)

    def get_all_connections(self) -> Set[WebSocket]:
        """Get all active WebSocket connections"""
        return self.active_connections.copy()
