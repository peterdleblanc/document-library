#!/bin/bash

# Document Library - Startup Script
# This script starts all Docker containers and provides helpful information

set -e

echo "================================================"
echo "  Document Library - Starting Services"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found, creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
fi

echo "🚀 Starting all containers..."
echo ""

# Start containers
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

# Wait a bit for health checks
sleep 5

# Check container status
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "================================================"
echo "  Services Started Successfully! 🎉"
echo "================================================"
echo ""
echo "Access your application at:"
echo ""
echo "  🌐 Main Application:    http://localhost:8080"
echo "  📚 API Documentation:   http://localhost:8080/docs"
echo "  💾 MinIO Console:       http://localhost:9001"
echo "  🔍 Meilisearch:         http://localhost:7700"
echo ""
echo "Direct service access (for development):"
echo "  - Backend API:          http://localhost:8800"
echo "  - Frontend:             http://localhost:8173"
echo "  - PostgreSQL:           localhost:5433"
echo "  - Redis:                localhost:6380"
echo ""
echo "================================================"
echo "  Next Steps"
echo "================================================"
echo ""
echo "1. Run database migrations:"
echo "   docker-compose exec backend alembic upgrade head"
echo ""
echo "2. Create your first user at:"
echo "   http://localhost:8080"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "4. Stop all services:"
echo "   docker-compose down"
echo ""
echo "================================================"
