#!/usr/bin/env python3
"""
Startup script for Fast Whisper API that loads .env file
"""

import os
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(".env")
    
    if env_path.exists():
        print(f"📁 Loading environment from {env_path}")
        
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    if 'TOKEN' in key:
                        print(f"✅ Loaded {key} (hidden)")
                    else:
                        print(f"✅ Loaded {key}={value}")
    else:
        print(f"⚠️ No .env file found at {env_path}")

if __name__ == "__main__":
    print("🚀 Starting Fast Whisper API with .env support")
    
    # Load environment variables first
    load_env_file()
    
    # Check if bot token is loaded
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if bot_token:
        print(f"✅ Telegram bot token loaded: {bot_token[:10]}...")
    else:
        print("❌ Telegram bot token not found")
    
    # Import and start the API
    print("🎤 Starting Fast Whisper API server...")
    
    # Change to the script directory and add to path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    import sys
    sys.path.insert(0, str(project_dir))
    
    # Import and run the API
    from scripts.fast_whisper_api import app
    import uvicorn
    
    print("📡 Access at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        workers=1
    )
