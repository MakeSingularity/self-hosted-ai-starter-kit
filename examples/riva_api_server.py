"""
NVIDIA Riva Speech Services API Server

This server provides speech-to-text and text-to-speech services using NVIDIA Riva.
It's designed to integrate with n8n workflows.

Usage:
1. Ensure NVIDIA Riva server is running
2. Set environment variables (RIVA_SERVER, NVIDIA_RIVA_API_KEY if using cloud)
3. Start server: python examples/riva_api_server.py
4. Use HTTP Request nodes in n8n to call the endpoints

Endpoints:
- POST /speech-to-text - Convert audio to text
- POST /text-to-speech - Convert text to audio
- GET /riva-status - Check Riva service status
- GET /health - Health check
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from typing import Optional
import os
import tempfile
import io

# Try to import Riva client and audio libraries
try:
    import riva.client
    import soundfile as sf
    import numpy as np
    RIVA_AVAILABLE = True
except ImportError as e:
    RIVA_AVAILABLE = False
    print(f"⚠️  NVIDIA Riva dependencies not available: {e}")
    print("Please install with: pip install nvidia-riva-client soundfile")

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="NVIDIA Riva Speech API",
    description="Speech services using NVIDIA Riva for n8n integration",
    version="1.0.0"
)

# Request/Response models
class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "English-US.Female-1"
    language_code: str = "en-US"

class SpeechToTextResponse(BaseModel):
    transcription: str
    language_code: str
    confidence: Optional[float] = None
    duration_seconds: Optional[float] = None
    status: str

class RivaService:
    """NVIDIA Riva service wrapper."""
    
    def __init__(self):
        self.available = RIVA_AVAILABLE
        self.auth = None
        self.asr_service = None
        self.tts_service = None
        self.nlp_service = None
        
        if self.available:
            self._initialize()
    
    def _initialize(self):
        """Initialize Riva services."""
        try:
            # Get configuration from environment
            server = os.getenv("RIVA_SERVER", "localhost:50051")
            api_key = os.getenv("NVIDIA_RIVA_API_KEY")
            use_ssl = api_key is not None  # Use SSL for cloud services
            
            # Initialize authentication
            if api_key:
                self.auth = riva.client.Auth(
                    uri=server,
                    use_ssl=use_ssl,
                    metadata_args=[("authorization", f"Bearer {api_key}")]
                )
                print(f"✓ Using NVIDIA cloud services with API key")
            else:
                self.auth = riva.client.Auth(uri=server, use_ssl=use_ssl)
                print(f"✓ Using local Riva server at {server}")
            
            # Initialize service clients
            self.asr_service = riva.client.ASRService(self.auth)
            self.tts_service = riva.client.SpeechSynthesisService(self.auth)
            self.nlp_service = riva.client.NLPService(self.auth)
            
            print("✓ All Riva services initialized successfully")
            
        except Exception as e:
            print(f"⚠️  Could not initialize Riva services: {e}")
            self.available = False
    
    def is_healthy(self) -> bool:
        """Check if services are healthy."""
        return self.available and self.asr_service and self.tts_service
    
    def transcribe_audio_file(self, audio_data: bytes, sample_rate: int, 
                             language_code: str = "en-US") -> dict:
        """Transcribe audio data to text."""
        if not self.asr_service:
            raise HTTPException(status_code=503, detail="ASR service not available")
        
        try:
            # Create ASR configuration
            config = riva.client.RecognitionConfig(
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                sample_rate_hertz=sample_rate,
                language_code=language_code,
                max_alternatives=1,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False
            )
            
            # Create recognition request
            request = riva.client.RecognizeRequest(
                config=config,
                audio=riva.client.RecognitionAudio(content=audio_data)
            )
            
            # Perform transcription
            response = self.asr_service.recognize(request)
            
            if response.results and response.results[0].alternatives:
                alternative = response.results[0].alternatives[0]
                return {
                    "transcription": alternative.transcript,
                    "confidence": alternative.confidence
                }
            else:
                return {
                    "transcription": "",
                    "confidence": 0.0
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ASR error: {str(e)}")
    
    def synthesize_speech(self, text: str, voice: str = "English-US.Female-1", 
                         language_code: str = "en-US") -> bytes:
        """Synthesize speech from text."""
        if not self.tts_service:
            raise HTTPException(status_code=503, detail="TTS service not available")
        
        try:
            # Use the correct Riva API
            response = self.tts_service.synthesize(
                text=text,
                voice_name=voice,
                language_code=language_code,
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                sample_rate_hz=22050
            )
            
            return response.audio
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

# Initialize Riva service
riva_service = RivaService()

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "NVIDIA Riva Speech API",
        "version": "1.0.0",
        "riva_available": riva_service.available,
        "endpoints": {
            "speech_to_text": "POST /speech-to-text",
            "text_to_speech": "POST /text-to-speech", 
            "status": "GET /riva-status",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if riva_service.is_healthy() else "degraded",
        "riva_available": riva_service.available,
        "services": {
            "asr": riva_service.asr_service is not None,
            "tts": riva_service.tts_service is not None,
            "nlp": riva_service.nlp_service is not None
        }
    }

@app.get("/riva-status")
async def riva_status():
    """Detailed Riva service status."""
    return {
        "riva_available": riva_service.available,
        "server": os.getenv("RIVA_SERVER", "localhost:50051"),
        "api_key_configured": bool(os.getenv("NVIDIA_RIVA_API_KEY")),
        "services": {
            "asr": riva_service.asr_service is not None,
            "tts": riva_service.tts_service is not None,
            "nlp": riva_service.nlp_service is not None
        },
        "auth_initialized": riva_service.auth is not None
    }

@app.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language_code: str = Form("en-US")
):
    """
    Convert uploaded audio file to text using NVIDIA Riva ASR.
    
    Supports: WAV, MP3, FLAC, and other audio formats supported by soundfile.
    """
    if not riva_service.available:
        raise HTTPException(
            status_code=503,
            detail="NVIDIA Riva service not available. Check server connection."
        )
    
    try:
        # Read uploaded audio file
        audio_content = await audio_file.read()
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        try:
            # Read audio with soundfile
            audio_data, sample_rate = sf.read(temp_file_path)
            
            # Ensure audio is mono
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Convert to int16 format expected by Riva
            if audio_data.dtype != np.int16:
                # Normalize to [-1, 1] then scale to int16 range
                if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                    audio_data = np.clip(audio_data, -1.0, 1.0)
                    audio_data = (audio_data * 32767).astype(np.int16)
                else:
                    audio_data = audio_data.astype(np.int16)
            
            # Convert to bytes
            audio_bytes = audio_data.tobytes()
            
            # Transcribe using Riva
            result = riva_service.transcribe_audio_file(audio_bytes, sample_rate, language_code)
            
            return SpeechToTextResponse(
                transcription=result["transcription"],
                language_code=language_code,
                confidence=result.get("confidence"),
                duration_seconds=len(audio_data) / sample_rate,
                status="success"
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using NVIDIA Riva TTS.
    
    Returns audio as WAV file download.
    """
    if not riva_service.available:
        raise HTTPException(
            status_code=503,
            detail="NVIDIA Riva service not available. Check server connection."
        )
    
    try:
        # Synthesize speech
        audio_bytes = riva_service.synthesize_speech(
            request.text, 
            request.voice, 
            request.language_code
        )
        
        # Convert raw audio bytes to WAV format
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_array, 22050, format='WAV')
        wav_buffer.seek(0)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(wav_buffer.getvalue()),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=synthesized_speech.wav"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {str(e)}")

if __name__ == "__main__":
    # Configuration
    port = int(os.getenv("RIVA_API_PORT", 8001))
    
    print("🎤 Starting NVIDIA Riva Speech API Server")
    print(f"📡 Server will run on http://localhost:{port}")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print(f"📊 Riva Status: http://localhost:{port}/riva-status")
    
    if not RIVA_AVAILABLE:
        print("\n⚠️  WARNING: NVIDIA Riva dependencies not available!")
        print("Install with: pip install nvidia-riva-client soundfile")
        print("Server will start but speech features will be disabled.\n")
    
    uvicorn.run(
        "riva_api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
