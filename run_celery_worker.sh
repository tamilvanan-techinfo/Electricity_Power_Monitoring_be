#!/bin/bash
# Start Celery Worker

echo "Starting Celery Worker..."
celery -A celery_app worker --loglevel=info --concurrency=4
