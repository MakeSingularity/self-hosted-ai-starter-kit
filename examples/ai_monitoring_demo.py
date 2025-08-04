#!/usr/bin/env python3
"""
AI Setup & Monitoring Demo Script

This script demonstrates how to trigger and interact with the 
AI Setup & Monitoring n8n workflow programmatically.
"""

import requests
import json
import time
import sys
from pathlib import Path

def print_header():
    """Print demo header"""
    print("🤖 AI Setup & Monitoring Demo")
    print("=" * 40)
    print("This demo shows intelligent setup automation")
    print("and AI-powered service monitoring in action!")
    print()

def check_environment_api():
    """Check if environment detector API is running"""
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Environment Detector API is running")
            return True
        else:
            print("❌ Environment Detector API not responding properly")
            return False
    except requests.RequestException:
        print("❌ Environment Detector API not accessible")
        print("💡 Start it with: python examples/environment_detector.py")
        return False

def get_environment_info():
    """Get comprehensive environment information"""
    print("\n🔍 Getting Environment Information...")
    try:
        response = requests.get("http://localhost:8002/environment", timeout=30)
        if response.status_code == 200:
            env_data = response.json()
            
            print(f"📍 Environment Type: {env_data.get('environment', {}).get('container_type', 'Unknown')}")
            
            hardware = env_data.get('environment', {}).get('hardware', {})
            print(f"💻 Hardware: {hardware.get('cpu_cores', 'N/A')} cores, {hardware.get('memory_total_gb', 'N/A')}GB RAM")
            print(f"🎮 GPU Available: {'Yes' if hardware.get('gpu_available') else 'No'}")
            
            software = env_data.get('environment', {}).get('software', {})
            print(f"🐍 Python: {software.get('python_version', 'N/A')}")
            print(f"🐳 Docker: {'Yes' if software.get('docker_available') else 'No'}")
            
            return env_data
        else:
            print("❌ Failed to get environment information")
            return None
    except requests.RequestException as e:
        print(f"❌ Error getting environment info: {e}")
        return None

def check_service_health():
    """Check health of all services"""
    print("\n🏥 Checking Service Health...")
    
    services = {
        "n8n": "http://localhost:5678/api/v1/workflows",
        "ollama": "http://localhost:11434/api/tags", 
        "qdrant": "http://localhost:6333/collections",
        "api_server": "http://localhost:8000/health"
    }
    
    results = {}
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {service.upper()}: Running")
                results[service] = "running"
            else:
                print(f"❌ {service.upper()}: Not responding")
                results[service] = "stopped"
        except requests.RequestException:
            print(f"❌ {service.upper()}: Not accessible")
            results[service] = "stopped"
    
    return results

def simulate_ai_analysis(env_data, service_results):
    """Simulate the AI analysis that the workflow performs"""
    print("\n🤖 Performing AI Analysis...")
    
    # Calculate performance score
    score = 0
    
    # Service availability (40 points)
    running_services = sum(1 for status in service_results.values() if status == "running")
    total_services = len(service_results)
    score += (running_services / total_services) * 40
    
    # Hardware score (30 points)
    if env_data and env_data.get('environment', {}).get('hardware', {}):
        hardware = env_data['environment']['hardware']
        if hardware.get('gpu_available'):
            score += 15
        if hardware.get('memory_total_gb', 0) >= 16:
            score += 10
        elif hardware.get('memory_total_gb', 0) >= 8:
            score += 5
        if hardware.get('cpu_cores', 0) >= 8:
            score += 5
    
    # Mock content score (30 points)
    score += 20  # Assume some content exists
    
    score = round(score)
    
    # Generate grade
    if score >= 90:
        grade = "A"
        status = "Excellent"
    elif score >= 80:
        grade = "B" 
        status = "Good"
    elif score >= 70:
        grade = "C"
        status = "Satisfactory"
    else:
        grade = "D"
        status = "Needs Improvement"
    
    print(f"📊 Performance Score: {score}/100 (Grade: {grade})")
    print(f"🎯 Status: {status}")
    
    # Generate recommendations
    recommendations = []
    if score < 70:
        recommendations.append("Run: docker-compose up -d to start missing services")
    if env_data and not env_data.get('environment', {}).get('hardware', {}).get('gpu_available'):
        recommendations.append("Consider NVIDIA GPU for AI workloads")
    if running_services < total_services:
        stopped = [name for name, status in service_results.items() if status == "stopped"]
        recommendations.append(f"Start stopped services: {', '.join(stopped)}")
    
    if recommendations:
        print("\n🎯 AI Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("\n🎉 No recommendations - everything looks great!")
    
    return {
        "score": score,
        "grade": grade,
        "status": status,
        "recommendations": recommendations
    }

def check_workflow_reports():
    """Check if workflow has generated reports"""
    print("\n📊 Checking for Workflow Reports...")
    
    json_report = Path("shared/ai-setup-status-report.json")
    txt_report = Path("shared/ai-setup-status-report.txt")
    
    if json_report.exists():
        print("✅ JSON report found")
        try:
            with open(json_report, 'r') as f:
                data = json.load(f)
                timestamp = data.get('timestamp', 'Unknown')
                score = data.get('performance', {}).get('score', 'N/A')
                print(f"   Last generated: {timestamp}")
                print(f"   Performance score: {score}")
        except Exception as e:
            print(f"   ⚠️  Error reading JSON report: {e}")
    else:
        print("❌ JSON report not found")
        print("   💡 Run the n8n workflow to generate reports")
    
    if txt_report.exists():
        print("✅ Human-readable report found")
        try:
            size = txt_report.stat().st_size
            print(f"   Report size: {size} bytes")
        except Exception as e:
            print(f"   ⚠️  Error checking txt report: {e}")
    else:
        print("❌ Human-readable report not found")

def show_workflow_info():
    """Show information about the n8n workflow"""
    print("\n📋 AI Setup & Monitoring Workflow Info:")
    print("=" * 45)
    print("🎯 Purpose: Intelligent setup automation and monitoring")
    print("📍 Location: n8n/demo-data/workflows/ai-setup-and-monitoring-workflow.json")
    print("🔄 Features:")
    print("   • Automatic environment detection")
    print("   • Service health monitoring")
    print("   • AI-powered analysis and recommendations")
    print("   • Automated setup when needed")
    print("   • Continuous monitoring (every 15 minutes)")
    print("   • Performance scoring and grading")
    print("   • Human and machine-readable reports")
    print()
    print("🚀 To use:")
    print("   1. Import workflow into n8n")
    print("   2. Trigger manually or wait for cron")
    print("   3. Check reports in shared/ directory")
    print("   4. Follow AI recommendations")

def main():
    """Main demo function"""
    print_header()
    
    # Check if environment API is running
    if not check_environment_api():
        print("\n⚠️  Environment Detector API must be running for full demo")
        print("Start it and run this demo again!")
        return
    
    # Get environment information
    env_data = get_environment_info()
    
    # Check service health
    service_results = check_service_health()
    
    # Perform AI analysis
    analysis = simulate_ai_analysis(env_data, service_results)
    
    # Check for workflow reports
    check_workflow_reports()
    
    # Show workflow information
    show_workflow_info()
    
    print("\n🎉 Demo Complete!")
    print("=" * 20)
    print("This demonstrates the same analysis that the")
    print("n8n workflow performs automatically!")
    
    # Suggest next steps
    if analysis["score"] < 70:
        print("\n💡 Suggested Action:")
        print("Import and run the n8n workflow to automatically")
        print("start missing services and improve your setup!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)
