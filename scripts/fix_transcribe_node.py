#!/usr/bin/env python3
"""
Fix the Transcribe Voice Message HTTP Request node configuration
"""

import requests
import json

def fix_transcribe_node():
    """Fix the HTTP Request node configuration for voice transcription"""
    
    n8n_url = "http://localhost:5678"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
    headers = {"X-N8N-API-KEY": api_key}
    workflow_id = "rKO0PUthz0jXtKhD"
    
    print("🔧 Fixing Transcribe Voice Message Node")
    print("=" * 45)
    
    # Get current workflow
    try:
        response = requests.get(f"{n8n_url}/api/v1/workflows/{workflow_id}", headers=headers)
        workflow = response.json()
        print(f"✅ Got workflow: {workflow['name']}")
    except Exception as e:
        print(f"❌ Could not get workflow: {e}")
        return False
    
    # Find the Transcribe Voice Message node
    transcribe_node = None
    for node in workflow["nodes"]:
        if node.get("name") == "Transcribe Voice Message":
            transcribe_node = node
            break
    
    if not transcribe_node:
        print("❌ Transcribe Voice Message node not found")
        return False
    
    print(f"🔍 Found node: {transcribe_node['name']}")
    print(f"   Current URL: {transcribe_node['parameters'].get('url', 'Not set')}")
    
    # Fix the HTTP Request configuration
    transcribe_node["parameters"] = {
        "method": "POST",
        "url": "http://localhost:8000/transcribe/telegram",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {
                    "name": "Content-Type",
                    "value": "application/json"
                }
            ]
        },
        "sendBody": True,
        "contentType": "json",
        "jsonBody": "={{ {\"file_id\": $json.file_id, \"file_unique_id\": $json.original_message.voice.file_unique_id, \"duration\": $json.duration, \"message\": $json.original_message} }}",
        "options": {
            "timeout": 30000
        }
    }
    
    print("✅ Updated HTTP Request configuration:")
    print(f"   URL: {transcribe_node['parameters']['url']}")
    print(f"   Content-Type: application/json")
    print("   Body: JSON with file_id, file_unique_id, duration, message")
    
    # Save the workflow
    try:
        update_workflow = {
            "name": workflow["name"],
            "nodes": workflow["nodes"],
            "connections": workflow["connections"],
            "settings": workflow.get("settings", {}),
            "staticData": workflow.get("staticData"),
            "tags": workflow.get("tags", [])
        }
        
        response = requests.put(
            f"{n8n_url}/api/v1/workflows/{workflow_id}",
            headers=headers,
            json=update_workflow
        )
        
        if response.status_code == 200:
            print("✅ Workflow updated successfully!")
            print("\n🧪 Testing the fix:")
            print("1. The HTTP request should now use proper JSON format")
            print("2. The endpoint points to the correct Whisper API")
            print("3. No more 'source.on is not a function' errors")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating workflow: {e}")
        return False

if __name__ == "__main__":
    success = fix_transcribe_node()
    if success:
        print("\n🎉 Transcribe Voice Message node fixed!")
        print("📊 The 'source.on is not a function' error should be resolved")
        print("🔄 Test with a voice message to verify the fix")
    else:
        print("\n❌ Fix failed - manual update needed:")
        print("1. Open n8n editor")
        print("2. Find 'Transcribe Voice Message' node")
        print("3. Change content type from 'multipart-form-data' to 'JSON'")
        print("4. Update URL to: http://localhost:8000/transcribe/telegram")
        print("5. Set body to JSON with voice message data")
