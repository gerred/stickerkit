# ComfyUI Kubernetes Deployment on H100 Nodes

This repository contains Kubernetes manifests for deploying ComfyUI on H100 GPU nodes with comprehensive configuration for high-performance AI inference workloads.

## Prerequisites

- Kubernetes cluster with H100 GPU nodes
- NVIDIA GPU Operator or device plugin installed
- Storage class `fast-ssd` available
- InfiniBand networking support (optional but recommended)
- Sufficient cluster resources (see resource requirements)

## Resource Requirements

### Per Pod:
- **CPU**: 16-32 cores
- **Memory**: 64-128 GiB
- **GPU**: 8x H100 GPUs
- **Storage**: 650 GiB total (500 GiB models + 100 GiB output + 50 GiB temp)
- **InfiniBand**: 8x HCA ports (for multi-node scaling)

### Node Requirements:
- Instance type: `p5.48xlarge` (AWS) or equivalent
- Node selector: `accelerator=nvidia_h100`
- InfiniBand support for optimal multi-GPU performance

## Quick Start

### 1. Deploy NVIDIA Device Plugin
```bash
kubectl apply -f k8s/nvidia-device-plugin.yaml
```

### 2. Deploy ComfyUI
```bash
# Apply all manifests
kubectl apply -f k8s/

# Or use Kustomize
kubectl apply -k k8s/
```

### 3. Verify Deployment
```bash
# Check pods
kubectl get pods -n comfyui

# Check GPU allocation
kubectl describe node <h100-node-name>

# Check services  
kubectl get svc -n comfyui
```

## Access Methods

### Port Forwarding (Development)
```bash
kubectl port-forward -n comfyui svc/comfyui-service 8188:8188
# Access at http://localhost:8188
```

### NodePort (Cluster Access)
```bash
kubectl get nodes -o wide
# Access at http://<node-ip>:30888
```

### LoadBalancer (Production)
```bash
kubectl get svc -n comfyui comfyui-loadbalancer
# Use external IP provided by load balancer
```

## Configuration

### Model Storage
Models are stored in persistent volumes:
- **Checkpoints**: `/app/models/checkpoints/`
- **LoRAs**: `/app/models/loras/`  
- **VAE**: `/app/models/vae/`
- **ControlNet**: `/app/models/controlnet/`

To add models:
```bash
# Get pod name
POD_NAME=$(kubectl get pods -n comfyui -l app=comfyui -o jsonpath='{.items[0].metadata.name}')

# Copy models
kubectl cp model.safetensors comfyui/$POD_NAME:/app/models/checkpoints/
```

### Environment Variables
Key environment variables for H100 optimization:
- `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`
- `NCCL_IB_DISABLE=0` (Enable InfiniBand)
- `NCCL_NET_GDR_LEVEL=2` (GPU Direct RDMA)

## Scaling

### Horizontal Pod Autoscaling
The HPA automatically scales based on CPU and memory usage:
```bash
kubectl get hpa -n comfyui
```

### Manual Scaling
```bash
kubectl scale deployment comfyui -n comfyui --replicas=3
```

### Resource Monitoring
```bash
# GPU utilization
kubectl exec -n comfyui <pod-name> -- nvidia-smi

# Resource usage
kubectl top pods -n comfyui
```

## InfiniBand Networking

For optimal multi-GPU performance across nodes:

1. **Verify InfiniBand**:
```bash
kubectl exec -n comfyui <pod-name> -- ls -la /dev/infiniband/
```

2. **Check NCCL Configuration**:
```bash
kubectl exec -n comfyui <pod-name> -- env | grep NCCL
```

3. **Test Multi-GPU Communication**:
```bash
kubectl exec -n comfyui <pod-name> -- python -c "
import torch
print(f'GPUs available: {torch.cuda.device_count()}')
print(f'NCCL available: {torch.distributed.is_nccl_available()}')
"
```

## Security

### Network Policies
- Restricts ingress to port 8188
- Allows InfiniBand communication between pods
- Permits DNS and external HTTP/HTTPS

### Security Context
- Non-root user (1000:1000)
- Read-only root filesystem where possible
- Required capabilities: IPC_LOCK, SYS_RESOURCE

### Resource Quotas
- Prevents resource exhaustion
- Limits GPU allocation per namespace
- Storage and compute boundaries

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA runtime
kubectl describe node <h100-node>

# Verify device plugin
kubectl get pods -n kube-system | grep nvidia

# Check GPU resources
kubectl get nodes -o json | jq '.items[].status.allocatable'
```

### Pod Scheduling Issues
```bash
# Check node affinity
kubectl describe pod -n comfyui <pod-name>

# Verify tolerations
kubectl get nodes --show-labels | grep h100
```

### Performance Issues
```bash
# Check GPU utilization
kubectl exec -n comfyui <pod-name> -- nvidia-smi

# Monitor NCCL performance
kubectl logs -n comfyui <pod-name> | grep NCCL

# Check InfiniBand status
kubectl exec -n comfyui <pod-name> -- ibv_devices
```

### Storage Issues
```bash
# Check PVC status
kubectl get pvc -n comfyui

# Verify storage class
kubectl get storageclass

# Check volume mounts
kubectl describe pod -n comfyui <pod-name>
```

## Monitoring

### Prometheus Metrics
- DCGM Exporter for GPU metrics
- ComfyUI application metrics
- Resource utilization monitoring

### Grafana Dashboards
Import provided dashboard configurations for:
- GPU utilization and temperature
- Model inference performance
- Resource consumption trends

## Production Considerations

1. **Storage Performance**: Use NVMe SSD storage classes for model loading
2. **Network Bandwidth**: Ensure 400Gb/s InfiniBand for multi-node setups  
3. **Cooling**: Monitor GPU temperatures under sustained load
4. **Model Caching**: Pre-load frequently used models to reduce latency
5. **Backup Strategy**: Regular snapshots of model storage volumes

## Cost Optimization

1. **Spot Instances**: Use spot instances for development workloads
2. **Auto-scaling**: Configure aggressive scale-down policies
3. **Resource Requests**: Right-size resource requests based on workload
4. **Storage Tiers**: Use different storage classes for different model types

## Updates and Maintenance

### Rolling Updates
```bash
kubectl set image deployment/comfyui -n comfyui comfyui=comfyanonymous/comfyui:new-tag
```

### Backup Models
```bash
kubectl exec -n comfyui <pod-name> -- tar czf - /app/models | \
  kubectl exec -i backup-pod -- tar xzf - -C /backup/
```

This deployment provides enterprise-grade ComfyUI hosting with optimal H100 utilization, comprehensive monitoring, and production-ready security configurations.
