# n8n with Python Integration Guide

## Overview

This guide shows how to integrate Python scripts with n8n using a custom Docker image. This approach provides full Python functionality with external libraries, unlike the limited Code node.

## 🚀 Quick Setup

### Windows Users:
```cmd
build_n8n_python.bat
```

### Linux/Mac Users:
```bash
chmod +x build_n8n_python.sh
./build_n8n_python.sh
```

## 🔧 Manual Setup

### 1. Build Custom n8n Image

```bash
# Build the custom image
docker build -f Dockerfile.n8n-python -t n8n-python:latest .

# Verify the build
docker images | grep n8n-python
```

### 2. Update Docker Compose

The `docker-compose.yml` has been updated to use `n8n-python:latest` instead of the default n8n image.

Key changes:
- **Custom Image**: Uses `n8n-python:latest`
- **Volume Mounts**: Maps scripts and shared directories
- **Environment Variables**: Adds Python-specific environment variables

### 3. Start Services

```bash
# Stop existing services
docker-compose down

# Start with new image
docker-compose up -d

# Check status
docker-compose ps
```

## 🐍 Python Integration Features

### Available in n8n Container:

1. **Python 3** with pip
2. **Common AI/ML Libraries**:
   - requests, fastapi, uvicorn
   - pydantic, python-dotenv
   - psutil, numpy, pandas
   - All packages from requirements.txt

3. **File System Access**:
   - `/app/scripts/` - Your Python scripts
   - `/app/shared/` - Shared data directory  
   - `/app/workspace/` - Project root (read-only)

4. **Environment Variables**:
   - `PYTHONPATH=/app`
   - `PYTHON_UNBUFFERED=1`
   - All n8n environment variables

## 📋 Using Execute Command Node

### Basic Python Script Execution:

```json
{
  "command": "python3",
  "additionalFlags": {
    "flags": ["/app/scripts/your_script.py"]
  },
  "options": {
    "cwd": "/app"
  }
}
```

### Passing Data to Python:

#### Method 1: Command Line Arguments
```json
{
  "command": "python3",
  "additionalFlags": {
    "flags": [
      "/app/scripts/process_data.py",
      "{{ $json.input_value }}",
      "--format", "json"
    ]
  }
}
```

#### Method 2: Environment Variables
```json
{
  "command": "python3",
  "additionalFlags": {
    "flags": ["/app/scripts/env_script.py"]
  },
  "options": {
    "env": {
      "INPUT_DATA": "{{ JSON.stringify($json) }}",
      "PROCESSING_MODE": "{{ $json.mode }}"
    }
  }
}
```

#### Method 3: Temporary Files
```json
{
  "command": "sh",
  "additionalFlags": {
    "flags": [
      "-c",
      "echo '{{ JSON.stringify($json) }}' > /tmp/input.json && python3 /app/scripts/file_processor.py /tmp/input.json"
    ]
  }
}
```

## 📊 Example Python Scripts

### 1. Environment Checker (`n8n_container_check.py`)

Already included! Provides comprehensive environment analysis:
- Container information
- System resources
- Network connectivity
- File system status
- Python package availability

Usage in n8n:
```json
{
  "command": "python3",
  "additionalFlags": {
    "flags": ["/app/n8n_container_check.py"]
  }
}
```

### 2. Data Processor Example

Create `/app/scripts/data_processor.py`:
```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def process_data(input_data):
    # Your processing logic here
    result = {
        "processed": True,
        "input_length": len(str(input_data)),
        "timestamp": datetime.now().isoformat()
    }
    return result

if __name__ == "__main__":
    try:
        # Read from command line or stdin
        if len(sys.argv) > 1:
            input_data = sys.argv[1]
        else:
            input_data = sys.stdin.read()
        
        # Process and output JSON
        result = process_data(input_data)
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
```

### 3. AI Service Integration

Create `/app/scripts/ai_service.py`:
```python
#!/usr/bin/env python3
import requests
import json
import os

def query_ollama(prompt, model="llama2"):
    """Query Ollama service"""
    url = f"http://ollama:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(url, json=data)
    return response.json()

def store_in_qdrant(data, collection="n8n_data"):
    """Store data in Qdrant vector database"""
    url = f"http://qdrant:6333/collections/{collection}/points"
    # Implementation depends on your data structure
    pass

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello, world!"
    result = query_ollama(prompt)
    print(json.dumps(result))
```

## 🔍 Workflow Integration

### Updated Workflow Features:

1. **Container-Native Execution**: All Python runs inside n8n container
2. **Proper Path Management**: Uses container file system paths
3. **Resource Sharing**: Access to shared directories and data
4. **Environment Isolation**: Clean, reproducible Python environment

### Key Workflow Nodes:

- **Check Environment**: Runs `n8n_container_check.py`
- **Docker Services**: Checks Docker containers from within n8n
- **AI Analysis**: Enhanced with container-aware logic
- **Auto Setup**: Can start services using container's Docker socket

## 🚨 Troubleshooting

### Common Issues:

1. **Python Script Not Found**
   ```bash
   # Check if script exists in container
   docker-compose exec n8n ls -la /app/scripts/
   ```

2. **Permission Issues**
   ```bash
   # Check file permissions
   docker-compose exec n8n chmod +x /app/scripts/your_script.py
   ```

3. **Missing Python Packages**
   ```bash
   # Install additional packages
   docker-compose exec n8n pip3 install package_name
   
   # Or rebuild image with updated requirements.txt
   docker build -f Dockerfile.n8n-python -t n8n-python:latest .
   ```

4. **Environment Variables**
   ```bash
   # Check environment in container
   docker-compose exec n8n env | grep PYTHON
   ```

### Debug Commands:

```bash
# Access n8n container shell
docker-compose exec n8n sh

# Test Python
docker-compose exec n8n python3 --version

# List available packages
docker-compose exec n8n pip3 list

# Check file system
docker-compose exec n8n find /app -type f -name "*.py"
```

## 🎯 Best Practices

### 1. Error Handling
Always output JSON from Python scripts:
```python
try:
    result = process_data()
    print(json.dumps({"success": True, "data": result}))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
```

### 2. Logging
Use structured logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 3. Resource Management
- Use timeouts for external API calls
- Clean up temporary files
- Handle large data sets efficiently

### 4. Security
- Validate input data
- Use environment variables for secrets
- Avoid shell injection

## 🔗 Integration Examples

### Slack Notifications:
```python
#!/usr/bin/env python3
import requests
import os

def send_slack_message(message, webhook_url):
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

if __name__ == "__main__":
    message = sys.argv[1]
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    success = send_slack_message(message, webhook)
    print(json.dumps({"sent": success}))
```

### Data Analysis:
```python
#!/usr/bin/env python3
import pandas as pd
import json

def analyze_data(csv_path):
    df = pd.read_csv(csv_path)
    stats = {
        "rows": len(df),
        "columns": list(df.columns),
        "summary": df.describe().to_dict()
    }
    return stats

if __name__ == "__main__":
    csv_file = sys.argv[1]
    result = analyze_data(csv_file)
    print(json.dumps(result))
```

## 🎉 Next Steps

1. **Import Updated Workflow**: Use the new `ai-setup-and-monitoring-workflow.json`
2. **Create Custom Scripts**: Add your Python scripts to `/app/scripts/`
3. **Test Integration**: Run the workflow to verify Python execution
4. **Extend Functionality**: Add more AI services and data processing

This setup provides a robust foundation for integrating Python with n8n, enabling complex AI workflows with full library support!
