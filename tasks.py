import random
from datetime import datetime
from celery_app import celery_app

# Sample power data generator
def generate_power_data():
    """Generate realistic power data"""
    return {
        "device_id": f"sensor_{random.randint(1, 5):03d}",
        "voltage": round(random.uniform(220, 250), 2),
        "current": round(random.uniform(5, 30), 2),
        "power": round(random.uniform(1000, 8000), 2),
        "frequency": round(random.uniform(49.9, 50.1), 2),
        "power_factor": round(random.uniform(0.8, 1.0), 2),
        "timestamp": datetime.now().isoformat()
    }

@celery_app.task(name="tasks.broadcast_power_data")
def broadcast_power_data():
    """
    Background task that broadcasts power data to all connected WebSocket clients
    Runs every 5 seconds
    """
    try:
        # Import here to avoid circular imports
        from main import ws_manager
        import asyncio
        
        # Generate sample data
        power_data = generate_power_data()
        
        # Create async task to broadcast
        async def async_broadcast():
            await ws_manager.broadcast_power_data(power_data)
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_broadcast())
        loop.close()
        
        print(f"✓ Power data broadcasted: {power_data}")
        return {"status": "success", "data": power_data}
        
    except Exception as e:
        print(f"✗ Error broadcasting power data: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="tasks.generate_alerts")
def generate_alerts():
    """
    Background task that generates and broadcasts power alerts
    Runs when thresholds are exceeded
    """
    try:
        from main import ws_manager
        import asyncio
        
        # Generate random alert (20% chance)
        if random.random() < 0.2:
            alert_data = {
                "alert_type": random.choice(["overvoltage", "undervoltage", "overcurrent", "low_power_factor"]),
                "device_id": f"sensor_{random.randint(1, 5):03d}",
                "value": round(random.uniform(100, 300), 2),
                "severity": random.choice(["warning", "critical"]),
                "message": "Power anomaly detected"
            }
            
            async def async_broadcast_alert():
                await ws_manager.broadcast_alert(alert_data)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_broadcast_alert())
            loop.close()
            
            print(f"✓ Alert broadcasted: {alert_data}")
            return {"status": "success", "alert": alert_data}
        
        return {"status": "no_alert"}
        
    except Exception as e:
        print(f"✗ Error generating alert: {e}")
        return {"status": "error", "message": str(e)}
