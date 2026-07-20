#!/bin/bash
# Start all services (FastAPI, Celery Worker, and Beat)

echo "Starting all services..."

# Start FastAPI server
echo "1. Starting FastAPI server on port 8000..."
python main.py &
API_PID=$!

# Start Celery Worker
echo "2. Starting Celery Worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 &
WORKER_PID=$!

# Start Celery Beat
echo "3. Starting Celery Beat Scheduler..."
celery -A celery_app beat --loglevel=info &
BEAT_PID=$!

echo ""
echo "═══════════════════════════════════════════════════════"
echo "All services started!"
echo "FastAPI:       http://localhost:8000"
echo "API PID:       $API_PID"
echo "Worker PID:    $WORKER_PID"
echo "Beat PID:      $BEAT_PID"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "To stop all services, press Ctrl+C"

# Wait for signals
trap "kill $API_PID $WORKER_PID $BEAT_PID 2>/dev/null" EXIT INT TERM

wait
