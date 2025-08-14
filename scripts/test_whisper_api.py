#!/usr/bin/env python3
"""
Test script for Whisper API Server
Tests various endpoints and functionality
"""

import requests
import json
import time
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test basic health check"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API running: {data['message']}")
            print(f"   Whisper ready: {data['whisper_ready']}")
            print(f"   Model: {data['model']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_status_endpoint():
    """Test detailed status information"""
    print("\n🔍 Testing status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status check successful")
            print(f"   Ollama connected: {data['ollama_connected']}")
            print(f"   Whisper models: {data['whisper_models_available']}")
            print(f"   Primary model: {data['primary_model']}")
            print(f"   Available models:")
            for model in data.get('models', []):
                print(f"     - {model['name']} ({model['size_mb']} MB)")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_model_endpoints():
    """Test model availability"""
    print("\n🔍 Testing model endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/test/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model test successful")
            print(f"   Total models: {data['total_models']}")
            print(f"   Whisper models: {data['whisper_models']}")
            print(f"   Model status:")
            for model in data.get('model_tests', []):
                status_icon = "✅" if model['status'] == 'available' else "❌"
                print(f"     {status_icon} {model['name']} ({model['size_mb']} MB) - {model['status']}")
                if model.get('error'):
                    print(f"        Error: {model['error']}")
            return True
        else:
            print(f"❌ Model test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_n8n_endpoint():
    """Test n8n integration endpoint"""
    print("\n🔍 Testing n8n integration endpoint...")
    try:
        # Test with voice message
        test_voice_message = {
            "message": {
                "voice": {
                    "file_id": "BAADBAADKwADBREAAakbm_kSL9XNAI",
                    "duration": 5
                },
                "from": {"id": 123456789, "username": "testuser"}
            }
        }
        
        response = requests.post(f"{BASE_URL}/transcribe/n8n", json=test_voice_message)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ n8n endpoint test successful")
            print(f"   Message type: {data['message_type']}")
            print(f"   Needs transcription: {data['needs_transcription']}")
            print(f"   Transcription: {data['transcription']['text']}")
            if data.get('setup_required'):
                print(f"   ⚠️ Setup required: {data['setup_required']}")
            return True
        else:
            print(f"❌ n8n endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ n8n endpoint test error: {e}")
        return False

def test_text_message():
    """Test with text message (should pass through)"""
    print("\n🔍 Testing text message handling...")
    try:
        test_text_message = {
            "message": {
                "text": "Hello, this is a text message",
                "from": {"id": 123456789, "username": "testuser"}
            }
        }
        
        response = requests.post(f"{BASE_URL}/transcribe/n8n", json=test_text_message)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text message test successful")
            print(f"   Message type: {data['message_type']}")
            print(f"   Needs transcription: {data['needs_transcription']}")
            print(f"   Text: {data['transcription']['text']}")
            return True
        else:
            print(f"❌ Text message test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Text message test error: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🎤 Whisper API Server Test Suite")
    print("=" * 50)
    
    tests = [
        test_api_health,
        test_status_endpoint,
        test_model_endpoints,
        test_n8n_endpoint,
        test_text_message
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is ready for production.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
