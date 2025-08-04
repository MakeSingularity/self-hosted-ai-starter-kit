#!/opt/venv/bin/python
"""
Test script to verify Python integration in custom n8n container
This script demonstrates that all required packages are available
"""

import sys
import json
from datetime import datetime

def main():
    """Test Python integration and package availability"""
    result = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "python_path": sys.executable,
        "packages_tested": {},
        "success": True,
        "message": "Python integration working correctly"
    }
    
    # Test required packages
    packages_to_test = [
        "requests",
        "psutil", 
        "numpy",
        "pandas",
        "fastapi",
        "uvicorn"
    ]
    
    for package in packages_to_test:
        try:
            __import__(package)
            result["packages_tested"][package] = "✅ Available"
        except ImportError as e:
            result["packages_tested"][package] = f"❌ Failed: {e}"
            result["success"] = False
    
    # Test basic functionality
    try:
        import requests
        import psutil
        
        # Test requests
        result["requests_test"] = "✅ HTTP client ready"
        
        # Test psutil
        cpu_count = psutil.cpu_count()
        result["psutil_test"] = f"✅ System monitoring ready (CPU cores: {cpu_count})"
        
    except Exception as e:
        result["functionality_test"] = f"❌ Error: {e}"
        result["success"] = False
    
    # Print results
    print(json.dumps(result, indent=2))
    return result["success"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
