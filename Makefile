.PHONY: build up down test clean dev-up prod-up

# Build Docker images
build:
	docker-compose build

# Start all services (production mode)
up:
	docker-compose up --build

# Start in production mode with all services
prod-up:
	docker-compose --profile production up --build

# Start in development mode (SQLite, no worker/redis/postgres)
dev-up:
	docker-compose up web --build

# Stop all services
down:
	docker-compose down

# Run tests
test:
	USE_SQLITE=true python -m pytest tests/ -v

# Clean up Docker resources
clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Clean everything (including images)
clean-all:
	docker-compose down -v
	docker system prune -a -f --volumes
	docker builder prune -f

# Install dependencies locally
install:
	pip install -r requirements.txt

# Run locally in dev mode
dev-local:
	USE_SQLITE=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
