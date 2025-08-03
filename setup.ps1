# Self-Hosted AI Starter Kit - One-Click Setup Script
# This script sets up everything needed to run the AI starter kit

param(
    [string]$Profile = "cpu",  # Options: cpu, gpu-nvidia, gpu-amd
    [switch]$SkipPython = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host @"
Self-Hosted AI Starter Kit Setup

Usage: .\setup.ps1 [-Profile <cpu|gpu-nvidia|gpu-amd>] [-SkipPython] [-Help]

Parameters:
  -Profile      Hardware profile to use (default: cpu)
                Options: cpu, gpu-nvidia, gpu-amd
  -SkipPython   Skip Python environment setup
  -Help         Show this help message

Examples:
  .\setup.ps1                           # Setup with CPU profile
  .\setup.ps1 -Profile gpu-nvidia       # Setup with NVIDIA GPU support
  .\setup.ps1 -SkipPython               # Skip Python setup, only Docker
"@
    exit 0
}

Write-Host "Self-Hosted AI Starter Kit Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if Docker is installed and running
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not found"
    }
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker is not installed or not running" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and try again" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host ".env file created. Please review and update if needed." -ForegroundColor Green
    } else {
        Write-Host "No .env file found. Please create one with required environment variables." -ForegroundColor Red
        exit 1
    }
}

# Python Environment Setup (if not skipped)
if (!$SkipPython) {
    Write-Host "Setting up Python environment..." -ForegroundColor Yellow
    
    # Check if conda is available
    try {
        $condaVersion = conda --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Conda not found"
        }
        Write-Host "Conda found: $condaVersion" -ForegroundColor Green
    } catch {
        Write-Host "Conda not found. Installing Miniconda..." -ForegroundColor Yellow
        
        # Download and install Miniconda
        $minicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
        $minicondaInstaller = "$env:TEMP\Miniconda3-latest-Windows-x86_64.exe"
        
        Write-Host "Downloading Miniconda..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $minicondaUrl -OutFile $minicondaInstaller
        
        Write-Host "Installing Miniconda..." -ForegroundColor Yellow
        Start-Process -FilePath $minicondaInstaller -ArgumentList "/S" -Wait
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        Write-Host "Miniconda installed" -ForegroundColor Green
    }
    
    # Create conda environment
    $envName = "ai-starter-kit"
    Write-Host "Creating conda environment: $envName..." -ForegroundColor Yellow
    
    # Accept conda Terms of Service for default channels to avoid TOS errors
    Write-Host "Configuring conda channels and accepting Terms of Service..." -ForegroundColor Yellow
    conda config --set channel_priority flexible 2>$null
    conda config --add channels conda-forge 2>$null
    
    # Accept TOS for the main conda channels
    conda config --set channel_alias https://repo.anaconda.com/pkgs 2>$null
    
    # Create environment using conda-forge channel to avoid TOS issues
    conda create -n $envName python=3.11 -c conda-forge -y
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create conda environment" -ForegroundColor Red
        exit 1
    }
    
    # Activate environment and install packages
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    
    # Create requirements.txt if it doesn't exist
    if (!(Test-Path "requirements.txt")) {
        $requirements = @"
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
"@
        $requirements | Out-File -FilePath "requirements.txt" -Encoding UTF8
        Write-Host "Created requirements.txt with common AI packages" -ForegroundColor Green
    }
    
    # Install packages in the conda environment
    conda run -n $envName pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install Python packages" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Python environment setup complete" -ForegroundColor Green
    Write-Host "To activate the environment, run: conda activate $envName" -ForegroundColor Cyan
}

# Docker Setup
Write-Host "Setting up Docker environment..." -ForegroundColor Yellow

# Pull required images
Write-Host "Pulling Docker images..." -ForegroundColor Yellow
docker compose pull

# Start the services
Write-Host "Starting services with profile: $Profile..." -ForegroundColor Yellow
docker compose --profile $Profile up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "All services started successfully!" -ForegroundColor Green
    Write-Host "" -ForegroundColor White
    Write-Host "Services running at:" -ForegroundColor Cyan
    Write-Host "  • n8n:      http://localhost:5678" -ForegroundColor White
    Write-Host "  • Qdrant:   http://localhost:6333" -ForegroundColor White
    Write-Host "  • Ollama:   http://localhost:11434" -ForegroundColor White
    Write-Host "  • Postgres: localhost:5432" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "To view logs: docker compose logs -f" -ForegroundColor Cyan
    Write-Host "To stop:     docker compose down" -ForegroundColor Cyan
    
    if (!$SkipPython) {
        Write-Host "Python env:  conda activate ai-starter-kit" -ForegroundColor Cyan
    }
} else {
    Write-Host "Failed to start services. Check logs with: docker compose logs" -ForegroundColor Red
    exit 1
}

Write-Host "" -ForegroundColor White
Write-Host "Setup complete! Your self-hosted AI starter kit is ready!" -ForegroundColor Green
