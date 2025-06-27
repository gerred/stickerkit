# ComfyUI Hackathon Deployment Guide

## Overview
This repository contains a complete setup for running ComfyUI on Kubernetes with 8xH100 GPUs for the hackathon. The setup supports both local development on macOS and remote GPU execution.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   macOS Dev     │    │  Kubernetes     │    │   H100 Node     │
│   Environment   │───▶│     Cluster     │───▶│   8x H100       │
│                 │    │                 │    │   InfiniBand    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
  Local Testing          Port Forward           GPU Execution
  Model Development      Load Balancing         CUDA Processing
```

## Quick Start

### 1. Local Development Setup
```bash
# Clone and setup environment
git clone <repo>
cd hackathon
make setup                 # Install dependencies & Python env
make models               # Download essential models (FLUX, SDXL)
make test                 # Validate setup
```

### 2. Deploy to Kubernetes
```bash
# Deploy ComfyUI to K8s cluster
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n comfyui

# Setup port forwarding
kubectl port-forward -n comfyui svc/comfyui-service 8188:8188
```

### 3. Access ComfyUI
- Local: http://localhost:8188
- Remote: Access via port-forward

## Development Workflow

### Local Development
```bash
# Start local ComfyUI (CPU/MPS on macOS)
make start

# Test workflow locally
make test-workflow

# Debug issues
make debug
```

### Remote GPU Execution
```bash
# Scale up for heavy workloads
kubectl scale deployment comfyui-deployment --replicas=2 -n comfyui

# Monitor GPU usage
kubectl top nodes
kubectl logs -f deployment/comfyui-deployment -n comfyui
```

## Model Management

### Included Models
- **FLUX.1-dev** (12GB) - Fast high-quality generation
- **SDXL Base + Refiner** (14GB) - Standard generation
- **ControlNet** (5GB) - Guided generation

### Adding Custom Models
```bash
# Add model to models/ directory
kubectl exec -it deployment/comfyui-deployment -n comfyui -- ls /app/models

# Or upload via ComfyUI interface
# Navigate to Model Manager in web UI
```

## Configuration

### GPU Configuration
```yaml
# k8s/deployment.yaml
resources:
  limits:
    nvidia.com/gpu: 8      # 8x H100 GPUs
  requests:
    nvidia.com/gpu: 8
    memory: "64Gi"         # 64GB RAM
    cpu: "16"              # 16 CPU cores
```

### Storage Configuration
```yaml
# k8s/pvc.yaml
- models: 500Gi           # Model storage
- output: 100Gi           # Generated outputs  
- temp: 50Gi              # Temporary files
```

## Performance Optimization

### Multi-GPU Setup
The deployment automatically configures:
- NCCL for multi-GPU communication
- InfiniBand networking for low latency
- CUDA memory optimization
- Batch processing capabilities

### Memory Management
```bash
# Monitor memory usage
kubectl exec -it deployment/comfyui-deployment -n comfyui -- nvidia-smi

# Adjust batch size in workflows based on available VRAM
# H100: 80GB VRAM per GPU = 640GB total
```

## Troubleshooting

### Common Issues

1. **GPU Not Detected**
```bash
kubectl describe node <node-name>
# Check for nvidia.com/gpu resource
```

2. **Out of Memory**
```bash
# Reduce batch size or enable model offloading
# Check logs: kubectl logs deployment/comfyui-deployment -n comfyui
```

3. **Port Forward Issues**
```bash
# Kill existing forwards
lsof -ti:8188 | xargs kill -9
kubectl port-forward -n comfyui svc/comfyui-service 8188:8188
```

### Debug Commands
```bash
# Check pod status
kubectl describe pod <pod-name> -n comfyui

# Access pod shell
kubectl exec -it deployment/comfyui-deployment -n comfyui -- /bin/bash

# View logs
kubectl logs -f deployment/comfyui-deployment -n comfyui
```

## Security Notes

- ComfyUI runs as non-root user (uid: 1000)
- Network policies restrict inter-pod communication
- Resource quotas prevent resource exhaustion
- No external services exposed by default

## Scaling

### Horizontal Pod Autoscaling
```bash
# HPA automatically scales based on CPU/GPU usage
kubectl get hpa -n comfyui

# Manual scaling
kubectl scale deployment comfyui-deployment --replicas=N -n comfyui
```

### Vertical Scaling
Adjust resource requests/limits in deployment.yaml for different workloads.

## Monitoring

```bash
# GPU monitoring
kubectl top nodes

# ComfyUI metrics
kubectl port-forward -n comfyui svc/comfyui-metrics 9090:9090
# Access Prometheus: http://localhost:9090
```

## Support

- Check logs: `kubectl logs -f deployment/comfyui-deployment -n comfyui`
- Monitor resources: `kubectl top pods -n comfyui`
- Debug connectivity: `kubectl exec -it deployment/comfyui-deployment -n comfyui -- curl localhost:8188`

## References

- [ComfyUI Documentation](https://docs.comfy.org/)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/getting-started.html)
- [Kubernetes GPU Support](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
