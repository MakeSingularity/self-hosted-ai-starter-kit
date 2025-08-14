#!/usr/bin/env python3
"""
n8n VS Code Integration Tool
Provides real-time visibility into n8n workflows for development
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

class N8nVSCodeIntegration:
    def __init__(self):
        self.base_url = "http://localhost:5678"
        self.api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw"
        self.headers = {
            "X-N8N-API-KEY": self.api_token,
            "Content-Type": "application/json"
        }
        self.workspace_dir = Path("./workflows_live")
        self.workspace_dir.mkdir(exist_ok=True)
    
    def get_workflow_status(self):
        """Get current status of all workflows"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers)
            response.raise_for_status()
            workflows = response.json()["data"]
            
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "total_workflows": len(workflows),
                "active_workflows": sum(1 for w in workflows if w["active"]),
                "workflows": []
            }
            
            for workflow in workflows:
                status_data["workflows"].append({
                    "id": workflow["id"],
                    "name": workflow["name"],
                    "active": workflow["active"],
                    "nodes_count": len(workflow.get("nodes", [])),
                    "last_updated": workflow["updatedAt"]
                })
            
            return status_data
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def get_executions(self, limit=10):
        """Get recent workflow executions"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions",
                headers=self.headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def export_current_state(self):
        """Export current n8n state to workspace"""
        # Get workflow status
        status = self.get_workflow_status()
        
        # Save to workspace
        with open(self.workspace_dir / "workflow_status.json", 'w') as f:
            json.dump(status, f, indent=2)
        
        # Get recent executions
        executions = self.get_executions()
        with open(self.workspace_dir / "recent_executions.json", 'w') as f:
            json.dump(executions, f, indent=2)
        
        # Create summary report
        self.create_summary_report(status, executions)
        
        return status
    
    def create_summary_report(self, status, executions):
        """Create a human-readable summary report"""
        report = []
        report.append("# n8n Workspace Status Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if "error" in status:
            report.append(f"❌ **Error**: {status['error']}")
            report.append("")
        else:
            report.append("## 📊 Workflow Overview")
            report.append(f"- **Total Workflows**: {status['total_workflows']}")
            report.append(f"- **Active Workflows**: {status['active_workflows']}")
            report.append(f"- **Inactive Workflows**: {status['total_workflows'] - status['active_workflows']}")
            report.append("")
            
            report.append("## 🔄 Workflow Details")
            for workflow in status["workflows"]:
                status_icon = "🟢" if workflow["active"] else "🔴"
                report.append(f"- {status_icon} **{workflow['name']}** ({workflow['nodes_count']} nodes)")
            report.append("")
        
        if "error" not in executions:
            report.append("## 📈 Recent Activity")
            recent_executions = executions.get("data", [])[:5]
            if recent_executions:
                for execution in recent_executions:
                    status_icon = "✅" if execution["finished"] else "🔄"
                    if execution.get("stoppedAt"):
                        status_icon = "❌"
                    report.append(f"- {status_icon} {execution.get('workflowData', {}).get('name', 'Unknown')} - {execution['startedAt']}")
            else:
                report.append("- No recent executions found")
            report.append("")
        
        report.append("## 🔗 Quick Links")
        report.append(f"- [n8n Web Interface]({self.base_url})")
        report.append("- [Workflow Status JSON](./workflow_status.json)")
        report.append("- [Recent Executions JSON](./recent_executions.json)")
        
        # Save report
        with open(self.workspace_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

def main():
    """Main function"""
    print("🔄 n8n VS Code Integration")
    print("=" * 40)
    
    integration = N8nVSCodeIntegration()
    
    # Export current state
    status = integration.export_current_state()
    
    if "error" in status:
        print(f"❌ Error: {status['error']}")
    else:
        print(f"✅ Exported status for {status['total_workflows']} workflows")
        print(f"📁 Files created in: {integration.workspace_dir}")
        print("\n📋 Quick Summary:")
        print(f"   - Total: {status['total_workflows']} workflows")
        print(f"   - Active: {status['active_workflows']} workflows")
        
        print("\n🔄 Workflows:")
        for workflow in status["workflows"]:
            status_icon = "🟢" if workflow["active"] else "🔴"
            print(f"   {status_icon} {workflow['name']} ({workflow['nodes_count']} nodes)")

if __name__ == "__main__":
    main()
