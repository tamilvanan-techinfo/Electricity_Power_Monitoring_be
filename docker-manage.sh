#!/bin/bash
# Docker Compose Management Script

set -e

usage() {
    echo "Usage: $0 {up|down|restart|logs|status|ps|clean}"
    echo ""
    echo "Commands:"
    echo "  up        - Start all services"
    echo "  down      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  logs      - View logs from all services"
    echo "  status    - Show status of services"
    echo "  ps        - List running containers"
    echo "  clean     - Stop and remove all containers, volumes, and networks"
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

case "$1" in
    up)
        echo "🚀 Starting all services..."
        docker-compose up -d
        echo ""
        echo "✓ Services started!"
        echo ""
        echo "API:       http://localhost:8000"
        echo "Docs:      http://localhost:8000/docs"
        echo "Redis:     localhost:6379"
        echo ""
        docker-compose ps
        ;;
    
    down)
        echo "🛑 Stopping all services..."
        docker-compose down
        echo "✓ All services stopped"
        ;;
    
    restart)
        echo "🔄 Restarting all services..."
        docker-compose restart
        echo "✓ All services restarted"
        docker-compose ps
        ;;
    
    logs)
        if [ -z "$2" ]; then
            docker-compose logs -f
        else
            docker-compose logs -f $2
        fi
        ;;
    
    status)
        echo "Service Status:"
        docker-compose ps
        ;;
    
    ps)
        docker-compose ps
        ;;
    
    clean)
        echo "⚠️  WARNING: This will remove all containers, volumes, and networks"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "Cleaning up..."
            docker-compose down -v
            echo "✓ Cleanup complete"
        else
            echo "Cancelled"
        fi
        ;;
    
    *)
        usage
        ;;
esac
