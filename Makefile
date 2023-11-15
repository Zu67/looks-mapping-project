# LooksMapping Scraper Makefile
# Common development tasks

.PHONY: help install install-dev test lint format type-check clean run-scrape run-analyze setup pre-commit

# Default target
help: ## Show this help message
	@echo "LooksMapping Scraper - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

# Development
setup: install-dev ## Set up development environment
	@echo "Setting up development environment..."
	playwright install
	@echo "Development environment ready!"

# Testing
test: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term-missing

test-fast: ## Run tests without coverage
	pytest -v

# Code Quality
lint: ## Run linting checks
	flake8 src tests scripts
	black --check src tests scripts
	mypy src

format: ## Format code with black
	black src tests scripts

type-check: ## Run type checking with mypy
	mypy src

# Pre-commit
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

# Application
run-scrape: ## Run the scraper
	python scripts/scrape.py

run-analyze: ## Run the analyzer
	python scripts/analyze.py

run-basic: ## Run basic HTTP scraper
	python scripts/scrape.py --method http

run-selenium: ## Run Selenium scraper
	python scripts/scrape.py --method selenium

run-playwright: ## Run Playwright scraper
	python scripts/scrape.py --method playwright

# Data Management
clean-data: ## Clean generated data files
	rm -rf data/*.json data/*.html data/*.png
	rm -f *.json *.html *.png *.log

clean: clean-data ## Clean all generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

# Documentation
docs: ## Generate documentation
	@echo "Documentation generation not implemented yet"

# Release
build: ## Build package
	python -m build

# Docker (if needed)
docker-build: ## Build Docker image
	docker build -t looksmapping-scraper .

docker-run: ## Run in Docker container
	docker run --rm -it looksmapping-scraper

# Development workflow
dev-setup: setup ## Complete development setup
	@echo "Development setup complete!"
	@echo "Run 'make test' to verify everything works"

ci: lint test ## Run CI pipeline locally
	@echo "CI pipeline completed successfully"
