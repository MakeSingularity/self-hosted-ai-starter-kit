#!/usr/bin/env python3
"""
AI Workflow Setup Script

This script prepares your environment for the AI Setup & Monitoring workflow.
It ensures all dependencies are installed and services are configured properly.
"""

import subprocess
import sys
import os
from pathlib import Path
import json

def print_header():
    """Print setup header"""
    print("🔧 AI Workflow Setup")
    print("=" * 30)
    print("Preparing your environment for intelligent AI monitoring...")
    print()

def ensure_shared_directory():
    """Ensure shared directory exists with proper permissions"""
    print("📁 Setting up shared directory...")
    
    shared_dir = Path("shared")
    shared_dir.mkdir(exist_ok=True)
    
    # Create placeholder files
    placeholder_json = shared_dir / "ai-setup-status-report.json"
    placeholder_txt = shared_dir / "ai-setup-status-report.txt"
    
    if not placeholder_json.exists():
        placeholder_data = {
            "timestamp": "1970-01-01T00:00:00.000Z",
            "status": "placeholder",
            "message": "Waiting for first workflow execution..."
        }
        with open(placeholder_json, 'w') as f:
            json.dump(placeholder_data, f, indent=2)
    
    if not placeholder_txt.exists():
        with open(placeholder_txt, 'w') as f:
            f.write("AI Setup Status Report\n")
            f.write("=" * 30 + "\n")
            f.write("Waiting for first workflow execution...\n")
            f.write("Run the n8n workflow to generate detailed reports.\n")
    
    print("✅ Shared directory ready")

def check_python_packages():
    """Check if required Python packages are installed"""
    print("🐍 Checking Python packages...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "requests",
        "psutil"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages, check=True)
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    
    return True

def start_environment_detector():
    """Start the environment detector API if not running"""
    print("🔍 Checking environment detector...")
    
    try:
        import requests
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Environment detector already running")
            return True
    except:
        pass
    
    print("🚀 Starting environment detector...")
    
    # Check if environment_detector.py exists
    detector_path = Path("examples/environment_detector.py")
    if not detector_path.exists():
        print("❌ environment_detector.py not found")
        return False
    
    try:
        # Start the environment detector in background
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                sys.executable, str(detector_path)
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen([
                sys.executable, str(detector_path)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Environment detector started")
        print("   Access at: http://localhost:8002/docs")
        return True
    except Exception as e:
        print(f"❌ Failed to start environment detector: {e}")
        return False

def validate_docker():
    """Validate Docker setup"""
    print("🐳 Validating Docker setup...")
    
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker available")
        else:
            print("❌ Docker not working")
            return False
    except FileNotFoundError:
        print("❌ Docker not found")
        return False
    
    # Check docker-compose
    compose_file = Path("docker-compose.yml")
    if compose_file.exists():
        print("✅ docker-compose.yml found")
    else:
        print("❌ docker-compose.yml not found")
        return False
    
    return True

def show_workflow_import_instructions():
    """Show instructions for importing the workflow"""
    print("\n📋 n8n Workflow Import Instructions:")
    print("=" * 40)
    print("1. 🌐 Open n8n in your browser:")
    print("   http://localhost:5678")
    print()
    print("2. 📥 Import the workflow:")
    print("   • Click 'Import from file' or use Ctrl+I")
    print("   • Select: n8n/demo-data/workflows/ai-setup-and-monitoring-workflow.json")
    print("   • Click 'Import'")
    print()
    print("3. 🚀 Run the workflow:")
    print("   • Click the 'Manual Setup Trigger' node")
    print("   • Click 'Execute Node' to run")
    print()
    print("4. 📊 View results:")
    print("   • Check shared/ai-setup-status-report.txt for human-readable report")
    print("   • Check shared/ai-setup-status-report.json for detailed data")

def show_demo_info():
    """Show information about the demo script"""
    print("\n🎮 Demo Script Available:")
    print("=" * 25)
    print("Run the monitoring demo to see the AI analysis in action:")
    print("   python examples/ai_monitoring_demo.py")
    print()
    print("This script demonstrates:")
    print("• Environment detection")
    print("• Service health checking") 
    print("• AI-powered analysis")
    print("• Performance scoring")
    print("• Intelligent recommendations")

def main():
    """Main setup function"""
    print_header()
    
    # Setup shared directory
    ensure_shared_directory()
    
    # Check Python packages
    if not check_python_packages():
        print("\n❌ Setup failed - package installation issues")
        return False
    
    # Validate Docker
    docker_ok = validate_docker()
    if not docker_ok:
        print("⚠️  Docker issues detected - some features may be limited")
    
    # Start environment detector
    start_environment_detector()
    
    # Show import instructions
    show_workflow_import_instructions()
    
    # Show demo info
    show_demo_info()
    
    print("\n🎉 Setup Complete!")
    print("=" * 20)
    print("Your environment is ready for the AI Setup & Monitoring workflow!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)
