#!/bin/bash
# Quick Docker Run Script for Development

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   Electricity Power Monitoring - Docker Setup        ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Make scripts executable
chmod +x docker-build.sh docker-manage.sh

# Build images
echo "Step 1: Building Docker images..."
./docker-build.sh

echo ""
echo "Step 2: Starting services with docker-compose..."
sleep 2

# Start services
docker-compose up -d

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✓ Setup Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Services:"
echo "  API:           http://localhost:8000"
echo "  Swagger Docs:  http://localhost:8000/docs"
echo "  ReDoc:         http://localhost:8000/redoc"
echo "  Redis:         localhost:6379"
echo ""
echo "Containers:"
docker-compose ps
echo ""
echo "Useful commands:"
echo "  ./docker-manage.sh logs          - View logs"
echo "  ./docker-manage.sh down          - Stop services"
echo "  ./docker-manage.sh restart       - Restart services"
echo "  ./docker-manage.sh clean         - Remove everything"
echo ""
echo "Test API Health:"
echo "  curl http://localhost:8000/health"
echo ""
