#!/usr/bin/env python3
"""
n8n Whisper API Health Check and Auto-Start
For use in n8n Function nodes to ensure Whisper API is running
"""

import os
import sys
import requests
import subprocess
import time
from pathlib import Path

def check_and_start_whisper_api():
    """
    Check if Whisper API is running, start it if not
    Returns status information for n8n workflow
    """
    
    # Configuration
    api_url = "http://localhost:8000"
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    venv_path = project_root / ".venv"
    
    # Get Python executable from venv
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Linux/Mac
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        python_exe = sys.executable  # Fallback
    
    result = {
        "timestamp": time.time(),
        "api_url": api_url,
        "python_executable": str(python_exe),
        "checks_performed": []
    }
    
    try:
        # Check 1: Is API responding?
        result["checks_performed"].append("api_health_check")
        response = requests.get(f"{api_url}/", timeout=3)
        
        if response.status_code == 200:
            result["status"] = "running"
            result["message"] = "✅ Whisper API is running"
            result["api_response"] = response.json()
            return result
        else:
            result["status"] = "unhealthy"
            result["message"] = f"⚠️ API responding but unhealthy: {response.status_code}"
            
    except requests.exceptions.RequestException:
        result["status"] = "not_running"
        result["message"] = "❌ Whisper API not responding"
    
    # Check 2: Try to start the API
    result["checks_performed"].append("auto_start_attempt")
    
    try:
        env = os.environ.copy()
        env["TELEGRAM_BOT_TOKEN"] = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        whisper_script = script_dir / "whisper_api_simple.py"
        
        # Start API in background
        if os.name == 'nt':  # Windows
            subprocess.Popen(
                [str(python_exe), str(whisper_script)],
                cwd=str(script_dir),
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Linux/Mac
            subprocess.Popen(
                [str(python_exe), str(whisper_script)],
                cwd=str(script_dir),
                env=env,
                start_new_session=True
            )
        
        # Wait for startup
        for i in range(8):
            time.sleep(1)
            try:
                response = requests.get(f"{api_url}/", timeout=2)
                if response.status_code == 200:
                    result["status"] = "started"
                    result["message"] = f"✅ Whisper API started successfully (took {i+1}s)"
                    result["api_response"] = response.json()
                    return result
            except:
                continue
        
        result["status"] = "start_failed"
        result["message"] = "❌ Failed to start Whisper API within 8 seconds"
        
    except Exception as e:
        result["status"] = "start_error"
        result["message"] = f"❌ Error starting Whisper API: {str(e)}"
    
    return result

if __name__ == "__main__":
    # For testing the script directly
    result = check_and_start_whisper_api()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if "api_response" in result:
        print(f"API Info: {result['api_response']}")
