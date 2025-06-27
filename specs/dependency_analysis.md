# Dependency Analysis - AR Sticker Factory
*Updated: December 2024*

## Current ComfyUI Setup Analysis

### ✅ Already Available
```python
# Core ML/AI (from requirements.txt) - UPDATED VERSIONS
torch>=2.5.0                # ✅ PyTorch for model inference (latest stable)
torchvision>=0.20.0         # ✅ Vision transforms (compatible with PyTorch 2.5)
transformers>=4.45.0        # ✅ HuggingFace models (current stable)
diffusers>=0.31.0          # ✅ Diffusion pipeline support (latest)
accelerate>=1.1.0          # ✅ Model acceleration (updated)
xformers>=0.0.28           # ✅ Memory efficient attention (current)

# Image Processing  
opencv-python>=4.10.0       # ✅ Image manipulation (latest)
Pillow>=11.0.0              # ✅ Image I/O (current)
numpy>=1.26.0               # ✅ Array operations (compatible with PyTorch 2.5)
scipy>=1.14.0               # ✅ Scientific computing (latest)
kornia>=0.7.3               # ✅ Computer vision (current)
einops>=0.8.0               # ✅ Tensor operations (latest)

# Utilities
requests>=2.32.0            # ✅ HTTP requests (current)
tqdm>=4.67.0                # ✅ Progress bars (latest)
safetensors>=0.4.5          # ✅ Safe model loading (current)
omegaconf>=2.3.0            # ✅ Configuration
```

### ❌ Required Additions

#### AR/3D Processing
```python
# OpenUSD for AR format export - CORRECTED VERSIONS
usd-core>=24.08             # 🔴 CRITICAL - USDZ export (updated July 2024)
# Note: pxr is included in usd-core package, no separate install needed

# 3D mesh processing
trimesh>=4.5.0              # 🟡 Mesh manipulation (current stable)
pymeshlab>=2023.12          # 🟡 Mesh optimization
open3d>=0.18.0              # 🟡 3D geometry processing

# Alternative: Blender Python API
bpy>=4.2.0                  # 🟠 Full Blender in Python (large, updated)
```

#### Segmentation Models - INSTALLATION CORRECTED
```python
# SAM2 (Segment Anything v2) - REQUIRES GIT INSTALLATION
# ❌ NO PyPI PACKAGE EXISTS - Use GitHub installation:
# git clone https://github.com/facebookresearch/sam2.git
# cd sam2 && pip install -e .
# Manual model download from Meta checkpoints required

ultralytics>=8.3.0         # 🟡 YOLO fallback option (current stable)
```

#### RTX Acceleration - UPDATED VERSIONS
```python
# TensorRT optimization - CORRECTED TO CURRENT VERSIONS
tensorrt>=10.0.0           # 🔴 CRITICAL - RTX speedup (TensorRT 10.x series)
torch-tensorrt>=2.5.0     # 🔴 PyTorch TensorRT bridge (compatible with PyTorch 2.5)
onnx>=1.17.0               # 🟡 Model format conversion (latest)
onnxruntime-gpu>=1.19.0    # 🟡 ONNX GPU execution (current)

# ⚠️ COMPATIBILITY WARNING: TensorRT 10.x requires CUDA 12.4+
```

#### File Handling
```python
# No additional deps needed - using stdlib
import zipfile              # ✅ USDZ packaging  
import tempfile             # ✅ Temporary files
import json                 # ✅ Metadata handling
```

## Installation Strategy

### Method 1: Minimal (Fastest Setup) - CORRECTED
**Goal**: Get working demo in 45 minutes (updated timing)
```bash
# Essential only - CORRECTED installation commands
pip install usd-core>=24.08 tensorrt>=10.0.0 torch-tensorrt>=2.5.0 trimesh>=4.5.0

# SAM2 requires Git installation (not available via pip)
git clone https://github.com/facebookresearch/sam2.git
cd sam2 && pip install -e .
```
**Trade-off**: Manual SAM2 installation required

### Method 2: Self-Contained (Recommended) - UPDATED
**Goal**: Full integration, 60-minute setup (realistic timing)
```bash
# Full AR pipeline included - CORRECTED versions
pip install usd-core>=24.08 tensorrt>=10.0.0 torch-tensorrt>=2.5.0 trimesh>=4.5.0 \
            ultralytics>=8.3.0 onnx>=1.17.0 onnxruntime-gpu>=1.19.0

# SAM2 manual installation
git clone https://github.com/facebookresearch/sam2.git
cd sam2 && pip install -e .

# Download SAM2 model checkpoints
cd checkpoints && wget https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
```
**Trade-off**: Larger install, requires manual model downloads

### Method 3: Development (Most Robust) - UPDATED
**Goal**: All options available for testing
```bash
# Everything including fallbacks - CORRECTED versions
pip install usd-core>=24.08 bpy>=4.2.0 tensorrt>=10.0.0 torch-tensorrt>=2.5.0 \
            trimesh>=4.5.0 pymeshlab>=2023.12 ultralytics>=8.3.0 \
            onnx>=1.17.0 onnxruntime-gpu>=1.19.0 open3d>=0.18.0

# SAM2 manual installation
git clone https://github.com/facebookresearch/sam2.git
cd sam2 && pip install -e .
```

### ⚠️ IMPORTANT COMPATIBILITY NOTES
- **Python Version**: Use Python 3.11 or 3.12 (USD-core has Python 3.13 compatibility issues)
- **CUDA Requirement**: TensorRT 10.x requires CUDA 12.4 or newer
- **Memory**: TensorRT installation requires 4GB+ disk space

## Platform Compatibility

### NVIDIA H100 Cluster (Primary Target) - UPDATED REQUIREMENTS
```yaml
OS: Ubuntu 22.04 LTS
CUDA: 12.4+ (REQUIRED for TensorRT 10.x)
Python: 3.11 or 3.12 (NOT 3.13 due to USD-core issues)
GPU Memory: 80GB per H100
Driver: 550.54.15+ (for CUDA 12.4 support)
Status: ✅ Full compatibility with updated versions
```

### macOS Development (Local) - UPDATED LIMITATIONS
```yaml
OS: macOS 14+ (Apple Silicon/Intel)
GPU: Metal Performance Shaders
Python: 3.11 or 3.12 (avoid 3.13)
Memory: 16GB+ RAM (32GB recommended for SAM2)
Limitations:
  - No TensorRT (NVIDIA only)
  - SAM2 CPU-only (10x slower)
  - USD-core limited Metal GPU support
  - Large model downloads required
Status: ⚠️ Development/testing only, not production-ready
```

## Model Size Analysis

### Required Models - UPDATED SIZES AND SOURCES
| Model | Size | Purpose | Download Source | Download Time* |
|-------|------|---------|-----------------|----------------|
| FLUX.1-dev | 24GB | Primary generation | HuggingFace Hub | ~90 min |
| SAM2.1 Large | 2.4GB | Segmentation | Meta checkpoints | ~10 min |
| **Total** | **26.4GB** | | | **~100 min** |

*Estimated on 50 Mbps connection - SIGNIFICANTLY LARGER than original estimate

### Alternative/Fallback Models
| Model | Size | Purpose | Benefit | Source |
|-------|------|---------|---------|--------|
| SAM2.1 Tiny | 38MB | Fast segmentation | 10x faster | Meta checkpoints |
| SAM2.1 Small | 183MB | Balanced speed/quality | 3x faster | Meta checkpoints |
| SDXL Base | 7GB | Lighter generation | Faster inference | HuggingFace Hub |
| UltraLytics YOLOv8 | 50MB | Object detection | SAM2 fallback | PyPI/Ultralytics |

## Fallback Strategy

### If Dependencies Fail - UPDATED FALLBACKS
1. **No USD/USDZ**: Export OBJ + MTL, manual USDZ conversion via Blender
2. **No TensorRT**: Use PyTorch with torch.compile() optimization
3. **No SAM2**: Use UltraLytics YOLOv8 + OpenCV masking
4. **No GPU/CUDA**: CPU inference (demonstration only, expect 10x slower)
5. **Python 3.13 incompatibility**: Downgrade to Python 3.11/3.12

### Graceful Degradation - UPDATED CODE
```python
# Example: Progressive fallbacks with current packages
import sys

# Check Python version compatibility
if sys.version_info >= (3, 13):
    print("⚠️  Warning: Python 3.13+ may have USD-core compatibility issues")
    print("   Recommended: Use Python 3.11 or 3.12")

try:
    from pxr import Usd  # USD-core import
    USDZ_EXPORT = True
    print("✅ USD-core available")
except ImportError:
    print("❌ USD not available, using OBJ export fallback")
    USDZ_EXPORT = False

try:
    import tensorrt
    import torch_tensorrt
    RTX_ACCELERATION = True
    print("✅ TensorRT acceleration available")
except ImportError:
    print("❌ TensorRT not available, using PyTorch torch.compile()")
    RTX_ACCELERATION = False

# SAM2 availability check
try:
    import sam2
    SAM2_AVAILABLE = True
    print("✅ SAM2 segmentation available")
except ImportError:
    print("❌ SAM2 not found, falling back to YOLO + OpenCV")
    SAM2_AVAILABLE = False
```

## Installation Commands

### Update requirements.txt - CORRECTED VERSIONS
```bash
# Add to existing requirements.txt - CORRECTED PACKAGE VERSIONS
echo "
# AR Sticker Factory additions - UPDATED December 2024
usd-core>=24.08
# Note: SAM2 requires manual Git installation, not available via pip
tensorrt>=10.0.0
torch-tensorrt>=2.5.0
trimesh>=4.5.0
ultralytics>=8.3.0
onnx>=1.17.0
onnxruntime-gpu>=1.19.0
" >> requirements.txt

# SAM2 manual installation required
echo "# SAM2 installation (manual):" >> requirements.txt
echo "# git clone https://github.com/facebookresearch/sam2.git" >> requirements.txt
echo "# cd sam2 && pip install -e ." >> requirements.txt
```

### Kubernetes Setup - UPDATED FOR CUDA 12.4
```bash
# Update deployment with CUDA 12.4 requirement
kubectl patch deployment comfyui-deployment -n comfyui -p '
spec:
  template:
    spec:
      containers:
      - name: comfyui
        image: nvidia/cuda:12.4-devel-ubuntu22.04
        command: [
          "bash", "-c", 
          "pip install -r requirements.txt && 
           git clone https://github.com/facebookresearch/sam2.git &&
           cd sam2 && pip install -e . && cd .. &&
           python main.py"
        ]
'
```

## Estimated Setup Time - REALISTIC UPDATES

### Optimistic (Everything Works) - UPDATED
- Dependency install: 15 minutes
- SAM2 Git clone/install: 10 minutes
- Model downloads: 100 minutes (26GB total)
- **Total: 125 minutes (2+ hours)**

### Realistic (Some Issues) - UPDATED  
- Dependency troubleshooting: 30 minutes
- CUDA/TensorRT compatibility: 20 minutes
- SAM2 manual installation: 15 minutes
- Model downloads: 120 minutes (with retries)
- Integration testing: 25 minutes
- **Total: 210 minutes (3.5 hours)**

### Pessimistic (Major Issues) - UPDATED
- Python version downgrade: 30 minutes
- CUDA 12.4 environment setup: 60 minutes
- Dependency rebuilds: 45 minutes
- Model download failures/retry: 180 minutes
- Fallback implementation: 45 minutes
- **Total: 360 minutes (6 hours)**

**⚠️ CRITICAL UPDATE**: Setup time is 3-5x longer than originally estimated due to:
- Manual SAM2 installation requirement
- 26GB model downloads (vs 8GB originally)
- TensorRT 10.x compatibility challenges
- Python version constraints

---

## Summary of Critical Corrections

### 🔴 MAJOR VERSION UPDATES REQUIRED
1. **USD-core**: `>=23.11` → `>=24.08` (latest stable release)
2. **TensorRT**: `>=8.6.0` → `>=10.0.0` (current version with CUDA 12.4+ requirement)
3. **PyTorch ecosystem**: All versions updated to current stable (PyTorch 2.5, etc.)

### 🔴 INSTALLATION METHOD CORRECTIONS
1. **SAM2**: No PyPI package exists - requires Git clone installation
2. **CUDA requirements**: Must use CUDA 12.4+ for TensorRT 10.x compatibility
3. **Python version**: Restrict to 3.11/3.12 (USD-core has 3.13 issues)

### 🔴 RESOURCE REQUIREMENT UPDATES
1. **Model storage**: 26GB required (vs 8GB originally estimated)
2. **Setup time**: 3.5-6 hours realistic (vs 1-2 hours originally)
3. **Memory requirements**: 32GB RAM recommended for development

### ✅ INSTALLATION RECOMMENDATIONS
1. Use **Method 2** (Self-Contained) for production deployment
2. Implement **graceful degradation** code for missing dependencies
3. Plan for **realistic 3.5-hour setup time** with troubleshooting
4. Use **Python 3.11 or 3.12** to avoid compatibility issues
5. Ensure **CUDA 12.4+ driver** installation before TensorRT

*Document validated and updated: December 2024*
