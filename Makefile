# Makefile for SIP Algorithmic Trading System

# Default target (runs when you type just 'make')
.DEFAULT_GOAL := help

# Variables
PYTHON := python
PIP := pip
VENV := venv
SOURCE_DIR := .

# Help target - shows available commands
.PHONY: help
help:
	@echo "SIP Algorithmic Trading System"
	@echo "=============================="
	@echo "Available commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup         Create virtual environment and install dependencies"
	@echo "  make install       Install package in production mode"
	@echo "  make install-dev   Install package in development mode"
	@echo "  make clean         Clean build artifacts and cache"
	@echo ""
	@echo "Development:"
	@echo "  make test          Run test suite"
	@echo "  make test-watch    Run tests in watch mode"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black and isort"
	@echo "  make type-check    Run type checking with mypy"
	@echo ""
	@echo "Running:"
	@echo "  make run           Run the main trading system"
	@echo "  make run-api       Start the web API server"
	@echo "  make run-scheduler Start the SIP scheduler"
	@echo "  make run-tests     Run the test system"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run with Docker Compose"
	@echo "  make docker-stop   Stop Docker containers"

# Setup and Installation
.PHONY: setup
setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e .[dev]
	@echo "Setup complete! Activate with: source $(VENV)/bin/activate"

.PHONY: install
install:
	$(PIP) install .

.PHONY: install-dev
install-dev:
	$(PIP) install -e .[dev]

.PHONY: install-all
install-all:
	$(PIP) install -e .[all]

# Development Tasks
.PHONY: test
test:
	pytest tests/ -v --cov=$(SOURCE_DIR) --cov-report=html --cov-report=term

.PHONY: test-watch
test-watch:
	pytest-watch tests/ -v

.PHONY: lint
lint:
	@echo "Running flake8..."
	flake8 $(SOURCE_DIR)
	@echo "Running black check..."
	black --check $(SOURCE_DIR)
	@echo "Running isort check..."
	isort --check-only $(SOURCE_DIR)
	@echo "All linting checks passed!"

.PHONY: format
format:
	@echo "Formatting with black..."
	black $(SOURCE_DIR)
	@echo "Sorting imports with isort..."
	isort $(SOURCE_DIR)
	@echo "Code formatted successfully!"

.PHONY: type-check
type-check:
	mypy $(SOURCE_DIR)

# Running the Application
.PHONY: run
run:
	$(PYTHON) main.py

.PHONY: run-api
run-api:
	uvicorn web_api:app --reload --host 0.0.0.0 --port 8000

.PHONY: run-scheduler
run-scheduler:
	$(PYTHON) scheduler.py

.PHONY: run-tests
run-tests:
	$(PYTHON) test_system.py

# Cleaning
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name "*.orig" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	@echo "Cleaned successfully!"

# Database operations
.PHONY: db-reset
db-reset:
	rm -f trading_data.db
	$(PYTHON) -c "from data.storage import DatabaseManager; DatabaseManager().init_database()"
	@echo "Database reset complete!"

# Docker operations
.PHONY: docker-build
docker-build:
	docker build -t sip-algo-trading .

.PHONY: docker-run
docker-run:
	docker-compose up -d

.PHONY: docker-stop
docker-stop:
	docker-compose down

.PHONY: docker-logs
docker-logs:
	docker-compose logs -f

# Backup operations
.PHONY: backup
backup:
	mkdir -p backups
	cp trading_data.db backups/trading_data_$(shell date +%Y%m%d_%H%M%S).db
	cp config.json backups/config_$(shell date +%Y%m%d_%H%M%S).json
	@echo "Backup created in backups/ directory"

# Development workflow
.PHONY: dev
dev: format lint test
	@echo "Development workflow complete!"

# Release workflow
.PHONY: release
release: clean format lint test
	@echo "Release checks passed!"
	@echo "Ready to release!"

# Quick development setup
.PHONY: quick-start
quick-start:
	@echo "Setting up development environment..."
	make setup
	@echo "Running tests..."
	make test
	@echo "Quick start complete!"
	@echo "Activate environment with: source venv/bin/activate"
	@echo "Then run: make run"