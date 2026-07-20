from celery.schedules import crontab
from celery_app import celery_app

# Celery Beat configuration for periodic tasks
celery_app.conf.beat_schedule = {
    # Broadcast power data every 5 seconds
    'broadcast-power-data-every-5s': {
        'task': 'tasks.broadcast_power_data',
        'schedule': 5.0,  # 5 seconds
    },
    # Generate alerts every 10 seconds
    'generate-alerts-every-10s': {
        'task': 'tasks.generate_alerts',
        'schedule': 10.0,  # 10 seconds
    },
}
