#!/usr/bin/env python3
"""
Test script for the hybrid speech API server
Demonstrates TTS functionality with different engines
"""

import requests
import json
import time
import os

def test_speech_api():
    """Test the speech API endpoints"""
    base_url = "http://localhost:8001"
    
    print("🎤 Testing Hybrid Speech API Server")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✓ Status: {health_data['status']}")
            print(f"✓ Engines: {health_data['engines']}")
            print(f"✓ Primary: {health_data['primary_engine']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: List Engines
    print("\n2. Available Engines")
    try:
        response = requests.get(f"{base_url}/engines", timeout=5)
        if response.status_code == 200:
            engines_data = response.json()
            print("TTS Engines:")
            for engine in engines_data['tts_engines']:
                status = "✓" if engine['available'] else "❌"
                print(f"  {status} {engine['name']}: {engine['description']}")
            
            print("ASR Engines:")
            for engine in engines_data['asr_engines']:
                status = "✓" if engine['available'] else "❌"
                print(f"  {status} {engine['name']}: {engine['description']}")
        else:
            print(f"❌ Engines check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Engines check error: {e}")
    
    # Test 3: TTS with pyttsx3
    print("\n3. Testing TTS with pyttsx3")
    try:
        payload = {
            "text": "Hello! This is a test of the pyttsx3 text-to-speech engine. It should work reliably on Windows.",
            "voice": "English-US.Female-1",
            "engine": "pyttsx3"
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            f"{base_url}/text-to-speech",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            # Save the audio file
            with open("test_pyttsx3.wav", "wb") as f:
                f.write(response.content)
            
            engine_used = response.headers.get('X-Engine-Used', 'unknown')
            audio_length = response.headers.get('X-Audio-Length', 'unknown')
            
            print(f"✓ TTS successful with {engine_used}")
            print(f"✓ Audio file saved: test_pyttsx3.wav ({audio_length} bytes)")
            
        else:
            print(f"❌ TTS failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ TTS error: {e}")
    
    # Test 4: TTS with auto engine
    print("\n4. Testing TTS with auto engine selection")
    try:
        payload = {
            "text": "This test uses automatic engine selection. The system will try the best available engine.",
            "voice": "English-US.Female-1",
            "engine": "auto"
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            f"{base_url}/text-to-speech",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            with open("test_auto.wav", "wb") as f:
                f.write(response.content)
            
            engine_used = response.headers.get('X-Engine-Used', 'unknown')
            audio_length = response.headers.get('X-Audio-Length', 'unknown')
            
            print(f"✓ Auto TTS successful with {engine_used}")
            print(f"✓ Audio file saved: test_auto.wav ({audio_length} bytes)")
            
        else:
            print(f"❌ Auto TTS failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Auto TTS error: {e}")
    
    # Test 5: File verification
    print("\n5. Verifying generated files")
    test_files = ["test_pyttsx3.wav", "test_auto.wav"]
    
    for filename in test_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename}: {size} bytes")
        else:
            print(f"❌ {filename}: Not found")
    
    print("\n" + "=" * 50)
    print("🎉 Speech API test completed!")
    print("\nGenerated files can be played to verify speech synthesis.")
    print("Use Windows Media Player, VLC, or any audio player to test the output.")
    
    return True

if __name__ == "__main__":
    print("Starting speech API tests...")
    print("Make sure the hybrid speech server is running on port 8001")
    print()
    
    # Give user a moment to verify server is running
    time.sleep(1)
    
    success = test_speech_api()
    
    if success:
        print("\n🚀 Ready for n8n integration!")
        print("You can now use the speech services in your n8n workflows.")
    else:
        print("\n❌ Tests failed. Check the server status and try again.")
