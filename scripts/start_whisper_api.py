#!/usr/bin/env python3
"""
Production startup script for Whisper API Server
Runs without file watching to avoid interference
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the scripts directory to the path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import our app
from whisper_api_simple import app

if __name__ == "__main__":
    print("🎤 Starting Whisper Speech Recognition API Server (Production)")
    print("📡 Access at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🔄 Running without file watching for stability")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        log_level="info"
    )
