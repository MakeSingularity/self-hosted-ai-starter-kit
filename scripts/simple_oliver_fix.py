#!/usr/bin/env python3
"""
Simple Oliver Code Node Fix
Just updates the code without extra properties that might cause issues
"""

import requests
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_oliver_code_node():
    """Update just the Code node with simplified approach"""
    
    n8n_url = "http://localhost:5678"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
    headers = {"X-N8N-API-KEY": api_key}
    workflow_id = "rKO0PUthz0jXtKhD"
    
    print("🔧 Simple Oliver Code Node Fix")
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
    
    # Find and update Code node
    code_node_found = False
    for node in workflow["nodes"]:
        if node.get("type") == "n8n-nodes-base.code":
            old_code = node["parameters"].get("jsCode", "")
            node["parameters"]["jsCode"] = new_code
            print(f"✅ Updated Code node: {len(old_code)} -> {len(new_code)} chars")
            code_node_found = True
            break
    
    if not code_node_found:
        print("❌ Code node not found")
        return False
    
    # Clean up workflow object for update
    # Remove properties that might cause issues
    update_workflow = {
        "name": workflow["name"],
        "active": workflow["active"],
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": workflow.get("settings", {}),
        "staticData": workflow.get("staticData"),
        "tags": workflow.get("tags", [])
    }
    
    # Update workflow
    try:
        response = requests.put(
            f"{n8n_url}/api/v1/workflows/{workflow_id}",
            headers=headers,
            json=update_workflow
        )
        
        if response.status_code == 200:
            print("✅ Workflow updated successfully!")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating workflow: {e}")
        return False

if __name__ == "__main__":
    success = fix_oliver_code_node()
    if success:
        print("\n🎉 Code node fix complete!")
        print("📊 Test the workflow in n8n editor")
    else:
        print("\n❌ Fix failed - check logs above")
