#!/usr/bin/env python3
"""
Quick setup script to add Telegram bot token to environment
"""

import os

def setup_telegram_token():
    print("🤖 Telegram Bot Token Setup")
    print("=" * 40)
    print()
    print("To get a Telegram bot token:")
    print("1. Go to @BotFather on Telegram")
    print("2. Send /newbot or /mybots")
    print("3. Follow the instructions")
    print("4. Copy the bot token (looks like: 1234567890:ABC-DEF1234ghIkl...)")
    print()
    
    token = input("Enter your Telegram bot token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    if not ":" in token or len(token) < 20:
        print("❌ Invalid token format")
        print("Token should look like: 1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
        return False
    
    # Read current .env file
    env_path = ".env"
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Remove any existing TELEGRAM_BOT_TOKEN lines
    lines = [line for line in lines if not line.startswith("TELEGRAM_BOT_TOKEN=")]
    
    # Add the new token
    lines.append(f"\n# Telegram Bot Configuration\nTELEGRAM_BOT_TOKEN={token}\n")
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ Token added to .env file")
    print("🔄 You need to restart the Fast Whisper API for changes to take effect")
    print()
    print("Next steps:")
    print("1. Restart the API (or we can do it automatically)")
    print("2. Test with a real voice message in your n8n workflow")
    
    return True

if __name__ == "__main__":
    setup_telegram_token()
