#!/usr/bin/env python3
"""
Quick script to check n8n execution logs and errors
"""

import requests
import json
from datetime import datetime

def check_executions():
    headers = {
        'X-N8N-API-KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get recent executions
        response = requests.get('http://localhost:5678/api/v1/executions', headers=headers, params={'limit': 5})
        if response.status_code == 200:
            executions = response.json()['data']
            print('🔍 Recent Execution Analysis:')
            print('=' * 60)
            
            for i, execution in enumerate(executions[:3]):
                print(f'\nExecution {i+1}:')
                print(f'  ID: {execution.get("id", "N/A")}')
                
                # Determine status
                if execution.get("finished") and not execution.get("stoppedAt"):
                    status = "✅ Success"
                elif execution.get("stoppedAt"):
                    status = "❌ Failed/Stopped"
                elif execution.get("waitTill"):
                    status = "⏳ Waiting"
                else:
                    status = "🔄 Running"
                
                print(f'  Status: {status}')
                print(f'  Started: {execution.get("startedAt", "N/A")}')
                print(f'  Stopped: {execution.get("stoppedAt", "N/A")}')
                print(f'  Mode: {execution.get("mode", "N/A")}')
                print(f'  Workflow: {execution.get("workflowData", {}).get("name", "Unknown")}')
                
                # Check for error data
                if execution.get("data"):
                    data = execution["data"]
                    if "resultData" in data and data["resultData"]:
                        result_data = data["resultData"]
                        if "error" in result_data:
                            print(f'  ❌ Error: {result_data["error"]}')
                        
                        # Check each node's execution
                        if "runData" in result_data:
                            run_data = result_data["runData"]
                            print(f'  Nodes executed: {len(run_data)}')
                            
                            for node_name, node_runs in run_data.items():
                                if node_runs:
                                    node_run = node_runs[0]  # Get first run
                                    if "error" in node_run:
                                        print(f'    ❌ {node_name}: {node_run["error"].get("message", "Unknown error")}')
                                    elif node_run.get("data"):
                                        print(f'    ✅ {node_name}: Executed successfully')
                                    else:
                                        print(f'    ⚠️ {node_name}: No data returned')
                
                print('-' * 40)
                
        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'Response: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('❌ Connection Error: Cannot connect to n8n instance')
        print('🔍 Possible issues:')
        print('  - n8n service is not running')
        print('  - Wrong URL (check if http://localhost:5678 is accessible)')
        print('  - Docker container might be down')
    except Exception as e:
        print(f'❌ Unexpected Error: {str(e)}')

def check_services():
    print('\n🔍 Checking service dependencies:')
    print('=' * 40)
    
    services_to_check = [
        ('n8n', 'http://localhost:5678'),
        ('Ollama', 'http://localhost:11434'),
        ('Postgres', 'localhost:5432'),
        ('Qdrant', 'http://localhost:6333')
    ]
    
    for service_name, url in services_to_check:
        try:
            if 'http' in url:
                response = requests.get(f'{url}/health' if 'ollama' in url.lower() else url, timeout=2)
                if response.status_code < 400:
                    print(f'✅ {service_name}: Running')
                else:
                    print(f'⚠️ {service_name}: Responding but may have issues ({response.status_code})')
            else:
                # For non-HTTP services like Postgres, we'll assume they're running if n8n can connect
                print(f'ℹ️ {service_name}: Check via n8n logs')
        except requests.exceptions.ConnectionError:
            print(f'❌ {service_name}: Not accessible')
        except Exception as e:
            print(f'⚠️ {service_name}: Unknown status - {str(e)}')

if __name__ == "__main__":
    check_executions()
    check_services()
