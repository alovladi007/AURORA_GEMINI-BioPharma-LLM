.PHONY: help init dev build up down logs clean test lint format test-backend test-frontend install-backend install-frontend db-migrate db-upgrade db-downgrade

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Pharma AI Platform - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

init: ## Initialize project (first-time setup)
	@echo "$(BLUE)Initializing Pharma AI Platform...$(NC)"
	@cp -n .env.example .env 2>/dev/null || echo ".env already exists"
	@echo "$(GREEN)✓ Environment file ready$(NC)"
	@docker-compose build
	@echo "$(GREEN)✓ Docker images built$(NC)"
	@echo "$(YELLOW)Run 'make dev' to start the platform$(NC)"

dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	@docker-compose up

dev-build: ## Rebuild and start development environment
	@echo "$(BLUE)Rebuilding and starting development environment...$(NC)"
	@docker-compose up --build

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker-compose build

up: ## Start all services in background
	@echo "$(BLUE)Starting all services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting all services...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs: ## View logs from all services
	@docker-compose logs -f

logs-backend: ## View backend logs only
	@docker-compose logs -f backend

logs-frontend: ## View frontend logs only
	@docker-compose logs -f frontend

logs-db: ## View database logs only
	@docker-compose logs -f db

clean: ## Clean build artifacts and containers
	@echo "$(BLUE)Cleaning up...$(NC)"
	@docker-compose down -v --remove-orphans
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Testing
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	@docker-compose exec backend pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@docker-compose exec frontend npm test

test-watch: ## Run backend tests in watch mode
	@docker-compose exec backend pytest tests/ -v --cov=app -f

# Linting and formatting
lint: lint-backend lint-frontend ## Lint all code

lint-backend: ## Lint backend code
	@echo "$(BLUE)Linting backend...$(NC)"
	@docker-compose exec backend ruff check app/
	@docker-compose exec backend mypy app/

lint-frontend: ## Lint frontend code
	@echo "$(BLUE)Linting frontend...$(NC)"
	@docker-compose exec frontend npm run lint

format: format-backend format-frontend ## Format all code

format-backend: ## Format backend code
	@echo "$(BLUE)Formatting backend...$(NC)"
	@docker-compose exec backend ruff format app/
	@docker-compose exec backend ruff check --fix app/

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend...$(NC)"
	@docker-compose exec frontend npm run format

# Database operations
db-migrate: ## Create a new database migration
	@echo "$(BLUE)Creating new migration...$(NC)"
	@docker-compose exec backend alembic revision --autogenerate -m "$(message)"

db-upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying migrations...$(NC)"
	@docker-compose exec backend alembic upgrade head

db-downgrade: ## Rollback last migration
	@echo "$(BLUE)Rolling back migration...$(NC)"
	@docker-compose exec backend alembic downgrade -1

db-current: ## Show current migration version
	@echo "$(BLUE)Current migration version:$(NC)"
	@docker-compose exec backend alembic current

db-history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	@docker-compose exec backend alembic history

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠️  WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d db; \
		sleep 5; \
		docker-compose exec backend alembic upgrade head; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	fi

db-shell: ## Open PostgreSQL shell
	@docker-compose exec db psql -U pharma_user -d pharma_db

# Installation (local development without Docker)
install-backend: ## Install backend dependencies locally
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	@cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies locally
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install

# Shell access
shell-backend: ## Open shell in backend container
	@docker-compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	@docker-compose exec frontend /bin/sh

shell-db: ## Open shell in database container
	@docker-compose exec db /bin/bash

# Training and ML
train-drug-design: ## Train drug design models
	@echo "$(BLUE)Training drug design models...$(NC)"
	@docker-compose exec backend python -m app.ml.drug_design.train

train-safety: ## Train safety prediction models
	@echo "$(BLUE)Training safety models...$(NC)"
	@docker-compose exec backend python -m app.ml.safety.train

train-clinical: ## Train clinical trial models
	@echo "$(BLUE)Training clinical trial models...$(NC)"
	@docker-compose exec backend python -m app.ml.clinical_trials.train

train-repurposing: ## Train repurposing models
	@echo "$(BLUE)Training repurposing models...$(NC)"
	@docker-compose exec backend python -m app.ml.repurposing.train

# Monitoring
status: ## Show status of all services
	@docker-compose ps

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -s http://localhost:8000/api/v1/health | jq . || echo "Backend not responding"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)✓ Frontend is healthy$(NC)" || echo "$(RED)✗ Frontend not responding$(NC)"

# Production
prod-build: ## Build production images
	@echo "$(BLUE)Building production images...$(NC)"
	@docker-compose -f docker-compose.prod.yml build

prod-up: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	@docker-compose -f docker-compose.prod.yml up -d

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@cd backend && pdoc --html --output-dir ../docs/api app

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8080$(NC)"
	@cd docs && python -m http.server 8080
