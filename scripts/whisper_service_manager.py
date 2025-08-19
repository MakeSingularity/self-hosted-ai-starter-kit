#!/usr/bin/env python3
"""
Whisper API Service Manager
Handles starting, stopping, and monitoring the Whisper API service
"""

import os
import sys
import time
import requests
import subprocess
import psutil
from pathlib import Path

class WhisperServiceManager:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.api_port = 8000
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.venv_path = self.project_root / ".venv"
        self.whisper_script = self.script_dir / "whisper_api_simple.py"
        
    def get_python_executable(self):
        """Get the correct Python executable from virtual environment"""
        if os.name == 'nt':  # Windows
            python_exe = self.venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            python_exe = self.venv_path / "bin" / "python"
            
        if python_exe.exists():
            return str(python_exe)
        else:
            print(f"⚠️ Virtual environment not found at {self.venv_path}")
            print("Please run: python -m venv .venv")
            return sys.executable  # Fallback to system Python
    
    def is_api_running(self):
        """Check if Whisper API is running and responding"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def is_port_in_use(self):
        """Check if port 8000 is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == self.api_port:
                return True
        return False
    
    def find_whisper_process(self):
        """Find running Whisper API process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'whisper_api_simple.py' in cmdline:
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def stop_api(self):
        """Stop the Whisper API if running"""
        print("🛑 Stopping Whisper API...")
        
        # Find and terminate the process
        proc = self.find_whisper_process()
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print("✅ Whisper API stopped")
                return True
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                try:
                    proc.kill()
                    print("🔥 Whisper API force-killed")
                    return True
                except:
                    pass
        
        print("ℹ️ No Whisper API process found")
        return False
    
    def start_api(self, background=True):
        """Start the Whisper API"""
        if self.is_api_running():
            print("✅ Whisper API already running")
            return True
        
        if self.is_port_in_use():
            print("⚠️ Port 8000 is in use by another process")
            return False
        
        print("🚀 Starting Whisper API...")
        
        # Prepare environment
        env = os.environ.copy()
        env["TELEGRAM_BOT_TOKEN"] = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        # Get Python executable
        python_exe = self.get_python_executable()
        
        # Start the process
        try:
            if background:
                # Start in background (detached)
                if os.name == 'nt':  # Windows
                    subprocess.Popen(
                        [python_exe, str(self.whisper_script)],
                        cwd=str(self.script_dir),
                        env=env,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                else:  # Linux/Mac
                    subprocess.Popen(
                        [python_exe, str(self.whisper_script)],
                        cwd=str(self.script_dir),
                        env=env,
                        start_new_session=True
                    )
            else:
                # Start in foreground
                subprocess.run(
                    [python_exe, str(self.whisper_script)],
                    cwd=str(self.script_dir),
                    env=env
                )
            
            # Wait for API to start
            for i in range(10):
                time.sleep(1)
                if self.is_api_running():
                    print("✅ Whisper API started successfully")
                    return True
                print(f"⏳ Waiting for API to start... ({i+1}/10)")
            
            print("❌ API failed to start within 10 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start API: {e}")
            return False
    
    def restart_api(self):
        """Restart the Whisper API"""
        print("🔄 Restarting Whisper API...")
        self.stop_api()
        time.sleep(2)
        return self.start_api()
    
    def status(self):
        """Get API status"""
        if self.is_api_running():
            try:
                response = requests.get(f"{self.api_url}/status", timeout=3)
                status_data = response.json()
                print("✅ Whisper API Status: RUNNING")
                print(f"🔗 URL: {self.api_url}")
                print(f"🤖 Model: {status_data.get('primary_model', 'Unknown')}")
                print(f"📡 Ollama Connected: {status_data.get('ollama_connected', False)}")
                print(f"🎙️ Whisper Models: {status_data.get('whisper_models_available', 0)}")
                return True
            except Exception as e:
                print(f"⚠️ API running but status unavailable: {e}")
                return True
        else:
            print("❌ Whisper API Status: NOT RUNNING")
            if self.is_port_in_use():
                print("⚠️ Port 8000 is in use by another process")
            return False

def main():
    """Command line interface"""
    manager = WhisperServiceManager()
    
    if len(sys.argv) < 2:
        print("Usage: python whisper_service_manager.py [start|stop|restart|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        background = "--foreground" not in sys.argv
        manager.start_api(background=background)
    elif command == "stop":
        manager.stop_api()
    elif command == "restart":
        manager.restart_api()
    elif command == "status":
        manager.status()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, restart, status")
        sys.exit(1)

if __name__ == "__main__":
    main()
