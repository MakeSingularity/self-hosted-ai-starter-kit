#!/usr/bin/env python3
"""
n8n Workflow Backup Script
Exports all workflows from n8n instance to local files for version control
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
N8N_BASE_URL = "http://localhost:5678"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
BACKUP_DIR = Path("./workflows_backup")

def get_workflows():
    """Fetch all workflows from n8n API"""
    headers = {
        "X-N8N-API-KEY": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{N8N_BASE_URL}/api/v1/workflows", headers=headers)
        response.raise_for_status()
        return response.json()["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflows: {e}")
        return []

def backup_workflows():
    """Backup all workflows to local files"""
    workflows = get_workflows()
    
    if not workflows:
        print("No workflows found or API connection failed")
        return
    
    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Backup each workflow
    for workflow in workflows:
        filename = f"{workflow['name'].replace(' ', '_').replace('/', '_')}.json"
        filepath = BACKUP_DIR / filename
        
        # Add metadata
        workflow_data = {
            "id": workflow["id"],
            "name": workflow["name"],
            "active": workflow["active"],
            "createdAt": workflow["createdAt"],
            "updatedAt": workflow["updatedAt"],
            "backup_timestamp": datetime.now().isoformat(),
            "nodes": workflow["nodes"],
            "connections": workflow["connections"],
            "settings": workflow.get("settings", {}),
            "staticData": workflow.get("staticData", {}),
            "tags": workflow.get("tags", [])
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backed up: {workflow['name']} -> {filename}")
    
    print(f"\n🎉 Successfully backed up {len(workflows)} workflows to {BACKUP_DIR}")

def list_workflows():
    """List all workflows with basic info"""
    workflows = get_workflows()
    
    if not workflows:
        print("No workflows found")
        return
    
    print(f"\n📋 Found {len(workflows)} workflows:")
    print("-" * 60)
    
    for workflow in workflows:
        status = "🟢 Active" if workflow["active"] else "🔴 Inactive"
        nodes_count = len(workflow.get("nodes", []))
        print(f"{status} | {workflow['name']} | {nodes_count} nodes")
    
    print("-" * 60)

if __name__ == "__main__":
    print("🔄 n8n Workflow Backup Tool")
    print("=" * 40)
    
    # List current workflows
    list_workflows()
    
    # Backup workflows
    print("\n🔄 Starting backup...")
    backup_workflows()
    
    print("\n✨ Done! Your workflows are now available in VS Code for version control.")
    print(f"📁 Location: {BACKUP_DIR.absolute()}")
