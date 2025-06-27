FROM nvcr.io/nvidia/pytorch:24.01-py3

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=all

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgoogle-perftools4 \
    libtcmalloc-minimal4 \
    && rm -rf /var/lib/apt/lists/*

# Set memory allocator
ENV LD_PRELOAD=libtcmalloc.so.4

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI

# Set ComfyUI as working directory
WORKDIR /app/ComfyUI

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install additional dependencies for ComfyUI
RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
    xformers \
    accelerate \
    transformers \
    diffusers \
    opencv-python \
    pillow \
    numpy \
    scipy \
    requests \
    tqdm \
    psutil \
    kornia \
    spandrel

# Create directories for models, outputs, and custom nodes
RUN mkdir -p /app/ComfyUI/models/checkpoints \
    /app/ComfyUI/models/vae \
    /app/ComfyUI/models/loras \
    /app/ComfyUI/models/controlnet \
    /app/ComfyUI/models/upscale_models \
    /app/ComfyUI/models/embeddings \
    /app/ComfyUI/output \
    /app/ComfyUI/custom_nodes \
    /app/ComfyUI/input

# Set permissions
RUN chmod -R 755 /app/ComfyUI

# Expose port
EXPOSE 8188

# Create entrypoint script
RUN echo '#!/bin/bash\n\
cd /app/ComfyUI\n\
python main.py --listen 0.0.0.0 --port 8188 "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
