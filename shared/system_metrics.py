#!/usr/bin/env python3
"""
Simple system metrics collector for n8n monitoring workflow
"""

import sys
import json
import psutil

try:
    # Collect system metrics
    metrics = {
        'python_version': sys.version,
        'memory_usage': psutil.virtual_memory()._asdict(),
        'cpu_percent': psutil.cpu_percent(),
        'disk_usage': psutil.disk_usage('/')._asdict()
    }
    
    # Output as JSON
    print(json.dumps(metrics))
    
except Exception as e:
    # Output error as JSON
    error_data = {
        'error': True,
        'message': str(e),
        'python_version': sys.version
    }
    print(json.dumps(error_data))
    sys.exit(1)
