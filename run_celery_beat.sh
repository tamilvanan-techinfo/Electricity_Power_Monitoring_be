#!/bin/bash
# Start Celery Beat Scheduler

echo "Starting Celery Beat Scheduler..."
celery -A celery_app beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
