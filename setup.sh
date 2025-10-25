#!/bin/bash

# Setup script untuk Superset-Django Integration
# Author: Generated with Claude Code

set -e

echo "========================================="
echo "Superset Django Integration - Setup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Generate Fernet Encryption Key${NC}"
echo "Generating encryption key for django-superset-integration..."

FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

if [ -z "$FERNET_KEY" ]; then
    echo -e "${RED}Failed to generate Fernet key. Make sure cryptography package is installed:${NC}"
    echo "  pip install cryptography"
    exit 1
fi

echo "Generated FERNET_KEY: $FERNET_KEY"
echo ""

# Create .env file if not exists
if [ ! -f .env ]; then
    echo -e "${GREEN}Step 2: Creating .env file${NC}"
    cat > .env <<EOF
# PostgreSQL Configuration
POSTGRES_DB=superset_db
POSTGRES_USER=superset_user
POSTGRES_PASSWORD=superset_password

# Django Configuration
DJANGO_SECRET_KEY=django-secret-key-$(openssl rand -hex 32)
DEBUG=True

# Superset Configuration
SUPERSET_SECRET_KEY=superset-secret-key-$(openssl rand -hex 32)
SUPERSET_ADMIN_USERNAME=admin
SUPERSET_ADMIN_PASSWORD=admin

# Django Superset Integration
FERNET_KEY=$FERNET_KEY
EOF
    echo -e "${GREEN}.env file created!${NC}"
else
    echo -e "${YELLOW}.env file already exists, skipping...${NC}"
fi

echo ""
echo -e "${GREEN}Step 3: Building Docker images${NC}"
docker compose build

echo ""
echo -e "${GREEN}Step 4: Starting services${NC}"
docker compose up -d postgres redis

echo "Waiting for PostgreSQL to be ready..."
sleep 10

echo ""
echo -e "${GREEN}Step 5: Starting Django and Superset${NC}"
docker compose up -d django superset

echo "Waiting for services to be ready..."
sleep 15

echo ""
echo -e "${GREEN}Step 6: Running Django migrations${NC}"
docker compose exec -T django python manage.py migrate

echo ""
echo -e "${GREEN}Step 7: Loading dummy data${NC}"
docker compose exec -T django python manage.py load_dummy_data

echo ""
echo -e "${GREEN}Step 8: Creating Django superuser${NC}"
echo "Please enter superuser details:"
docker compose exec django python manage.py createsuperuser

echo ""
echo -e "${GREEN}Step 9: Starting Caddy reverse proxy${NC}"
docker compose up -d caddy

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Services are running:"
echo "  - Django App:        http://localhost"
echo "  - Django Admin:      http://localhost/admin"
echo "  - Apache Superset:   http://localhost/superset"
echo "  - Dashboard:         http://localhost/dashboard"
echo ""
echo "Default credentials:"
echo "  - Superset: admin / admin"
echo "  - Django: (superuser yang baru dibuat)"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost/superset and login"
echo "  2. Create database connection to PostgreSQL"
echo "  3. Create datasets from tables"
echo "  4. Create charts and dashboard"
echo "  5. Setup SupersetInstance and SupersetDashboard in Django Admin"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
echo ""
