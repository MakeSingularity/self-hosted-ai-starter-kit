#!/usr/bin/env python3
"""
Test Environment Detection API
Demonstrates how AI agents can use environment detection for adaptive behavior
"""

import requests
import json
import time

def test_environment_detection():
    """Test the environment detection API"""
    
    base_url = "http://localhost:8002"
    
    print("🔍 Testing Environment Detection API")
    print("=" * 50)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API health check failed")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Environment Detection API")
        print("💡 Start it with: python examples/environment_detector.py")
        return False
    
    # Test quick check
    print("\n🚀 Quick Environment Check:")
    try:
        response = requests.get(f"{base_url}/quick-check", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  Environment Type: {data['environment_type']}")
            print(f"  Memory: {data['memory_gb']} GB")
            print(f"  CPU Cores: {data['cpu_count']}")
            print(f"  GPU Available: {data['gpu_available']}")
            print(f"  Internet Connected: {data['internet_connected']}")
            print(f"  Services Running: {len([s for s in data['services_running'].values() if s])}/{len(data['services_running'])}")
        else:
            print(f"❌ Quick check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Quick check error: {e}")
    
    # Test AI capabilities
    print("\n🤖 AI Capabilities Assessment:")
    try:
        response = requests.get(f"{base_url}/ai-capabilities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  LLM Support: {data['llm_support']}")
            print(f"  GPU Acceleration: {data['gpu_acceleration']}")
            print(f"  Speech Synthesis: {data['speech_synthesis']}")
            print(f"  Speech Recognition: {data['speech_recognition']}")
            print(f"  Vector Database: {data['vector_database']}")
        else:
            print(f"❌ AI capabilities check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ AI capabilities error: {e}")
    
    # Test recommendations
    print("\n💡 Environment Recommendations:")
    try:
        response = requests.get(f"{base_url}/recommendations", timeout=10)
        if response.status_code == 200:
            data = response.json()
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"  {i}. {rec}")
            
            print(f"\n📊 Summary:")
            print(f"  Memory Status: {data['summary']['memory_status']}")
            print(f"  GPU Status: {data['summary']['gpu_status']}")
            print(f"  AI Ready: {data['summary']['ai_ready']}")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
    
    # Test full environment detection
    print("\n🔬 Full Environment Detection:")
    try:
        response = requests.get(f"{base_url}/detect-environment", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"  Environment Type: {data['environment_type']}")
            print(f"  Container Info: {data['container_info']['is_container']}")
            print(f"  System: {data['system_info']['system']} {data['system_info']['release']}")
            print(f"  Python Version: {data['system_info']['python_version']}")
            print(f"  Hostname: {data['system_info']['hostname']}")
            print(f"  AI Capabilities: {len([k for k, v in data['ai_capabilities'].items() if v and k != 'recommended_config'])}")
            print(f"  Recommendations: {len(data['recommendations'])}")
        else:
            print(f"❌ Full detection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Full detection error: {e}")
    
    print("\n🎉 Environment detection test complete!")
    return True

def demonstrate_ai_agent_adaptation():
    """Demonstrate how an AI agent would adapt based on environment"""
    
    print("\n🤖 AI Agent Adaptation Demo")
    print("=" * 40)
    
    try:
        # Get environment info
        response = requests.get("http://localhost:8002/quick-check", timeout=5)
        if response.status_code != 200:
            print("❌ Cannot get environment info")
            return
        
        env_data = response.json()
        
        # Simulate AI agent decision making
        print("🧠 AI Agent analyzing environment...")
        
        # Memory-based decisions
        memory_gb = env_data['memory_gb']
        if memory_gb < 4:
            model_size = "small"
            batch_size = 4
            optimization = "aggressive"
        elif memory_gb < 8:
            model_size = "medium"
            batch_size = 16
            optimization = "moderate"
        else:
            model_size = "large"
            batch_size = 32
            optimization = "minimal"
        
        # GPU-based decisions
        gpu_available = env_data['gpu_available']
        processing_mode = "GPU-accelerated" if gpu_available else "CPU-optimized"
        
        # Environment-based decisions
        env_type = env_data['environment_type']
        resource_mode = "conservative" if env_type == "container" else "aggressive"
        
        # Service availability decisions
        services = env_data['services_running']
        available_services = [service for service, running in services.items() if running]
        
        print(f"\n📋 AI Agent Decisions:")
        print(f"  Model Size: {model_size} (based on {memory_gb}GB memory)")
        print(f"  Batch Size: {batch_size}")
        print(f"  Processing Mode: {processing_mode}")
        print(f"  Resource Mode: {resource_mode} (for {env_type} environment)")
        print(f"  Memory Optimization: {optimization}")
        print(f"  Available Services: {', '.join(available_services) if available_services else 'None'}")
        
        # Generate workflow strategy
        strategy = {
            "model_config": {
                "size": model_size,
                "batch_size": batch_size,
                "use_gpu": gpu_available
            },
            "resource_management": {
                "memory_optimization": optimization != "minimal",
                "conservative_mode": resource_mode == "conservative"
            },
            "service_integration": {
                "local_only": not env_data['internet_connected'],
                "available_apis": available_services
            }
        }
        
        print(f"\n⚙️ Generated Strategy:")
        print(json.dumps(strategy, indent=2))
        
    except Exception as e:
        print(f"❌ Agent adaptation demo failed: {e}")

if __name__ == "__main__":
    success = test_environment_detection()
    if success:
        demonstrate_ai_agent_adaptation()
    else:
        print("\n💡 To run this test:")
        print("1. Start the environment detector: python examples/environment_detector.py")
        print("2. Run this test: python tests/test_environment_detection.py")
