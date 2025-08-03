#!/usr/bin/env python3
"""
Quick Start Script for Self-Hosted AI Starter Kit
This script will guide you through the setup process step by step.

Run this script first to ensure everything is properly configured.
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("🚀 Self-Hosted AI Starter Kit - Quick Start")
    print("=" * 50)
    print("This script will help you get started quickly!")
    print()

def check_python():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        print("💡 Please install Python 3.8 or newer")
        return False

def check_docker():
    """Check if Docker is available"""
    print("🐳 Checking Docker...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker not working properly")
            return False
    except FileNotFoundError:
        print("❌ Docker not found")
        print("💡 Install Docker Desktop: https://www.docker.com/products/docker-desktop")
        return False

def install_basic_requirements():
    """Install basic Python requirements"""
    print("📦 Installing basic requirements...")
    
    basic_packages = [
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0", 
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0"
    ]
    
    try:
        for package in basic_packages:
            print(f"   Installing {package.split('>=')[0]}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install {package}")
                return False
        
        print("✅ Basic requirements installed")
        return True
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        return False

def test_api_server():
    """Test if the API server can start"""
    print("🧪 Testing API server...")
    
    try:
        # Try importing the main components
        import fastapi
        import uvicorn
        import pydantic
        print("✅ API server components available")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n🎉 Setup Complete!")
    print("=" * 30)
    print("Next steps:")
    print("1. 🐳 Start Docker services:")
    print("   docker-compose up -d")
    print()
    print("2. 🚀 Start the API server:")
    print("   python examples/api_server.py")
    print()
    print("3. 🌐 Open n8n in your browser:")
    print("   http://localhost:5678")
    print()
    print("4. 📚 View API documentation:")
    print("   http://localhost:8000/docs")
    print()
    print("5. 📖 Read the documentation:")
    print("   README.md - Main guide")
    print("   docs/SETUP_GUIDE.md - Detailed setup")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Step 1: Check Python
    if not check_python():
        print("\n❌ Setup failed - Python version issue")
        return False
    
    # Step 2: Check Docker
    docker_available = check_docker()
    if not docker_available:
        print("⚠️  Docker not available - some features will be limited")
        print("💡 You can still use the Python API server")
    
    # Step 3: Install basic requirements
    print("\n📦 Setting up Python environment...")
    if not install_basic_requirements():
        print("\n❌ Failed to install basic requirements")
        print("💡 Try running manually: pip install -r requirements.txt")
        return False
    
    # Step 4: Test components
    if not test_api_server():
        print("\n❌ API server test failed")
        return False
    
    # Step 5: Show next steps
    show_next_steps()
    
    # Ask if user wants to start services
    if docker_available:
        start_now = input("\nWould you like to start Docker services now? (y/N): ").strip().lower()
        if start_now in ['y', 'yes']:
            print("🐳 Starting Docker services...")
            try:
                subprocess.run(["docker-compose", "up", "-d"], check=True)
                print("✅ Docker services started!")
                print("🌐 n8n is available at: http://localhost:5678")
            except subprocess.CalledProcessError:
                print("❌ Failed to start Docker services")
                print("💡 Try running manually: docker-compose up -d")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
