#!/usr/bin/env python3
"""
NVIDIA Riva Client Integration Example

This script demonstrates how to integrate NVIDIA Riva speech services 
with the n8n AI starter kit.

Features:
- Automatic Speech Recognition (ASR)
- Text-to-Speech (TTS)
- Natural Language Processing (NLP)
- Integration with n8n workflows via HTTP API

Usage:
    python examples/riva_integration_example.py --help
"""

import argparse
import asyncio
import sys
import os
from typing import Optional

try:
    import riva.client
    import soundfile as sf
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please install with: pip install nvidia-riva-client soundfile")
    sys.exit(1)


class RivaClient:
    """NVIDIA Riva client wrapper for ASR, TTS, and NLP services."""
    
    def __init__(self, server: str = "localhost:50051", 
                 use_ssl: bool = False, 
                 api_key: Optional[str] = None):
        """
        Initialize Riva client.
        
        Args:
            server: Riva server address (default: localhost:50051)
            use_ssl: Whether to use SSL connection
            api_key: NVIDIA API key if using cloud services
        """
        self.server = server
        self.use_ssl = use_ssl
        self.api_key = api_key
        
        # Initialize service clients
        self.auth = None
        self.asr_service = None
        self.tts_service = None
        self.nlp_service = None
        
        self._initialize_auth()
    
    def _initialize_auth(self):
        """Initialize authentication."""
        try:
            if self.api_key:
                # Use API key for cloud services
                self.auth = riva.client.Auth(uri=self.server, use_ssl=self.use_ssl, 
                                           metadata_args=[("authorization", f"Bearer {self.api_key}")])
            else:
                # Use local server
                self.auth = riva.client.Auth(uri=self.server, use_ssl=self.use_ssl)
            
            # Initialize service clients
            self.asr_service = riva.client.ASRService(self.auth)
            self.tts_service = riva.client.TTSService(self.auth)
            self.nlp_service = riva.client.NLPService(self.auth)
            
            print(f"✓ Connected to Riva server at {self.server}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to Riva server: {e}")
            print("Make sure the Riva server is running or check your configuration.")
    
    def transcribe_audio(self, audio_file: str, language_code: str = "en-US") -> str:
        """
        Transcribe audio file to text using ASR.
        
        Args:
            audio_file: Path to audio file
            language_code: Language code (e.g., 'en-US')
            
        Returns:
            Transcribed text
        """
        if not self.asr_service:
            return "Error: ASR service not available"
        
        try:
            # Read audio file
            audio_data, sample_rate = sf.read(audio_file)
            
            # Convert to bytes
            if audio_data.dtype != np.int16:
                audio_data = (audio_data * 32767).astype(np.int16)
            
            audio_bytes = audio_data.tobytes()
            
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
            return f"Error transcribing audio: {e}"
    
    def synthesize_speech(self, text: str, output_file: str = None, 
                         voice: str = "English-US.Female-1") -> bytes:
        """
        Synthesize speech from text using TTS.
        
        Args:
            text: Text to synthesize
            output_file: Optional output file path
            voice: Voice to use for synthesis
            
        Returns:
            Audio data as bytes
        """
        if not self.tts_service:
            print("Error: TTS service not available")
            return b""
        
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
            audio_data = response.audio
            
            # Save to file if specified
            if output_file:
                # Convert bytes to numpy array and save
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                sf.write(output_file, audio_array, 22050)
                print(f"✓ Audio saved to {output_file}")
            
            return audio_data
            
        except Exception as e:
            print(f"Error synthesizing speech: {e}")
            return b""
    
    def analyze_intent(self, text: str) -> dict:
        """
        Analyze intent and slots in text using NLP.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with intent and slots
        """
        if not self.nlp_service:
            return {"error": "NLP service not available"}
        
        try:
            # Create intent recognition request
            request = riva.client.AnalyzeIntentRequest(
                query=text
            )
            
            # Analyze
            response = self.nlp_service.analyze_intent(request)
            
            return {
                "intent": response.intent.intent_name,
                "confidence": response.intent.score,
                "slots": [
                    {
                        "slot": slot.slot_name,
                        "value": slot.slot_value,
                        "confidence": slot.score
                    }
                    for slot in response.slots
                ]
            }
            
        except Exception as e:
            return {"error": f"Error analyzing intent: {e}"}
    
    def analyze_entities(self, text: str) -> list:
        """
        Extract named entities from text using NLP.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected entities
        """
        if not self.nlp_service:
            return [{"error": "NLP service not available"}]
        
        try:
            # Create NER request
            request = riva.client.TokenClassRequest(
                text=[text]
            )
            
            # Analyze
            response = self.nlp_service.analyze_entities(request)
            
            entities = []
            for result in response.results:
                for token in result.results:
                    if token.label != "O":  # "O" means "outside" (no entity)
                        entities.append({
                            "text": token.token,
                            "label": token.label,
                            "confidence": token.score
                        })
            
            return entities
            
        except Exception as e:
            return [{"error": f"Error analyzing entities: {e}"}]


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(description="NVIDIA Riva Integration Example")
    parser.add_argument("--server", default="localhost:50051", 
                       help="Riva server address")
    parser.add_argument("--api-key", help="NVIDIA API key (for cloud services)")
    parser.add_argument("--use-ssl", action="store_true", 
                       help="Use SSL connection")
    
    # Operation selection
    parser.add_argument("--operation", choices=["asr", "tts", "nlp"], 
                       required=True, help="Operation to perform")
    
    # ASR options
    parser.add_argument("--audio-file", help="Audio file for ASR")
    parser.add_argument("--language", default="en-US", 
                       help="Language code for ASR")
    
    # TTS options
    parser.add_argument("--text", help="Text for TTS or NLP")
    parser.add_argument("--output-audio", help="Output audio file for TTS")
    parser.add_argument("--voice", default="English-US.Female-1", 
                       help="Voice for TTS")
    
    # NLP options
    parser.add_argument("--nlp-task", choices=["intent", "entities"], 
                       default="intent", help="NLP task to perform")
    
    args = parser.parse_args()
    
    # Initialize Riva client
    client = RivaClient(
        server=args.server,
        use_ssl=args.use_ssl,
        api_key=args.api_key
    )
    
    # Perform operation
    if args.operation == "asr":
        if not args.audio_file:
            print("Error: --audio-file required for ASR")
            return
        
        if not os.path.exists(args.audio_file):
            print(f"Error: Audio file not found: {args.audio_file}")
            return
        
        print(f"Transcribing {args.audio_file}...")
        transcript = client.transcribe_audio(args.audio_file, args.language)
        print(f"Transcript: {transcript}")
    
    elif args.operation == "tts":
        if not args.text:
            print("Error: --text required for TTS")
            return
        
        print(f"Synthesizing speech for: '{args.text}'")
        audio_data = client.synthesize_speech(
            args.text, 
            args.output_audio, 
            args.voice
        )
        
        if audio_data:
            print(f"✓ Generated {len(audio_data)} bytes of audio")
        else:
            print("✗ Failed to generate audio")
    
    elif args.operation == "nlp":
        if not args.text:
            print("Error: --text required for NLP")
            return
        
        if args.nlp_task == "intent":
            print(f"Analyzing intent for: '{args.text}'")
            result = client.analyze_intent(args.text)
            print(f"Result: {result}")
        
        elif args.nlp_task == "entities":
            print(f"Extracting entities from: '{args.text}'")
            entities = client.analyze_entities(args.text)
            print(f"Entities: {entities}")


if __name__ == "__main__":
    main()
