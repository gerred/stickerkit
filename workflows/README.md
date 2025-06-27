# ComfyUI Hackathon Workflows

This directory contains example workflows and templates for the ComfyUI hackathon.

## Example Workflows

### 1. Basic FLUX Generation (`basic_flux.json`)
- **Purpose**: Fast image generation using FLUX.1-schnell
- **Features**: 4-step generation, minimal setup
- **Use Case**: Rapid prototyping and iteration
- **Models Required**: 
  - `flux1-schnell.safetensors`
  - FLUX text encoders (`clip_l.safetensors`, `t5xxl_fp16.safetensors`)

### 2. ControlNet Workflow (`controlnet_workflow.json`)
- **Purpose**: Controlled image generation using edge detection
- **Features**: Canny edge detection, precise composition control
- **Use Case**: Architecture, product design, specific layouts
- **Models Required**:
  - `sd_xl_base_1.0.safetensors`
  - `diffusers_xl_canny_full.safetensors`

### 3. Upscale Workflow (`upscale_workflow.json`)
- **Purpose**: Enhance and upscale existing images
- **Features**: AI upscaling with detail enhancement
- **Use Case**: Improving low-resolution images, final output polish
- **Models Required**:
  - `sd_xl_base_1.0.safetensors`
  - `RealESRGAN_x4plus.pth`

## How to Use Workflows

### Method 1: ComfyUI Web Interface
1. Start ComfyUI server: `./scripts/start-comfyui.sh`
2. Open browser to http://127.0.0.1:8188
3. Load workflow: Drag and drop JSON file or use "Load" button
4. Modify parameters as needed
5. Click "Queue Prompt" to generate

### Method 2: API (Advanced)
```bash
# Execute workflow via API
curl -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  -d @workflows/examples/basic_flux.json
```

### Method 3: Debug Script
```bash
# Validate workflow before execution
./scripts/debug-workflow.sh workflows/examples/basic_flux.json
```

## Creating Custom Workflows

### Workflow Structure
```json
{
  "node_id": {
    "inputs": {
      "parameter": "value",
      "connection": ["source_node_id", output_index]
    },
    "class_type": "NodeClassName",
    "_meta": {
      "title": "Display Name"
    }
  }
}
```

### Common Node Types
- **CheckpointLoaderSimple**: Load base models
- **FluxLoader**: Load FLUX models
- **CLIPTextEncode**: Text to conditioning
- **KSampler**: Generation/denoising
- **VAEDecode/VAEEncode**: Latent space conversion
- **SaveImage**: Output results
- **ControlNetLoader**: Load ControlNet models
- **UpscaleModelLoader**: Load upscaling models

### Best Practices

1. **Model Compatibility**: Ensure model files match workflow requirements
2. **Resource Management**: Monitor VRAM usage with large models
3. **Parameter Tuning**:
   - FLUX: Low CFG (1.0-2.0), few steps (4-8)
   - SDXL: Higher CFG (6.0-8.0), more steps (15-25)
4. **Batch Processing**: Adjust batch_size based on available memory
5. **Error Handling**: Use debug script to validate before execution

## Hackathon Tips

### Rapid Development
- Start with `basic_flux.json` for quick iterations
- Use low step counts during development
- Test with small resolutions first (512x512)

### Performance Optimization
- Monitor GPU memory usage
- Use CPU mode for workflow testing: `--cpu` flag
- Cache frequently used models locally

### Troubleshooting
```bash
# Check model files
ls -la models/checkpoints/
ls -la models/vae/

# Validate workflow
./scripts/debug-workflow.sh your_workflow.json

# Check ComfyUI logs
tail -f logs/comfyui.log
```

### Integration with K8s
- Test workflows locally first
- Use environment variables for model paths
- Consider model size limits in cluster deployment

## Resources

- [ComfyUI Documentation](https://github.com/comfyanonymous/ComfyUI)
- [FLUX Models](https://huggingface.co/black-forest-labs)
- [ControlNet Collection](https://huggingface.co/lllyasviel/sd_control_collection)
- [Community Workflows](https://comfyworkflows.com/)

Happy hacking! 🎨🚀
