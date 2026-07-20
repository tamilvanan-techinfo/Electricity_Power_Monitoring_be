import asyncio
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manage background tasks for power data broadcasting"""
    
    def __init__(self, ws_manager):
        self.ws_manager = ws_manager
        self.is_running = False
        self.task = None
        
    async def start(self):
        """Start background tasks"""
        if self.is_running:
            logger.warning("Background tasks already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._broadcast_loop())
        logger.info("✓ Background power data broadcast started")
        
    async def stop(self):
        """Stop background tasks"""
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.is_running = False
        logger.info("✗ Background power data broadcast stopped")
        
    async def _broadcast_loop(self):
        """Loop that broadcasts power data every 5 seconds"""
        try:
            while self.is_running:
                await asyncio.sleep(5)  # Wait 5 seconds
                await self._send_power_data()
                
                # Send alerts every 10 seconds (alternate)
                if random.random() < 0.2:
                    await self._send_alert()
                    
        except asyncio.CancelledError:
            logger.info("Background task cancelled")
        except Exception as e:
            logger.error(f"Error in broadcast loop: {e}")
            
    async def _send_power_data(self):
        """Generate and send power data to all clients"""
        try:
            power_data = {
                "device_id": f"sensor_{random.randint(1, 5):03d}",
                "voltage": round(random.uniform(220, 250), 2),
                "current": round(random.uniform(5, 30), 2),
                "power": round(random.uniform(1000, 8000), 2),
                "frequency": round(random.uniform(49.9, 50.1), 2),
                "power_factor": round(random.uniform(0.8, 1.0), 2),
            }
            
            await self.ws_manager.broadcast_power_data(power_data)
            logger.debug(f"✓ Power data sent: {power_data}")
            
        except Exception as e:
            logger.error(f"Error sending power data: {e}")
            
    async def _send_alert(self):
        """Generate and send power alert"""
        try:
            alert_data = {
                "alert_type": random.choice(["overvoltage", "undervoltage", "overcurrent", "low_power_factor"]),
                "device_id": f"sensor_{random.randint(1, 5):03d}",
                "value": round(random.uniform(100, 300), 2),
                "severity": random.choice(["warning", "critical"]),
                "message": "Power anomaly detected"
            }
            
            await self.ws_manager.broadcast_alert(alert_data)
            logger.info(f"⚠ Alert sent: {alert_data['alert_type']}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
