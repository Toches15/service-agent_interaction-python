# Makefile for FastAPI Template

.PHONY: help install dev upgrade test test-cov test-cov-html cov-open test-parallel test-verbose test-failed test-watch lint mypy format format-targeted clean run env env-dev postgres-dev postgres-stop

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: ## Install development dependencies
	uv sync --extra dev

upgrade: ## Upgrade all dependencies to latest versions
	uv sync --upgrade

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=app --cov-report=html --cov-report=term --cov-report=xml

test-cov-html: ## Run tests with HTML coverage report and open in browser
	uv run pytest --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"
	@echo "Opening coverage report in browser..."
	@open htmlcov/index.html

cov-open: ## Open existing HTML coverage report in browser
	@if [ -f htmlcov/index.html ]; then \
		echo "Opening existing coverage report..."; \
		open htmlcov/index.html; \
	else \
		echo "No coverage report found. Run 'make test-cov-html' first."; \
	fi

test-parallel: ## Run tests in parallel
	uv run pytest -n auto

test-verbose: ## Run tests with verbose output
	uv run pytest -v

test-failed: ## Run only failed tests from last run
	uv run pytest --lf

test-watch: ## Run tests in watch mode (requires pytest-watch)
	uv run ptw --runner "pytest --cov=app"

lint: ## Run linting
	uv run ruff check app tests

mypy: ## Run type checking (optional)
	uv run mypy app

format: ## Format entire project
	uv run ruff format .
	uv run ruff check --fix .

format-targeted: ## Format only app and tests directories
	uv run ruff format app tests
	uv run ruff check --fix app tests

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

run: ## Run the development server
	uv run python main.py

run-prod: ## Run in production mode
	ENVIRONMENT=production uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t fastapi-template .

docker-run: ## Run Docker container
	docker run -p 8000:8000 fastapi-template

postgres-dev: ## Start development PostgreSQL
	docker-compose -f docker-compose.dev.yml up -d

postgres-stop: ## Stop development PostgreSQL
	docker-compose -f docker-compose.dev.yml down

requirements: ## Export production dependencies to requirements.txt
	uv export --format requirements-txt --no-hashes --no-dev -o requirements.txt

env: ## Load environment variables from .env file
	@echo "Loading environment variables from .env..."
	@set -a && source .env && set +a && echo "Environment loaded from .env"

env-dev: ## Load environment variables from .env.dev file
	@echo "Loading environment variables from .env.dev..."
	@set -a && source .env.dev && set +a && echo "Environment loaded from .env.dev"