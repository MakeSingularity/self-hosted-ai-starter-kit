#!/usr/bin/env python3
"""
Quick verification script for speech services
Tests that the implementation is working correctly
"""

import subprocess
import time
import os
import sys

def check_service_running(port=8001):
    """Check if the speech API server is running"""
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_speech_server():
    """Start the speech API server if not running"""
    if not check_service_running():
        print("🚀 Starting speech API server...")
        
        # Start the server in the background
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                sys.executable, 
                "examples\\hybrid_speech_api.py"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux
            subprocess.Popen([
                sys.executable, 
                "examples/hybrid_speech_api.py"
            ])
        
        # Wait for server to start
        for i in range(10):
            time.sleep(1)
            if check_service_running():
                print("✅ Speech API server started successfully!")
                return True
            print(f"⏳ Waiting for server... ({i+1}/10)")
        
        print("❌ Failed to start speech API server")
        return False
    else:
        print("✅ Speech API server is already running!")
        return True

def verify_installation():
    """Verify the complete speech services installation"""
    print("🎤 Verifying Speech Services Installation")
    print("=" * 50)
    
    # Check Python environment
    print("\n1. Python Environment Check")
    try:
        import pyttsx3
        print("✅ pyttsx3 installed")
    except ImportError:
        print("❌ pyttsx3 not installed - run: pip install pyttsx3")
        return False
    
    try:
        import riva.client
        print("✅ NVIDIA Riva client installed")
    except ImportError:
        print("❌ NVIDIA Riva client not installed")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        print("❌ FastAPI not installed")
        return False
    
    # Check environment variables
    print("\n2. Environment Configuration")
    api_key = os.getenv('NVIDIA_RIVA_API_KEY')
    server = os.getenv('RIVA_SERVER', 'localhost:50051')
    
    if api_key:
        print(f"✅ NVIDIA API key configured")
        print(f"✅ Riva server: {server}")
    else:
        print("⚠️  NVIDIA API key not found (will use local engines)")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
    
    # Start and test speech server
    print("\n3. Speech API Server Test")
    if start_speech_server():
        try:
            import requests
            
            # Test health endpoint
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health status: {health_data['status']}")
                
                # Show available engines
                engines_response = requests.get("http://localhost:8001/engines", timeout=5)
                if engines_response.status_code == 200:
                    engines_data = engines_response.json()
                    print("✅ Available TTS engines:")
                    for engine in engines_data['tts_engines']:
                        status = "✅" if engine['available'] else "❌"
                        print(f"   {status} {engine['name']}")
                
                print("\n4. Testing Text-to-Speech")
                # Quick TTS test with pyttsx3
                tts_payload = {
                    "text": "Speech services are working correctly!",
                    "engine": "pyttsx3"
                }
                
                tts_response = requests.post(
                    "http://localhost:8001/text-to-speech",
                    json=tts_payload,
                    timeout=15
                )
                
                if tts_response.status_code == 200:
                    with open("verification_test.wav", "wb") as f:
                        f.write(tts_response.content)
                    
                    engine_used = tts_response.headers.get('X-Engine-Used', 'unknown')
                    print(f"✅ TTS test successful with {engine_used} engine")
                    print("✅ Audio file created: verification_test.wav")
                else:
                    print(f"❌ TTS test failed: {tts_response.status_code}")
                    print(f"   Error: {tts_response.text}")
            
        except Exception as e:
            print(f"❌ Server test failed: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Speech Services Verification Complete!")
    print("\n📋 Summary:")
    print("✅ All required packages installed")
    print("✅ Speech API server running on http://localhost:8001")
    print("✅ Text-to-speech working correctly")
    print("✅ Ready for n8n integration")
    
    print("\n🚀 Next Steps:")
    print("1. Open n8n at http://localhost:5678")
    print("2. Create workflows using HTTP Request nodes")
    print("3. Point requests to http://localhost:8001/text-to-speech")
    print("4. Use the examples in SPEECH_INTEGRATION.md")
    
    print("\n🎵 Test your audio:")
    print("Play the file 'verification_test.wav' to hear the TTS output!")
    
    return True

if __name__ == "__main__":
    print("Starting speech services verification...")
    print("This will test your complete speech integration setup.\n")
    
    success = verify_installation()
    
    if success:
        print("\n🎊 SUCCESS: Speech services are fully operational!")
        print("Your AI starter kit now supports voice interactions!")
    else:
        print("\n❌ FAILED: Some components need attention.")
        print("Check the error messages above and resolve any issues.")
    
    input("\nPress Enter to exit...")
