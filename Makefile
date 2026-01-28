# ===========================================
# Randol's Marketing Platform - Makefile
# Common development and deployment commands
# Cross-platform support (Unix/Windows)
# ===========================================

.PHONY: help install dev build test lint clean docker-up docker-down deploy

# Detect OS
ifeq ($(OS),Windows_NT)
    SHELL := powershell.exe
    .SHELLFLAGS := -NoProfile -Command
    ACTIVATE_BACKEND = backend\venv\Scripts\activate.ps1;
    PYTHON = python
    RM = Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    MKDIR = New-Item -ItemType Directory -Force -Path
    SEP = \\
else
    SHELL := /bin/bash
    ACTIVATE_BACKEND = . backend/venv/bin/activate &&
    PYTHON = python3
    RM = rm -rf
    MKDIR = mkdir -p
    SEP = /
endif

# Default target
help:
	@echo "Randol's Marketing Platform - Available Commands"
	@echo "================================================"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Start development servers"
	@echo "  make dev-backend  - Start backend only"
	@echo "  make dev-frontend - Start frontend only"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-backend - Run backend tests"
	@echo "  make test-frontend- Run frontend tests"
	@echo "  make coverage     - Run tests with coverage"
	@echo ""
	@echo "Linting:"
	@echo "  make lint         - Run all linters"
	@echo "  make format       - Format all code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services with Docker"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make docker-build - Rebuild Docker images"
	@echo ""
	@echo "Database:"
	@echo "  make db-init      - Initialize database"
	@echo "  make db-seed      - Seed with sample data"
	@echo ""
	@echo "Production:"
	@echo "  make build        - Build for production"
	@echo "  make deploy       - Deploy to production"
	@echo ""

# ===========================================
# Installation
# ===========================================

install: install-backend install-frontend
	@echo "All dependencies installed"

install-backend:
	@echo "Installing backend dependencies..."
ifeq ($(OS),Windows_NT)
	cd backend && $(PYTHON) -m venv venv && \
		.\venv\Scripts\activate.ps1 && \
		$(PYTHON) -m pip install --upgrade pip && \
		pip install -r requirements.txt
else
	cd backend && $(PYTHON) -m venv venv && \
		. venv/bin/activate && \
		$(PYTHON) -m pip install --upgrade pip && \
		pip install -r requirements.txt
endif
	@echo "Backend dependencies installed"

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Frontend dependencies installed"

# ===========================================
# Development
# ===========================================

dev:
	@echo "Starting development servers..."
ifeq ($(OS),Windows_NT)
	Start-Process -NoNewWindow -FilePath "make" -ArgumentList "dev-backend" ; \
	Start-Process -NoNewWindow -FilePath "make" -ArgumentList "dev-frontend"
else
	make -j2 dev-backend dev-frontend
endif

dev-backend:
	@echo "Starting backend server..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && $(PYTHON) main.py
else
	cd backend && . venv/bin/activate && $(PYTHON) main.py
endif

dev-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

# ===========================================
# Testing
# ===========================================

test: test-backend test-frontend
	@echo "All tests completed"

test-backend:
	@echo "Running backend tests..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && pytest tests/ -v
else
	cd backend && . venv/bin/activate && pytest tests/ -v
endif

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

coverage:
	@echo "Running tests with coverage..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && pytest tests/ --cov=. --cov-report=html
else
	cd backend && . venv/bin/activate && pytest tests/ --cov=. --cov-report=html
endif
	cd frontend && npm run test:coverage

# ===========================================
# Linting & Formatting
# ===========================================

lint: lint-backend lint-frontend
	@echo "Linting completed"

lint-backend:
	@echo "Linting backend..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && \
		flake8 . && \
		black --check . && \
		isort --check-only .
else
	cd backend && . venv/bin/activate && \
		flake8 . && \
		black --check . && \
		isort --check-only .
endif

lint-frontend:
	@echo "Linting frontend..."
	cd frontend && npm run lint

format: format-backend format-frontend
	@echo "Formatting completed"

format-backend:
	@echo "Formatting backend..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && \
		black . && \
		isort .
else
	cd backend && . venv/bin/activate && \
		black . && \
		isort .
endif

format-frontend:
	@echo "Formatting frontend..."
	cd frontend && npm run format

# ===========================================
# Docker
# ===========================================

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Services started"
	@echo "   Backend:  http://localhost:5000"
	@echo "   Frontend: http://localhost:3000"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	@echo "Building Docker images..."
	docker-compose build --no-cache

docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v --rmi local
	docker system prune -f

# ===========================================
# Database
# ===========================================

db-init:
	@echo "Initializing database..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && $(PYTHON) scripts/init_db.py
else
	cd backend && . venv/bin/activate && $(PYTHON) scripts/init_db.py
endif

db-seed:
	@echo "Seeding database with sample data..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && $(PYTHON) scripts/init_db.py --samples
else
	cd backend && . venv/bin/activate && $(PYTHON) scripts/init_db.py --samples
endif

db-validate:
	@echo "Validating environment configuration..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && $(PYTHON) utils/env_validation.py --show-config
else
	cd backend && . venv/bin/activate && $(PYTHON) utils/env_validation.py --show-config
endif

# ===========================================
# Production Build
# ===========================================

build: build-backend build-frontend
	@echo "Production build completed"

build-backend:
	@echo "Building backend..."
	cd backend && docker build -t randols-backend .

build-frontend:
	@echo "Building frontend..."
	cd frontend && npm run build

# ===========================================
# Deployment
# ===========================================

deploy:
	@echo "Deploying to production..."
	@echo "Please use CI/CD pipeline for production deployments"
	@echo "Push to main branch to trigger automatic deployment"

deploy-staging:
	@echo "Deploying to staging..."
	git push origin develop

# ===========================================
# Cleanup
# ===========================================

clean:
	@echo "Cleaning up..."
ifeq ($(OS),Windows_NT)
	$(RM) backend\__pycache__
	$(RM) backend\.pytest_cache
	$(RM) backend\htmlcov
	$(RM) backend\.coverage
	$(RM) frontend\.next
	$(RM) frontend\node_modules\.cache
else
	$(RM) backend/__pycache__
	$(RM) backend/.pytest_cache
	$(RM) backend/htmlcov
	$(RM) backend/.coverage
	$(RM) frontend/.next
	$(RM) frontend/node_modules/.cache
endif
	@echo "Cleanup completed"

# ===========================================
# Health Checks
# ===========================================

health:
	@echo "Checking service health..."
ifeq ($(OS),Windows_NT)
	Invoke-RestMethod -Uri http://localhost:5000/api/v1/health -Method Get | ConvertTo-Json
	Invoke-RestMethod -Uri http://localhost:3000 -Method Get -ErrorAction SilentlyContinue && echo "Frontend: OK" || echo "Frontend not running"
else
	@curl -s http://localhost:5000/api/v1/health | python -m json.tool || echo "Backend not running"
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend: OK" || echo "Frontend not running"
endif

status:
	@echo "Service status..."
ifeq ($(OS),Windows_NT)
	Invoke-RestMethod -Uri http://localhost:5000/api/v1/status -Method Get | ConvertTo-Json
else
	@curl -s http://localhost:5000/api/v1/status | python -m json.tool || echo "Backend not running"
endif

# ===========================================
# Environment Validation
# ===========================================

validate-env:
	@echo "Validating environment variables..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && $(PYTHON) -c "from utils.env_validation import validate_environment; validate_environment()"
else
	cd backend && . venv/bin/activate && $(PYTHON) -c "from utils.env_validation import validate_environment; validate_environment()"
endif

# ===========================================
# LLM Stats
# ===========================================

llm-stats:
	@echo "Getting LLM usage statistics..."
ifeq ($(OS),Windows_NT)
	cd backend && .\venv\Scripts\activate.ps1 && $(PYTHON) -c "from utils.llm_client import get_llm_client; print(get_llm_client().get_stats())"
else
	cd backend && . venv/bin/activate && $(PYTHON) -c "from utils.llm_client import get_llm_client; print(get_llm_client().get_stats())"
endif
