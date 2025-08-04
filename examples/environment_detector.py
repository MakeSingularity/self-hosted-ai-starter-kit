#!/usr/bin/env python3
"""
Environment Detection API for AI Agents
Provides comprehensive environment information for adaptive AI workflows

This API helps AI agents understand their execution context:
- Container vs native environment
- Available resources (CPU, memory, GPU)
- Installed packages and capabilities
- Network connectivity
- File system access
- Hardware information

Usage:
1. Run: python examples/environment_detector.py
2. Use in n8n: HTTP Request to http://localhost:8002/detect-environment
3. AI agents can adapt behavior based on environment info
"""

import sys
import os
import platform
import psutil
import subprocess
import json
import socket
from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib.util

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("💡 Please run: pip install fastapi uvicorn pydantic python-dotenv psutil")
    exit(1)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Environment Detection API",
    description="Comprehensive environment detection for AI agents",
    version="1.0.0"
)

class EnvironmentInfo(BaseModel):
    environment_type: str
    container_info: Dict[str, Any]
    system_info: Dict[str, Any]
    hardware_info: Dict[str, Any]
    software_capabilities: Dict[str, Any]
    network_info: Dict[str, Any]
    ai_capabilities: Dict[str, Any]
    recommendations: List[str]

class EnvironmentDetector:
    """Comprehensive environment detection for AI agents"""
    
    def __init__(self):
        self.info = {}
    
    def detect_container_environment(self) -> Dict[str, Any]:
        """Detect if running in a container and what type"""
        container_info = {
            "is_container": False,
            "container_type": "native",
            "container_runtime": None,
            "docker_available": False,
            "kubernetes": False
        }
        
        # Check for container indicators
        try:
            # Check for Docker
            if os.path.exists("/.dockerenv"):
                container_info.update({
                    "is_container": True,
                    "container_type": "docker",
                    "container_runtime": "docker"
                })
            
            # Check for Kubernetes
            if os.path.exists("/var/run/secrets/kubernetes.io"):
                container_info["kubernetes"] = True
            
            # Check if Docker is available
            try:
                subprocess.run(["docker", "--version"], capture_output=True, check=True)
                container_info["docker_available"] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            # Check cgroup for container indicators
            if os.path.exists("/proc/1/cgroup"):
                with open("/proc/1/cgroup", "r") as f:
                    cgroup_content = f.read()
                    if "docker" in cgroup_content:
                        container_info.update({
                            "is_container": True,
                            "container_type": "docker"
                        })
                    elif "containerd" in cgroup_content:
                        container_info.update({
                            "is_container": True,
                            "container_type": "containerd"
                        })
        
        except Exception as e:
            container_info["detection_error"] = str(e)
        
        return container_info
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "python_version": platform.python_version(),
            "hostname": socket.gethostname(),
            "user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
            "home_directory": str(Path.home()),
            "current_directory": os.getcwd(),
            "environment_variables": {
                key: value for key, value in os.environ.items() 
                if not key.lower().startswith(('password', 'secret', 'key', 'token'))
            }
        }
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware and resource information"""
        hardware = {
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2)
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent,
                "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2)
            }
        }
        
        # Check for GPU
        gpu_info = self.detect_gpu()
        if gpu_info:
            hardware["gpu"] = gpu_info
        
        return hardware
    
    def detect_gpu(self) -> Optional[Dict[str, Any]]:
        """Detect GPU capabilities"""
        gpu_info = {
            "available": False,
            "nvidia_gpu": False,
            "cuda_available": False,
            "devices": []
        }
        
        try:
            # Check for NVIDIA GPU
            result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                gpu_info["nvidia_gpu"] = True
                gpu_info["available"] = True
                
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split(', ')
                        if len(parts) >= 3:
                            gpu_info["devices"].append({
                                "name": parts[0],
                                "memory_total_mb": int(parts[1]),
                                "memory_free_mb": int(parts[2])
                            })
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Check for CUDA
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info["cuda_available"] = True
                gpu_info["cuda_device_count"] = torch.cuda.device_count()
        except ImportError:
            pass
        
        return gpu_info if gpu_info["available"] else None
    
    def check_software_capabilities(self) -> Dict[str, Any]:
        """Check what software and capabilities are available"""
        capabilities = {
            "python_packages": {},
            "system_tools": {},
            "ai_frameworks": {},
            "speech_services": {},
            "databases": {}
        }
        
        # Check Python packages
        packages_to_check = [
            "fastapi", "uvicorn", "pydantic", "requests", "numpy", "pandas",
            "torch", "tensorflow", "transformers", "langchain", "openai",
            "nvidia-riva-client", "soundfile", "pyttsx3", "edge-tts",
            "qdrant-client", "sentence-transformers", "scikit-learn"
        ]
        
        for package in packages_to_check:
            try:
                spec = importlib.util.find_spec(package)
                if spec is not None:
                    try:
                        module = importlib.import_module(package)
                        version = getattr(module, "__version__", "unknown")
                        capabilities["python_packages"][package] = {
                            "available": True,
                            "version": version
                        }
                    except Exception:
                        capabilities["python_packages"][package] = {
                            "available": True,
                            "version": "unknown"
                        }
                else:
                    capabilities["python_packages"][package] = {"available": False}
            except Exception:
                capabilities["python_packages"][package] = {"available": False}
        
        # Check system tools
        tools_to_check = ["docker", "git", "curl", "wget", "ffmpeg"]
        for tool in tools_to_check:
            try:
                result = subprocess.run([tool, "--version"], capture_output=True)
                capabilities["system_tools"][tool] = {"available": result.returncode == 0}
            except FileNotFoundError:
                capabilities["system_tools"][tool] = {"available": False}
        
        # Categorize AI capabilities
        ai_packages = ["torch", "tensorflow", "transformers", "langchain", "openai"]
        capabilities["ai_frameworks"] = {
            pkg: capabilities["python_packages"].get(pkg, {"available": False})
            for pkg in ai_packages
        }
        
        # Speech capabilities
        speech_packages = ["nvidia-riva-client", "soundfile", "pyttsx3", "edge-tts"]
        capabilities["speech_services"] = {
            pkg: capabilities["python_packages"].get(pkg, {"available": False})
            for pkg in speech_packages
        }
        
        # Database capabilities
        db_packages = ["qdrant-client", "sentence-transformers"]
        capabilities["databases"] = {
            pkg: capabilities["python_packages"].get(pkg, {"available": False})
            for pkg in db_packages
        }
        
        return capabilities
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network connectivity information"""
        network_info = {
            "hostname": socket.gethostname(),
            "local_ip": self.get_local_ip(),
            "internet_connectivity": self.check_internet_connectivity(),
            "open_ports": self.check_common_ports(),
            "dns_resolution": self.check_dns_resolution()
        }
        
        return network_info
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "unknown"
    
    def check_internet_connectivity(self) -> bool:
        """Check if internet is available"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def check_common_ports(self) -> Dict[str, bool]:
        """Check if common service ports are open locally"""
        common_ports = {
            "n8n": 5678,
            "api_server": 8000,
            "speech_api": 8001,
            "ollama": 11434,
            "qdrant": 6333,
            "postgres": 5432
        }
        
        port_status = {}
        for service, port in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                port_status[service] = result == 0
                sock.close()
            except Exception:
                port_status[service] = False
        
        return port_status
    
    def check_dns_resolution(self) -> bool:
        """Check if DNS resolution works"""
        try:
            socket.gethostbyname("google.com")
            return True
        except socket.gaierror:
            return False
    
    def get_ai_capabilities(self) -> Dict[str, Any]:
        """Assess AI-specific capabilities"""
        capabilities = {
            "llm_support": False,
            "gpu_acceleration": False,
            "speech_synthesis": False,
            "speech_recognition": False,
            "vector_database": False,
            "recommended_config": {}
        }
        
        software = self.check_software_capabilities()
        hardware = self.get_hardware_info()
        
        # Check LLM support
        if (software["ai_frameworks"]["torch"]["available"] or 
            software["ai_frameworks"]["transformers"]["available"]):
            capabilities["llm_support"] = True
        
        # Check GPU acceleration
        if hardware.get("gpu", {}).get("cuda_available", False):
            capabilities["gpu_acceleration"] = True
        
        # Check speech capabilities
        if (software["speech_services"]["nvidia-riva-client"]["available"] or
            software["speech_services"]["pyttsx3"]["available"]):
            capabilities["speech_synthesis"] = True
            capabilities["speech_recognition"] = True
        
        # Check vector database
        if software["databases"]["qdrant-client"]["available"]:
            capabilities["vector_database"] = True
        
        # Generate recommendations
        recommendations = self.generate_recommendations(capabilities, hardware, software)
        capabilities["recommended_config"] = recommendations
        
        return capabilities
    
    def generate_recommendations(self, ai_caps: Dict, hardware: Dict, software: Dict) -> List[str]:
        """Generate recommendations based on environment"""
        recommendations = []
        
        # Memory recommendations
        memory_gb = hardware["memory"]["total_gb"]
        if memory_gb < 4:
            recommendations.append("⚠️ Low memory detected. Consider lightweight models only.")
        elif memory_gb < 8:
            recommendations.append("💡 Moderate memory. Suitable for small to medium AI models.")
        else:
            recommendations.append("✅ Sufficient memory for large AI models.")
        
        # GPU recommendations
        if hardware.get("gpu", {}).get("available"):
            recommendations.append("🚀 GPU detected. Enable GPU acceleration for faster AI processing.")
        else:
            recommendations.append("💡 No GPU detected. Use CPU-optimized models.")
        
        # Container recommendations
        container_info = self.detect_container_environment()
        if container_info["is_container"]:
            recommendations.append("🐳 Container environment detected. Ensure resource limits are appropriate.")
        
        # Service recommendations
        network_info = self.get_network_info()
        if not network_info["internet_connectivity"]:
            recommendations.append("⚠️ No internet connectivity. Use local models only.")
        
        if network_info["open_ports"]["n8n"]:
            recommendations.append("✅ n8n is running and accessible.")
        else:
            recommendations.append("💡 Start n8n service: docker-compose up -d")
        
        return recommendations
    
    def detect_full_environment(self) -> EnvironmentInfo:
        """Get comprehensive environment information"""
        
        container_info = self.detect_container_environment()
        system_info = self.get_system_info()
        hardware_info = self.get_hardware_info()
        software_capabilities = self.check_software_capabilities()
        network_info = self.get_network_info()
        ai_capabilities = self.get_ai_capabilities()
        
        # Determine environment type
        env_type = "native"
        if container_info["is_container"]:
            env_type = f"container-{container_info['container_type']}"
        elif container_info["kubernetes"]:
            env_type = "kubernetes"
        
        recommendations = ai_capabilities["recommended_config"]
        
        return EnvironmentInfo(
            environment_type=env_type,
            container_info=container_info,
            system_info=system_info,
            hardware_info=hardware_info,
            software_capabilities=software_capabilities,
            network_info=network_info,
            ai_capabilities=ai_capabilities,
            recommendations=recommendations
        )

# Initialize detector
detector = EnvironmentDetector()

@app.get("/")
async def root():
    return {
        "message": "Environment Detection API for AI Agents",
        "endpoints": [
            "/detect-environment - GET - Full environment detection",
            "/quick-check - GET - Quick environment summary",
            "/ai-capabilities - GET - AI-specific capabilities only",
            "/recommendations - GET - Environment-based recommendations",
            "/health - GET - Health check"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "environment-detection"}

@app.get("/detect-environment", response_model=EnvironmentInfo)
async def detect_environment():
    """
    Comprehensive environment detection for AI agents
    Returns detailed information about the execution environment
    """
    try:
        return detector.detect_full_environment()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Environment detection error: {str(e)}")

@app.get("/quick-check")
async def quick_environment_check():
    """
    Quick environment summary for fast decisions
    """
    try:
        container_info = detector.detect_container_environment()
        hardware_info = detector.get_hardware_info()
        network_info = detector.get_network_info()
        
        return {
            "environment_type": "container" if container_info["is_container"] else "native",
            "memory_gb": hardware_info["memory"]["total_gb"],
            "cpu_count": hardware_info["cpu_count"],
            "gpu_available": hardware_info.get("gpu", {}).get("available", False),
            "internet_connected": network_info["internet_connectivity"],
            "services_running": network_info["open_ports"],
            "timestamp": psutil.boot_time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick check error: {str(e)}")

@app.get("/ai-capabilities")
async def get_ai_capabilities():
    """
    AI-specific capabilities assessment
    """
    try:
        return detector.get_ai_capabilities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI capabilities error: {str(e)}")

@app.get("/recommendations")
async def get_recommendations():
    """
    Get environment-based recommendations for AI workflows
    """
    try:
        ai_caps = detector.get_ai_capabilities()
        hardware = detector.get_hardware_info()
        software = detector.check_software_capabilities()
        
        recommendations = detector.generate_recommendations(ai_caps, hardware, software)
        
        return {
            "recommendations": recommendations,
            "summary": {
                "memory_status": "sufficient" if hardware["memory"]["total_gb"] >= 8 else "limited",
                "gpu_status": "available" if hardware.get("gpu", {}).get("available") else "none",
                "ai_ready": ai_caps["llm_support"] and ai_caps["vector_database"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations error: {str(e)}")

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("ENVIRONMENT_API_PORT", 8002))
    
    print(f"🔍 Starting Environment Detection API on port {port}")
    print(f"📝 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print(f"🎯 Quick Check: http://localhost:{port}/quick-check")
    
    uvicorn.run(
        "environment_detector:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
