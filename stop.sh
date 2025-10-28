#!/bin/bash

# Stop script for Django + Superset Integration

echo "🛑 Stopping Django + Superset Integration"
echo "=========================================="

docker compose stop

echo ""
echo "✅ All services stopped"
echo ""
echo "To start again: ./start.sh"
echo "To remove containers: docker compose down"
echo "To remove all data: docker compose down -v"
