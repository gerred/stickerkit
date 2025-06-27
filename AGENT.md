# AGENT.md - ComfyUI NVIDIA Hackathon Development Guide

## Commands
- **Build/Test**: `make test` (runs pytest tests), `pytest tests/test_setup.py::TestClass::test_method` (single test)
- **Lint**: `make lint` (flake8), `make format` (black + isort)
- **Dev Environment**: `make setup` (full setup), `make install` (deps only), `make start` (ComfyUI server)
- **Debug**: `make debug WORKFLOW=workflows/examples/basic_flux.json` or `python debug_workflow.py <workflow.json>`
- **Kubernetes**: `make deploy` (K8s deployment), `make k8s-status` (check status)

## Architecture
- **Core**: ComfyUI node-based AI image generation on 8xH100 GPUs
- **Local Dev**: macOS with Python 3.12+ virtual environment (.venv)
- **Remote**: Kubernetes cluster with NVIDIA GPU operator, persistent storage for models
- **Models**: FLUX.1, SDXL, ControlNet in models/ subdirectories (checkpoints, vae, loras, controlnet, upscale_models)
- **Workflows**: JSON node graphs in workflows/examples/
- **Custom Nodes**: custom_nodes/ directory for extensions

## Code Style
- **Python**: Black formatter (88 chars), isort for imports, flake8 linting
- **Structure**: validate_json_structure() for workflows, analyze_workflow() for stats
- **Dependencies**: PyTorch, transformers, diffusers, ComfyUI modules (nodes, execution, server)
- **Testing**: pytest with environment, dependencies, workflows, scripts, configuration test classes
- **Imports**: Standard library first, third-party, then local modules
- **Error Handling**: Try/catch with descriptive messages, validate inputs before processing
