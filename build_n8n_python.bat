@echo off
REM Build and Deploy n8n with Python Support - Windows Version

echo 🚀 Building n8n with Python Support
echo =====================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Build the custom n8n image
echo 🔨 Building custom n8n-python image...
docker build -f Dockerfile.n8n-python -t n8n-python:latest .

if %errorlevel% equ 0 (
    echo ✅ n8n-python image built successfully
) else (
    echo ❌ Failed to build n8n-python image
    exit /b 1
)

REM Stop existing services
echo 🛑 Stopping existing services...
docker-compose down

REM Start services with new image
echo 🚀 Starting services with Python support...
docker-compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to initialize...
timeout /t 30 /nobreak

REM Check service status
echo 🔍 Checking service status...
docker-compose ps

REM Test Python in n8n container
echo 🐍 Testing Python in n8n container...
docker-compose exec n8n python3 --version

if %errorlevel% equ 0 (
    echo ✅ Python is working in n8n container!
) else (
    echo ❌ Python test failed in n8n container
)

REM Test our custom script
echo 🧪 Testing custom environment checker...
docker-compose exec n8n python3 /app/n8n_container_check.py

echo.
echo 🎉 Setup Complete!
echo ===================
echo • n8n with Python: http://localhost:5678
echo • Import workflow: n8n/demo-data/workflows/ai-setup-and-monitoring-workflow.json
echo • Python scripts are available in the n8n container at /app/scripts/
echo • Shared directory: /app/shared/

pause
