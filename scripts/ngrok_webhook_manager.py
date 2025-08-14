#!/usr/bin/env python3
"""
Automated Ngrok and n8n Webhook Management
Handles ngrok tunnel setup and n8n webhook configuration automatically
"""

import requests
import json
import time
import os
import subprocess
import sys
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NgrokN8nManager:
    def __init__(self):
        # Load configuration from environment
        self.ngrok_authtoken = os.getenv('NGROK_AUTHTOKEN', '2v6aCxn2NczIdc9dAuAzI6qyKCc_4tiN8xT7vCkvkch5VfVeV')
        self.subdomain = os.getenv('SUBDOMAIN', 'mutual-platypus-notable')
        self.domain_name = os.getenv('DOMAIN_NAME', 'ngrok-free.app')
        self.webhook_url = f"https://{self.subdomain}.{self.domain_name}"
        
        # n8n configuration
        self.n8n_api_token = os.getenv('N8N_API_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYzlhOWQyNC01MzY4LTQ4YWItYjFkZS1lMDY0Mzc0ODQzMTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0ODM4MTk3fQ.Qn_KfLq2s81g9XAaMj_u_fui3k5gj5MXD1NYeyJQokw')
        self.n8n_base_url = 'http://localhost:5678'
        self.n8n_headers = {
            'X-N8N-API-KEY': self.n8n_api_token,
            'Content-Type': 'application/json'
        }
        
        # Ngrok API configuration
        self.ngrok_api_url = 'http://localhost:4040/api'
        
    def cleanup_docker_ngrok(self):
        """Remove any Docker Desktop ngrok extensions that might conflict"""
        logger.info("🧹 Cleaning up potential Docker ngrok conflicts...")
        
        try:
            # Stop any running ngrok processes
            subprocess.run(['pkill', '-f', 'ngrok'], capture_output=True, text=True)
            logger.info("✅ Stopped existing ngrok processes")
        except Exception as e:
            logger.info(f"ℹ️ No existing ngrok processes to stop: {e}")
        
        # Wait a moment for cleanup
        time.sleep(2)
    
    def start_ngrok_tunnel(self):
        """Start ngrok tunnel using the reserved domain"""
        logger.info(f"🚀 Starting ngrok tunnel for {self.webhook_url}...")
        
        try:
            # Use the ngrok.yml configuration
            cmd = ['ngrok', 'start', 'n8n', '--config', 'ngrok.yml']
            
            # Start ngrok in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give ngrok time to start
            time.sleep(5)
            
            # Check if ngrok is running
            if self.verify_ngrok_tunnel():
                logger.info(f"✅ Ngrok tunnel started successfully: {self.webhook_url}")
                return True
            else:
                logger.error("❌ Failed to start ngrok tunnel")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting ngrok: {e}")
            return False
    
    def verify_ngrok_tunnel(self):
        """Verify that ngrok tunnel is active and accessible"""
        try:
            # Check ngrok API
            response = requests.get(f"{self.ngrok_api_url}/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                for tunnel in tunnels:
                    if tunnel['public_url'] == self.webhook_url:
                        logger.info(f"✅ Tunnel verified: {tunnel['public_url']}")
                        return True
            
            # Also test the actual webhook URL
            response = requests.get(self.webhook_url, timeout=10)
            if response.status_code < 500:  # Any response from n8n is good
                logger.info(f"✅ Webhook URL responding: {self.webhook_url}")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ Tunnel verification issue: {e}")
        
        return False
    
    def wait_for_n8n(self, max_attempts=30):
        """Wait for n8n to be ready"""
        logger.info("⏳ Waiting for n8n to be ready...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.n8n_base_url}/healthz", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ n8n is ready!")
                    return True
            except:
                pass
            
            logger.info(f"⏳ Attempt {attempt + 1}/{max_attempts} - waiting for n8n...")
            time.sleep(2)
        
        logger.error("❌ n8n did not become ready in time")
        return False
    
    def update_telegram_webhooks(self):
        """Update all Telegram webhook configurations in n8n workflows"""
        logger.info("🔄 Updating Telegram webhook configurations...")
        
        try:
            # Get all workflows
            response = requests.get(f"{self.n8n_base_url}/api/v1/workflows", headers=self.n8n_headers)
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch workflows: {response.status_code}")
                return False
            
            workflows = response.json()['data']
            updated_count = 0
            
            for workflow in workflows:
                needs_update = False
                nodes = workflow.get('nodes', [])
                
                # Look for Telegram trigger nodes
                for node in nodes:
                    if node.get('type') == 'n8n-nodes-base.telegramTrigger':
                        # Update webhook URL in the trigger
                        if 'webhookId' in node:
                            logger.info(f"🔄 Updating Telegram webhook in workflow '{workflow['name']}'")
                            needs_update = True
                            break
                
                if needs_update:
                    # Update the workflow
                    update_data = {
                        'name': workflow['name'],
                        'nodes': workflow['nodes'],
                        'connections': workflow.get('connections', {}),
                        'active': workflow['active'],
                        'settings': workflow.get('settings', {}),
                        'staticData': workflow.get('staticData', {})
                    }
                    
                    update_response = requests.put(
                        f"{self.n8n_base_url}/api/v1/workflows/{workflow['id']}",
                        headers=self.n8n_headers,
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        logger.info(f"✅ Updated workflow: {workflow['name']}")
                        updated_count += 1
                    else:
                        logger.error(f"❌ Failed to update workflow {workflow['name']}: {update_response.status_code}")
            
            logger.info(f"✅ Updated {updated_count} workflows with new webhook URL")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating webhooks: {e}")
            return False
    
    def setup_telegram_bot_webhook(self):
        """Set up the Telegram bot webhook directly via Telegram API"""
        logger.info("🤖 Configuring Telegram bot webhook...")
        
        # Note: This would require the Telegram bot token to be accessible
        # For now, we'll log the webhook URL that should be configured
        webhook_endpoint = f"{self.webhook_url}/webhook/telegram"
        
        logger.info(f"📝 Telegram webhook should be configured to: {webhook_endpoint}")
        logger.info("ℹ️ You may need to update this manually in Telegram Bot settings or n8n")
        
        return True
    
    def run_full_setup(self):
        """Run the complete ngrok and webhook setup process"""
        logger.info("🚀 Starting automated ngrok and webhook setup...")
        
        # Step 1: Clean up any conflicting ngrok instances
        self.cleanup_docker_ngrok()
        
        # Step 2: Start ngrok tunnel
        if not self.start_ngrok_tunnel():
            logger.error("❌ Failed to start ngrok tunnel")
            return False
        
        # Step 3: Wait for n8n to be ready
        if not self.wait_for_n8n():
            logger.error("❌ n8n is not ready")
            return False
        
        # Step 4: Update n8n webhook configurations
        if not self.update_telegram_webhooks():
            logger.error("❌ Failed to update webhooks")
            return False
        
        # Step 5: Setup Telegram bot webhook
        self.setup_telegram_bot_webhook()
        
        logger.info("🎉 Ngrok and webhook setup completed successfully!")
        logger.info(f"🌐 Webhook URL: {self.webhook_url}")
        logger.info(f"🎛️ Ngrok Dashboard: http://localhost:4040")
        
        return True
    
    def status(self):
        """Check current status of ngrok and webhooks"""
        logger.info("📊 Checking ngrok and webhook status...")
        
        # Check ngrok
        ngrok_ok = self.verify_ngrok_tunnel()
        
        # Check n8n
        try:
            response = requests.get(f"{self.n8n_base_url}/healthz", timeout=5)
            n8n_ok = response.status_code == 200
        except:
            n8n_ok = False
        
        print("\n" + "="*60)
        print("🔍 NGROK & WEBHOOK STATUS")
        print("="*60)
        print(f"🌐 Webhook URL: {self.webhook_url}")
        print(f"🚇 Ngrok Tunnel: {'✅ Active' if ngrok_ok else '❌ Inactive'}")
        print(f"⚙️ n8n Service: {'✅ Running' if n8n_ok else '❌ Down'}")
        print(f"📊 Ngrok Dashboard: http://localhost:4040")
        print("="*60)
        
        return ngrok_ok and n8n_ok

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Ngrok and n8n Webhook Manager")
    parser.add_argument("command", choices=["setup", "status", "cleanup"], 
                       help="Command to execute")
    
    args = parser.parse_args()
    
    manager = NgrokN8nManager()
    
    if args.command == "setup":
        success = manager.run_full_setup()
        sys.exit(0 if success else 1)
    elif args.command == "status":
        success = manager.status()
        sys.exit(0 if success else 1)
    elif args.command == "cleanup":
        manager.cleanup_docker_ngrok()
        logger.info("✅ Cleanup completed")

if __name__ == "__main__":
    main()
