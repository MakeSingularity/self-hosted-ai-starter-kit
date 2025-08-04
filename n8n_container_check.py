#!/usr/bin/env python3
"""
n8n Container Environment Checker
This script is designed to run within the n8n Docker container
and provides comprehensive environment analysis.
"""

import json
import sys
import os
import subprocess
import platform
import psutil
from pathlib import Path
from datetime import datetime

def get_container_info():
    """Get information about the container environment"""
    container_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }
    
    # Check if we're in a Docker container
    try:
        with open('/proc/1/cgroup', 'r') as f:
            content = f.read()
            container_info["is_docker"] = 'docker' in content or 'containerd' in content
    except:
        container_info["is_docker"] = False
    
    # Check for container-specific files
    container_files = [
        '/.dockerenv',
        '/proc/self/cgroup',
        '/etc/hostname'
    ]
    
    container_info["container_indicators"] = []
    for file_path in container_files:
        if os.path.exists(file_path):
            container_info["container_indicators"].append(file_path)
    
    return container_info

def get_system_resources():
    """Get system resource information"""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_count = psutil.cpu_count()
        
        return {
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": round((disk.used / disk.total) * 100, 2)
            },
            "cpu": {
                "count": cpu_count,
                "logical_count": psutil.cpu_count(logical=True)
            }
        }
    except Exception as e:
        return {"error": str(e)}

def check_python_packages():
    """Check available Python packages"""
    required_packages = [
        'requests', 'fastapi', 'uvicorn', 'pydantic', 
        'psutil', 'numpy', 'pandas'
    ]
    
    package_status = {}
    for package in required_packages:
        try:
            __import__(package)
            package_status[package] = "available"
        except ImportError:
            package_status[package] = "missing"
    
    return package_status

def check_file_system():
    """Check file system and important paths"""
    important_paths = {
        "/app": "App directory",
        "/app/scripts": "Scripts directory", 
        "/app/shared": "Shared directory",
        "/app/workspace": "Workspace mount",
        "/usr/bin/python3": "Python executable",
        "/usr/bin/python": "Python symlink"
    }
    
    path_status = {}
    for path, description in important_paths.items():
        path_obj = Path(path)
        path_status[path] = {
            "description": description,
            "exists": path_obj.exists(),
            "is_file": path_obj.is_file() if path_obj.exists() else False,
            "is_dir": path_obj.is_dir() if path_obj.exists() else False,
            "permissions": oct(path_obj.stat().st_mode)[-3:] if path_obj.exists() else None
        }
    
    return path_status

def check_network_connectivity():
    """Check network connectivity to key services"""
    services = {
        "ollama": "http://ollama:11434",
        "postgres": "postgres:5432",
        "qdrant": "http://qdrant:6333"
    }
    
    connectivity = {}
    for service, endpoint in services.items():
        try:
            if endpoint.startswith('http'):
                import requests
                response = requests.get(f"{endpoint}/health", timeout=5)
                connectivity[service] = {
                    "status": "reachable",
                    "response_code": response.status_code,
                    "endpoint": endpoint
                }
            else:
                # For non-HTTP services, try a simple socket connection
                import socket
                host, port = endpoint.split(':')
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, int(port)))
                sock.close()
                connectivity[service] = {
                    "status": "reachable" if result == 0 else "unreachable",
                    "endpoint": endpoint
                }
        except Exception as e:
            connectivity[service] = {
                "status": "error",
                "error": str(e),
                "endpoint": endpoint
            }
    
    return connectivity

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, 
            text=True, timeout=30
        )
        return {
            "success": True,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "timeout": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main function to gather all environment information"""
    
    print("🔍 n8n Container Environment Analysis")
    print("=" * 40)
    
    # Gather all information
    environment_data = {
        "timestamp": datetime.now().isoformat(),
        "container_info": get_container_info(),
        "system_resources": get_system_resources(),
        "python_packages": check_python_packages(),
        "file_system": check_file_system(),
        "network_connectivity": check_network_connectivity(),
        "environment_variables": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set"),
            "PYTHON_UNBUFFERED": os.environ.get("PYTHON_UNBUFFERED", "Not set"),
            "OLLAMA_HOST": os.environ.get("OLLAMA_HOST", "Not set"),
            "N8N_HOST": os.environ.get("N8N_HOST", "Not set")
        }
    }
    
    # Test some commands
    commands_to_test = [
        "whoami",
        "pwd",
        "ls -la /app",
        "python3 --version",
        "pip3 --version",
        "df -h"
    ]
    
    command_results = {}
    for cmd in commands_to_test:
        print(f"Running: {cmd}")
        command_results[cmd] = run_command(cmd)
    
    environment_data["command_tests"] = command_results
    
    # Output results
    print("\n📊 Environment Summary:")
    print(f"Container: {'Yes' if environment_data['container_info']['is_docker'] else 'No'}")
    print(f"Python: {environment_data['container_info']['python_version']}")
    print(f"Memory: {environment_data['system_resources'].get('memory', {}).get('total_gb', 'Unknown')}GB")
    print(f"CPU Cores: {environment_data['system_resources'].get('cpu', {}).get('count', 'Unknown')}")
    
    # Save to shared directory
    shared_dir = Path("/app/shared")
    if shared_dir.exists():
        output_file = shared_dir / "n8n-container-environment.json"
        try:
            with open(output_file, 'w') as f:
                json.dump(environment_data, f, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    # Output JSON for n8n to capture
    print("\n📄 JSON Output:")
    print(json.dumps(environment_data, indent=2))
    
    return environment_data

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "success": False
        }
        print(json.dumps(error_data, indent=2))
        sys.exit(1)
