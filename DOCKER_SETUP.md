# Docker Setup Guide

## Quick Start

### Prerequisites
- Docker (version 20.10+)
- Docker Compose (version 1.29+)

### Installation

**Check if Docker is installed:**
```bash
docker --version
docker-compose --version
```

**Install Docker:**
- **Windows/Mac**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: `sudo apt-get install docker.io docker-compose`

## Usage

### Option 1: Automated Setup (Recommended)
```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

This will:
1. Build Docker images
2. Start all services
3. Display service URLs and useful commands

### Option 2: Manual Setup

**Build images:**
```bash
chmod +x docker-build.sh
./docker-build.sh
```

**Start services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop services:**
```bash
docker-compose down
```

### Option 3: Using Management Script
```bash
chmod +x docker-manage.sh

# Start services
./docker-manage.sh up

# View logs
./docker-manage.sh logs

# Check status
./docker-manage.sh status

# Restart services
./docker-manage.sh restart

# Stop and cleanup
./docker-manage.sh clean
```

## Architecture

### Services
1. **API** (FastAPI)
   - Port: 8000
   - Container: `electricity_monitoring_api`
   - Automatic reload on code changes (development)

2. **Redis** (Message Broker)
   - Port: 6379
   - Container: `electricity_monitoring_redis`
   - Persistent volume: `redis_data`

3. **Celery Worker**
   - Container: `electricity_monitoring_celery_worker`
   - Processes background tasks

4. **Celery Beat** (Scheduler)
   - Container: `electricity_monitoring_celery_beat`
   - Schedules periodic tasks

### Network
- Network: `power_monitoring_net`
- All containers communicate internally
- Only API (port 8000) and Redis (port 6379) exposed

## API Access

**After starting services:**
```
API:           http://localhost:8000
Swagger UI:    http://localhost:8000/docs
ReDoc:         http://localhost:8000/redoc
Health Check:  http://localhost:8000/health
```

## Testing

### WebSocket Connection
```bash
# Using Python test script
docker-compose exec api python test_background_tasks.py

# Using curl
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  ws://localhost:8000/ws/power-data
```

### API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Task status
curl http://localhost:8000/tasks/status

# Start power broadcast
curl -X POST http://localhost:8000/tasks/start-power-broadcast

# Stop power broadcast
curl -X POST http://localhost:8000/tasks/stop-power-broadcast
```

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Development image |
| `Dockerfile.prod` | Production-optimized image |
| `docker-compose.yml` | Orchestration configuration |
| `.dockerignore` | Exclude files from build |
| `docker-build.sh` | Build script |
| `docker-manage.sh` | Service management script |
| `docker-setup.sh` | Automated setup script |

## Development Workflow

### Local Code Changes
Code changes automatically reflect in the container due to volume mounting:
```yaml
volumes:
  - .:/app
```

### View Live Logs
```bash
docker-compose logs -f api
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
```

### Debug Mode
```bash
# Interactive shell in API container
docker-compose exec api bash

# Run Python commands
docker-compose exec api python
```

## Production Deployment

### Build Production Image
```bash
docker build -f Dockerfile.prod -t electricity-monitoring:prod .
```

### Push to Registry
```bash
docker tag electricity-monitoring:prod your-registry/electricity-monitoring:latest
docker push your-registry/electricity-monitoring:latest
```

### Security Improvements (Production)
- Use `Dockerfile.prod` (multi-stage, non-root user)
- Update image tags in `docker-compose.yml`
- Use environment variables for sensitive data
- Add authentication and HTTPS
- Use volume management for persistent data
- Set resource limits on containers

### Environment Variables (Production)
Create `.env` file:
```
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
PYTHONUNBUFFERED=1
```

Reference in `docker-compose.yml`:
```yaml
env_file:
  - .env
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
# From: "8000:8000"
# To:   "8001:8000"

docker-compose up -d
```

### Memory Issues
Increase Docker's memory limit:
- **Docker Desktop**: Preferences → Resources → Memory

### Logs Show Errors
```bash
# View specific service logs
docker-compose logs api
docker-compose logs redis
docker-compose logs celery_worker

# Follow logs in real-time
docker-compose logs -f
```

### Container Won't Start
```bash
# Check logs
docker-compose logs api

# Rebuild image
docker-compose build --no-cache

# Restart
docker-compose up -d
```

### Redis Connection Error
```bash
# Verify Redis is running
docker-compose ps

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## Performance

### Increase Concurrency
Edit `docker-compose.yml`:
```yaml
celery_worker:
  command: celery -A celery_app worker --loglevel=info --concurrency=8
```

### Resource Limits
Add to `docker-compose.yml` service:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 512M
    reservations:
      cpus: '1'
      memory: 256M
```

## Cleanup

### Remove Containers
```bash
docker-compose down
```

### Remove Images
```bash
docker rmi electricity-monitoring:latest electricity-monitoring:prod
```

### Remove Volumes
```bash
docker-compose down -v
```

### Complete Cleanup
```bash
./docker-manage.sh clean
```

## Next Steps

1. ✓ Docker setup complete
2. Start services: `./docker-setup.sh`
3. Test API: `curl http://localhost:8000/health`
4. Connect WebSocket: `ws://localhost:8000/ws/power-data`
5. View Swagger docs: `http://localhost:8000/docs`
6. Deploy to production (AWS/GCP/Azure/DigitalOcean)

---

**Version**: 1.0.0  
**Last Updated**: 2026-07-20
