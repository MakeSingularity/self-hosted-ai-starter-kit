#!/usr/bin/env python3
"""
Local Whisper Speech Recognition for Telegram Audio
Handles audio files from Telegram and converts them to text using local Ollama Whisper models
"""

import os
import json
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import wave
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperSpeechRecognizer:
    """Local Whisper speech recognition using Ollama"""
    
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 model_name: str = "ZimaBlueAI/whisper-large-v3:latest",
                 fallback_model: str = "dimavz/whisper-tiny:latest"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.temp_dir = Path(tempfile.gettempdir()) / "whisper_audio"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Supported audio formats
        self.supported_formats = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.webm']
        
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and models are available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            logger.info(f"Available models: {model_names}")
            
            # Check if our preferred model is available
            if self.model_name in model_names:
                logger.info(f"Primary model {self.model_name} is available")
                return True
            elif self.fallback_model in model_names:
                logger.info(f"Using fallback model {self.fallback_model}")
                self.model_name = self.fallback_model
                return True
            else:
                logger.error("No Whisper models found in Ollama")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def convert_audio_format(self, input_path: Path, output_path: Path) -> bool:
        """Convert audio to WAV format using ffmpeg"""
        try:
            cmd = [
                "ffmpeg", "-i", str(input_path),
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y",  # Overwrite output file
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Audio converted successfully: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install ffmpeg for audio conversion.")
            return False
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return False
    
    def get_audio_info(self, audio_path: Path) -> Dict:
        """Get audio file information"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                str(audio_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": "Could not get audio info"}
                
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return {"error": str(e)}
    
    def transcribe_with_ollama(self, audio_path: Path) -> Dict:
        """Transcribe audio using Ollama Whisper model"""
        try:
            # Read audio file as binary
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # Prepare request for Ollama
            url = f"{self.ollama_url}/api/generate"
            
            # For Whisper models in Ollama, we need to use a different approach
            # First, let's try the standard generate endpoint
            payload = {
                "model": self.model_name,
                "prompt": "Transcribe this audio:",
                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            }
            
            # Convert audio to base64 for transmission
            import base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            payload["images"] = [audio_b64]  # Some Whisper implementations use images field
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "text": result.get("response", ""),
                "model_used": self.model_name,
                "confidence": 0.95  # Placeholder confidence
            }
            
        except Exception as e:
            logger.error(f"Ollama transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def transcribe_with_whisper_direct(self, audio_path: Path) -> Dict:
        """Fallback: Use OpenAI Whisper directly if available"""
        try:
            import whisper
            
            # Load model (this will download if not cached)
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(str(audio_path))
            
            return {
                "success": True,
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "confidence": 0.9,
                "segments": result.get("segments", [])
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "OpenAI Whisper not installed",
                "text": ""
            }
        except Exception as e:
            logger.error(f"Direct Whisper transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def process_telegram_audio(self, audio_file_path: str, file_format: str = None) -> Dict:
        """Process audio file from Telegram"""
        input_path = Path(audio_file_path)
        
        if not input_path.exists():
            return {
                "success": False,
                "error": f"Audio file not found: {audio_file_path}",
                "text": ""
            }
        
        # Get audio information
        audio_info = self.get_audio_info(input_path)
        logger.info(f"Audio info: {audio_info}")
        
        # Check Ollama status
        if not self.check_ollama_status():
            logger.warning("Ollama not available, trying direct Whisper")
            return self.transcribe_with_whisper_direct(input_path)
        
        # Convert to WAV if needed
        if input_path.suffix.lower() not in ['.wav']:
            wav_path = self.temp_dir / f"{input_path.stem}_converted.wav"
            if not self.convert_audio_format(input_path, wav_path):
                return {
                    "success": False,
                    "error": "Audio conversion failed",
                    "text": ""
                }
            transcribe_path = wav_path
        else:
            transcribe_path = input_path
        
        # Try transcription with Ollama
        result = self.transcribe_with_ollama(transcribe_path)
        
        # If Ollama fails, try direct Whisper
        if not result["success"]:
            logger.warning("Ollama transcription failed, trying direct Whisper")
            result = self.transcribe_with_whisper_direct(transcribe_path)
        
        # Cleanup temporary files
        if transcribe_path != input_path and transcribe_path.exists():
            transcribe_path.unlink()
        
        return result
    
    def process_telegram_voice_message(self, voice_data: Dict) -> Dict:
        """Process Telegram voice message format"""
        try:
            # Extract voice message info
            file_id = voice_data.get("file_id")
            duration = voice_data.get("duration", 0)
            mime_type = voice_data.get("mime_type", "audio/ogg")
            
            logger.info(f"Processing voice message: {file_id}, duration: {duration}s, type: {mime_type}")
            
            # Note: In real implementation, you'd download the file from Telegram
            # For now, assume we have a local file path
            # voice_file_path = download_telegram_file(file_id)
            
            return {
                "success": False,
                "error": "Telegram file download not implemented yet",
                "text": "",
                "file_id": file_id,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Voice message processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }

class TelegramAudioHandler:
    """Handle Telegram audio integration with n8n workflow"""
    
    def __init__(self, whisper_recognizer: WhisperSpeechRecognizer):
        self.whisper = whisper_recognizer
        self.n8n_api_url = "http://localhost:5678/api/v1"
        self.n8n_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
        self.headers = {"X-N8N-API-KEY": self.n8n_api_key}
    
    def create_speech_recognition_node_data(self, transcription_result: Dict, original_message: Dict) -> Dict:
        """Create data structure for n8n speech recognition node"""
        return {
            "transcription": {
                "text": transcription_result.get("text", ""),
                "success": transcription_result.get("success", False),
                "confidence": transcription_result.get("confidence", 0.0),
                "language": transcription_result.get("language", "unknown"),
                "model_used": transcription_result.get("model_used", "unknown"),
                "duration": transcription_result.get("duration", 0),
                "error": transcription_result.get("error", None)
            },
            "original_message": original_message,
            "processed_at": "{{ $now }}",
            "speech_to_text_enabled": True
        }
    
    def test_with_sample_audio(self, sample_path: str) -> Dict:
        """Test speech recognition with a sample audio file"""
        if not os.path.exists(sample_path):
            return {
                "success": False,
                "error": f"Sample file not found: {sample_path}"
            }
        
        result = self.whisper.process_telegram_audio(sample_path)
        
        # Create n8n-compatible data structure
        n8n_data = self.create_speech_recognition_node_data(
            result, 
            {"type": "voice", "file_path": sample_path}
        )
        
        return {
            "transcription_result": result,
            "n8n_data": n8n_data,
            "test_successful": result.get("success", False)
        }

def main():
    """Command line interface for Whisper speech recognition"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python whisper_speech_recognition.py <command> [options]")
        print("Commands:")
        print("  test [audio_file]     - Test with audio file")
        print("  status               - Check Whisper/Ollama status")
        print("  models               - List available models")
        print("  transcribe <file>    - Transcribe audio file")
        return
    
    recognizer = WhisperSpeechRecognizer()
    handler = TelegramAudioHandler(recognizer)
    command = sys.argv[1].lower()
    
    if command == "status":
        status = recognizer.check_ollama_status()
        print(f"Whisper Status: {'✅ Ready' if status else '❌ Not Ready'}")
        print(f"Model: {recognizer.model_name}")
        print(f"Ollama URL: {recognizer.ollama_url}")
    
    elif command == "models":
        try:
            response = requests.get(f"{recognizer.ollama_url}/api/tags")
            models = response.json().get("models", [])
            whisper_models = [m for m in models if "whisper" in m["name"].lower()]
            
            print("Available Whisper Models:")
            for model in whisper_models:
                size_mb = model["size"] / (1024 * 1024)
                print(f"  - {model['name']} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"Error getting models: {e}")
    
    elif command == "transcribe" and len(sys.argv) > 2:
        audio_file = sys.argv[2]
        result = recognizer.process_telegram_audio(audio_file)
        print(json.dumps(result, indent=2))
    
    elif command == "test":
        audio_file = sys.argv[2] if len(sys.argv) > 2 else "test_audio.wav"
        result = handler.test_with_sample_audio(audio_file)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
