"""
FastAPI server that provides AI services to n8n workflows
Run this server and use HTTP Request nodes in n8n to call the endpoints

Usage:
1. Activate your conda environment: conda activate ai-starter-kit
2. Run the server: python examples/api_server.py
3. Use HTTP Request nodes in n8n to call: http://localhost:8000/process-text
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
from typing import Optional
import os
import tempfile
import io

# Try to import Riva client (optional)
try:
    import riva.client
    import soundfile as sf
    import numpy as np
    RIVA_AVAILABLE = True
except ImportError:
    RIVA_AVAILABLE = False
    print("⚠️  NVIDIA Riva client not available. Speech features will be disabled.")
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="n8n AI Integration API",
    description="Local AI services for n8n workflows",
    version="1.0.0"
)

class TextProcessRequest(BaseModel):
    text: str
    operation: str = "summarize"  # summarize, sentiment, extract_entities
    options: Optional[dict] = None

class TextProcessResponse(BaseModel):
    result: dict
    status: str
    operation: str

class SpeechToTextRequest(BaseModel):
    language_code: str = "en-US"

class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "English-US.Female-1"
    output_format: str = "wav"

class RivaClientWrapper:
    """Wrapper for NVIDIA Riva client services."""
    
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
            # Use environment variables or defaults
            server = os.getenv("RIVA_SERVER", "localhost:50051")
            api_key = os.getenv("NVIDIA_RIVA_API_KEY")
            
            if api_key:
                # Use API key for cloud services
                self.auth = riva.client.Auth(
                    uri=server, 
                    use_ssl=True,
                    metadata_args=[("authorization", f"Bearer {api_key}")]
                )
            else:
                # Use local server
                self.auth = riva.client.Auth(uri=server, use_ssl=False)
            
            # Initialize service clients
            self.asr_service = riva.client.ASRService(self.auth)
            self.tts_service = riva.client.TTSService(self.auth)
            self.nlp_service = riva.client.NLPService(self.auth)
            
            print(f"✓ Connected to Riva server at {server}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to Riva server: {e}")
            self.available = False
    
    def transcribe_audio(self, audio_bytes: bytes, sample_rate: int = 16000, 
                        language_code: str = "en-US") -> str:
        """Transcribe audio bytes to text."""
        if not self.available or not self.asr_service:
            raise HTTPException(status_code=503, detail="ASR service not available")
        
        try:
            # Create ASR config
            config = riva.client.RecognitionConfig(
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                sample_rate_hertz=sample_rate,
                language_code=language_code,
                max_alternatives=1,
                enable_automatic_punctuation=True,
            )
            
            # Create request
            request = riva.client.RecognizeRequest(
                config=config,
                audio=riva.client.RecognitionAudio(content=audio_bytes)
            )
            
            # Transcribe
            response = self.asr_service.recognize(request)
            
            if response.results:
                return response.results[0].alternatives[0].transcript
            else:
                return "No speech detected"
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ASR error: {e}")
    
    def synthesize_speech(self, text: str, voice: str = "English-US.Female-1") -> bytes:
        """Synthesize speech from text."""
        if not self.available or not self.tts_service:
            raise HTTPException(status_code=503, detail="TTS service not available")
        
        try:
            # Create TTS request
            request = riva.client.SynthesizeSpeechRequest(
                input=riva.client.SynthesisInput(text=text),
                voice=riva.client.VoiceSelectionParams(
                    language_code="en-US",
                    name=voice
                ),
                audio_config=riva.client.AudioConfig(
                    audio_encoding=riva.client.AudioEncoding.LINEAR_PCM,
                    sample_rate_hertz=22050
                )
            )
            
            # Synthesize
            response = self.tts_service.synthesize(request)
            return response.audio
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS error: {e}")

# Initialize Riva client
riva_client = RivaClientWrapper()

@app.get("/")
async def root():
    endpoints = [
        "/process-text - POST - Process text with AI",
        "/health - GET - Health check",
        "/docs - GET - API documentation"
    ]
    
    if riva_client.available:
        endpoints.extend([
            "/speech-to-text - POST - Convert audio to text (ASR)",
            "/text-to-speech - POST - Convert text to audio (TTS)"
        ])
    
    return {
        "message": "n8n AI Integration API",
        "riva_available": riva_client.available,
        "endpoints": endpoints
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "n8n-ai-integration"}

@app.post("/process-text", response_model=TextProcessResponse)
async def process_text(request: TextProcessRequest):
    """
    Process text using various AI operations
    """
    try:
        if request.operation == "summarize":
            # Simple summarization (in production, use transformers, etc.)
            words = request.text.split()
            summary = " ".join(words[:min(30, len(words))])
            if len(words) > 30:
                summary += "..."
            
            result = {
                "summary": summary,
                "original_length": len(request.text),
                "word_count": len(words),
                "compression_ratio": len(summary) / len(request.text)
            }
            
        elif request.operation == "sentiment":
            # Sentiment analysis (in production, use proper models)
            text_lower = request.text.lower()
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "awesome"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing", "sad", "angry"]
            
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                sentiment = "positive"
                confidence = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
            elif neg_count > pos_count:
                sentiment = "negative" 
                confidence = min(0.9, 0.5 + (neg_count - pos_count) * 0.1)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            result = {
                "sentiment": sentiment,
                "confidence": confidence,
                "positive_indicators": pos_count,
                "negative_indicators": neg_count
            }
            
        elif request.operation == "extract_entities":
            # Simple entity extraction (in production, use spaCy, etc.)
            import re
            
            # Extract emails
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', request.text)
            
            # Extract phone numbers (simple pattern)
            phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', request.text)
            
            # Extract URLs
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', request.text)
            
            result = {
                "entities": {
                    "emails": emails,
                    "phone_numbers": phones,
                    "urls": urls
                },
                "counts": {
                    "emails": len(emails),
                    "phone_numbers": len(phones),
                    "urls": len(urls)
                }
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {request.operation}")
        
        return TextProcessResponse(
            result=result,
            status="success",
            operation=request.operation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/riva-speech")
async def riva_speech_to_text(audio_data: bytes):
    """
    Example endpoint for NVIDIA Riva speech-to-text
    In production, this would connect to your Riva service
@app.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language_code: str = Form("en-US")
):
    """
    Convert uploaded audio file to text using NVIDIA Riva ASR.
    
    Parameters:
    - audio_file: Audio file (WAV, MP3, etc.)
    - language_code: Language code (default: en-US)
    """
    if not riva_client.available:
        raise HTTPException(
            status_code=503, 
            detail="NVIDIA Riva ASR service not available. Please check server connection."
        )
    
    try:
        # Read uploaded file
        audio_content = await audio_file.read()
        
        # Create temporary file to process audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        try:
            # Read audio with soundfile
            audio_data, sample_rate = sf.read(temp_file_path)
            
            # Convert to int16 if needed
            if audio_data.dtype != np.int16:
                audio_data = (audio_data * 32767).astype(np.int16)
            
            # Convert to bytes
            audio_bytes = audio_data.tobytes()
            
            # Transcribe using Riva
            transcript = riva_client.transcribe_audio(audio_bytes, sample_rate, language_code)
            
            return {
                "transcription": transcript,
                "language_code": language_code,
                "audio_duration_seconds": len(audio_data) / sample_rate,
                "sample_rate": sample_rate,
                "status": "success"
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")

@app.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using NVIDIA Riva TTS.
    
    Parameters:
    - text: Text to synthesize
    - voice: Voice to use (default: English-US.Female-1)
    - output_format: Output format (default: wav)
    """
    if not riva_client.available:
        raise HTTPException(
            status_code=503,
            detail="NVIDIA Riva TTS service not available. Please check server connection."
        )
    
    try:
        # Synthesize speech
        audio_bytes = riva_client.synthesize_speech(request.text, request.voice)
        
        # Convert to numpy array and then to WAV bytes
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Create WAV file in memory
        wav_io = io.BytesIO()
        sf.write(wav_io, audio_array, 22050, format='WAV')
        wav_io.seek(0)
        
        # Return audio file
        return StreamingResponse(
            io.BytesIO(wav_io.getvalue()),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=synthesized_speech.wav"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {e}")

@app.post("/riva-status")
async def riva_status():
    """
    Check NVIDIA Riva service status and capabilities.
    """
    return {
        "riva_available": riva_client.available,
        "services": {
            "asr": riva_client.asr_service is not None,
            "tts": riva_client.tts_service is not None,
            "nlp": riva_client.nlp_service is not None
        },
        "server": os.getenv("RIVA_SERVER", "localhost:50051"),
        "api_key_configured": bool(os.getenv("NVIDIA_RIVA_API_KEY"))
    }

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("API_PORT", 8000))
    
    print(f"🚀 Starting n8n AI Integration API on port {port}")
    print(f"📝 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
