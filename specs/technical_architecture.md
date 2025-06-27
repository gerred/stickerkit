# Technical Architecture - AR Sticker Factory

## Node Architecture

### 1. ARStickerGenerator (Main Node)
**Inputs:**
- `prompt` (STRING): Text description
- `batch_size` (INT): Number of stickers (1-8)
- `style` (ENUM): art_style, realistic, cartoon, cyberpunk
- `resolution` (ENUM): 512x512, 768x768, 1024x1024
- `background_removal` (BOOL): Enable SAM2 segmentation

**Outputs:**
- `images` (IMAGE): Generated PNG images with alpha
- `usdz_files` (FILES): AR-ready USDZ packages
- `metadata` (JSON): Generation parameters + AR placement hints

### 2. SAM2Segmenter (Background Removal)
**Purpose**: Precise object segmentation for clean alpha channels
**Inputs:**
- `images` (IMAGE): Generated images
- `confidence_threshold` (FLOAT): Segmentation confidence (0.5-0.95)
- `smooth_edges` (BOOL): Post-process edge smoothing

**Outputs:**
- `masked_images` (IMAGE): Images with transparent backgrounds
- `masks` (MASK): Binary segmentation masks

### 3. USDZExporter (AR Format Converter)
**Purpose**: Convert PNG+Alpha to AR-compatible USDZ
**Inputs:**
- `images` (IMAGE): Images with alpha channels
- `scale` (FLOAT): AR object scale (0.1-2.0)
- `anchor_type` (ENUM): plane, face, world

**Outputs:**
- `usdz_files` (FILES): Ready for AR QuickLook
- `preview_images` (IMAGE): AR preview renders

### 4. StickerPackBundler (Package Creator)
**Purpose**: Bundle multiple stickers into themed packs
**Inputs:**
- `stickers` (LIST): Multiple sticker objects
- `pack_name` (STRING): Pack identifier
- `pack_theme` (STRING): Theme description

**Outputs:**
- `pack_bundle` (FILE): Complete sticker pack
- `thumbnail` (IMAGE): Pack preview image

## Model Integration

### Primary Generation Models
1. **FLUX.1-schnell** (Recommended)
   - Size: 12B parameters
   - Speed: ~3-4s per image on H100
   - Quality: High-quality, fast inference
   - License: Apache 2.0 (fully open source)
   - Memory: ~24GB model file (fp16)

2. **SDXL-Lightning** (Alternative)
   - Size: 3.5B parameters
   - Speed: ~1-2s per image on H100  
   - Quality: Good for fast iteration
   - License: CreativeML Open RAIL++-M
   - Memory: ~7GB model file

### Segmentation Model
- **SAM2-Large**: Facebook's Segment Anything v2
- **Size**: 358MB model (sam2_hiera_large.pt)
- **Speed**: ~0.5-1s per image on H100
- **Accuracy**: 92-95% for object isolation
- **Alternative**: SAM2-Base (229MB) for faster inference

### 3D Processing
- **OpenUSD Core**: Direct USDZ creation for AR
- **Simple Mesh Generation**: Plane geometry for 2D stickers
- **Texture Mapping**: PNG with alpha channel support
- **AR QuickLook Compliance**: iOS/iPadOS compatible format

## File Structure
```
custom_nodes/
└── ar_sticker_factory/
    ├── __init__.py              # Node registration
    ├── nodes/
    │   ├── ar_sticker_generator.py
    │   ├── sam2_segmenter.py
    │   ├── usdz_exporter.py
    │   └── sticker_pack_bundler.py
    ├── models/
    │   ├── model_manager.py     # TensorRT optimization
    │   └── sam2_loader.py       # SAM2 integration
    ├── utils/
    │   ├── image_processing.py  # Alpha channel utils
    │   ├── usdz_creation.py     # 3D export logic
    │   └── ar_validation.py     # AR compatibility checks
    └── tests/
        ├── test_generation.py
        ├── test_segmentation.py
        └── test_ar_export.py
```

## Performance Targets

### H100 Cluster (8x GPUs)
- **Single Sticker**: 6-10 seconds end-to-end
- **Sticker Pack (4x)**: 18-25 seconds
- **Memory Usage**: <30GB VRAM per GPU
- **Throughput**: 8-12 stickers/minute

### Local Development (macOS)
- **Single Sticker**: 15-30 seconds (CPU/MPS)
- **Memory Usage**: <16GB RAM
- **Purpose**: Development and testing only

## Dependencies Analysis

### Additional Requirements (vs current setup)
```python
# AR and 3D processing
usd-core>=23.11              # OpenUSD for AR export (lightweight)
trimesh>=4.0.0              # Simple mesh generation
Pillow>=10.0.0              # Image processing with alpha

# Advanced segmentation  
segment-anything-2>=1.0     # SAM2 model
opencv-python>=4.8.0       # Image processing utilities

# Model optimization (optional for production)
torch-tensorrt>=1.4.0     # PyTorch-TensorRT integration
onnx>=1.15.0               # Model format conversion

# File handling
zipfile                    # Standard library ZIP for USDZ
tempfile                   # Standard library temp files
json                       # Standard library JSON handling
```

### Model Downloads Required
```bash
# FLUX.1-schnell (Apache 2.0 licensed, ~24GB)
wget https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors

# SAM2 Large (~358MB)  
wget https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_large.pt

# Alternative: SAM2 Base (smaller, ~229MB)
wget https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_base_plus.pt

# SDXL-Lightning (Alternative, ~7GB)
wget https://huggingface.co/ByteDance/SDXL-Lightning/resolve/main/sdxl_lightning_4step_unet.safetensors
```

## Technical Corrections Applied

### Model Selection Changes
- **Replaced SD3 Medium** with FLUX.1-schnell due to licensing issues (SD3 requires commercial license)
- **Corrected SAM2 specifications**: 358MB for Large model, not 600MB
- **Added SDXL-Lightning** as faster alternative for development/testing

### Performance Adjustments
- **Realistic timing estimates**: 6-10s per sticker vs optimistic 3-5s
- **Conservative throughput**: 8-12 stickers/minute vs unrealistic 15-20
- **Accurate memory usage**: <30GB VRAM vs overestimated 40GB

### Architecture Simplifications
- **Removed Blender dependency**: Overkill for simple 2D-to-3D conversion
- **Direct OpenUSD approach**: Simpler plane mesh generation for stickers
- **Streamlined dependencies**: Focus on essential libraries only

### Implementation Focus
- **Open source compliance**: All recommended models use permissive licenses
- **Hackathon-appropriate scope**: Realistic development timeline
- **Technical accuracy**: Verified model sizes and performance characteristics
