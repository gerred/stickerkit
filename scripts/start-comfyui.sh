#!/bin/bash

# ComfyUI Server Startup Script for Development

set -e

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

# Default values
HOST=${COMFYUI_HOST:-"127.0.0.1"}
PORT=${COMFYUI_PORT:-"8188"}
GPU_MODE=${GPU_MODE:-"auto"}

echo "🎨 Starting ComfyUI Development Server"
echo "Host: $HOST"
echo "Port: $PORT"
echo "GPU Mode: $GPU_MODE"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./scripts/setup-dev.sh first"
    exit 1
fi

# Change to ComfyUI directory
if [ ! -d "ComfyUI" ]; then
    echo "❌ ComfyUI not found. Run ./scripts/setup-dev.sh first"
    exit 1
fi

cd ComfyUI

# Build command arguments
ARGS=""

# GPU/CPU mode
if [ "$GPU_MODE" = "cpu" ]; then
    ARGS="$ARGS --cpu"
elif [ "$GPU_MODE" = "auto" ]; then
    # Let ComfyUI auto-detect
    :
fi

# Network settings
ARGS="$ARGS --listen $HOST --port $PORT"

# Add extra arguments from environment
if [ -n "$COMFYUI_EXTRA_ARGS" ]; then
    ARGS="$ARGS $COMFYUI_EXTRA_ARGS"
fi

# Create log directory
mkdir -p ../logs

echo "🚀 Starting ComfyUI with arguments: $ARGS"
echo "📝 Logs will be saved to logs/comfyui.log"
echo "🌐 Web UI will be available at: http://$HOST:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start ComfyUI server with logging
python main.py $ARGS 2>&1 | tee ../logs/comfyui.log
