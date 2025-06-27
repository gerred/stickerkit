#!/bin/bash

# Model Download Script for ComfyUI Hackathon
# Downloads essential models for development and testing

set -e

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

# Default model directory
MODELS_DIR=${MODELS_DIR:-"$(pwd)/models"}

echo "🎯 Downloading ComfyUI Models for Hackathon"
echo "Models directory: $MODELS_DIR"

# Create model directories
mkdir -p "$MODELS_DIR"/{checkpoints,vae,loras,controlnet,upscale_models,clip_vision,embeddings}

# Function to download with progress
download_with_progress() {
    local url="$1"
    local output="$2"
    local description="$3"
    
    echo "📥 Downloading $description..."
    if [ ! -f "$output" ]; then
        curl -L --progress-bar "$url" -o "$output"
        echo "✅ Downloaded: $(basename "$output")"
    else
        echo "⏭️  Already exists: $(basename "$output")"
    fi
}

# FLUX Models (Recommended for hackathon)
echo "🌟 Downloading FLUX Models..."

# FLUX.1-schnell (4-step model, great for fast iteration)
download_with_progress \
    "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors" \
    "$MODELS_DIR/checkpoints/flux1-schnell.safetensors" \
    "FLUX.1-schnell checkpoint"

# FLUX VAE
download_with_progress \
    "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors" \
    "$MODELS_DIR/vae/flux-vae.safetensors" \
    "FLUX VAE"

# FLUX Text Encoders
mkdir -p "$MODELS_DIR/clip"
download_with_progress \
    "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors" \
    "$MODELS_DIR/clip/clip_l.safetensors" \
    "FLUX CLIP-L text encoder"

download_with_progress \
    "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors" \
    "$MODELS_DIR/clip/t5xxl_fp16.safetensors" \
    "FLUX T5-XXL text encoder"

# SDXL Base Model (fallback option)
echo "🎨 Downloading SDXL Base Model..."
download_with_progress \
    "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
    "$MODELS_DIR/checkpoints/sd_xl_base_1.0.safetensors" \
    "SDXL Base 1.0"

# SDXL VAE
download_with_progress \
    "https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors" \
    "$MODELS_DIR/vae/sdxl_vae.safetensors" \
    "SDXL VAE"

# ControlNet Models
echo "🎮 Downloading ControlNet Models..."
download_with_progress \
    "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/diffusers_xl_canny_full.safetensors" \
    "$MODELS_DIR/controlnet/diffusers_xl_canny_full.safetensors" \
    "SDXL Canny ControlNet"

download_with_progress \
    "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/diffusers_xl_depth_full.safetensors" \
    "$MODELS_DIR/controlnet/diffusers_xl_depth_full.safetensors" \
    "SDXL Depth ControlNet"

# Upscaler Models
echo "⬆️ Downloading Upscaler Models..."
download_with_progress \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" \
    "$MODELS_DIR/upscale_models/RealESRGAN_x4plus.pth" \
    "RealESRGAN 4x Upscaler"

# LORAs for experimentation
echo "🎭 Downloading Popular LORAs..."
mkdir -p "$MODELS_DIR/loras"

# Popular style LORAs
download_with_progress \
    "https://civitai.com/api/download/models/16677" \
    "$MODELS_DIR/loras/add_detail.safetensors" \
    "Add Detail LORA"

# Embeddings
echo "🎯 Downloading Negative Embeddings..."
download_with_progress \
    "https://huggingface.co/embed/negative/resolve/main/bad-hands-5.pt" \
    "$MODELS_DIR/embeddings/bad-hands-5.pt" \
    "Bad Hands Negative Embedding"

echo ""
echo "✅ Model download complete!"
echo ""
echo "📊 Storage usage:"
du -sh "$MODELS_DIR"/*
echo ""
echo "🎯 Quick start models ready:"
echo "  • FLUX.1-schnell (fast, 4-step generation)"
echo "  • SDXL Base (high quality, slower)"
echo "  • ControlNet (Canny, Depth)"
echo "  • RealESRGAN (4x upscaling)"
echo ""
echo "💡 Pro tip: Start with FLUX.1-schnell for rapid prototyping!"
