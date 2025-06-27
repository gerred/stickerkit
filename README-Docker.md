# ComfyUI Docker Setup for NVIDIA H100 GPUs

This Docker setup provides a complete ComfyUI installation optimized for NVIDIA H100 GPUs with CUDA 12.1 support.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit
- NVIDIA drivers compatible with CUDA 12.1+
- NVIDIA H100 GPU(s)

## Quick Start

1. **Clone and prepare the environment:**
   ```bash
   git clone <your-repo>
   cd <your-repo>
   mkdir -p models output input custom_nodes
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

3. **Access ComfyUI:**
   - Open http://localhost:8188 in your browser

## Directory Structure

```
.
├── Dockerfile                 # ComfyUI container definition
├── docker-compose.yml        # Container orchestration
├── requirements.txt          # Python dependencies
├── models/                   # AI models storage
│   ├── checkpoints/         # Stable Diffusion models
│   ├── vae/                 # VAE models
│   ├── loras/               # LoRA models
│   ├── controlnet/          # ControlNet models
│   └── upscale_models/      # Upscaling models
├── output/                   # Generated images
├── input/                    # Input images
└── custom_nodes/            # ComfyUI extensions
```

## Configuration

### GPU Configuration

The setup automatically detects and uses all available H100 GPUs. To limit GPU usage:

```yaml
# In docker-compose.yml
environment:
  - CUDA_VISIBLE_DEVICES=0,1  # Use only first two GPUs
```

### Memory Optimization

For H100s with 80GB VRAM:

```yaml
environment:
  - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
```

### Performance Tuning

```yaml
environment:
  - CUDA_LAUNCH_BLOCKING=0           # Async GPU operations
  - OMP_NUM_THREADS=8                # CPU threads
  - CUDA_CACHE_DISABLE=0             # Enable CUDA caching
```

## Commands

### Basic Operations
```bash
# Start ComfyUI
docker-compose up -d

# View logs
docker-compose logs -f comfyui

# Stop ComfyUI
docker-compose down

# Rebuild container
docker-compose up --build
```

### Model Management
```bash
# Download models using the model-downloader service
docker-compose --profile models up model-downloader

# Access container shell
docker-compose exec comfyui bash
```

### Development Mode
```bash
# Mount local ComfyUI source for development
# Uncomment the ComfyUI volume mount in docker-compose.yml
# - ./ComfyUI:/app/ComfyUI

# Clone ComfyUI locally first
git clone https://github.com/comfyanonymous/ComfyUI.git
docker-compose up
```

## Installing Custom Nodes

1. **Via container shell:**
   ```bash
   docker-compose exec comfyui bash
   cd custom_nodes
   git clone https://github.com/your-custom-node.git
   pip install -r your-custom-node/requirements.txt
   exit
   docker-compose restart comfyui
   ```

2. **Via volume mount:**
   ```bash
   cd custom_nodes
   git clone https://github.com/your-custom-node.git
   docker-compose restart comfyui
   ```

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu20.04 nvidia-smi

# Verify container toolkit
sudo systemctl status nvidia-container-toolkit
```

### Memory Issues
```bash
# Monitor GPU memory
nvidia-smi -l 1

# Adjust memory allocation in docker-compose.yml
environment:
  - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256
```

### Port Conflicts
```bash
# Use different port
ports:
  - "8189:8188"  # Change host port
```

## Advanced Configuration

### Multi-GPU Setup
```yaml
environment:
  - CUDA_VISIBLE_DEVICES=all
  - NCCL_P2P_DISABLE=1  # If P2P issues occur
```

### Production Deployment
```yaml
deploy:
  replicas: 1
  restart_policy:
    condition: on-failure
    max_attempts: 3
  resources:
    limits:
      memory: 64G
    reservations:
      memory: 32G
```

### Monitoring
```bash
# Add monitoring container
services:
  nvidia-exporter:
    image: mindprince/nvidia_gpu_prometheus_exporter:0.1
    ports:
      - "9445:9445"
    volumes:
      - /usr/lib/x86_64-linux-gnu/libnvidia-ml.so:/usr/lib/x86_64-linux-gnu/libnvidia-ml.so
      - /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1:/usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1
```

## Model Recommendations for H100

- **Checkpoints:** SDXL, SD 2.1, Flux
- **VAE:** SDXL VAE, SD 2.1 VAE
- **Upscalers:** RealESRGAN, ESRGAN
- **ControlNet:** SDXL ControlNet models

Download models to the appropriate directories in `./models/`.
