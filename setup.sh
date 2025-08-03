#!/bin/bash

# Self-Hosted AI Starter Kit - One-Click Setup Script
# This script sets up everything needed to run the AI starter kit

set -e  # Exit on any error

# Default values
PROFILE="cpu"
SKIP_PYTHON=false
SHOW_HELP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --skip-python)
            SKIP_PYTHON=true
            shift
            ;;
        --help)
            SHOW_HELP=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ "$SHOW_HELP" = true ]; then
    cat << EOF
Self-Hosted AI Starter Kit Setup

Usage: ./setup.sh [--profile <cpu|gpu-nvidia|gpu-amd>] [--skip-python] [--help]

Parameters:
  --profile      Hardware profile to use (default: cpu)
                 Options: cpu, gpu-nvidia, gpu-amd
  --skip-python  Skip Python environment setup
  --help         Show this help message

Examples:
  ./setup.sh                           # Setup with CPU profile
  ./setup.sh --profile gpu-nvidia      # Setup with NVIDIA GPU support
  ./setup.sh --skip-python             # Skip Python setup, only Docker
EOF
    exit 0
fi

echo "🚀 Self-Hosted AI Starter Kit Setup"
echo "================================================"

# Check if Docker is installed and running
echo "📋 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker and try again"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from .env.example..."
        cp ".env.example" ".env"
        echo "✅ .env file created. Please review and update if needed."
    else
        echo "❌ No .env file found. Please create one with required environment variables."
        exit 1
    fi
fi

# Python Environment Setup (if not skipped)
if [ "$SKIP_PYTHON" = false ]; then
    echo "🐍 Setting up Python environment..."
    
    # Check if conda is available
    if ! command -v conda &> /dev/null; then
        echo "⚠️  Conda not found. Please install Miniconda or Anaconda first."
        echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
        echo ""
        echo "Or run with --skip-python to skip Python environment setup"
        exit 1
    fi
    
    echo "✅ Conda found: $(conda --version)"
    
    # Create conda environment
    ENV_NAME="ai-starter-kit"
    echo "🌟 Creating conda environment: $ENV_NAME..."
    
    # Accept conda Terms of Service for default channels to avoid TOS errors
    echo "📋 Configuring conda channels and accepting Terms of Service..."
    conda config --set channel_priority flexible 2>/dev/null
    conda config --add channels conda-forge 2>/dev/null
    
    # Accept TOS for the main conda channels
    conda config --set channel_alias https://repo.anaconda.com/pkgs 2>/dev/null
    
    # Create environment using conda-forge channel to avoid TOS issues
    conda create -n "$ENV_NAME" python=3.11 -c conda-forge -y
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << EOF
# Core AI/ML packages
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0

# NVIDIA Riva dependencies
grpcio>=1.54.0
grpcio-tools>=1.54.0
grpcio-status>=1.54.0

# Vector database and embeddings
qdrant-client>=1.6.0
sentence-transformers>=2.2.0

# API and web frameworks
fastapi>=0.100.0
uvicorn>=0.22.0
requests>=2.31.0

# Data processing
pydantic>=2.0.0
python-dotenv>=1.0.0

# Optional: Jupyter for development
jupyter>=1.0.0
ipykernel>=6.24.0
EOF
        echo "✅ Created requirements.txt with common AI packages"
    fi
    
    # Install packages in the conda environment
    echo "📦 Installing Python packages..."
    conda run -n "$ENV_NAME" pip install -r requirements.txt
    
    echo "✅ Python environment setup complete"
    echo "💡 To activate the environment, run: conda activate $ENV_NAME"
fi

# Docker Setup
echo "🐳 Setting up Docker environment..."

# Pull required images
echo "📥 Pulling Docker images..."
docker compose pull

# Start the services
echo "🚀 Starting services with profile: $PROFILE..."
docker compose --profile "$PROFILE" up -d

echo "✅ All services started successfully!"
echo ""
echo "🌐 Services running at:"
echo "  • n8n:      http://localhost:5678"
echo "  • Qdrant:   http://localhost:6333"
echo "  • Ollama:   http://localhost:11434"
echo "  • Postgres: localhost:5432"
echo ""
echo "📋 To view logs: docker compose logs -f"
echo "📋 To stop:     docker compose down"

if [ "$SKIP_PYTHON" = false ]; then
    echo "📋 Python env:  conda activate ai-starter-kit"
fi

echo ""
echo "🎉 Setup complete! Your self-hosted AI starter kit is ready!"
