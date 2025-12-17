.PHONY: help install test lint format typecheck all clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install package with dev dependencies"
	@echo "  make test       - Run tests with coverage"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make typecheck  - Run mypy type checker"
	@echo "  make all        - Run format, lint, typecheck, and test"
	@echo "  make clean      - Remove build artifacts"

install:
	uv pip install -e ".[dev]"

test:
	pytest --cov=agent_cli --cov-report=term-missing --cov-report=html

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy agent_cli --ignore-missing-imports

all: format lint typecheck test

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
