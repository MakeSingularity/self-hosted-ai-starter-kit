#!/usr/bin/env python3
"""
AI Agent Debugging Tool for GitHub Copilot
Provides specific analysis and fixes for AI Agent prompt issues in n8n workflows
"""

import json
import requests
import sys
from datetime import datetime

class AIAgentDebugger:
    """Specialized tool for debugging AI Agent nodes in n8n workflows"""
    
    def __init__(self):
        self.base_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
        self.headers = {"X-N8N-API-KEY": self.api_key}
    
    def get_ai_agent_config(self, workflow_name="Oliver"):
        """Get current AI Agent configuration from workflow"""
        try:
            # Get workflows
            response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers)
            response.raise_for_status()
            workflows = response.json()["data"]
            
            # Find the specified workflow
            target_workflow = None
            for workflow in workflows:
                if workflow["name"].lower() == workflow_name.lower():
                    target_workflow = workflow
                    break
            
            if not target_workflow:
                return {"error": f"Workflow '{workflow_name}' not found"}
            
            # Find AI Agent node
            ai_agent_nodes = []
            for node in target_workflow.get("nodes", []):
                if "agent" in node.get("type", "").lower():
                    ai_agent_nodes.append({
                        "name": node["name"],
                        "type": node["type"],
                        "parameters": node.get("parameters", {}),
                        "position": node.get("position", [0, 0])
                    })
            
            return {
                "workflow_name": target_workflow["name"],
                "workflow_id": target_workflow["id"],
                "ai_agent_nodes": ai_agent_nodes,
                "total_nodes": len(target_workflow.get("nodes", [])),
                "workflow_active": target_workflow.get("active", False)
            }
            
        except Exception as e:
            return {"error": f"Failed to get AI Agent config: {str(e)}"}
    
    def analyze_recent_failures(self, workflow_name="Oliver", limit=5):
        """Analyze recent execution failures focusing on AI Agent issues"""
        try:
            # Get recent executions
            response = requests.get(
                f"{self.base_url}/api/v1/executions",
                headers=self.headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            executions = response.json()["data"]
            
            analysis = {
                "total_executions": len(executions),
                "failed_executions": [],
                "ai_agent_issues": [],
                "common_problems": [],
                "recommendations": []
            }
            
            for execution in executions:
                if execution.get("status") == "error" or not execution.get("finished"):
                    # Get detailed execution data
                    detail_response = requests.get(
                        f"{self.base_url}/api/v1/executions/{execution['id']}",
                        headers=self.headers
                    )
                    
                    if detail_response.status_code == 200:
                        details = detail_response.json()
                        
                        failure_info = {
                            "execution_id": execution["id"],
                            "started_at": execution.get("startedAt"),
                            "status": execution.get("status"),
                            "mode": execution.get("mode"),
                            "error_details": None,
                            "ai_agent_error": False
                        }
                        
                        # Check for AI Agent specific errors
                        run_data = details.get("data", {}).get("resultData", {}).get("runData", {})
                        for node_name, node_data in run_data.items():
                            if "agent" in node_name.lower() and node_data:
                                for run in node_data:
                                    if run.get("error"):
                                        failure_info["ai_agent_error"] = True
                                        failure_info["error_details"] = run["error"]
                                        analysis["ai_agent_issues"].append({
                                            "node_name": node_name,
                                            "error": run["error"],
                                            "execution_id": execution["id"]
                                        })
                        
                        analysis["failed_executions"].append(failure_info)
            
            # Generate recommendations based on patterns
            if analysis["ai_agent_issues"]:
                analysis["recommendations"].append("AI Agent errors detected - check prompt configuration")
            
            error_types = [issue.get("error", {}).get("message", "") for issue in analysis["ai_agent_issues"]]
            if any("timeout" in error.lower() for error in error_types):
                analysis["recommendations"].append("Timeout issues detected - consider increasing timeout or optimizing prompt")
            
            if any("token" in error.lower() for error in error_types):
                analysis["recommendations"].append("Token limit issues - reduce prompt length or split into smaller chunks")
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze failures: {str(e)}"}
    
    def get_prompt_analysis(self, workflow_name="Oliver"):
        """Analyze current AI Agent prompt configuration"""
        config = self.get_ai_agent_config(workflow_name)
        
        if "error" in config:
            return config
        
        prompt_analysis = {
            "workflow_name": workflow_name,
            "prompt_issues": [],
            "prompt_suggestions": [],
            "current_config": {}
        }
        
        for agent in config.get("ai_agent_nodes", []):
            parameters = agent.get("parameters", {})
            
            # Extract prompt information
            prompt_template = parameters.get("promptTemplate", "")
            system_message = parameters.get("systemMessage", "")
            
            agent_analysis = {
                "node_name": agent["name"],
                "has_prompt_template": bool(prompt_template),
                "has_system_message": bool(system_message),
                "prompt_length": len(prompt_template),
                "system_message_length": len(system_message)
            }
            
            # Check for common prompt issues
            if not prompt_template and not system_message:
                prompt_analysis["prompt_issues"].append(f"{agent['name']}: No prompt or system message configured")
            
            if len(prompt_template) > 4000:
                prompt_analysis["prompt_issues"].append(f"{agent['name']}: Prompt template very long ({len(prompt_template)} chars)")
                prompt_analysis["prompt_suggestions"].append(f"{agent['name']}: Consider breaking down long prompt into smaller parts")
            
            if "{{" not in prompt_template and prompt_template:
                prompt_analysis["prompt_suggestions"].append(f"{agent['name']}: Consider using variables in prompt template")
            
            prompt_analysis["current_config"][agent["name"]] = agent_analysis
        
        return prompt_analysis
    
    def suggest_prompt_fixes(self, issue_description):
        """Generate specific prompt fix suggestions based on issue description"""
        suggestions = {
            "issue_description": issue_description,
            "suggested_fixes": [],
            "example_prompts": []
        }
        
        issue_lower = issue_description.lower()
        
        # Common prompt issues and fixes
        if "not responding" in issue_lower or "no output" in issue_lower:
            suggestions["suggested_fixes"].extend([
                "Add explicit instruction to respond to user",
                "Check if prompt template includes {{$json.message}} or similar input variable",
                "Ensure system message defines the bot's role clearly"
            ])
            suggestions["example_prompts"].append(
                "You are Oliver, a helpful AI assistant. Always respond to the user's message: {{$json.message}}"
            )
        
        if "too long" in issue_lower or "verbose" in issue_lower:
            suggestions["suggested_fixes"].extend([
                "Add instruction to keep responses concise",
                "Specify maximum response length",
                "Use bullet points or numbered lists"
            ])
            suggestions["example_prompts"].append(
                "Respond in 2-3 sentences maximum. Be concise and direct."
            )
        
        if "context" in issue_lower or "memory" in issue_lower:
            suggestions["suggested_fixes"].extend([
                "Check if memory node is properly connected",
                "Ensure conversation history is being passed to AI Agent",
                "Add context instructions in system message"
            ])
            suggestions["example_prompts"].append(
                "Use the conversation history to maintain context. Previous messages: {{$json.chat_history}}"
            )
        
        if "error" in issue_lower or "failing" in issue_lower:
            suggestions["suggested_fixes"].extend([
                "Check Ollama model is running and accessible",
                "Verify model name matches installed model",
                "Test with simpler prompt first",
                "Check for special characters in prompt"
            ])
        
        return suggestions

def main():
    """Command line interface for AI Agent debugging"""
    if len(sys.argv) < 2:
        print("Usage: python ai_agent_debugger.py <command> [options]")
        print("Commands:")
        print("  config [workflow_name]     - Get AI Agent configuration")
        print("  failures [workflow_name]   - Analyze recent failures")
        print("  prompt [workflow_name]     - Analyze prompt configuration")
        print("  suggest 'issue description' - Get prompt fix suggestions")
        return
    
    debugger = AIAgentDebugger()
    command = sys.argv[1].lower()
    
    workflow_name = sys.argv[2] if len(sys.argv) > 2 else "Oliver"
    
    if command == "config":
        result = debugger.get_ai_agent_config(workflow_name)
        print(json.dumps(result, indent=2))
    
    elif command == "failures":
        result = debugger.analyze_recent_failures(workflow_name)
        print(json.dumps(result, indent=2))
    
    elif command == "prompt":
        result = debugger.get_prompt_analysis(workflow_name)
        print(json.dumps(result, indent=2))
    
    elif command == "suggest" and len(sys.argv) > 2:
        issue_description = " ".join(sys.argv[2:])
        result = debugger.suggest_prompt_fixes(issue_description)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: config, failures, prompt, suggest")

if __name__ == "__main__":
    main()
