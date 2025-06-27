#!/usr/bin/env python3
"""
Setup script for JobAppsMailTracker
Helps with initial project setup and dependency installation
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python 3.7 or higher is required")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    return run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def create_virtual_environment():
    """Create a virtual environment"""
    if os.path.exists("venv"):
        print("✓ Virtual environment already exists")
        return True
    
    return run_command(
        "python -m venv venv",
        "Creating virtual environment"
    )

def check_credentials():
    """Check if credentials.json exists"""
    if os.path.exists("credentials.json"):
        print("✓ credentials.json found")
        return True
    else:
        print("✗ credentials.json not found")
        print("  Please download your OAuth 2.0 credentials from Google Cloud Console")
        print("  and save them as 'credentials.json' in the project root directory")
        return False

def main():
    """Main setup function"""
    print("=== JobAppsMailTracker Setup ===\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\nPlease create a virtual environment manually:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\nPlease install dependencies manually:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Check credentials
    if not check_credentials():
        print("\nSetup incomplete. Please:")
        print("1. Go to Google Cloud Console")
        print("2. Enable Gmail API and Google Sheets API")
        print("3. Create OAuth 2.0 credentials for Desktop Application")
        print("4. Download credentials.json and place in project root")
        sys.exit(1)
    
    print("\n=== Setup Complete! ===")
    print("\nNext steps:")
    print("1. Activate your virtual environment:")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("2. Create a Gmail label called 'Job Applications'")
    print("3. Apply this label to job-related emails")
    print("4. Run the tracker:")
    print("   python job_tracker.py")
    print("\nFor detailed instructions, see README.md")

if __name__ == "__main__":
    main() 