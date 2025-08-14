#!/usr/bin/env python3
"""
GitHub Copilot n8n Integration Tool
A specialized tool for GitHub Copilot to monitor and manage n8n workflows

IMPORTANT: This project uses Docker Compose with the 'gpu-nvidia' profile
All Docker operations should use: docker compose --profile gpu-nvidia [command]
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class CopilotN8nTool:
    """
    GitHub Copilot tool for n8n workflow management and monitoring
    
    This tool provides GitHub Copilot with the ability to:
    - Monitor n8n workflow status
    - Backup workflows for version control
    - Analyze workflow structure and performance
    - Provide development insights
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the Copilot n8n tool"""
        self.config = self._load_config(config_file)
        self.base_url = self.config.get("base_url", "http://localhost:5678")
        self.api_token = self.config.get("api_token")
        self.headers = {
            "X-N8N-API-KEY": self.api_token,
            "Content-Type": "application/json"
        } if self.api_token else {}
        
        self.workspace_dir = Path(self.config.get("workspace_dir", "./workflows_live"))
        self.backup_dir = Path(self.config.get("backup_dir", "./workflows_backup"))
        
        # Ensure directories exist
        self.workspace_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        config = {}
        
        # Try to load from VS Code settings
        settings_file = Path(".vscode/settings.json")
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    config.update({
                        "base_url": settings.get("n8n.instanceBaseUrl", "http://localhost:5678"),
                        "api_token": settings.get("n8n.apiKey"),
                        "workspace_dir": settings.get("n8n.liveWorkspaceDirectory", "./workflows_live"),
                        "backup_dir": settings.get("n8n.workflowDirectory", "./workflows_backup")
                    })
            except Exception as e:
                print(f"Warning: Could not load VS Code settings: {e}")
        
        # Override with environment variables if available
        config.update({
            "base_url": os.getenv("N8N_BASE_URL", config.get("base_url", "http://localhost:5678")),
            "api_token": os.getenv("N8N_API_TOKEN", config.get("api_token"))
        })
        
        return config
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get current status of all workflows
        Returns detailed information about workflows for Copilot analysis
        """
        try:
            if not self.api_token:
                return {"error": "No API token configured", "status": "configuration_required"}
            
            response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers, timeout=10)
            response.raise_for_status()
            workflows = response.json()["data"]
            
            # Enhanced status information for Copilot
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "n8n_instance": self.base_url,
                "total_workflows": len(workflows),
                "active_workflows": sum(1 for w in workflows if w["active"]),
                "inactive_workflows": sum(1 for w in workflows if not w["active"]),
                "workflows": [],
                "health_score": 0,
                "recommendations": []
            }
            
            for workflow in workflows:
                workflow_info = {
                    "id": workflow["id"],
                    "name": workflow["name"],
                    "active": workflow["active"],
                    "nodes_count": len(workflow.get("nodes", [])),
                    "connections_count": self._count_connections(workflow.get("connections", {})),
                    "last_updated": workflow["updatedAt"],
                    "created": workflow["createdAt"],
                    "tags": workflow.get("tags", []),
                    "complexity_score": self._calculate_complexity(workflow)
                }
                status_data["workflows"].append(workflow_info)
            
            # Calculate health score and recommendations
            status_data["health_score"] = self._calculate_health_score(status_data)
            status_data["recommendations"] = self._generate_recommendations(status_data)
            
            return status_data
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API connection failed: {str(e)}",
                "status": "connection_failed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_workflow_executions(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent workflow executions for analysis"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions",
                headers=self.headers,
                params={"limit": limit},
                timeout=10
            )
            response.raise_for_status()
            executions = response.json()
            
            # Analyze execution patterns
            analysis = self._analyze_executions(executions.get("data", []))
            executions.update(analysis)
            
            return executions
        except Exception as e:
            return {"error": str(e), "executions": []}
    
    def backup_workflows(self, include_credentials: bool = False) -> Dict[str, Any]:
        """
        Backup all workflows to local files for version control
        Returns backup summary for Copilot
        """
        try:
            workflows = self._fetch_workflows_detailed()
            if not workflows:
                return {"error": "No workflows found or API connection failed"}
            
            backup_summary = {
                "timestamp": datetime.now().isoformat(),
                "total_backed_up": 0,
                "files_created": [],
                "backup_location": str(self.backup_dir.absolute())
            }
            
            for workflow in workflows:
                filename = f"{workflow['name'].replace(' ', '_').replace('/', '_')}.json"
                filepath = self.backup_dir / filename
                
                # Enhanced workflow data for version control
                workflow_data = {
                    "backup_metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "source": "copilot_tool",
                        "n8n_instance": self.base_url
                    },
                    "workflow": workflow
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(workflow_data, f, indent=2, ensure_ascii=False)
                
                backup_summary["files_created"].append(filename)
                backup_summary["total_backed_up"] += 1
            
            return backup_summary
            
        except Exception as e:
            return {"error": f"Backup failed: {str(e)}"}
    
    def analyze_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        Analyze a specific workflow for Copilot insights
        Provides detailed analysis of workflow structure, performance, and optimization opportunities
        """
        try:
            workflows = self._fetch_workflows_detailed()
            workflow = next((w for w in workflows if w["name"] == workflow_name), None)
            
            if not workflow:
                return {"error": f"Workflow '{workflow_name}' not found"}
            
            analysis = {
                "workflow_name": workflow_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "basic_info": {
                    "id": workflow["id"],
                    "active": workflow["active"],
                    "nodes_count": len(workflow.get("nodes", [])),
                    "created": workflow["createdAt"],
                    "updated": workflow["updatedAt"]
                },
                "structure_analysis": self._analyze_workflow_structure(workflow),
                "performance_insights": self._analyze_workflow_performance(workflow),
                "security_analysis": self._analyze_workflow_security(workflow),
                "optimization_suggestions": self._generate_optimization_suggestions(workflow),
                "complexity_metrics": self._calculate_detailed_complexity(workflow)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def sync_to_workspace(self) -> Dict[str, Any]:
        """
        Sync current n8n state to VS Code workspace
        This is the main function Copilot should use for regular updates
        """
        try:
            # Get current status
            status = self.get_workflow_status()
            
            if "error" in status:
                return status
            
            # Get recent executions
            executions = self.get_workflow_executions()
            
            # Save to workspace
            workspace_files = {}
            
            # Main status file
            status_file = self.workspace_dir / "workflow_status.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2)
            workspace_files["status"] = str(status_file)
            
            # Executions file
            executions_file = self.workspace_dir / "recent_executions.json"
            with open(executions_file, 'w', encoding='utf-8') as f:
                json.dump(executions, f, indent=2)
            workspace_files["executions"] = str(executions_file)
            
            # Create enhanced README for developers
            readme_content = self._generate_enhanced_readme(status, executions)
            readme_file = self.workspace_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            workspace_files["readme"] = str(readme_file)
            
            # Create development insights
            insights = self._generate_development_insights(status, executions)
            insights_file = self.workspace_dir / "development_insights.json"
            with open(insights_file, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2)
            workspace_files["insights"] = str(insights_file)
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "files_updated": workspace_files,
                "summary": {
                    "total_workflows": status.get("total_workflows", 0),
                    "active_workflows": status.get("active_workflows", 0),
                    "health_score": status.get("health_score", 0),
                    "recommendations_count": len(status.get("recommendations", []))
                }
            }
            
        except Exception as e:
            return {"error": f"Workspace sync failed: {str(e)}"}
    
    # Helper methods for analysis
    def _fetch_workflows_detailed(self) -> List[Dict[str, Any]]:
        """Fetch detailed workflow information"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers)
            response.raise_for_status()
            return response.json()["data"]
        except:
            return []
    
    def _count_connections(self, connections: Dict) -> int:
        """Count total connections in workflow"""
        count = 0
        for node_connections in connections.values():
            for connection_type in node_connections.values():
                count += len(connection_type)
        return count
    
    def _calculate_complexity(self, workflow: Dict) -> int:
        """Calculate workflow complexity score"""
        nodes = len(workflow.get("nodes", []))
        connections = self._count_connections(workflow.get("connections", {}))
        return min(nodes + connections * 2, 100)
    
    def _calculate_health_score(self, status_data: Dict) -> int:
        """Calculate overall health score"""
        if status_data["total_workflows"] == 0:
            return 0
        
        active_ratio = status_data["active_workflows"] / status_data["total_workflows"]
        base_score = int(active_ratio * 70)
        
        # Add points for recent activity, proper naming, etc.
        bonus_points = min(30, status_data["total_workflows"] * 5)
        
        return min(100, base_score + bonus_points)
    
    def _generate_recommendations(self, status_data: Dict) -> List[str]:
        """Generate recommendations based on status"""
        recommendations = []
        
        if status_data["active_workflows"] == 0:
            recommendations.append("Consider activating at least one workflow for continuous operation")
        
        if status_data["total_workflows"] > 10:
            recommendations.append("Consider organizing workflows with tags for better management")
        
        for workflow in status_data["workflows"]:
            if workflow["nodes_count"] > 20:
                recommendations.append(f"Workflow '{workflow['name']}' is complex - consider breaking into smaller workflows")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _analyze_executions(self, executions: List[Dict]) -> Dict[str, Any]:
        """Analyze execution patterns"""
        if not executions:
            return {"analysis": "No recent executions found"}
        
        success_count = sum(1 for ex in executions if ex.get("finished") and not ex.get("stoppedAt"))
        error_count = sum(1 for ex in executions if ex.get("stoppedAt"))
        
        return {
            "execution_analysis": {
                "total_executions": len(executions),
                "successful_executions": success_count,
                "failed_executions": error_count,
                "success_rate": (success_count / len(executions)) * 100 if executions else 0
            }
        }
    
    def _analyze_workflow_structure(self, workflow: Dict) -> Dict[str, Any]:
        """Analyze workflow structure"""
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})
        
        node_types = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        return {
            "total_nodes": len(nodes),
            "node_types": node_types,
            "total_connections": self._count_connections(connections),
            "entry_points": self._find_entry_points(nodes, connections),
            "exit_points": self._find_exit_points(nodes, connections)
        }
    
    def _analyze_workflow_performance(self, workflow: Dict) -> Dict[str, Any]:
        """Analyze workflow performance characteristics"""
        nodes = workflow.get("nodes", [])
        
        # Identify potentially slow nodes
        slow_node_types = ["@n8n/n8n-nodes-langchain", "n8n-nodes-base.httpRequest", "n8n-nodes-base.postgres"]
        slow_nodes = [node for node in nodes if any(slow_type in node.get("type", "") for slow_type in slow_node_types)]
        
        return {
            "potentially_slow_nodes": len(slow_nodes),
            "parallel_branches": self._count_parallel_branches(workflow.get("connections", {})),
            "performance_score": self._calculate_performance_score(workflow)
        }
    
    def _analyze_workflow_security(self, workflow: Dict) -> Dict[str, Any]:
        """Analyze workflow security aspects"""
        nodes = workflow.get("nodes", [])
        
        # Check for credential usage
        credential_nodes = [node for node in nodes if node.get("credentials")]
        
        # Check for HTTP nodes (potential security considerations)
        http_nodes = [node for node in nodes if "http" in node.get("type", "").lower()]
        
        return {
            "credential_nodes_count": len(credential_nodes),
            "http_nodes_count": len(http_nodes),
            "security_score": self._calculate_security_score(workflow)
        }
    
    def _generate_optimization_suggestions(self, workflow: Dict) -> List[str]:
        """Generate optimization suggestions for workflow"""
        suggestions = []
        nodes = workflow.get("nodes", [])
        
        if len(nodes) > 15:
            suggestions.append("Consider breaking this workflow into smaller, more focused workflows")
        
        # Check for sequential HTTP requests that could be parallelized
        http_nodes = [node for node in nodes if "http" in node.get("type", "").lower()]
        if len(http_nodes) > 3:
            suggestions.append("Consider parallelizing HTTP requests where possible")
        
        # Check for missing error handling
        error_nodes = [node for node in nodes if "error" in node.get("type", "").lower()]
        if not error_nodes and len(nodes) > 5:
            suggestions.append("Consider adding error handling nodes for better reliability")
        
        return suggestions
    
    def _calculate_detailed_complexity(self, workflow: Dict) -> Dict[str, Any]:
        """Calculate detailed complexity metrics"""
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})
        
        return {
            "node_complexity": len(nodes),
            "connection_complexity": self._count_connections(connections),
            "depth_complexity": self._calculate_workflow_depth(workflow),
            "branching_factor": self._calculate_branching_factor(connections),
            "overall_complexity": self._calculate_complexity(workflow)
        }
    
    def _find_entry_points(self, nodes: List[Dict], connections: Dict) -> List[str]:
        """Find workflow entry points"""
        # Simplified - look for trigger nodes
        triggers = [node["name"] for node in nodes if "trigger" in node.get("type", "").lower()]
        return triggers or ["Manual Trigger"]
    
    def _find_exit_points(self, nodes: List[Dict], connections: Dict) -> List[str]:
        """Find workflow exit points"""
        # Simplified - look for nodes with no outgoing connections
        connected_nodes = set()
        for source_connections in connections.values():
            for target_list in source_connections.values():
                for target in target_list:
                    connected_nodes.add(target.get("node", ""))
        
        all_nodes = {node["name"] for node in nodes}
        exit_points = list(all_nodes - connected_nodes)
        return exit_points or ["End"]
    
    def _count_parallel_branches(self, connections: Dict) -> int:
        """Count parallel execution branches"""
        max_parallel = 0
        for source_connections in connections.values():
            for target_list in source_connections.values():
                max_parallel = max(max_parallel, len(target_list))
        return max_parallel
    
    def _calculate_performance_score(self, workflow: Dict) -> int:
        """Calculate performance score (0-100)"""
        nodes = workflow.get("nodes", [])
        base_score = max(0, 100 - len(nodes) * 2)  # Penalty for complexity
        
        # Bonus for parallel execution capability
        parallel_bonus = min(20, self._count_parallel_branches(workflow.get("connections", {})) * 5)
        
        return min(100, base_score + parallel_bonus)
    
    def _calculate_security_score(self, workflow: Dict) -> int:
        """Calculate security score (0-100)"""
        nodes = workflow.get("nodes", [])
        base_score = 80
        
        # Deduct points for each HTTP node (potential security risk)
        http_nodes = [node for node in nodes if "http" in node.get("type", "").lower()]
        security_penalty = len(http_nodes) * 5
        
        return max(0, base_score - security_penalty)
    
    def _calculate_workflow_depth(self, workflow: Dict) -> int:
        """Calculate maximum execution depth"""
        # Simplified calculation - in a real implementation, this would trace the execution path
        return min(10, len(workflow.get("nodes", [])))
    
    def _calculate_branching_factor(self, connections: Dict) -> float:
        """Calculate average branching factor"""
        if not connections:
            return 0.0
        
        total_branches = sum(
            len(target_list)
            for source_connections in connections.values()
            for target_list in source_connections.values()
        )
        
        return total_branches / len(connections) if connections else 0.0
    
    def _generate_enhanced_readme(self, status: Dict, executions: Dict) -> str:
        """Generate enhanced README for developers"""
        return f"""# n8n Workspace Status Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Overview
- **Total Workflows**: {status.get('total_workflows', 0)}
- **Active Workflows**: {status.get('active_workflows', 0)}
- **Health Score**: {status.get('health_score', 0)}/100

## 🔄 Workflows
{self._format_workflows_table(status.get('workflows', []))}

## 📈 Recent Activity
{self._format_execution_summary(executions)}

## 🎯 Recommendations
{self._format_recommendations(status.get('recommendations', []))}

## 🔗 Quick Actions
- [Open n8n Web Interface]({status.get('n8n_instance', 'http://localhost:5678')})
- [View Detailed Status](./workflow_status.json)
- [View Execution History](./recent_executions.json)
- [Development Insights](./development_insights.json)

---
*This report is automatically generated by the Copilot n8n Tool*
"""
    
    def _format_workflows_table(self, workflows: List[Dict]) -> str:
        """Format workflows as a table"""
        if not workflows:
            return "No workflows found."
        
        lines = ["| Status | Name | Nodes | Complexity | Last Updated |", "|--------|------|-------|------------|--------------|"]
        
        for workflow in workflows:
            status_icon = "🟢" if workflow["active"] else "🔴"
            complexity = workflow.get("complexity_score", 0)
            lines.append(f"| {status_icon} | {workflow['name']} | {workflow['nodes_count']} | {complexity}/100 | {workflow['last_updated'][:10]} |")
        
        return "\n".join(lines)
    
    def _format_execution_summary(self, executions: Dict) -> str:
        """Format execution summary"""
        analysis = executions.get("execution_analysis", {})
        if not analysis:
            return "No recent execution data available."
        
        return f"""- Total Executions: {analysis.get('total_executions', 0)}
- Success Rate: {analysis.get('success_rate', 0):.1f}%
- Failed Executions: {analysis.get('failed_executions', 0)}"""
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations list"""
        if not recommendations:
            return "No specific recommendations at this time."
        
        return "\n".join(f"- {rec}" for rec in recommendations)
    
    def _generate_development_insights(self, status: Dict, executions: Dict) -> Dict[str, Any]:
        """Generate development insights for Copilot"""
        return {
            "timestamp": datetime.now().isoformat(),
            "workflow_patterns": self._analyze_workflow_patterns(status.get("workflows", [])),
            "development_suggestions": self._generate_development_suggestions(status, executions),
            "maintenance_tasks": self._identify_maintenance_tasks(status, executions),
            "performance_metrics": self._calculate_performance_metrics(status, executions)
        }
    
    def _analyze_workflow_patterns(self, workflows: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns across workflows"""
        if not workflows:
            return {"no_data": True}
        
        total_nodes = sum(w["nodes_count"] for w in workflows)
        avg_complexity = sum(w.get("complexity_score", 0) for w in workflows) / len(workflows)
        
        return {
            "total_workflows": len(workflows),
            "average_nodes_per_workflow": total_nodes / len(workflows),
            "average_complexity": avg_complexity,
            "active_percentage": (sum(1 for w in workflows if w["active"]) / len(workflows)) * 100
        }
    
    def _generate_development_suggestions(self, status: Dict, executions: Dict) -> List[str]:
        """Generate development-focused suggestions"""
        suggestions = []
        
        if status.get("health_score", 0) < 70:
            suggestions.append("Consider reviewing and optimizing workflow health")
        
        execution_analysis = executions.get("execution_analysis", {})
        if execution_analysis.get("success_rate", 100) < 90:
            suggestions.append("Review failed executions and add error handling")
        
        return suggestions
    
    def _identify_maintenance_tasks(self, status: Dict, executions: Dict) -> List[str]:
        """Identify maintenance tasks"""
        tasks = []
        
        # Check for inactive workflows
        inactive_count = status.get("total_workflows", 0) - status.get("active_workflows", 0)
        if inactive_count > 0:
            tasks.append(f"Review {inactive_count} inactive workflow(s)")
        
        # Check execution failure rate
        execution_analysis = executions.get("execution_analysis", {})
        if execution_analysis.get("failed_executions", 0) > 5:
            tasks.append("Investigate recent execution failures")
        
        return tasks
    
    def _calculate_performance_metrics(self, status: Dict, executions: Dict) -> Dict[str, Any]:
        """Calculate performance metrics"""
        return {
            "health_score": status.get("health_score", 0),
            "success_rate": executions.get("execution_analysis", {}).get("success_rate", 0),
            "workflow_efficiency": self._calculate_workflow_efficiency(status),
            "maintenance_score": self._calculate_maintenance_score(status, executions)
        }
    
    def _calculate_workflow_efficiency(self, status: Dict) -> float:
        """Calculate workflow efficiency score"""
        workflows = status.get("workflows", [])
        if not workflows:
            return 0.0
        
        # Simple efficiency metric based on active workflows and complexity
        active_workflows = sum(1 for w in workflows if w["active"])
        avg_complexity = sum(w.get("complexity_score", 0) for w in workflows) / len(workflows)
        
        return (active_workflows / len(workflows)) * (1 - avg_complexity / 100) * 100
    
    def _calculate_maintenance_score(self, status: Dict, executions: Dict) -> float:
        """Calculate maintenance score (higher is better)"""
        base_score = status.get("health_score", 0)
        execution_analysis = executions.get("execution_analysis", {})
        success_rate = execution_analysis.get("success_rate", 100)
        
        return (base_score + success_rate) / 2


def main():
    """Main entry point for the Copilot tool"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Copilot n8n Integration Tool")
    parser.add_argument("command", choices=["status", "backup", "sync", "analyze"], 
                       help="Command to execute")
    parser.add_argument("--workflow", help="Workflow name for analysis")
    parser.add_argument("--output", choices=["json", "summary"], default="summary",
                       help="Output format")
    
    args = parser.parse_args()
    
    tool = CopilotN8nTool()
    
    if args.command == "status":
        result = tool.get_workflow_status()
    elif args.command == "backup":
        result = tool.backup_workflows()
    elif args.command == "sync":
        result = tool.sync_to_workspace()
    elif args.command == "analyze":
        if not args.workflow:
            print("Error: --workflow required for analyze command")
            sys.exit(1)
        result = tool.analyze_workflow(args.workflow)
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        # Summary output
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            if args.command == "sync":
                print(f"✅ Synced {result.get('summary', {}).get('total_workflows', 0)} workflows")
                print(f"📊 Health Score: {result.get('summary', {}).get('health_score', 0)}/100")
            elif args.command == "status":
                print(f"📋 {result.get('total_workflows', 0)} workflows found")
                print(f"🟢 {result.get('active_workflows', 0)} active")
                print(f"📊 Health Score: {result.get('health_score', 0)}/100")
            elif args.command == "backup":
                print(f"💾 Backed up {result.get('total_backed_up', 0)} workflows")
            elif args.command == "analyze":
                analysis = result.get('structure_analysis', {})
                print(f"📊 Analysis for '{args.workflow}':")
                print(f"   Nodes: {analysis.get('total_nodes', 0)}")
                print(f"   Connections: {analysis.get('total_connections', 0)}")


if __name__ == "__main__":
    main()
