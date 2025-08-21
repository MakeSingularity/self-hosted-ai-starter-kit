#!/usr/bin/env python3
"""
Oliver Code Node Direct Fix
Updates only the Code node parameters using a more targeted approach
"""

import requests
import json

def patch_oliver_code():
    """Patch just the Code node with minimal data"""
    
    n8n_url = "http://localhost:5678"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
    headers = {"X-N8N-API-KEY": api_key}
    workflow_id = "rKO0PUthz0jXtKhD"
    
    print("🔧 Direct Oliver Code Node Patch")
    print("=" * 35)
    
    # Load the simplified code
    try:
        with open("workflows_backup/oliver_fixed_code_node.js", 'r', encoding='utf-8') as f:
            new_code = f.read()
        print(f"✅ Loaded fixed code ({len(new_code)} characters)")
    except Exception as e:
        print(f"❌ Could not load code file: {e}")
        return False
    
    # Get current workflow
    try:
        response = requests.get(f"{n8n_url}/api/v1/workflows/{workflow_id}", headers=headers)
        workflow = response.json()
        print(f"✅ Got workflow: {workflow['name']}")
    except Exception as e:
        print(f"❌ Could not get workflow: {e}")
        return False
    
    # Find Code node
    code_node = None
    for node in workflow["nodes"]:
        if node.get("type") == "n8n-nodes-base.code":
            code_node = node
            break
    
    if not code_node:
        print("❌ Code node not found")
        return False
    
    # Update just the jsCode parameter
    old_code = code_node["parameters"].get("jsCode", "")
    code_node["parameters"]["jsCode"] = new_code
    print(f"✅ Updated Code node: {len(old_code)} -> {len(new_code)} chars")
    
    # Try sending minimal update - just the nodes array
    minimal_update = {
        "nodes": workflow["nodes"],
        "connections": workflow["connections"]
    }
    
    try:
        response = requests.put(
            f"{n8n_url}/api/v1/workflows/{workflow_id}",
            headers=headers,
            json=minimal_update
        )
        
        if response.status_code == 200:
            print("✅ Code node updated successfully!")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try even more minimal approach - check what's required
            print("\n🔍 Trying to identify required fields...")
            
            # Get the exact structure needed by examining what we got back
            current_structure = {
                "name": workflow["name"],
                "nodes": workflow["nodes"],
                "connections": workflow["connections"]
            }
            
            response2 = requests.put(
                f"{n8n_url}/api/v1/workflows/{workflow_id}",
                headers=headers,
                json=current_structure
            )
            
            if response2.status_code == 200:
                print("✅ Minimal update worked!")
                return True
            else:
                print(f"❌ Minimal update also failed: {response2.status_code}")
                print(f"Response: {response2.text}")
                return False
            
    except Exception as e:
        print(f"❌ Error updating workflow: {e}")
        return False

if __name__ == "__main__":
    success = patch_oliver_code()
    if success:
        print("\n🎉 Code node fix complete!")
        print("📊 Test the workflow in n8n editor")
        print("🔄 Try sending a test message to see if issues are resolved")
    else:
        print("\n❌ Direct API update failed")
        print("📝 Manual fix: Copy the code from oliver_fixed_code_node.js")
        print("   and paste it into the Code node in n8n editor")
