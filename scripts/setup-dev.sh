#!/bin/bash

# ComfyUI Hackathon Development Setup Script
# For macOS with remote K8s cluster connection

set -e

echo "🚀 Setting up ComfyUI Hackathon Development Environment"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  This script is designed for macOS. Proceed with caution."
fi

# Create project directories
echo "📁 Creating project directories..."
mkdir -p models/{checkpoints,vae,loras,controlnet,upscale_models,clip_vision,embeddings}
mkdir -p output
mkdir -p custom_nodes
mkdir -p logs
mkdir -p temp
mkdir -p scripts
mkdir -p workflows/examples
mkdir -p .vscode

# Check for Python 3.12+
echo "🐍 Checking Python version..."
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12+ is required. Please install via Homebrew:"
    echo "   brew install python@3.12"
    exit 1
fi

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3.12 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install uv for faster package management
echo "📦 Updating package managers..."
pip install --upgrade pip uv

# Install dependencies
echo "📚 Installing Python dependencies..."
uv pip install -r requirements.txt

# Install ComfyUI
echo "🎨 Installing ComfyUI..."
if [ ! -d "ComfyUI" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI
    uv pip install -r requirements.txt
    cd ..
fi

# Install common custom nodes
echo "🔌 Installing popular custom nodes..."
cd ComfyUI/custom_nodes

# ComfyUI Manager (essential for node management)
if [ ! -d "ComfyUI-Manager" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi

# ControlNet Auxiliary Preprocessors
if [ ! -d "comfyui_controlnet_aux" ]; then
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
fi

# Impact Pack (workflow utilities)
if [ ! -d "ComfyUI-Impact-Pack" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
fi

cd ../..

# Setup environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "📝 Please edit .env file with your specific settings"
fi

# Install kubectl if not present (for K8s cluster access)
if ! command -v kubectl &> /dev/null; then
    echo "☸️ Installing kubectl..."
    brew install kubectl
fi

# Install development tools
echo "🛠️ Installing development tools..."
uv pip install black isort flake8 pytest pytest-asyncio jupyter ipykernel

# Setup Jupyter kernel
python -m ipykernel install --user --name hackathon --display-name "ComfyUI Hackathon"

# Make scripts executable
chmod +x scripts/*.sh

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your settings"
echo "2. Run ./scripts/download-models.sh to download base models"
echo "3. Run ./scripts/test-setup.sh to verify everything works"
echo "4. Open project in VS Code: code ."
echo ""
echo "To activate the environment: source .venv/bin/activate"
