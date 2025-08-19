#!/usr/bin/env python3
"""
Setup and Install Dependencies for AI Starter Kit
Ensures virtual environment is created and dependencies are installed
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def main():
    """Setup virtual environment and install dependencies"""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"
    requirements_file = project_root / "requirements.txt"
    
    print("🔧 AI Starter Kit - Dependency Setup")
    print(f"📁 Project Root: {project_root}")
    print(f"🐍 Virtual Environment: {venv_path}")
    
    # Step 1: Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Step 2: Get the correct Python executable
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    print(f"🐍 Using Python: {python_exe}")
    
    # Step 3: Upgrade pip
    print("⬆️ Upgrading pip...")
    subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], 
                  cwd=str(project_root))
    
    # Step 4: Install requirements
    if requirements_file.exists():
        print("📋 Installing requirements...")
        result = subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)], 
                              cwd=str(project_root), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
        else:
            print("❌ Error installing requirements:")
            print(result.stderr)
            return False
    else:
        print("⚠️ requirements.txt not found")
    
    # Step 5: Test imports
    print("🧪 Testing critical imports...")
    test_imports = [
        "fastapi",
        "uvicorn", 
        "requests",
        "psutil"
    ]
    
    for module in test_imports:
        result = subprocess.run([str(python_exe), "-c", f"import {module}; print(f'✅ {module}')"], 
                              cwd=str(project_root), capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ {module} import failed")
    
    # Step 6: Display usage information
    print("\n🎉 Setup Complete!")
    print("\n📋 Usage Commands:")
    print(f"   Activate venv (Windows): {venv_path / 'Scripts' / 'activate.bat'}")
    print(f"   Activate venv (Linux/Mac): source {venv_path / 'bin' / 'activate'}")
    print(f"   Start Whisper API: python scripts/whisper_service_manager.py start")
    print(f"   Check API status: python scripts/whisper_service_manager.py status")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
