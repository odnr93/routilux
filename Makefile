.PHONY: help clean install dev-install test test-builtin test-all test-cov lint format check build sdist wheel docs html clean-docs

help:
	@echo "Available targets:"
	@echo "  install       - Install the package"
	@echo "  dev-install   - Install with development dependencies"
	@echo "  test          - Run tests"
	@echo "  test-builtin  - Run built-in routines tests"
	@echo "  test-all      - Run all tests (main + builtin)"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  lint          - Run linting checks (flake8)"
	@echo "  format        - Format code with black"
	@echo "  check         - Run all checks (lint + format check + tests)"
	@echo "  build         - Build source and wheel distributions"
	@echo "  sdist         - Build source distribution"
	@echo "  wheel         - Build wheel distribution"
	@echo "  docs          - Build documentation"
	@echo "  html          - Build HTML documentation"
	@echo "  clean         - Clean build artifacts"
	@echo "  clean-docs    - Clean documentation build"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-builtin:
	pytest flowforge/builtin_routines/ -v

test-all: test test-builtin

test-cov:
	pytest tests/ flowforge/builtin_routines/ --cov=flowforge --cov-report=html --cov-report=term

lint:
	flake8 flowforge/ tests/ examples/ --max-line-length=100 --extend-ignore=E203,W503

format:
	black flowforge/ tests/ examples/

format-check:
	black --check flowforge/ tests/ examples/

check: lint format-check test
	@echo "All checks passed!"

build: clean
	python -m build

sdist: clean
	python -m build --sdist

wheel: clean
	python -m build --wheel

docs:
	cd docs && make html

html:
	cd docs && make html

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

clean-docs:
	cd docs && make clean

