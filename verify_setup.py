#!/usr/bin/env python3
"""
Setup Verification Script for Self-Hosted AI Starter Kit
Run this script to verify your environment is properly configured.

Usage: python verify_setup.py
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable"""
    import_name = import_name or package_name
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def install_requirements():
    """Install requirements.txt packages"""
    print("\n🔧 Installing missing packages...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Self-Hosted AI Starter Kit - Setup Verification")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup verification failed - Python version incompatible")
        return False
    
    # Core packages to verify
    core_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("python-dotenv", "dotenv"),
        ("requests", "requests"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    print("\n📦 Checking core packages...")
    missing_packages = []
    
    for package_name, import_name in core_packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    # If packages are missing, try to install them
    if missing_packages:
        print(f"\n⚠️  Found {len(missing_packages)} missing packages")
        user_input = input("Would you like to install missing packages? (y/N): ").lower().strip()
        
        if user_input in ['y', 'yes']:
            if install_requirements():
                print("\n🔄 Re-checking packages after installation...")
                missing_after_install = []
                for package_name, import_name in core_packages:
                    if not check_package(package_name, import_name):
                        missing_after_install.append(package_name)
                
                if not missing_after_install:
                    print("\n✅ All core packages are now installed!")
                else:
                    print(f"\n⚠️  Still missing: {', '.join(missing_after_install)}")
                    print("💡 Try running: pip install -r requirements.txt")
            else:
                print("\n❌ Failed to install packages automatically")
                print("💡 Try running manually: pip install -r requirements.txt")
                return False
        else:
            print("\n💡 To install missing packages, run: pip install -r requirements.txt")
            return False
    
    # Check optional NVIDIA Riva (won't fail if missing)
    print("\n🎤 Checking optional speech packages...")
    optional_packages = [
        ("nvidia-riva-client", "riva.client"),
        ("pyttsx3", "pyttsx3"),
        ("edge-tts", "edge_tts"),
    ]
    
    riva_available = True
    for package_name, import_name in optional_packages:
        if not check_package(package_name, import_name):
            riva_available = False
    
    if riva_available:
        print("✅ NVIDIA Riva speech services - Available")
    else:
        print("⚠️  NVIDIA Riva speech services - Some packages missing (optional)")
        print("💡 For speech features, see docs/SPEECH_INTEGRATION.md")
    
    # Check if Docker is available
    print("\n🐳 Checking Docker availability...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker - Available")
        else:
            print("❌ Docker - Not available")
    except FileNotFoundError:
        print("❌ Docker - Not installed")
        print("💡 Install Docker Desktop: https://www.docker.com/products/docker-desktop")
    
    print("\n" + "=" * 60)
    print("🎉 Setup verification complete!")
    print("\n📚 Next steps:")
    print("1. Start Docker services: docker-compose up -d")
    print("2. Run API server: python examples/api_server.py")
    print("3. Visit n8n: http://localhost:5678")
    print("4. API docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    main()
