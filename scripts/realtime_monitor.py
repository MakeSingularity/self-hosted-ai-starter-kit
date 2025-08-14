#!/usr/bin/env python3
"""
Real-time N8N Workflow Monitor for GitHub Copilot
Provides live monitoring and analysis of workflow executions, especially AI Agent nodes
"""

import json
import requests
import time
from datetime import datetime, timezone
import sys
from typing import Dict, List, Optional

class N8nWorkflowMonitor:
    """Real-time monitor for N8N workflows with focus on AI Agent debugging"""
    
    def __init__(self):
        self.base_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
        self.headers = {"X-N8N-API-KEY": self.api_key}
        self.last_execution_id = None
        
    def get_recent_executions(self, limit=5):
        """Get recent workflow executions"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions",
                headers=self.headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            return {"error": f"Failed to get executions: {str(e)}"}
    
    def get_execution_details(self, execution_id):
        """Get detailed execution information including node outputs"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions/{execution_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to get execution details: {str(e)}"}
    
    def analyze_ai_agent_execution(self, execution_details):
        """Analyze AI Agent node execution for prompt issues"""
        analysis = {
            "ai_agent_found": False,
            "ai_agent_status": "unknown",
            "prompt_info": {},
            "response_info": {},
            "error_details": None,
            "recommendations": []
        }
        
        try:
            run_data = execution_details.get("data", {}).get("resultData", {}).get("runData", {})
            
            # Look for AI Agent node
            for node_name, node_data in run_data.items():
                if "ai agent" in node_name.lower() or "agent" in node_name.lower():
                    analysis["ai_agent_found"] = True
                    analysis["ai_agent_status"] = "executed"
                    
                    if node_data and len(node_data) > 0:
                        latest_run = node_data[0]
                        
                        # Check for errors
                        if latest_run.get("error"):
                            analysis["error_details"] = latest_run["error"]
                            analysis["ai_agent_status"] = "error"
                            analysis["recommendations"].append("AI Agent node encountered an error")
                        
                        # Extract prompt and response info
                        if latest_run.get("data", {}).get("main"):
                            main_data = latest_run["data"]["main"][0]
                            if "input" in main_data:
                                analysis["prompt_info"] = {
                                    "input_received": True,
                                    "input_keys": list(main_data.get("json", {}).keys())
                                }
                            if "output" in main_data:
                                analysis["response_info"] = {
                                    "output_generated": True,
                                    "output_keys": list(main_data.get("json", {}).keys())
                                }
                    
                    break
            
            if not analysis["ai_agent_found"]:
                analysis["recommendations"].append("No AI Agent node found in execution")
                
        except Exception as e:
            analysis["error_details"] = f"Analysis failed: {str(e)}"
        
        return analysis
    
    def monitor_live_executions(self):
        """Monitor for new executions and analyze them"""
        print("🔍 Starting live workflow monitoring...")
        print("Watching for new executions, AI Agent issues, and prompt problems...")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                executions = self.get_recent_executions(3)
                
                if executions and isinstance(executions, list) and len(executions) > 0:
                    latest = executions[0]
                    
                    # Check if this is a new execution
                    if latest["id"] != self.last_execution_id:
                        self.last_execution_id = latest["id"]
                        
                        # Get detailed execution info
                        details = self.get_execution_details(latest["id"])
                        
                        # Analyze the execution
                        ai_analysis = self.analyze_ai_agent_execution(details)
                        
                        # Report findings
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        status = latest.get("status", "running")
                        
                        print(f"🆕 [{timestamp}] New Execution #{latest['id']}")
                        print(f"   Status: {status} | Mode: {latest.get('mode', 'unknown')}")
                        
                        if ai_analysis["ai_agent_found"]:
                            print(f"   🤖 AI Agent: {ai_analysis['ai_agent_status']}")
                            
                            if ai_analysis["error_details"]:
                                print(f"   ❌ Error: {ai_analysis['error_details']}")
                            
                            if ai_analysis["prompt_info"].get("input_received"):
                                print(f"   📝 Prompt received with keys: {ai_analysis['prompt_info']['input_keys']}")
                            
                            if ai_analysis["response_info"].get("output_generated"):
                                print(f"   💬 Response generated with keys: {ai_analysis['response_info']['output_keys']}")
                        
                        if ai_analysis["recommendations"]:
                            for rec in ai_analysis["recommendations"]:
                                print(f"   💡 {rec}")
                        
                        print()
                
                time.sleep(2)  # Check every 2 seconds
                
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {str(e)}")
                time.sleep(5)
    
    def get_workflow_analysis(self):
        """Get current workflow analysis including AI Agent configuration"""
        try:
            # Get workflows
            workflows_response = requests.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers
            )
            workflows_response.raise_for_status()
            workflows = workflows_response.json()["data"]
            
            analysis = {
                "total_workflows": len(workflows),
                "active_workflows": 0,
                "ai_agent_workflows": [],
                "recent_execution_summary": {}
            }
            
            for workflow in workflows:
                if workflow.get("active"):
                    analysis["active_workflows"] += 1
                
                # Check for AI Agent nodes
                nodes = workflow.get("nodes", [])
                ai_agent_nodes = [n for n in nodes if "agent" in n.get("type", "").lower()]
                
                if ai_agent_nodes:
                    analysis["ai_agent_workflows"].append({
                        "name": workflow["name"],
                        "id": workflow["id"],
                        "ai_agents": len(ai_agent_nodes),
                        "active": workflow.get("active", False)
                    })
            
            # Get recent execution summary
            recent_executions = self.get_recent_executions(10)
            if isinstance(recent_executions, list):
                statuses = {}
                for exec in recent_executions:
                    status = exec.get("status", "running")
                    statuses[status] = statuses.get(status, 0) + 1
                analysis["recent_execution_summary"] = statuses
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

def main():
    """Command line interface for workflow monitoring"""
    if len(sys.argv) < 2:
        print("Usage: python realtime_monitor.py <command>")
        print("Commands:")
        print("  live     - Start live execution monitoring")
        print("  status   - Get current workflow analysis")
        print("  analyze  - Analyze specific execution (provide execution ID)")
        return
    
    monitor = N8nWorkflowMonitor()
    command = sys.argv[1].lower()
    
    if command == "live":
        monitor.monitor_live_executions()
    
    elif command == "status":
        analysis = monitor.get_workflow_analysis()
        print(json.dumps(analysis, indent=2))
    
    elif command == "analyze" and len(sys.argv) > 2:
        execution_id = sys.argv[2]
        details = monitor.get_execution_details(execution_id)
        ai_analysis = monitor.analyze_ai_agent_execution(details)
        print(json.dumps(ai_analysis, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: live, status, analyze")

if __name__ == "__main__":
    main()
