#!/usr/bin/env python3
"""
Oliver Workflow Diagnostic and Fix Tool
Analyzes the current Oliver workflow and provides specific fixes
"""

import requests
import json
import logging
from typing import Dict, List
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OliverDiagnostic:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
        self.headers = {"X-N8N-API-KEY": self.api_key}
        self.workflow_id = "rKO0PUthz0jXtKhD"  # Oliver workflow ID
    
    def check_n8n_connection(self) -> bool:
        """Test connection to n8n API"""
        try:
            response = requests.get(f"{self.n8n_url}/api/v1/workflows", headers=self.headers, timeout=5)
            if response.status_code == 200:
                logger.info("✅ n8n API connection successful")
                return True
            else:
                logger.error(f"❌ n8n API error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Could not connect to n8n: {e}")
            return False
    
    def get_workflow_details(self) -> Dict:
        """Get current Oliver workflow details"""
        try:
            response = requests.get(
                f"{self.n8n_url}/api/v1/workflows/{self.workflow_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                workflow = response.json()
                logger.info(f"✅ Retrieved workflow: {workflow['name']}")
                return workflow
            else:
                logger.error(f"❌ Could not get workflow: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error getting workflow: {e}")
            return {}
    
    def get_recent_executions(self, limit: int = 10) -> List[Dict]:
        """Get recent execution details"""
        try:
            response = requests.get(
                f"{self.n8n_url}/api/v1/executions",
                headers=self.headers,
                params={"workflowId": self.workflow_id, "limit": limit}
            )
            if response.status_code == 200:
                executions = response.json()["data"]
                logger.info(f"✅ Retrieved {len(executions)} recent executions")
                return executions
            else:
                logger.error(f"❌ Could not get executions: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting executions: {e}")
            return []
    
    def analyze_execution_errors(self, execution_id: str) -> Dict:
        """Get detailed error information for a specific execution"""
        try:
            response = requests.get(
                f"{self.n8n_url}/api/v1/executions/{execution_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                execution = response.json()
                status = execution.get("status", "unknown")
                
                # Look for error details in the execution data
                error_info = {
                    "execution_id": execution_id,
                    "status": status,
                    "started_at": execution.get("startedAt"),
                    "stopped_at": execution.get("stoppedAt"),
                    "errors": []
                }
                
                if status == "error" and "data" in execution:
                    # Extract error details from execution data
                    exec_data = execution["data"]
                    if "resultData" in exec_data:
                        result_data = exec_data["resultData"]
                        if "error" in result_data:
                            error_info["errors"].append({
                                "type": "execution_error",
                                "message": result_data["error"].get("message", "Unknown error"),
                                "stack": result_data["error"].get("stack", "")
                            })
                
                return error_info
            else:
                logger.error(f"❌ Could not get execution details: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error analyzing execution: {e}")
            return {}
    
    def check_dependencies(self) -> Dict:
        """Check if required services are running"""
        dependencies = {}
        
        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            dependencies["ollama"] = {
                "status": "running" if response.status_code == 200 else "error",
                "models": len(response.json().get("models", [])) if response.status_code == 200 else 0
            }
        except:
            dependencies["ollama"] = {"status": "not_running", "models": 0}
        
        # Check PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="n8n",
                user="root",
                password="D34D8YT3"
            )
            conn.close()
            dependencies["postgres"] = {"status": "running"}
        except:
            dependencies["postgres"] = {"status": "error"}
        
        # Check Whisper API
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            dependencies["whisper_api"] = {
                "status": "running" if response.status_code == 200 else "error"
            }
        except:
            dependencies["whisper_api"] = {"status": "not_running"}
        
        return dependencies
    
    def identify_code_node_issues(self, workflow: Dict) -> List[str]:
        """Analyze the Code node for potential issues"""
        issues = []
        
        # Find the Code node
        code_node = None
        for node in workflow.get("nodes", []):
            if node.get("type") == "n8n-nodes-base.code":
                code_node = node
                break
        
        if not code_node:
            issues.append("No Code node found in workflow")
            return issues
        
        code = code_node.get("parameters", {}).get("jsCode", "")
        
        # Check for common issues
        if len(code) > 5000:
            issues.append("Code node is very large (>5000 chars) - consider splitting")
        
        if "console.log" in code and code.count("console.log") > 10:
            issues.append("Excessive console.log statements may impact performance")
        
        if "items[0].json" in code and "allItems" in code:
            issues.append("Mixed data access patterns may cause confusion")
        
        if "original_message" in code and code.count("original_message") > 5:
            issues.append("Complex original_message handling - consider simplification")
        
        if "try" not in code and "catch" not in code:
            issues.append("No error handling in Code node")
        
        return issues
    
    def generate_recommendations(self, workflow: Dict, executions: List[Dict], dependencies: Dict) -> List[str]:
        """Generate specific recommendations for fixing Oliver"""
        recommendations = []
        
        # Check execution success rate
        if executions:
            failed_count = sum(1 for ex in executions if ex.get("status") != "success")
            success_rate = (len(executions) - failed_count) / len(executions) * 100
            
            if success_rate < 50:
                recommendations.append("🚨 CRITICAL: Low success rate - immediate attention needed")
            elif success_rate < 80:
                recommendations.append("⚠️ Moderate issues - workflow needs optimization")
        
        # Check dependencies
        if dependencies.get("ollama", {}).get("status") != "running":
            recommendations.append("🔧 Start Ollama service for AI functionality")
        
        if dependencies.get("whisper_api", {}).get("status") != "running":
            recommendations.append("🔧 Start Whisper API service for voice transcription")
        
        if dependencies.get("postgres", {}).get("status") != "running":
            recommendations.append("🔧 Check PostgreSQL connection for chat memory")
        
        # Check workflow structure
        code_issues = self.identify_code_node_issues(workflow)
        if code_issues:
            recommendations.append("📝 Simplify Code node logic:")
            recommendations.extend(f"  • {issue}" for issue in code_issues)
        
        # Check for missing error handling
        nodes = workflow.get("nodes", [])
        if not any(node.get("type") == "n8n-nodes-base.if" for node in nodes):
            recommendations.append("🛡️ Add error handling nodes (If, Switch)")
        
        return recommendations
    
    def run_full_diagnostic(self):
        """Run complete diagnostic and provide recommendations"""
        print("🔍 Oliver Workflow Diagnostic Report")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test connection
        if not self.check_n8n_connection():
            print("❌ Cannot connect to n8n - check if container is running")
            return
        
        # Get workflow details
        workflow = self.get_workflow_details()
        if not workflow:
            print("❌ Cannot retrieve workflow details")
            return
        
        print(f"📋 Workflow: {workflow['name']}")
        print(f"   Active: {workflow.get('active', False)}")
        print(f"   Nodes: {len(workflow.get('nodes', []))}")
        print(f"   Updated: {workflow.get('updatedAt', 'Unknown')}")
        print()
        
        # Check dependencies
        print("🔧 Service Dependencies:")
        dependencies = self.check_dependencies()
        for service, info in dependencies.items():
            status_icon = "✅" if info["status"] == "running" else "❌"
            print(f"   {status_icon} {service}: {info['status']}")
            if service == "ollama" and "models" in info:
                print(f"      Models available: {info['models']}")
        print()
        
        # Analyze recent executions
        executions = self.get_recent_executions(10)
        if executions:
            print("📊 Recent Execution Analysis:")
            success_count = sum(1 for ex in executions if ex.get("status") == "success")
            print(f"   Success rate: {success_count}/{len(executions)} ({success_count/len(executions)*100:.1f}%)")
            
            # Show recent failures
            failed_executions = [ex for ex in executions if ex.get("status") != "success"][:3]
            if failed_executions:
                print("   Recent failures:")
                for ex in failed_executions:
                    print(f"     • ID {ex['id']}: {ex.get('status', 'unknown')} at {ex.get('startedAt', 'unknown')}")
        print()
        
        # Generate recommendations
        recommendations = self.generate_recommendations(workflow, executions, dependencies)
        if recommendations:
            print("💡 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        else:
            print("✅ No immediate issues detected")
        
        print()
        print("🛠️ Quick Fixes:")
        print("   1. Restart services: docker restart n8n ollama")
        print("   2. Check logs: docker logs n8n --tail 50")
        print("   3. Test workflow: Manual execution in n8n editor")
        print("   4. Simplify Code node if issues persist")

def main():
    diagnostic = OliverDiagnostic()
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()
