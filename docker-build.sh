#!/bin/bash
# Docker Build Script

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   Building Electricity Power Monitoring Container    ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "✗ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "1. Building Docker image..."
docker build -t electricity-monitoring:latest .

echo ""
echo "2. Building production image..."
docker build -f Dockerfile.prod -t electricity-monitoring:prod .

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✓ Images built successfully!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Available images:"
docker images | grep electricity-monitoring
echo ""
echo "To run with docker-compose:"
echo "  docker-compose up -d"
echo ""
echo "To run single container:"
echo "  docker run -p 8000:8000 electricity-monitoring:latest"
