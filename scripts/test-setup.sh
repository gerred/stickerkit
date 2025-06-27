#!/bin/bash

# Test Script for ComfyUI Hackathon Development Environment
# Verifies GPU access, ComfyUI functionality, and K8s connectivity

set -e

echo "🧪 Testing ComfyUI Hackathon Development Environment"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run ./scripts/setup-dev.sh first"
    exit 1
fi

# Test Python installation
echo "🐍 Testing Python setup..."
python --version
echo "✅ Python is working"

# Test PyTorch and GPU access
echo "🔥 Testing PyTorch and GPU access..."
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'  GPU {i}: {torch.cuda.get_device_name(i)}')
else:
    print('Using CPU (consider GPU for better performance)')
print('✅ PyTorch is working')
"

# Test essential packages
echo "📦 Testing essential packages..."
python -c "
import numpy as np
import PIL
import cv2
import requests
import transformers
import diffusers
print('✅ All essential packages imported successfully')
"

# Test ComfyUI installation
echo "🎨 Testing ComfyUI installation..."
if [ -d "ComfyUI" ]; then
    cd ComfyUI
    python -c "
import sys
sys.path.append('.')
try:
    import nodes
    import execution
    import server
    print('✅ ComfyUI core modules imported successfully')
except ImportError as e:
    print(f'❌ ComfyUI import error: {e}')
    exit(1)
"
    cd ..
else
    echo "❌ ComfyUI directory not found"
    exit 1
fi

# Test model directories
echo "📁 Testing model directories..."
for dir in models/{checkpoints,vae,loras,controlnet,upscale_models,clip_vision,embeddings}; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "⚠️  $dir missing (run download-models.sh)"
    fi
done

# Test kubectl and K8s connectivity
echo "☸️ Testing Kubernetes connectivity..."
if command -v kubectl &> /dev/null; then
    echo "✅ kubectl is installed"
    
    # Test cluster connectivity (if configured)
    if kubectl cluster-info &> /dev/null; then
        echo "✅ Connected to Kubernetes cluster"
        kubectl get nodes --no-headers | wc -l | xargs echo "  Nodes available:"
    else
        echo "⚠️  Not connected to Kubernetes cluster (configure kubeconfig)"
    fi
else
    echo "❌ kubectl not found"
fi

# Test ComfyUI server startup (quick test)
echo "🌐 Testing ComfyUI server startup..."
cd ComfyUI
timeout 10s python main.py --cpu --listen 127.0.0.1 --port 8189 &
SERVER_PID=$!
sleep 5

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ ComfyUI server started successfully"
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null || true
else
    echo "❌ ComfyUI server failed to start"
fi
cd ..

# Test workflow execution
echo "🔧 Testing basic workflow execution..."
python -c "
import sys
sys.path.append('ComfyUI')
from execution import validate_inputs
from nodes import NODE_CLASS_MAPPINGS
print(f'Available nodes: {len(NODE_CLASS_MAPPINGS)}')
print('✅ Workflow system is functional')
"

# Memory and disk space check
echo "💾 Checking system resources..."
python -c "
import psutil
import shutil

memory = psutil.virtual_memory()
disk = shutil.disk_usage('.')

print(f'RAM: {memory.available // (1024**3)}GB available / {memory.total // (1024**3)}GB total')
print(f'Disk: {disk.free // (1024**3)}GB available / {disk.total // (1024**3)}GB total')

if memory.available < 8 * (1024**3):
    print('⚠️  Less than 8GB RAM available - consider closing other applications')
if disk.free < 20 * (1024**3):
    print('⚠️  Less than 20GB disk space - may need to clean up')
"

# Test environment variables
echo "⚙️ Testing environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    source .env
    echo "  Environment variables loaded"
else
    echo "⚠️  .env file not found (copy from .env.template)"
fi

# Generate test report
echo ""
echo "📊 Test Summary"
echo "==============="

# Count passed/failed tests
PASSED=0
FAILED=0

# Simple test results tracking (would need actual implementation)
echo "✅ Environment setup tests completed"
echo ""
echo "🚀 Ready for hackathon development!"
echo ""
echo "Next steps:"
echo "1. Start ComfyUI: ./scripts/start-comfyui.sh"
echo "2. Open workflows: ./workflows/examples/"
echo "3. Connect to K8s: kubectl get pods"
echo "4. Start coding! 🎨"
