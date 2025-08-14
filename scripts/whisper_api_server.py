#!/usr/bin/env python3
"""
Whisper Transcription API Server for n8n Integration
FastAPI server that provides speech-to-text endpoints for Telegram voice messages
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import requests
from pathlib import Path
import logging
from typing import Optional, Dict
import asyncio

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    logger.warning("aiofiles not available, using synchronous file operations")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx not available, using requests for HTTP operations")

from whisper_speech_recognition import WhisperSpeechRecognizer, TelegramAudioHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Whisper Speech Recognition API",
    description="Local speech-to-text service for n8n Telegram workflows",
    version="1.0.0"
)

# Initialize Whisper recognizer
whisper_recognizer = WhisperSpeechRecognizer()
telegram_handler = TelegramAudioHandler(whisper_recognizer)

# Telegram Bot Token (you'll need to set this)
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
        "model": whisper_recognizer.model_name
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
            "temp_dir": str(whisper_recognizer.temp_dir)
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
        
        async with aiofiles.open(temp_file, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
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

@app.post("/transcribe/telegram")
async def transcribe_telegram_voice(request: Dict):
    """Transcribe Telegram voice/audio message"""
    try:
        file_id = request.get("file_id")
        message_id = request.get("message_id")
        user_id = request.get("user_id")
        duration = request.get("duration", 0)
        
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
        
        logger.info(f"Processing Telegram voice message: {file_id} (user: {user_id}, duration: {duration}s)")
        
        # Download file from Telegram
        audio_file_path = await download_telegram_file(file_id)
        
        if not audio_file_path:
            raise HTTPException(status_code=400, detail="Failed to download Telegram file")
        
        # Transcribe the audio
        result = whisper_recognizer.process_telegram_audio(audio_file_path)
        
        # Clean up downloaded file
        Path(audio_file_path).unlink(missing_ok=True)
        
        # Create n8n-compatible response
        return {
            "success": result["success"],
            "transcription": {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", "unknown"),
                "model_used": result.get("model_used", whisper_recognizer.model_name)
            },
            "telegram_info": {
                "file_id": file_id,
                "message_id": message_id,
                "user_id": user_id,
                "duration": duration
            },
            "error": result.get("error", None),
            "processed_at": "{{ $now }}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/n8n")
async def transcribe_for_n8n(request: Dict):
    """Optimized endpoint for n8n workflow integration"""
    try:
        # Extract message data from n8n format
        message = request.get("message", {})
        voice_data = message.get("voice", {})
        audio_data = message.get("audio", {})
        
        # Determine message type and file info
        if voice_data:
            file_id = voice_data.get("file_id")
            duration = voice_data.get("duration", 0)
            message_type = "voice"
        elif audio_data:
            file_id = audio_data.get("file_id")
            duration = audio_data.get("duration", 0)
            message_type = "audio"
        else:
            return {
                "success": False,
                "error": "No voice or audio data found in message",
                "message_type": "text",
                "transcription": {"text": message.get("text", "")},
                "needs_transcription": False
            }
        
        # Download and transcribe
        audio_file_path = await download_telegram_file(file_id)
        
        if not audio_file_path:
            return {
                "success": False,
                "error": "Failed to download audio file",
                "message_type": message_type,
                "transcription": {"text": "Audio transcription failed"},
                "needs_transcription": True
            }
        
        # Process transcription
        result = whisper_recognizer.process_telegram_audio(audio_file_path)
        
        # Clean up
        Path(audio_file_path).unlink(missing_ok=True)
        
        # Return n8n-formatted response
        return {
            "success": result["success"],
            "message_type": message_type,
            "transcription": {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", "unknown"),
                "duration": duration,
                "model_used": result.get("model_used", whisper_recognizer.model_name)
            },
            "original_message": message,
            "needs_transcription": True,
            "processed_at": "{{ $now }}",
            "error": result.get("error", None)
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

async def download_telegram_file(file_id: str) -> Optional[str]:
    """Download file from Telegram using file_id"""
    try:
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not set")
            return None
        
        # Get file info from Telegram
        file_info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
        params = {"file_id": file_id}
        
        async with aiofiles.get(file_info_url, params=params) as response:
            if response.status != 200:
                logger.error(f"Failed to get file info: {response.status}")
                return None
            
            data = await response.json()
            file_path = data["result"]["file_path"]
        
        # Download the actual file
        download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        temp_file = whisper_recognizer.temp_dir / f"telegram_{file_id}_{Path(file_path).name}"
        
        async with aiofiles.get(download_url) as response:
            if response.status != 200:
                logger.error(f"Failed to download file: {response.status}")
                return None
            
            async with aiofiles.open(temp_file, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
        
        logger.info(f"Downloaded Telegram file: {temp_file}")
        return str(temp_file)
        
    except Exception as e:
        logger.error(f"Telegram file download failed: {e}")
        return None

@app.post("/test/sample")
async def test_with_sample():
    """Test endpoint with a sample audio file"""
    try:
        # Look for sample audio files
        sample_files = list(whisper_recognizer.temp_dir.glob("*.wav"))
        sample_files.extend(list(Path("examples").glob("*.wav")))
        sample_files.extend(list(Path("assets").glob("*.wav")))
        
        if not sample_files:
            return {
                "success": False,
                "error": "No sample audio files found",
                "suggestion": "Upload a sample audio file to test transcription"
            }
        
        sample_file = sample_files[0]
        result = whisper_recognizer.process_telegram_audio(str(sample_file))
        
        return {
            "test_file": str(sample_file),
            "transcription_result": result,
            "test_successful": result.get("success", False)
        }
        
    except Exception as e:
        logger.error(f"Sample test failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "whisper_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
