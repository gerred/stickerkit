# AR Sticker Factory - ComfyUI Custom Nodes

## Overview

The AR Sticker Generator is a custom ComfyUI node designed for the NVIDIA x ComfyUI Hackathon 2025. It generates AR-ready stickers from text prompts using a multi-stage pipeline:

1. **Text-to-Image Generation**: FLUX.1 or SDXL models
2. **Background Removal**: SAM2 segmentation 
3. **AR Export**: USDZ format for AR applications

## Node Structure

### ARStickerGenerator

**Category**: "AR Sticker Factory"
**Function**: `generate_ar_sticker`

#### Inputs (Required)
- `prompt` (STRING): Text description of the sticker
- `negative_prompt` (STRING): What to avoid in generation
- `width` (INT): Output width (256-2048, default: 512)
- `height` (INT): Output height (256-2048, default: 512)
- `steps` (INT): Diffusion steps (1-100, default: 20)
- `cfg_scale` (FLOAT): Guidance scale (1.0-20.0, default: 7.5)
- `seed` (INT): Random seed (-1 for random)
- `model_type` (CHOICE): "flux" or "sdxl"
- `export_format` (CHOICE): "png", "usdz", or "both"

#### Inputs (Optional)
- `input_image` (IMAGE): For img2img generation
- `mask` (MASK): For inpainting

#### Outputs
- `image` (IMAGE): Generated/segmented image
- `mask` (MASK): Background removal mask
- `png_path` (STRING): Path to PNG export
- `usdz_path` (STRING): Path to USDZ export

## ComfyUI Integration

### Node Registration

The node is registered through the standard ComfyUI mechanism:

```python
NODE_CLASS_MAPPINGS = {
    "ARStickerGenerator": ARStickerGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ARStickerGenerator": "AR Sticker Generator"
}
```

### Directory Structure

```
custom_nodes/
├── __init__.py                 # ComfyUI registration
├── ar_sticker_generator.py     # Main node implementation
├── ar_sticker_factory/         # Extended package structure
└── README.md                   # This file
```

### Installation

1. Copy the `custom_nodes/` directory to your ComfyUI installation
2. Ensure required dependencies are installed:
   - torch
   - torchvision
   - PIL (Pillow)
   - numpy

3. Restart ComfyUI
4. Look for "AR Sticker Generator" in the "AR Sticker Factory" category

## Workflow Integration

### Basic Usage

```json
{
  "1": {
    "inputs": {
      "prompt": "A cute cartoon sticker of a smiling cat",
      "model_type": "flux",
      "export_format": "both"
    },
    "class_type": "ARStickerGenerator"
  }
}
```

### With Save Image

The node outputs ComfyUI-compatible IMAGE tensors that can be connected to:
- SaveImage nodes
- Preview nodes  
- Other image processing nodes

## Implementation Status

### ✅ Completed
- [x] ComfyUI node structure and registration
- [x] Input/output type definitions
- [x] Basic interface implementation
- [x] Error handling and validation
- [x] Placeholder pipeline structure

### 🚧 In Progress (TODO)
- [ ] FLUX.1 model integration
- [ ] SDXL model integration  
- [ ] SAM2 segmentation implementation
- [ ] USDZ export functionality
- [ ] Transparent background handling
- [ ] Performance optimization

## Development Notes

### Node Class Requirements

ComfyUI nodes must implement:

1. `INPUT_TYPES()` - classmethod returning input schema
2. `RETURN_TYPES()` - classmethod returning output types tuple
3. `FUNCTION()` - classmethod returning main function name
4. `CATEGORY()` - classmethod returning UI category
5. Main execution function with proper signature

### Tensor Format

ComfyUI uses specific tensor formats:
- **Images**: `(batch, height, width, channels)` float tensor [0-1]
- **Masks**: `(batch, height, width)` float tensor [0-1]

### Error Handling

The node includes comprehensive error handling:
- Invalid parameters → default values
- Model loading failures → graceful fallback
- Export errors → placeholder outputs
- All errors logged with descriptive messages

## Testing

Test the node with the provided workflow:

```bash
# From project root
python debug_workflow.py workflows/ar_sticker_test.json
```

The node will:
1. Generate a placeholder image
2. Create a circular mask
3. Export PNG and USDZ placeholders
4. Return proper ComfyUI tensors

## Extension Points

The node is designed for easy extension:

1. **Model Integration**: Replace `_generate_base_image()` placeholder
2. **Segmentation**: Replace `_remove_background()` placeholder  
3. **Export Formats**: Add new export methods
4. **UI Enhancements**: Add more input parameters
5. **Performance**: Add model caching and optimization

## H100 GPU Optimization

The node is designed to leverage H100 capabilities:
- Model loading detection with CUDA support
- Batch processing ready
- Mixed precision support (TODO)
- Multi-GPU scaling (TODO)

This provides a solid foundation for the hackathon implementation while maintaining professional ComfyUI integration standards.
