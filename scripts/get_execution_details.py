#!/usr/bin/env python3
"""
Get detailed execution error information
"""

import requests
import json

def get_execution_details(execution_id):
    headers = {
        'X-N8N-API-KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw'
    }
    
    try:
        response = requests.get(f'http://localhost:5678/api/v1/executions/{execution_id}', headers=headers)
        if response.status_code == 200:
            execution = response.json()
            print(f'🔍 Execution {execution_id} Details:')
            print('=' * 60)
            
            data = execution.get('data', {})
            result_data = data.get('resultData', {})
            
            # Main error
            if 'error' in result_data:
                error = result_data['error']
                print(f'❌ Main Error:')
                print(f'   Message: {error.get("message", "Unknown")}')
                print(f'   Type: {error.get("name", "Unknown")}')
                if 'stack' in error:
                    stack_lines = error['stack'].split('\n')[:5]  # First 5 lines
                    print(f'   Stack: {stack_lines[0]}')
            
            # Node errors
            run_data = result_data.get('runData', {})
            if run_data:
                print(f'\n🔍 Node Analysis:')
                for node_name, node_runs in run_data.items():
                    if node_runs and len(node_runs) > 0:
                        node_run = node_runs[0]
                        if 'error' in node_run:
                            error = node_run['error']
                            print(f'❌ {node_name}:')
                            print(f'   Message: {error.get("message", "Unknown")}')
                            print(f'   Type: {error.get("name", "Unknown")}')
                        else:
                            execution_time = node_run.get('executionTime', 0)
                            data_count = len(node_run.get('data', {}).get('main', [{}]))
                            print(f'✅ {node_name}: Success ({execution_time}ms, {data_count} items)')
            
            print('\n' + '=' * 60)
        else:
            print(f'❌ API Error {response.status_code}: {response.text}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

# Get details for the most recent failed executions
recent_ids = [96, 95, 94]

for exec_id in recent_ids:
    get_execution_details(exec_id)
    print()
