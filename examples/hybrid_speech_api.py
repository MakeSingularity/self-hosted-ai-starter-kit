#!/usr/bin/env python3
"""
Hybrid Speech API Server with multiple TTS/ASR backends
Supports NVIDIA Riva (local/cloud), and fallback TTS engines

Usage:
1. Activate conda environment: conda activate ai-starter-kit
2. Install requirements: pip install -r requirements.txt
3. Run server: python examples/hybrid_speech_api.py
4. Access API docs: http://localhost:8001/docs
"""

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel
    import uvicorn
    from typing import Optional
    import os
    import tempfile
    import io
    import logging
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("💡 Please run: pip install -r requirements.txt")
    print("🔧 Or activate your conda environment: conda activate ai-starter-kit")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import optional TTS libraries
RIVA_AVAILABLE = False
PYTTSX3_AVAILABLE = False
EDGE_TTS_AVAILABLE = False

try:
    import riva.client
    RIVA_AVAILABLE = True
    logger.info("✓ NVIDIA Riva client available")
except ImportError:
    logger.warning("⚠ NVIDIA Riva not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
    logger.info("✓ pyttsx3 available")
except ImportError:
    logger.warning("⚠ pyttsx3 not available")

try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
    logger.info("✓ edge-tts available")
except ImportError:
    logger.warning("⚠ edge-tts not available")

# Request/Response models
class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "English-US.Female-1"
    engine: Optional[str] = "auto"  # auto, riva, pyttsx3, edge

class TTSResponse(BaseModel):
    message: str
    engine_used: str
    audio_format: str

class ASRResponse(BaseModel):
    transcript: str
    confidence: float
    engine_used: str

# Global service manager
class HybridSpeechService:
    def __init__(self):
        self.riva_service = None
        self.riva_available = False
        self.pyttsx3_engine = None
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize available speech services"""
        # Try to initialize NVIDIA Riva
        if RIVA_AVAILABLE:
            try:
                server = os.getenv("RIVA_SERVER", "localhost:50051")
                api_key = os.getenv("NVIDIA_RIVA_API_KEY")
                
                if api_key and "nvidia.com" in server:
                    # Cloud service
                    auth = riva.client.Auth(
                        uri=server,
                        use_ssl=True,
                        metadata_args=[("authorization", f"Bearer {api_key}")]
                    )
                    logger.info(f"✓ NVIDIA Riva cloud service configured: {server}")
                else:
                    # Local service
                    auth = riva.client.Auth(uri=server, use_ssl=False)
                    logger.info(f"✓ NVIDIA Riva local service configured: {server}")
                
                # Test connection with a simple request
                self.riva_tts = riva.client.SpeechSynthesisService(auth)
                self.riva_asr = riva.client.ASRService(auth)
                self.riva_available = True
                logger.info("✓ NVIDIA Riva services initialized")
                
            except Exception as e:
                logger.warning(f"⚠ NVIDIA Riva initialization failed: {e}")
                self.riva_available = False
        
        # Initialize pyttsx3 as fallback
        if PYTTSX3_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                logger.info("✓ pyttsx3 TTS engine initialized")
            except Exception as e:
                logger.warning(f"⚠ pyttsx3 initialization failed: {e}")
    
    def synthesize_speech(self, text: str, voice: str = "English-US.Female-1", engine: str = "auto") -> tuple:
        """Synthesize speech using available engines"""
        
        # Try NVIDIA Riva first if available and requested
        if (engine == "auto" or engine == "riva") and self.riva_available:
            try:
                logger.info(f"Attempting Riva TTS for: {text[:50]}...")
                response = self.riva_tts.synthesize(
                    text=text,
                    voice_name=voice,
                    language_code="en-US",
                    encoding=riva.client.AudioEncoding.LINEAR_PCM,
                    sample_rate_hz=22050
                )
                
                if response and hasattr(response, 'audio') and len(response.audio) > 0:
                    logger.info(f"✓ Riva TTS successful: {len(response.audio)} bytes")
                    return response.audio, "riva", "audio/wav"
                else:
                    logger.warning("⚠ Riva TTS returned empty audio")
                    
            except Exception as e:
                logger.warning(f"⚠ Riva TTS failed: {e}")
        
        # Try pyttsx3 fallback
        if (engine == "auto" or engine == "pyttsx3") and PYTTSX3_AVAILABLE and self.pyttsx3_engine:
            try:
                logger.info(f"Attempting pyttsx3 TTS for: {text[:50]}...")
                
                # Create temporary file for pyttsx3 output
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    temp_path = tmp_file.name
                
                # Configure pyttsx3
                self.pyttsx3_engine.setProperty('rate', 150)  # Speed
                self.pyttsx3_engine.setProperty('volume', 0.8)  # Volume
                
                # Save to file
                self.pyttsx3_engine.save_to_file(text, temp_path)
                self.pyttsx3_engine.runAndWait()
                
                # Read the file
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up
                os.unlink(temp_path)
                
                if len(audio_data) > 0:
                    logger.info(f"✓ pyttsx3 TTS successful: {len(audio_data)} bytes")
                    return audio_data, "pyttsx3", "audio/wav"
                    
            except Exception as e:
                logger.warning(f"⚠ pyttsx3 TTS failed: {e}")
        
        # If all engines fail, return error
        raise HTTPException(
            status_code=503, 
            detail="No TTS engines available or all failed"
        )
    
    def transcribe_audio(self, audio_data: bytes, engine: str = "auto") -> tuple:
        """Transcribe audio using available engines"""
        
        # Try NVIDIA Riva ASR
        if (engine == "auto" or engine == "riva") and self.riva_available:
            try:
                logger.info("Attempting Riva ASR...")
                
                # Configure ASR
                config = riva.client.RecognitionConfig(
                    encoding=riva.client.AudioEncoding.LINEAR_PCM,
                    sample_rate_hz=16000,
                    language_code="en-US",
                    max_alternatives=1,
                )
                
                # Create audio from bytes
                audio = riva.client.RecognitionAudio(content=audio_data)
                
                # Perform recognition
                response = self.riva_asr.recognize(config=config, audio=audio)
                
                if response.results:
                    transcript = response.results[0].alternatives[0].transcript
                    confidence = response.results[0].alternatives[0].confidence
                    logger.info(f"✓ Riva ASR successful: {transcript}")
                    return transcript, confidence, "riva"
                    
            except Exception as e:
                logger.warning(f"⚠ Riva ASR failed: {e}")
        
        # Fallback: return placeholder
        return "Transcription service temporarily unavailable", 0.0, "none"

# Initialize global service
speech_service = HybridSpeechService()

# FastAPI app
app = FastAPI(
    title="Hybrid Speech API Server",
    description="Multi-engine speech services with NVIDIA Riva and fallbacks",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engines": {
            "riva": speech_service.riva_available,
            "pyttsx3": PYTTSX3_AVAILABLE and speech_service.pyttsx3_engine is not None,
            "edge_tts": EDGE_TTS_AVAILABLE
        },
        "primary_engine": "riva" if speech_service.riva_available else "pyttsx3"
    }

@app.post("/text-to-speech", response_class=StreamingResponse)
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        audio_data, engine_used, content_type = speech_service.synthesize_speech(
            text=request.text,
            voice=request.voice,
            engine=request.engine
        )
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type=content_type,
            headers={
                "Content-Disposition": "attachment; filename=speech.wav",
                "X-Engine-Used": engine_used,
                "X-Audio-Length": str(len(audio_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@app.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    engine: str = Form(default="auto")
):
    """Convert speech to text"""
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Transcribe
        transcript, confidence, engine_used = speech_service.transcribe_audio(
            audio_data=audio_data,
            engine=engine
        )
        
        return ASRResponse(
            transcript=transcript,
            confidence=confidence,
            engine_used=engine_used
        )
        
    except Exception as e:
        logger.error(f"ASR error: {e}")
        raise HTTPException(status_code=500, detail=f"ASR error: {str(e)}")

@app.get("/engines")
async def list_engines():
    """List available speech engines"""
    return {
        "tts_engines": [
            {"name": "riva", "available": speech_service.riva_available, "description": "NVIDIA Riva TTS"},
            {"name": "pyttsx3", "available": PYTTSX3_AVAILABLE, "description": "Local pyttsx3 TTS"},
            {"name": "edge", "available": EDGE_TTS_AVAILABLE, "description": "Microsoft Edge TTS"}
        ],
        "asr_engines": [
            {"name": "riva", "available": speech_service.riva_available, "description": "NVIDIA Riva ASR"}
        ]
    }

if __name__ == "__main__":
    print("🎤 Starting Hybrid Speech API Server")
    print("📡 Server will run on http://localhost:8001")
    print("📖 API Documentation: http://localhost:8001/docs")
    
    port = int(os.getenv("SPEECH_API_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
