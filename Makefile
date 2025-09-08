# AI Interviewer Bot - Development Makefile
# Simplifies common Docker and development operations

.PHONY: help build test run dev clean deploy stop logs status

# Default target
help: ## Show this help message
	@echo "AI Interviewer Bot - Development Commands"
	@echo "========================================"
	@awk 'BEGIN {FS = ":.*##"}; /^[a-zA-Z_-]+:.*?##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Docker operations
build: ## Build production Docker image
	@echo "🐳 Building production Docker image..."
	docker build -f docker/Dockerfile -t ai-interviewer-bot:latest .

build-dev: ## Build development Docker image
	@echo "🐳 Building development Docker image..."
	docker build -f docker/Dockerfile --target builder -t ai-interviewer-bot:dev .

test: ## Run Docker build tests
	@echo "🧪 Running Docker configuration tests..."
	./scripts/deploy/test_docker_build.sh

test-unit: ## Run unit tests in container
	@echo "🧪 Running unit tests..."
	cd docker && docker-compose -f docker-compose.development.yml up --profile testing test-runner

run: ## Run production containers
	@echo "🚀 Starting production deployment..."
	cd docker && docker-compose up -d

dev: ## Start development environment
	@echo "🛠️  Starting development environment..."
	cd docker && docker-compose -f docker-compose.development.yml up -d --profile development

stop: ## Stop all containers
	@echo "🛑 Stopping containers..."
	cd docker && docker-compose down
	cd docker && docker-compose -f docker-compose.development.yml down

clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker system prune -f
	docker image prune -f
	docker volume prune -f

deploy: ## Deploy to production (with backups and health checks)
	@echo "🚀 Deploying to production..."
	./scripts/deploy/deploy_docker.sh

logs: ## View container logs
	@echo "📋 Viewing container logs..."
	cd docker && docker-compose logs -f

logs-dev: ## View development container logs
	@echo "📋 Viewing development container logs..."
	cd docker && docker-compose -f docker-compose.development.yml logs -f

status: ## Show container status
	@echo "📊 Container status:"
	@cd docker && docker-compose ps
	@echo ""
	@echo "📊 Development containers:"
	@cd docker && docker-compose -f docker-compose.development.yml ps

shell: ## Open shell in running container
	@echo "🐚 Opening shell in container..."
	docker exec -it ai-interviewer-bot bash

shell-dev: ## Open shell in development container
	@echo "🐚 Opening shell in development container..."
	docker exec -it ai-interviewer-bot-dev bash

# Development operations
install: ## Install package in development mode
	@echo "📦 Installing package in development mode..."
	pip install -e .

install-dev: ## Install with development dependencies
	@echo "📦 Installing with development dependencies..."
	pip install -e ".[dev]"

lint: ## Run code linting
	@echo "🔍 Running linters..."
	black --check src/
	flake8 src/

format: ## Format code
	@echo "✨ Formatting code..."
	black src/
	isort src/

# Environment setup
env: ## Create .env from template
	@if [ ! -f .env ]; then \
		echo "🔧 Creating .env from template..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env with your API keys"; \
	else \
		echo "✅ .env already exists"; \
	fi

check-env: ## Validate environment configuration
	@echo "🔍 Checking environment configuration..."
	@python -c "import os; from pathlib import Path; \
	env_file = Path('.env'); \
	if not env_file.exists(): exit('❌ .env file not found'); \
	required = ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY']; \
	content = env_file.read_text(); \
	missing = [var for var in required if f'{var}=' not in content or f'{var}=$$' in content]; \
	exit(f'❌ Missing/empty: {missing}' if missing else '✅ Environment configured')"

# Monitoring
stats: ## Show resource usage
	@echo "📊 Resource usage:"
	docker stats --no-stream

health: ## Check container health
	@echo "🏥 Container health status:"
	@docker inspect --format='{{.State.Health.Status}}' ai-interviewer-bot 2>/dev/null || echo "Container not running"

# Quick start
setup: env build ## Initial project setup
	@echo "🎉 Project setup complete!"
	@echo "Next steps:"
	@echo "  1. Edit .env with your API keys"
	@echo "  2. Run 'make run' to start the bot"

# All-in-one commands
start: env build run ## Complete startup (setup + build + run)
	@echo "🎉 Bot is now running!"
	@echo "Monitor with: make logs"

restart: stop run ## Restart containers
	@echo "🔄 Restart complete"

# Backup operations
backup: ## Create data backup
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker run --rm -v ai-interviewer-bot_sessions:/source -v $$(pwd)/backups:/backup alpine \
		tar czf /backup/sessions_$$timestamp.tar.gz -C /source . || true; \
	cp .env backups/.env_$$timestamp 2>/dev/null || true; \
	echo "✅ Backup created with timestamp: $$timestamp"