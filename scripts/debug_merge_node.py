#!/usr/bin/env python3
"""
Debug n8n merge node and data flow issues
"""

import requests
import json
import os
from datetime import datetime

def debug_merge_node():
    """Debug merge node data flow in Oliver workflow"""
    
    print("🔍 n8n Merge Node Debug Report")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    n8n_url = "http://localhost:5678"
    
    try:
        # Get workflow executions with details
        executions_url = f"{n8n_url}/api/v1/executions"
        print(f"🔗 Checking recent executions...")
        
        response = requests.get(executions_url, timeout=10)
        if response.status_code == 200:
            executions = response.json()
            
            print(f"📊 Found {len(executions.get('data', []))} recent executions")
            
            # Look at the most recent execution
            if executions.get('data'):
                latest = executions['data'][0]
                execution_id = latest['id']
                
                print(f"\n🔍 Analyzing execution ID: {execution_id}")
                print(f"   Status: {latest.get('status', 'unknown')}")
                print(f"   Started: {latest.get('startedAt', 'unknown')}")
                print(f"   Finished: {latest.get('finishedAt', 'unknown')}")
                
                # Get detailed execution data
                exec_detail_url = f"{n8n_url}/api/v1/executions/{execution_id}"
                detail_response = requests.get(exec_detail_url, timeout=10)
                
                if detail_response.status_code == 200:
                    exec_data = detail_response.json()
                    
                    print(f"\n📋 Execution Data Analysis:")
                    
                    # Check for merge node
                    if 'data' in exec_data and 'resultData' in exec_data['data']:
                        result_data = exec_data['data']['resultData']
                        
                        if 'runData' in result_data:
                            run_data = result_data['runData']
                            
                            # Look for merge-related nodes
                            merge_nodes = [node for node in run_data.keys() if 'merge' in node.lower()]
                            get_file_nodes = [node for node in run_data.keys() if 'get' in node.lower() and 'file' in node.lower()]
                            
                            print(f"🔗 Merge nodes found: {merge_nodes}")
                            print(f"📁 Get file nodes found: {get_file_nodes}")
                            
                            # Analyze each node's data
                            for node_name, node_data in run_data.items():
                                if 'merge' in node_name.lower() or 'get' in node_name.lower():
                                    print(f"\n🔧 Node: {node_name}")
                                    
                                    if isinstance(node_data, list) and node_data:
                                        first_run = node_data[0]
                                        
                                        if 'data' in first_run:
                                            data = first_run['data']
                                            if 'main' in data:
                                                main_data = data['main']
                                                
                                                print(f"   📦 Output items: {len(main_data) if main_data else 0}")
                                                
                                                if main_data:
                                                    for i, item in enumerate(main_data[:2]):  # Show first 2 items
                                                        if isinstance(item, list) and item:
                                                            item_data = item[0]
                                                            print(f"   📄 Item {i}: {list(item_data.get('json', {}).keys())}")
                                                        
                                        if 'error' in first_run:
                                            print(f"   ❌ Error: {first_run['error']}")
                            
                            # Show specific recommendations
                            print(f"\n💡 Merge Node Troubleshooting:")
                            print(f"   1. Check that 'Get a file' node produces file data")
                            print(f"   2. Verify merge node input configuration")
                            print(f"   3. Ensure correct node connections")
                            print(f"   4. Check merge mode (Append, Keep Key Matches, etc.)")
                            
                        else:
                            print("   ❌ No run data found")
                    else:
                        print("   ❌ No result data found")
                else:
                    print(f"   ❌ Could not get execution details: {detail_response.status_code}")
            else:
                print("   ❌ No recent executions found")
        else:
            print(f"❌ Could not get executions: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    
    # Additional troubleshooting tips
    print(f"\n🛠️ Common Merge Node Issues:")
    print(f"   • Input 1 (Get file): Should contain file data with file_id, file_path")
    print(f"   • Input 2 (Previous): Should contain message/trigger data")
    print(f"   • Merge mode: Try 'Append' or 'Keep Key Matches'")
    print(f"   • Output: Should combine both inputs for transcription node")
    print()
    print(f"🔧 Quick Fixes:")
    print(f"   1. Open n8n editor and check merge node inputs")
    print(f"   2. Test 'Get a file' node independently")
    print(f"   3. Check merge node configuration")
    print(f"   4. Verify node connections and data flow")

if __name__ == "__main__":
    debug_merge_node()
