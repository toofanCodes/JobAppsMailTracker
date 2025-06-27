#!/usr/bin/env python3
"""
Gemini API Setup Script
Helps you configure your Gemini API key for the JobAppsMailTracker
"""

import os
import sys
from pathlib import Path

def setup_gemini_api():
    """Interactive setup for Gemini API key"""
    
    print("🤖 Gemini AI API Setup for JobAppsMailTracker")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv('GEMINI_API_KEY')
    if current_key and current_key != 'your_api_key_here':
        print(f"✅ Gemini API key already configured: {current_key[:10]}...")
        response = input("Do you want to update it? (y/N): ").lower()
        if response != 'y':
            print("Keeping existing API key.")
            return
    
    print("\n📋 Step-by-step instructions:")
    print("1. Go to https://aistudio.google.com/")
    print("2. Sign in with your Google account")
    print("3. Click 'Get API key' in the top right")
    print("4. Choose 'Create API key in new project'")
    print("5. Copy the generated API key")
    print()
    
    # Get API key from user
    api_key = input("🔑 Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    if not api_key.startswith('AIza'):
        print("⚠️  Warning: API key doesn't start with 'AIza'. Please double-check.")
        confirm = input("Continue anyway? (y/N): ").lower()
        if confirm != 'y':
            return
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = api_key
    
    # Create shell profile entry
    shell_profile = Path.home() / '.zshrc'  # Since you're using zsh
    
    if shell_profile.exists():
        with open(shell_profile, 'r') as f:
            content = f.read()
        
        if 'GEMINI_API_KEY' not in content:
            with open(shell_profile, 'a') as f:
                f.write(f'\n# Gemini AI API Key for JobAppsMailTracker\nexport GEMINI_API_KEY="{api_key}"\n')
            print(f"✅ Added API key to {shell_profile}")
        else:
            print(f"⚠️  GEMINI_API_KEY already exists in {shell_profile}")
            print("   You may need to manually update it.")
    else:
        print(f"⚠️  {shell_profile} not found. Please manually add:")
        print(f'   export GEMINI_API_KEY="{api_key}"')
    
    print(f"\n✅ API key configured for current session!")
    print(f"   Key: {api_key[:10]}...")
    
    # Test the setup
    print("\n🧪 Testing Gemini API connection...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Simple test
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello! Just testing the connection.")
        
        if response.text:
            print("✅ Gemini API connection successful!")
        else:
            print("⚠️  API connected but no response received")
            
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        print("   Please check your API key and try again.")
        return
    
    print("\n🎉 Setup complete! You can now run:")
    print("   python job_tracker.py")
    print("   python import_and_track.py")
    print("\n💡 The system will automatically use Gemini AI for intelligent email parsing!")

if __name__ == "__main__":
    setup_gemini_api() 