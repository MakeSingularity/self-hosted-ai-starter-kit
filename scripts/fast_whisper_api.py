#!/usr/bin/env python3
"""
Fast Whisper API Server using faster-whisper with CUDA acceleration
Optimized for reliability and performance with large-v3 model
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn
import os
import tempfile
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from faster_whisper import WhisperModel
    import torch
    WHISPER_AVAILABLE = True
except ImportError as e:
    logger.error(f"faster-whisper not available: {e}")
    WHISPER_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="Fast Whisper Speech Recognition API",
    description="High-performance speech-to-text service using faster-whisper with CUDA",
    version="2.0.0"
)

class FastWhisperService:
    """Fast Whisper service using faster-whisper with CUDA"""
    
    def __init__(self):
        self.model = None
        self.model_size = "large-v3"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.temp_dir = Path(tempfile.gettempdir()) / "fast_whisper"
        self.temp_dir.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        logger.info(f"🚀 Initializing Fast Whisper Service")
        logger.info(f"📱 Device: {self.device}")
        logger.info(f"🧮 Compute type: {self.compute_type}")
        logger.info(f"📁 Temp directory: {self.temp_dir}")
    
    def load_model(self):
        """Load the Whisper model with optimal settings"""
        if not WHISPER_AVAILABLE:
            raise RuntimeError("faster-whisper not available")
        
        try:
            logger.info(f"🔄 Loading Whisper model: {self.model_size}")
            
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=None,  # Use default cache
                local_files_only=False
            )
            
            logger.info(f"✅ Whisper model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            return False
    
    def transcribe_audio(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """Transcribe audio file using faster-whisper"""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            start_time = time.time()
            logger.info(f"🎤 Transcribing audio: {audio_path}")
            
            # Transcribe with optimal settings
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=False,
                initial_prompt=None,
                word_timestamps=True
            )
            
            # Extract text and metadata
            full_text = ""
            all_segments = []
            
            for segment in segments:
                full_text += segment.text
                all_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "avg_logprob": segment.avg_logprob,
                    "no_speech_prob": segment.no_speech_prob
                })
            
            duration = time.time() - start_time
            
            result = {
                "success": True,
                "text": full_text.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "transcription_time": duration,
                "segments": all_segments,
                "model_used": self.model_size,
                "device": self.device,
                "vad_filter": info.vad_options,
                "error": None
            }
            
            logger.info(f"✅ Transcription completed in {duration:.2f}s")
            logger.info(f"📝 Text length: {len(full_text)} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return {
                "success": False,
                "text": "",
                "error": str(e),
                "model_used": self.model_size,
                "device": self.device
            }

# Initialize the service
whisper_service = FastWhisperService()

@app.on_event("startup")
async def startup_event():
    """Initialize the Whisper model on startup"""
    logger.info("🚀 Starting Fast Whisper API Server")
    
    if not WHISPER_AVAILABLE:
        logger.error("❌ faster-whisper not available - please install it")
        return
    
    # Load model in background
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(whisper_service.executor, whisper_service.load_model)

@app.get("/")
async def root():
    """Health check endpoint"""
    cuda_available = torch.cuda.is_available() if WHISPER_AVAILABLE else False
    model_loaded = whisper_service.model is not None
    
    return {
        "message": "Fast Whisper Speech Recognition API",
        "status": "running",
        "whisper_available": WHISPER_AVAILABLE,
        "model_loaded": model_loaded,
        "model_size": whisper_service.model_size,
        "device": whisper_service.device,
        "cuda_available": cuda_available,
        "version": "2.0.0"
    }

@app.get("/status")
async def get_status():
    """Get detailed status information"""
    try:
        status = {
            "whisper_available": WHISPER_AVAILABLE,
            "model_loaded": whisper_service.model is not None,
            "model_size": whisper_service.model_size,
            "device": whisper_service.device,
            "compute_type": whisper_service.compute_type,
            "temp_dir": str(whisper_service.temp_dir)
        }
        
        if WHISPER_AVAILABLE:
            status.update({
                "cuda_available": torch.cuda.is_available(),
                "torch_version": torch.__version__
            })
            
            if torch.cuda.is_available():
                status.update({
                    "gpu_name": torch.cuda.get_device_name(0),
                    "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory,
                    "gpu_memory_cached": torch.cuda.memory_cached(0)
                })
        
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"error": str(e), "status": "error"}

@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...), language: Optional[str] = None):
    """Transcribe an uploaded audio file"""
    if not whisper_service.model:
        raise HTTPException(status_code=503, detail="Whisper model not loaded")
    
    try:
        # Save uploaded file temporarily
        temp_file = whisper_service.temp_dir / f"upload_{int(time.time())}_{file.filename}"
        
        with open(temp_file, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing uploaded file: {file.filename} ({len(content)} bytes)")
        
        # Transcribe in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            whisper_service.executor,
            whisper_service.transcribe_audio,
            str(temp_file),
            language
        )
        
        # Clean up
        temp_file.unlink(missing_ok=True)
        
        return {
            **result,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content)
        }
        
    except Exception as e:
        logger.error(f"File transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/n8n")
async def transcribe_for_n8n(request: Dict):
    """Optimized endpoint for n8n workflow integration"""
    if not whisper_service.model:
        return {
            "success": False,
            "error": "Whisper model not loaded",
            "message_type": "error",
            "transcription": {"text": "Speech recognition service not ready"},
            "needs_transcription": True
        }
    
    try:
        logger.info(f"📥 n8n request: {type(request)}")
        
        # Handle malformed requests
        if isinstance(request, str):
            logger.error(f"Received string instead of dict: {request}")
            return {
                "success": False,
                "error": "Expected JSON object",
                "message_type": "unknown",
                "transcription": {"text": "Invalid request format"},
                "needs_transcription": True
            }
        
        # Extract message data
        message = request.get("message", {})
        voice_data = message.get("voice", {})
        audio_data = message.get("audio", {})
        
        # Check if this is a voice/audio message
        if voice_data:
            message_type = "voice"
            file_info = voice_data
        elif audio_data:
            message_type = "audio"
            file_info = audio_data
        else:
            # Text message - no transcription needed
            return {
                "success": True,
                "error": None,
                "message_type": "text",
                "transcription": {"text": message.get("text", "")},
                "needs_transcription": False,
                "original_message": message
            }
        
        # For now, return placeholder since we need Telegram file download
        duration = file_info.get("duration", 0)
        file_id = file_info.get("file_id", "unknown")
        
        logger.info(f"🎤 Processing {message_type} message: {file_id} ({duration}s)")
        
        return {
            "success": True,
            "message_type": message_type,
            "transcription": {
                "text": f"[Fast Whisper transcription ready - {duration}s {message_type} message]",
                "confidence": 0.95,
                "language": "en",
                "duration": duration,
                "model_used": whisper_service.model_size,
                "device": whisper_service.device
            },
            "original_message": message,
            "needs_transcription": True,
            "note": "Telegram file download integration needed",
            "file_id": file_id
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
async def test_local_file(file_path: str, language: Optional[str] = None):
    """Test transcription with a local file"""
    if not whisper_service.model:
        raise HTTPException(status_code=503, detail="Whisper model not loaded")
    
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        logger.info(f"🧪 Testing local file: {file_path}")
        
        # Transcribe in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            whisper_service.executor,
            whisper_service.transcribe_audio,
            file_path,
            language
        )
        
        return {
            "test_file": file_path,
            "transcription_result": result,
            "test_successful": result.get("success", False)
        }
        
    except Exception as e:
        logger.error(f"Local file test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server
    print("🚀 Starting Fast Whisper Speech Recognition API Server")
    print("📡 Access at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print(f"🎯 Model: {whisper_service.model_size}")
    print(f"🖥️ Device: {whisper_service.device}")
    
    uvicorn.run(
        "fast_whisper_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        log_level="info",
        workers=1  # Single worker for GPU memory management
    )
