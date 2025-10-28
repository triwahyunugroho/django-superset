#!/bin/bash

# Start script for Django + Superset Integration
# This script helps you start the application step by step

set -e

echo "🚀 Starting Django + Superset Integration"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and change passwords/secrets before continuing!"
    echo "   Then run this script again."
    exit 1
fi

echo "✅ .env file found"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Start services
echo ""
echo "🐳 Starting Docker containers..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo "   This may take a few minutes on first run..."

# Wait for PostgreSQL
echo "   - Waiting for PostgreSQL..."
until docker exec superset-postgres pg_isready -U superset > /dev/null 2>&1; do
    sleep 2
done
echo "   ✅ PostgreSQL is ready"

# Wait for Redis
echo "   - Waiting for Redis..."
until docker exec superset-redis redis-cli ping > /dev/null 2>&1; do
    sleep 2
done
echo "   ✅ Redis is ready"

# Wait for Superset
echo "   - Waiting for Superset (this takes longer)..."
sleep 30  # Give Superset time to initialize
until curl -sf http://localhost:8088/health > /dev/null 2>&1; do
    sleep 5
done
echo "   ✅ Superset is ready"

# Wait for Django
echo "   - Waiting for Django..."
until curl -sf http://localhost:8000 > /dev/null 2>&1; do
    sleep 2
done
echo "   ✅ Django is ready"

echo ""
echo "=========================================="
echo "✨ All services are ready!"
echo ""
echo "📊 Access Points:"
echo "   - Django (Public):  http://localhost"
echo "   - Superset (Admin): http://localhost:8088"
echo ""
echo "🔑 Default Credentials:"
echo "   Superset Admin:"
echo "   - Username: admin"
echo "   - Password: admin"
echo ""
echo "📝 Next Steps:"
echo "   1. Login to Superset: http://localhost:8088"
echo "   2. Create service account for Django:"
echo ""
echo "      docker exec -it superset bash"
echo "      superset fab create-user \\"
echo "        --username django_service \\"
echo "        --firstname Django \\"
echo "        --lastname Service \\"
echo "        --email service@example.com \\"
echo "        --password <password-from-.env> \\"
echo "        --role Admin"
echo "      exit"
echo ""
echo "   3. Create database connection and dashboards"
echo "   4. Make dashboards public (Published + Public role)"
echo "   5. Access public dashboards: http://localhost"
echo ""
echo "📚 Full documentation: README.md"
echo "=========================================="
