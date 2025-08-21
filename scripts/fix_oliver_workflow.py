#!/usr/bin/env python3
"""
Oliver Workflow Fix Tool
Updates the existing Oliver workflow with simplified Code node
"""

import requests
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OliverWorkflowFixer:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
        self.headers = {"X-N8N-API-KEY": self.api_key}
        self.workflow_id = "rKO0PUthz0jXtKhD"
    
    def get_current_workflow(self):
        """Get the current Oliver workflow"""
        try:
            response = requests.get(
                f"{self.n8n_url}/api/v1/workflows/{self.workflow_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get workflow: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting workflow: {e}")
            return None
    
    def load_fixed_code(self):
        """Load the fixed Code node JavaScript"""
        try:
            code_file = Path("workflows_backup/oliver_fixed_code_node.js")
            if code_file.exists():
                with open(code_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.error(f"Code file not found: {code_file}")
                return None
        except Exception as e:
            logger.error(f"Error loading code file: {e}")
            return None
    
    def update_code_node(self, workflow, new_code):
        """Update the Code node in the workflow"""
        try:
            # Find the Code node
            code_node = None
            for i, node in enumerate(workflow["nodes"]):
                if node.get("type") == "n8n-nodes-base.code":
                    code_node = node
                    node_index = i
                    break
            
            if not code_node:
                logger.error("Code node not found in workflow")
                return False
            
            # Update the code
            old_code_length = len(code_node["parameters"].get("jsCode", ""))
            code_node["parameters"]["jsCode"] = new_code
            
            logger.info(f"Updated Code node: {old_code_length} -> {len(new_code)} characters")
            return True
            
        except Exception as e:
            logger.error(f"Error updating code node: {e}")
            return False
    
    def fix_whisper_api_url(self, workflow):
        """Fix the Whisper API URL in HTTP Request nodes"""
        try:
            fixes_made = 0
            for node in workflow["nodes"]:
                if node.get("type") == "n8n-nodes-base.httpRequest":
                    url = node.get("parameters", {}).get("url", "")
                    if "host.docker.internal:8000" in url:
                        # Update to localhost since we're running Whisper API locally
                        new_url = url.replace("host.docker.internal:8000", "localhost:8000")
                        node["parameters"]["url"] = new_url
                        logger.info(f"Fixed HTTP URL: {url} -> {new_url}")
                        fixes_made += 1
            
            return fixes_made > 0
            
        except Exception as e:
            logger.error(f"Error fixing Whisper API URLs: {e}")
            return False
    
    def save_workflow(self, workflow):
        """Save the updated workflow back to n8n"""
        try:
            response = requests.put(
                f"{self.n8n_url}/api/v1/workflows/{self.workflow_id}",
                headers=self.headers,
                json=workflow
            )
            
            if response.status_code == 200:
                logger.info("✅ Workflow updated successfully")
                return True
            else:
                logger.error(f"Failed to update workflow: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving workflow: {e}")
            return False
    
    def test_workflow(self):
        """Test the workflow by triggering a manual execution"""
        try:
            # Create a simple test execution
            test_data = {
                "workflowData": {
                    "id": self.workflow_id
                },
                "runData": {},
                "pinData": {
                    "Telegram Trigger": [
                        {
                            "json": {
                                "message": {
                                    "message_id": 999,
                                    "from": {
                                        "id": 12345,
                                        "first_name": "Test",
                                        "username": "testuser"
                                    },
                                    "chat": {
                                        "id": 12345,
                                        "type": "private"
                                    },
                                    "date": 1692547200,
                                    "text": "Hello Oliver, this is a test message!"
                                }
                            }
                        }
                    ]
                }
            }
            
            response = requests.post(
                f"{self.n8n_url}/api/v1/workflows/{self.workflow_id}/run",
                headers=self.headers,
                json=test_data
            )
            
            if response.status_code == 201:
                result = response.json()
                execution_id = result.get("data", {}).get("executionId")
                logger.info(f"✅ Test execution started: {execution_id}")
                return execution_id
            else:
                logger.error(f"Failed to start test execution: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error testing workflow: {e}")
            return None
    
    def run_fix(self):
        """Run the complete fix process"""
        print("🔧 Oliver Workflow Fix Tool")
        print("=" * 40)
        
        # Step 1: Get current workflow
        print("📥 Getting current workflow...")
        workflow = self.get_current_workflow()
        if not workflow:
            print("❌ Failed to get workflow")
            return False
        
        print(f"✅ Got workflow: {workflow['name']} ({len(workflow['nodes'])} nodes)")
        
        # Step 2: Load fixed code
        print("📝 Loading fixed Code node...")
        new_code = self.load_fixed_code()
        if not new_code:
            print("❌ Failed to load fixed code")
            return False
        
        print(f"✅ Loaded fixed code ({len(new_code)} characters)")
        
        # Step 3: Create backup
        print("💾 Creating backup...")
        backup_file = Path(f"workflows_backup/Oliver_backup_{workflow['updatedAt'].replace(':', '-')}.json")
        with open(backup_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        print(f"✅ Backup saved: {backup_file}")
        
        # Step 4: Update Code node
        print("🔄 Updating Code node...")
        if not self.update_code_node(workflow, new_code):
            print("❌ Failed to update Code node")
            return False
        
        # Step 5: Fix Whisper API URLs
        print("🔗 Fixing Whisper API URLs...")
        if self.fix_whisper_api_url(workflow):
            print("✅ Fixed Whisper API URLs")
        else:
            print("ℹ️ No Whisper API URLs to fix")
        
        # Step 6: Save workflow
        print("💾 Saving updated workflow...")
        if not self.save_workflow(workflow):
            print("❌ Failed to save workflow")
            return False
        
        # Step 7: Test workflow
        print("🧪 Testing workflow...")
        execution_id = self.test_workflow()
        if execution_id:
            print(f"✅ Test execution started: {execution_id}")
            print("   Check n8n editor for results")
        else:
            print("⚠️ Could not start test execution")
        
        print("\n🎉 Oliver workflow fix complete!")
        print("📊 Next steps:")
        print("   1. Check n8n editor for the updated workflow")
        print("   2. Test with a real Telegram message")
        print("   3. Monitor execution logs for any remaining issues")
        
        return True

def main():
    fixer = OliverWorkflowFixer()
    fixer.run_fix()

if __name__ == "__main__":
    main()
