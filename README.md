# StickerKit

AI-powered sticker generation toolkit using ComfyUI and FLUX.1 models on NVIDIA H100 GPUs.

## Features

- **FLUX.1-based sticker generation** with high-quality AI image synthesis
- **AR sticker pipeline** with transparent background support
- **ControlNet integration** for precise control over generation
- **Upscaling workflows** for high-resolution output
- **Kubernetes deployment** ready for GPU clusters
- **Development environment** with macOS local setup

## Quick Start

### Local Development (macOS)

```bash
# Setup environment
make setup

# Install dependencies only
make install

# Start ComfyUI server
make start
```

### Kubernetes Deployment

```bash
# Deploy to K8s cluster with GPU support
make deploy

# Check deployment status  
make k8s-status
```

## Workflows

Pre-built ComfyUI workflows for common sticker generation tasks:

- **Basic FLUX**: `workflows/examples/basic_flux.json`
- **AR Sticker Pipeline**: `workflows/examples/complete_ar_sticker_pipeline.json`  
- **ControlNet**: `workflows/examples/controlnet_workflow.json`
- **Upscaling**: `workflows/examples/upscale_workflow.json`

### Running Workflows

```bash
# Debug workflow locally
make debug WORKFLOW=workflows/examples/basic_flux.json

# Or directly with Python
python debug_workflow.py workflows/examples/basic_flux.json
```

## Development

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Run tests
make test
```

### Project Structure

```
├── custom_nodes/          # ComfyUI extensions
├── k8s/                   # Kubernetes manifests
├── scripts/               # Setup and utility scripts
├── workflows/examples/    # Pre-built workflows
├── main.py               # Main application entry
├── pyproject.toml        # Python project config
└── Makefile              # Development commands
```

## Requirements

- **Python 3.12+**
- **PyTorch** with CUDA support
- **ComfyUI** (installed via comfy-cli)
- **NVIDIA GPUs** (H100 recommended)
- **Kubernetes** (for deployment)

## Models

The toolkit supports:

- **FLUX.1** (Schnell/Dev)
- **SDXL** variants
- **ControlNet** models
- **Upscaling** models

Models are automatically downloaded to `models/` directory when needed.

## License

This project was developed for the NVIDIA H100 ComfyUI Hackathon 2025.
