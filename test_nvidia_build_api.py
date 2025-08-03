#!/usr/bin/env python3
"""
Test NVIDIA Build API for speech services
"""
import os
import requests
from dotenv import load_dotenv
import json

def test_nvidia_build_api():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('NVIDIA_RIVA_API_KEY') or os.getenv('NVIDIA_API_KEY')
    
    print(f"Testing NVIDIA Build API for speech services...")
    print(f"API Key: {'Set' if api_key else 'Not set'}")
    
    if not api_key:
        print("❌ API key not found in environment")
        return False
    
    # Test TTS via NVIDIA Build API
    try:
        print("Testing TTS via NVIDIA Build API...")
        
        # NVIDIA Build API endpoint for TTS
        url = "https://api.nvidia.com/v1/riva/speech_synthesis/synthesize"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": "Hello from NVIDIA Build API!",
            "voice": "English-US.Female-1",
            "encoding": "LINEAR_PCM",
            "sample_rate_hz": 22050
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✓ TTS synthesis successful via Build API")
            # Save audio if returned
            with open("build_api_test.wav", "wb") as f:
                f.write(response.content)
            print(f"✓ Audio saved to build_api_test.wav ({len(response.content)} bytes)")
            return True
        else:
            print(f"❌ TTS failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error with Build API: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_nvidia_build_api()
