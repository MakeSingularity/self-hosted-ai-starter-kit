#!/usr/bin/env python3
"""
Test Whisper API connection from Docker network perspective
"""

import requests
import json

def test_host_connection():
    """Test connection using host.docker.internal"""
    try:
        print("🔍 Testing connection to Whisper API from Docker perspective...")
        
        # Test basic health check
        response = requests.get("http://host.docker.internal:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connection successful!")
            print(f"   API: {data['message']}")
            print(f"   Status: {data['status']}")
            print(f"   Whisper Ready: {data['whisper_ready']}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("💡 This suggests n8n cannot reach host.docker.internal:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_n8n_endpoint():
    """Test the specific n8n endpoint"""
    try:
        print("\n🔍 Testing n8n transcription endpoint...")
        
        test_payload = {
            "message": {
                "voice": {
                    "file_id": "test_file_id",
                    "duration": 5
                },
                "from": {"id": 123456789, "username": "testuser"}
            }
        }
        
        response = requests.post(
            "http://host.docker.internal:8000/transcribe/n8n",
            json=test_payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ n8n endpoint working!")
            print(f"   Message type: {data.get('message_type')}")
            print(f"   Needs transcription: {data.get('needs_transcription')}")
            return True
        else:
            print(f"❌ n8n endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ n8n endpoint error: {e}")
        return False

def suggest_alternatives():
    """Suggest alternative solutions"""
    print("\n🔧 Alternative Solutions:")
    print("1. **Add Whisper service to docker-compose.yml**")
    print("2. **Use ngrok tunnel for Whisper API**")
    print("3. **Run Whisper API inside Docker network**")
    print("4. **Use Docker host networking mode**")

if __name__ == "__main__":
    print("🐳 Docker Network Connection Test for Whisper API")
    print("=" * 60)
    
    health_ok = test_host_connection()
    endpoint_ok = test_n8n_endpoint()
    
    if health_ok and endpoint_ok:
        print("\n🎉 All tests passed! n8n should be able to reach Whisper API")
        print("   Use: http://host.docker.internal:8000/transcribe/n8n")
    else:
        print("\n⚠️ Connection issues detected")
        suggest_alternatives()
