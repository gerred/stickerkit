# AR Sticker Factory - Project Specifications

## Project Overview
**Name**: AR Sticker Factory  
**Track**: Custom Node Development  
**Goal**: First ComfyUI custom node for generating AR-ready stickers from text prompts

## Core Value Proposition
Transform text prompts into AR-compatible stickers with automatic background removal and 3D format export. Initial focus on iOS USDZ format with 10-15 second generation time, optimized for RTX acceleration.

## Technical Pipeline
```
Text Prompt → SD3/FLUX Generation → SAM2 Segmentation → Alpha Channel Processing → USDZ Export → AR Sticker Pack
```

## Key Features

1. **One-Click AR Generation**: Prompt → AR sticker in single node
2. **Multi-Format Output**: PNG with alpha + USDZ for iOS AR
3. **Background Removal**: Automatic segmentation with SAM2
4. **RTX Acceleration**: TensorRT optimization for 2x speedup
5. **AR-Compatible Export**: USDZ format for iOS AR QuickLook

## RTX Optimization Strategy

- **TensorRT Engine**: Convert SD3/FLUX to TensorRT for 2x inference speedup
- **Mixed Precision**: FP16/FP8 on Tensor Cores for memory efficiency  
- **Model Optimization**: Quantization for reduced VRAM usage
- **Pipeline Efficiency**: Minimize model loading/unloading overhead

## Target Demo Sequence (30 seconds)

1. Type prompt: "cyberpunk neon cat"
2. Hit generate → 10-15 seconds later PNG + USDZ ready
3. AirDrop to iPhone → Open in AR QuickLook
4. Place virtual sticker in room using AR
5. Demonstrate AR sticker placement and interaction

## Success Metrics

- **Speed**: 10-15 seconds per sticker generation (initial target)
- **Quality**: Clean alpha channels, proper USDZ format
- **Compatibility**: iOS AR QuickLook support (future: Android GLB)
- **Usability**: Single ComfyUI node workflow
- **Technical**: Successful SAM2 segmentation and USDZ export

## Technical Constraints

- **Hardware**: Requires RTX GPU with 12GB+ VRAM
- **Models**: SD3/FLUX + SAM2 loaded simultaneously
- **Formats**: USDZ for iOS (GLB support planned for Android)
- **File Size**: <10MB per sticker for mobile compatibility
- **Geometry**: Optimized for AR viewing distances
