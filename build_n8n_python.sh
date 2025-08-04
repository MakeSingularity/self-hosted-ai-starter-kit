#!/bin/bash
# Build and Deploy n8n with Python Support

echo "🚀 Building n8n with Python Support"
echo "====================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build the custom n8n image
echo "🔨 Building custom n8n-python image..."
docker build -f Dockerfile.n8n-python -t n8n-python:latest .

if [ $? -eq 0 ]; then
    echo "✅ n8n-python image built successfully"
else
    echo "❌ Failed to build n8n-python image"
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Start services with new image
echo "🚀 Starting services with Python support..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Test Python in n8n container
echo "🐍 Testing Python in n8n container..."
docker-compose exec n8n python3 --version

if [ $? -eq 0 ]; then
    echo "✅ Python is working in n8n container!"
else
    echo "❌ Python test failed in n8n container"
fi

# Test our custom script
echo "🧪 Testing custom environment checker..."
docker-compose exec n8n python3 /app/n8n_container_check.py

echo ""
echo "🎉 Setup Complete!"
echo "==================="
echo "• n8n with Python: http://localhost:5678"
echo "• Import workflow: n8n/demo-data/workflows/ai-setup-and-monitoring-workflow.json"
echo "• Python scripts are available in the n8n container at /app/scripts/"
echo "• Shared directory: /app/shared/"
