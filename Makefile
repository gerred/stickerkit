# ComfyUI Hackathon Development Makefile

.PHONY: help setup install test clean lint format start debug deploy

# Default target
help:
	@echo "ComfyUI Hackathon Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup      - Full development environment setup"
	@echo "  install    - Install Python dependencies only"
	@echo "  models     - Download essential models"
	@echo ""
	@echo "Development Commands:"
	@echo "  start      - Start ComfyUI server"
	@echo "  test       - Run test suite"
	@echo "  lint       - Run code linting"
	@echo "  format     - Format code with black"
	@echo "  debug      - Debug workflow (requires WORKFLOW variable)"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean      - Clean temporary files"
	@echo "  reset      - Reset environment (removes .venv)"
	@echo ""
	@echo "Kubernetes Commands:"
	@echo "  deploy     - Deploy to K8s cluster"
	@echo "  k8s-status - Check K8s deployment status"
	@echo ""
	@echo "Examples:"
	@echo "  make setup"
	@echo "  make models"
	@echo "  make start"
	@echo "  make debug WORKFLOW=workflows/examples/basic_flux.json"

# Setup targets
setup:
	@echo "🚀 Setting up ComfyUI Hackathon environment..."
	chmod +x scripts/*.sh
	./scripts/setup-dev.sh

install:
	@echo "📦 Installing Python dependencies..."
	source .venv/bin/activate && uv pip install -r requirements.txt

models:
	@echo "🎯 Downloading models..."
	./scripts/download-models.sh

# Development targets
start:
	@echo "🎨 Starting ComfyUI server..."
	./scripts/start-comfyui.sh

test:
	@echo "🧪 Running tests..."
	./scripts/test-setup.sh
	source .venv/bin/activate && python -m pytest tests/ -v

lint:
	@echo "🔍 Linting code..."
	source .venv/bin/activate && flake8 . --max-line-length=88 --ignore=E203,W503

format:
	@echo "✨ Formatting code..."
	source .venv/bin/activate && black . --line-length=88
	source .venv/bin/activate && isort .

debug:
ifndef WORKFLOW
	@echo "❌ Please specify WORKFLOW variable"
	@echo "Example: make debug WORKFLOW=workflows/examples/basic_flux.json"
	@exit 1
endif
	@echo "🔧 Debugging workflow: $(WORKFLOW)"
	source .venv/bin/activate && python debug_workflow.py $(WORKFLOW)

# Maintenance targets
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf output/*
	rm -rf temp/*
	rm -rf logs/*

reset:
	@echo "🔄 Resetting environment..."
	rm -rf .venv
	rm -rf ComfyUI
	rm -rf models
	rm -rf output
	rm -rf temp
	rm -rf logs
	rm -f .env

# Kubernetes targets
deploy:
	@echo "☸️ Deploying to Kubernetes..."
	kubectl apply -k k8s/

k8s-status:
	@echo "📊 Kubernetes deployment status..."
	kubectl get pods -n comfyui-hackathon
	kubectl get services -n comfyui-hackathon

# Jupyter notebook
jupyter:
	@echo "📓 Starting Jupyter notebook..."
	source .venv/bin/activate && jupyter lab --port=8889

# Development server with hot reload
dev:
	@echo "🔥 Starting development server with monitoring..."
	source .venv/bin/activate && python -m watchdog shell-command \
		--patterns="*.py;*.json" \
		--recursive \
		--command='echo "File changed, restart ComfyUI if needed"' \
		.

# Build documentation
docs:
	@echo "📚 Building documentation..."
	@echo "Documentation available in workflows/README.md"

# Quick validation
validate:
	@echo "✅ Quick validation..."
	@test -f .venv/bin/activate || (echo "❌ Virtual environment not found" && exit 1)
	@test -d ComfyUI || (echo "❌ ComfyUI not found" && exit 1)
	@test -f .env || (echo "⚠️  .env file not found, copy from .env.template" && exit 1)
	@echo "✅ Basic validation passed"

# Show environment info
info:
	@echo "📋 Environment Information"
	@echo "========================="
	@echo "Python: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "Virtual Environment: $$(test -d .venv && echo 'Present' || echo 'Missing')"
	@echo "ComfyUI: $$(test -d ComfyUI && echo 'Present' || echo 'Missing')"
	@echo "Models Directory: $$(test -d models && echo 'Present' || echo 'Missing')"
	@echo "kubectl: $$(kubectl version --client --short 2>/dev/null || echo 'Not found')"
	@echo ""
	@echo "Disk Usage:"
	@du -sh models/ 2>/dev/null || echo "  models/: Not present"
	@du -sh output/ 2>/dev/null || echo "  output/: Not present"
	@du -sh .venv/ 2>/dev/null || echo "  .venv/: Not present"
