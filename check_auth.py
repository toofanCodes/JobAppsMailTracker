#!/usr/bin/env python3
"""
Check current authorization and help change authorized email
"""

import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def check_current_auth():
    """Check which email is currently authorized"""
    token_file = 'token.json'
    
    if not os.path.exists(token_file):
        print("❌ No token.json found - no email is currently authorized")
        return None
    
    try:
        # Load credentials
        creds = Credentials.from_authorized_user_file(token_file, [
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/spreadsheets"
        ])
        
        if not creds or not creds.valid:
            print("❌ Token is invalid or expired")
            return None
        
        # Get user info from Gmail API
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        email = profile.get('emailAddress', 'Unknown')
        print(f"✅ Currently authorized email: {email}")
        return email
        
    except Exception as e:
        print(f"❌ Error checking authorization: {e}")
        return None

def show_change_options():
    """Show options for changing authorized email"""
    print("\n" + "="*50)
    print("CHANGING AUTHORIZED EMAIL")
    print("="*50)
    
    print("\n📧 Option 1: Same Google Account, Different Email")
    print("   If you want to use a different email from the same Google account:")
    print("   1. Delete token.json: rm token.json")
    print("   2. Run: python job_tracker.py")
    print("   3. When browser opens, log in with the different email")
    
    print("\n🔄 Option 2: Completely Different Google Account")
    print("   If you want to use a completely different Google account:")
    print("   1. Delete all auth files:")
    print("      rm token.json auth_state.json")
    print("   2. Add the new email as a test user in Google Cloud Console")
    print("   3. Run: python job_tracker.py")
    print("   4. Authenticate with the new account")
    
    print("\n🔧 Option 3: Manual Token Management")
    print("   For advanced users who want to manage tokens manually:")
    print("   1. Delete token.json")
    print("   2. Edit config.json if needed")
    print("   3. Run authentication flow manually")
    
    print("\n⚠️  Important Notes:")
    print("   - Make sure the new email is added as a test user in Google Cloud Console")
    print("   - The script will create a new spreadsheet for the new account")
    print("   - Old authorization data will be preserved in auth_log.jsonl")

def main():
    """Main function"""
    print("🔍 Checking current authorization...")
    
    current_email = check_current_auth()
    
    if current_email:
        print(f"\nCurrent setup is working for: {current_email}")
        response = input("\nDo you want to change the authorized email? (y/n): ").lower()
        
        if response == 'y':
            show_change_options()
        else:
            print("No changes made. Current authorization remains active.")
    else:
        print("\nNo valid authorization found.")
        show_change_options()

if __name__ == "__main__":
    main() 