#!/usr/bin/env python3
"""
Test NVIDIA Riva cloud connection
"""
import os
import sys
from dotenv import load_dotenv
import riva.client

def test_riva_connection():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('NVIDIA_RIVA_API_KEY') or os.getenv('NVIDIA_API_KEY')
    server = os.getenv('RIVA_SERVER', 'grpc.nvcf.nvidia.com:443')
    
    print(f"Testing connection to NVIDIA Riva cloud services...")
    print(f"Server: {server}")
    print(f"API Key: {'Set' if api_key else 'Not set'}")
    
    if not api_key:
        print("❌ NVIDIA_RIVA_API_KEY not found in environment")
        return False
    
    try:
        # Create auth with API key and function ID for cloud services
        metadata_args = [
            ("authorization", f"Bearer {api_key}"),
            ("x-nvcf-reqid", "test-request-123"),  # Optional request ID
        ]
        
        # For TTS, we need to specify the function ID
        if "nvcf.nvidia.com" in server:
            # NVIDIA Cloud Functions TTS function ID
            metadata_args.append(("function-id", "nv-riva-tts"))
        
        auth = riva.client.Auth(
            uri=server,
            use_ssl=True,
            metadata_args=metadata_args
        )
        
        print("✓ Auth object created successfully")
        
        # Test TTS service
        print("Testing TTS service...")
        tts_service = riva.client.SpeechSynthesisService(auth)
        print("✓ TTS service created successfully")
        
        # Test ASR service with ASR function ID
        print("Testing ASR service...")
        asr_metadata_args = [
            ("authorization", f"Bearer {api_key}"),
            ("function-id", "nv-riva-asr"),  # ASR function ID
        ]
        asr_auth = riva.client.Auth(
            uri=server,
            use_ssl=True,
            metadata_args=asr_metadata_args
        )
        asr_service = riva.client.ASRService(asr_auth)
        print("✓ ASR service created successfully")
        
        # Try a simple TTS request
        print("Testing TTS synthesis...")
        response = tts_service.synthesize(
            text="Test",
            voice_name="English-US.Female-1",
            language_code="en-US",
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            sample_rate_hz=22050
        )
        
        if response and hasattr(response, 'audio'):
            print(f"✓ TTS synthesis successful - audio length: {len(response.audio)} bytes")
            return True
        else:
            print("❌ TTS synthesis returned no audio")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Riva: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_riva_connection()
    sys.exit(0 if success else 1)
