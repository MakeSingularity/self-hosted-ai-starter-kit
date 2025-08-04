#!/usr/bin/env python3
"""
Environment Checker and Script Runner
Ensures the correct Python environment is activated before running scripts
"""

import sys
import subprocess
import os
from pathlib import Path

def check_and_activate_environment():
    """Check if we're in the correct Python environment"""
    
    print("🔍 Checking Python environment...")
    
    # Get current Python executable path
    current_python = sys.executable
    project_root = Path(__file__).parent
    
    # Expected virtual environment path
    expected_venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    
    # Check if we're using the project's virtual environment
    if Path(current_python).resolve() == expected_venv_python.resolve():
        print(f"✅ Correct virtual environment active: {current_python}")
        return True, current_python
    
    # Check if virtual environment exists
    if expected_venv_python.exists():
        print(f"⚠️  Wrong environment detected")
        print(f"   Current: {current_python}")
        print(f"   Expected: {expected_venv_python}")
        print(f"💡 Switching to project virtual environment...")
        return True, str(expected_venv_python)
    
    # Check for conda environment
    conda_python = project_root / "ai-starter-kit" / "Scripts" / "python.exe"
    if conda_python.exists():
        print(f"💡 Found conda environment: {conda_python}")
        return True, str(conda_python)
    
    # Fallback to system Python
    print(f"⚠️  No project-specific environment found, using system Python")
    return True, current_python

def run_verify_setup(python_executable):
    """Run the verify_setup.py script with the correct Python"""
    
    script_path = Path(__file__).parent / "verify_setup.py"
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    print(f"🚀 Running verify_setup.py with: {python_executable}")
    print("=" * 60)
    
    try:
        # Run the script
        result = subprocess.run([
            python_executable, 
            str(script_path)
        ], cwd=Path(__file__).parent)
        
        print("=" * 60)
        if result.returncode == 0:
            print("✅ verify_setup.py completed successfully")
            return True
        else:
            print(f"⚠️  verify_setup.py exited with code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running verify_setup.py: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Environment Checker and Script Runner")
    print("=" * 50)
    
    # Check and get correct Python executable
    env_ok, python_exec = check_and_activate_environment()
    
    if not env_ok:
        print("❌ Environment setup failed")
        return False
    
    # Run verify_setup.py
    success = run_verify_setup(python_exec)
    
    if success:
        print("\n🎉 Environment verification complete!")
    else:
        print("\n⚠️  Some issues were detected - see output above")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
