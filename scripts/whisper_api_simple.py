#!/usr/bin/env python3
"""
Simple Whisper Transcription API Server for n8n Integration
Synchronous version using only standard dependencies
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn
import os
import tempfile
import requests
from pathlib import Path
import logging
from typing import Optional, Dict
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from whisper_speech_recognition import WhisperSpeechRecognizer, TelegramAudioHandler
except ImportError:
    logger.error("whisper_speech_recognition module not found")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Whisper Speech Recognition API",
    description="Local speech-to-text service for n8n Telegram workflows",
    version="1.0.0"
)

# Initialize Whisper recognizer
whisper_recognizer = WhisperSpeechRecognizer(
    ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434")
)
telegram_handler = TelegramAudioHandler(whisper_recognizer)

# Telegram Bot Token (set this in your environment)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

@app.on_event("startup")
async def startup_event():
    """Initialize the service on startup"""
    logger.info("Starting Whisper Speech Recognition API")
    
    # Check if Whisper models are available
    if whisper_recognizer.check_ollama_status():
        logger.info("✅ Whisper models ready")
    else:
        logger.warning("⚠️ Whisper models not fully available")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Whisper Speech Recognition API",
        "status": "running",
        "whisper_ready": whisper_recognizer.check_ollama_status(),
        "model": whisper_recognizer.model_name,
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get detailed status information"""
    try:
        # Check Ollama status
        ollama_status = whisper_recognizer.check_ollama_status()
        
        # Get available models
        response = requests.get(f"{whisper_recognizer.ollama_url}/api/tags", timeout=5)
        models = response.json().get("models", []) if response.status_code == 200 else []
        whisper_models = [m for m in models if "whisper" in m["name"].lower()]
        
        return {
            "ollama_connected": ollama_status,
            "whisper_models_available": len(whisper_models),
            "primary_model": whisper_recognizer.model_name,
            "fallback_model": whisper_recognizer.fallback_model,
            "models": [{"name": m["name"], "size_mb": round(m["size"] / (1024*1024), 1)} for m in whisper_models],
            "temp_dir": str(whisper_recognizer.temp_dir),
            "telegram_token_set": bool(TELEGRAM_BOT_TOKEN)
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"error": str(e), "status": "error"}

@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file"""
    try:
        # Save uploaded file temporarily
        temp_file = whisper_recognizer.temp_dir / f"upload_{file.filename}"
        
        # Write file synchronously
        with open(temp_file, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing uploaded file: {file.filename} ({file.content_type})")
        
        # Process the audio file
        result = whisper_recognizer.process_telegram_audio(str(temp_file))
        
        # Clean up
        temp_file.unlink(missing_ok=True)
        
        return {
            "success": result["success"],
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "model_used": result.get("model_used", whisper_recognizer.model_name),
            "error": result.get("error", None),
            "filename": file.filename,
            "content_type": file.content_type
        }
        
    except Exception as e:
        logger.error(f"File transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/n8n")
async def transcribe_for_n8n(request: Dict):
    """Optimized endpoint for n8n workflow integration"""
    try:
        logger.info(f"Received request type: {type(request)}, content: {request}")
        
        # Handle case where request might be malformed
        if isinstance(request, str):
            logger.error(f"Received string instead of dict: {request}")
            return {
                "success": False,
                "error": f"Expected JSON object, got string: {request}",
                "message_type": "unknown",
                "transcription": {"text": "Transcription error"},
                "needs_transcription": True
            }
        
        # Extract message data from n8n format
        message = request.get("message", {})
        voice_data = message.get("voice", {})
        audio_data = message.get("audio", {})
        
        # Determine message type and file info
        if voice_data:
            file_id = voice_data.get("file_id")
            duration = voice_data.get("duration", 0)
            message_type = "voice"
            logger.info(f"Processing voice message: {file_id} ({duration}s)")
        elif audio_data:
            file_id = audio_data.get("file_id")
            duration = audio_data.get("duration", 0)
            message_type = "audio"
            logger.info(f"Processing audio message: {file_id} ({duration}s)")
        else:
            return {
                "success": True,
                "error": None,
                "message_type": "text",
                "transcription": {"text": message.get("text", "")},
                "needs_transcription": False,
                "original_message": message
            }
        
        # For now, return a placeholder response since we need Telegram bot token setup
        if not TELEGRAM_BOT_TOKEN:
            return {
                "success": False,
                "error": "TELEGRAM_BOT_TOKEN not configured",
                "message_type": message_type,
                "transcription": {"text": "Voice message received but bot token not configured"},
                "needs_transcription": True,
                "original_message": message,
                "setup_required": "Set TELEGRAM_BOT_TOKEN environment variable"
            }
        
        # Download and transcribe (placeholder for now)
        return {
            "success": True,
            "message_type": message_type,
            "transcription": {
                "text": f"[Voice message transcription would appear here - {duration}s]",
                "confidence": 0.95,
                "language": "en",
                "duration": duration,
                "model_used": whisper_recognizer.model_name
            },
            "original_message": message,
            "needs_transcription": True,
            "note": "Telegram file download implementation needed"
        }
        
    except Exception as e:
        logger.error(f"n8n transcription failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message_type": "unknown",
            "transcription": {"text": "Transcription error"},
            "needs_transcription": True
        }

@app.post("/test/local")
async def test_local_file(file_path: str):
    """Test transcription with a local file path"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        logger.info(f"Testing local file: {file_path}")
        
        # Process the audio file
        result = whisper_recognizer.process_telegram_audio(file_path)
        
        return {
            "test_file": file_path,
            "transcription_result": result,
            "test_successful": result.get("success", False)
        }
        
    except Exception as e:
        logger.error(f"Local file test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/models")
async def test_models():
    """Test available Whisper models"""
    try:
        # Test Ollama connection
        response = requests.get(f"{whisper_recognizer.ollama_url}/api/tags", timeout=5)
        
        if response.status_code != 200:
            return {"error": "Could not connect to Ollama", "status": "failed"}
        
        models = response.json().get("models", [])
        whisper_models = [m for m in models if "whisper" in m["name"].lower()]
        
        # Test each Whisper model
        model_tests = []
        for model in whisper_models:
            model_name = model["name"]
            try:
                # Quick test of model availability
                test_payload = {
                    "model": model_name,
                    "prompt": "Test prompt",
                    "stream": False
                }
                
                test_response = requests.post(
                    f"{whisper_recognizer.ollama_url}/api/generate",
                    json=test_payload,
                    timeout=10
                )
                
                model_tests.append({
                    "name": model_name,
                    "size_mb": round(model["size"] / (1024*1024), 1),
                    "status": "available" if test_response.status_code == 200 else "error",
                    "error": None if test_response.status_code == 200 else test_response.text
                })
                
            except Exception as e:
                model_tests.append({
                    "name": model_name,
                    "size_mb": round(model["size"] / (1024*1024), 1),
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "total_models": len(models),
            "whisper_models": len(whisper_models),
            "model_tests": model_tests,
            "primary_model": whisper_recognizer.model_name,
            "ollama_url": whisper_recognizer.ollama_url
        }
        
    except Exception as e:
        logger.error(f"Model test failed: {e}")
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    # Run the server
    print("🎤 Starting Whisper Speech Recognition API Server")
    print("📡 Access at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "whisper_api_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
