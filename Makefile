.PHONY: help build up down restart logs shell-django shell-superset migrate makemigrations loaddata createsuperuser clean test

help:
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-django    - View Django logs"
	@echo "  make logs-superset  - View Superset logs"
	@echo "  make shell-django   - Open Django shell"
	@echo "  make shell-superset - Open Superset shell"
	@echo "  make bash-django    - Open bash in Django container"
	@echo "  make bash-superset  - Open bash in Superset container"
	@echo "  make migrate        - Run Django migrations"
	@echo "  make makemigrations - Create Django migrations"
	@echo "  make loaddata       - Load dummy data"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make clean          - Stop and remove all containers, volumes"
	@echo "  make test           - Run tests"
	@echo "  make setup          - Run initial setup"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-django:
	docker compose logs -f django

logs-superset:
	docker compose logs -f superset

logs-postgres:
	docker compose logs -f postgres

shell-django:
	docker compose exec django python manage.py shell

shell-superset:
	docker compose exec superset superset shell

bash-django:
	docker compose exec django bash

bash-superset:
	docker compose exec superset bash

migrate:
	docker compose exec django python manage.py migrate

makemigrations:
	docker compose exec django python manage.py makemigrations

loaddata:
	docker compose exec django python manage.py load_dummy_data

createsuperuser:
	docker compose exec django python manage.py createsuperuser

collectstatic:
	docker compose exec django python manage.py collectstatic --noinput

clean:
	docker compose down -v
	@echo "All containers and volumes removed"

test:
	docker compose exec django python manage.py test

setup:
	@chmod +x setup.sh
	@./setup.sh

# Database operations
db-backup:
	docker compose exec postgres pg_dump -U superset_user superset_db > backup_$$(date +%Y%m%d_%H%M%S).sql

db-restore:
	@read -p "Enter backup file name: " file; \
	docker compose exec -T postgres psql -U superset_user superset_db < $$file

# Quick restart services
restart-django:
	docker compose restart django

restart-superset:
	docker compose restart superset

restart-caddy:
	docker compose restart caddy

# Development helpers
check-health:
	@echo "Checking services health..."
	@docker compose ps

install-deps:
	docker compose exec django pip install -r requirements.txt

freeze-deps:
	docker compose exec django pip freeze > django/requirements.txt
