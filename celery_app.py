from celery import Celery
import os

# Try Redis first, fall back to in-memory if not available
try:
    # Redis URL for message broker
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    broker_type = "redis"
except:
    # Fallback to memory broker for development
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"
    broker_type = "memory"

# Create Celery app
celery_app = Celery(
    "electricity_monitoring",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
)

print(f"✓ Celery configured with {broker_type} broker")
