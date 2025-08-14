#!/usr/bin/env python3
"""
GitHub Copilot Integration Tools for Ngrok Automation
Provides direct tool access to ngrok webhook management functionality
"""

import sys
import json
import subprocess
import os
from pathlib import Path

class CopilotNgrokTools:
    """GitHub Copilot tool interface for ngrok automation"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.ngrok_script = self.script_dir / "ngrok_webhook_manager.py"
        self.n8n_script = self.script_dir / "copilot_n8n_tool.py"
    
    def setup_ngrok_webhooks(self, verbose=False):
        """
        Setup ngrok tunnel and configure webhooks automatically
        
        Args:
            verbose (bool): Enable verbose output
            
        Returns:
            dict: Status and result information
        """
        try:
            cmd = [sys.executable, str(self.ngrok_script), "setup"]
            if verbose:
                cmd.append("--verbose")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.script_dir.parent
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Failed to execute ngrok setup: {str(e)}",
                "command": ""
            }
    
    def check_ngrok_status(self):
        """
        Check current ngrok tunnel and webhook status
        
        Returns:
            dict: Current status information
        """
        try:
            result = subprocess.run(
                [sys.executable, str(self.ngrok_script), "status"],
                capture_output=True,
                text=True,
                cwd=self.script_dir.parent
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "tunnel_active": "✅ Tunnel is active" in result.stdout,
                "webhooks_configured": "✅ All webhooks configured" in result.stdout
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Failed to check ngrok status: {str(e)}",
                "tunnel_active": False,
                "webhooks_configured": False
            }
    
    def cleanup_ngrok_conflicts(self):
        """
        Clean up conflicting ngrok processes (especially Docker Desktop conflicts)
        
        Returns:
            dict: Cleanup result information
        """
        try:
            result = subprocess.run(
                [sys.executable, str(self.ngrok_script), "cleanup"],
                capture_output=True,
                text=True,
                cwd=self.script_dir.parent
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "processes_cleaned": "processes stopped" in result.stdout.lower()
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Failed to cleanup ngrok conflicts: {str(e)}",
                "processes_cleaned": False
            }
    
    def get_n8n_workflow_status(self):
        """
        Get comprehensive n8n workflow status including webhook information
        
        Returns:
            dict: Workflow status and webhook information
        """
        try:
            result = subprocess.run(
                [sys.executable, str(self.n8n_script), "status"],
                capture_output=True,
                text=True,
                cwd=self.script_dir.parent
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Failed to get n8n status: {str(e)}"
            }
    
    def diagnose_webhook_issues(self):
        """
        Comprehensive diagnosis of webhook and tunnel issues
        
        Returns:
            dict: Diagnostic information and recommendations
        """
        diagnosis = {
            "ngrok_status": self.check_ngrok_status(),
            "n8n_status": self.get_n8n_workflow_status(),
            "recommendations": []
        }
        
        # Analyze results and provide recommendations
        if not diagnosis["ngrok_status"]["tunnel_active"]:
            diagnosis["recommendations"].append("🔧 Run ngrok setup to create tunnel")
        
        if not diagnosis["ngrok_status"]["webhooks_configured"]:
            diagnosis["recommendations"].append("🔗 Update webhook URLs in workflows")
        
        if not diagnosis["ngrok_status"]["success"]:
            diagnosis["recommendations"].append("🧹 Clean up ngrok conflicts first")
        
        if not diagnosis["n8n_status"]["success"]:
            diagnosis["recommendations"].append("🚀 Ensure n8n services are running")
        
        return diagnosis

def main():
    """Command line interface for Copilot tools"""
    if len(sys.argv) < 2:
        print("Usage: python copilot_ngrok_tools.py <command>")
        print("Commands: setup, status, cleanup, diagnose, n8n-status")
        return
    
    tools = CopilotNgrokTools()
    command = sys.argv[1].lower()
    
    if command == "setup":
        verbose = "--verbose" in sys.argv
        result = tools.setup_ngrok_webhooks(verbose)
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        result = tools.check_ngrok_status()
        print(json.dumps(result, indent=2))
    
    elif command == "cleanup":
        result = tools.cleanup_ngrok_conflicts()
        print(json.dumps(result, indent=2))
    
    elif command == "diagnose":
        result = tools.diagnose_webhook_issues()
        print(json.dumps(result, indent=2))
    
    elif command == "n8n-status":
        result = tools.get_n8n_workflow_status()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: setup, status, cleanup, diagnose, n8n-status")

if __name__ == "__main__":
    main()
