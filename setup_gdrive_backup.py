#!/usr/bin/env python3
"""
Quick setup helper for Google Drive backup system
Run this script to verify your credentials and test the backup system
"""

import os
import sys
import json
from pathlib import Path

def check_credentials():
    """Check if credentials.json exists and is valid"""
    print("🔍 Checking credentials...")
    
    if not os.path.exists('credentials.json'):
        print("❌ File credentials.json not found!")
        print("📋 Please follow the setup guide in GDRIVE_BACKUP_SETUP.md")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        required_keys = ['installed', 'client_id', 'client_secret']
        if 'installed' in creds:
            client_info = creds['installed']
            if all(key in client_info for key in ['client_id', 'client_secret']):
                print("✅ credentials.json is valid!")
                return True
        
        print("❌ credentials.json format is incorrect!")
        print("📋 Please re-download from Google Cloud Console")
        return False
        
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check actual module imports
    required_imports = [
        ('googleapiclient', 'google-api-python-client'),
        ('google.auth', 'google-auth'),
        ('google_auth_oauthlib', 'google-auth-oauthlib')
    ]
    
    missing_packages = []
    for module_name, package_name in required_imports:
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed!")
    return True

def test_backup_system():
    """Test the backup system"""
    print("🧪 Testing backup system...")
    
    try:
        # Import backup functions
        from gdrive_backup import GoogleDriveBackup
        
        # Create backup instance
        print("🔐 Testing Google Drive authentication...")
        backup = GoogleDriveBackup()
        
        if backup.authenticate():
            print("✅ Google Drive authentication successful!")
        else:
            print("❌ Google Drive authentication failed!")
            return False
        
        # Test folder creation
        print("📁 Testing backup folder creation...")
        if backup.create_backup_folder():
            print("✅ Backup folder created/found successfully!")
            print(f"📂 Folder ID: {backup.backup_folder_id}")
        else:
            print("❌ Failed to create backup folder!")
            return False
        
        print("🎉 Backup system is ready!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📋 Make sure gdrive_backup.py exists")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup verification"""
    print("🚀 Google Drive Backup Setup Verification")
    print("=" * 50)
    
    # Check credentials
    if not check_credentials():
        return False
    
    # Check dependencies  
    if not check_dependencies():
        return False
    
    # Test backup system
    if not test_backup_system():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("📋 You can now use the backup system in your application")
    print("💡 Go to 'Quản lý Hệ thống' → 'Sao lưu & Khôi phục' to start backing up")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup verification failed!")
        print("📋 Please check the issues above and try again")
        sys.exit(1)
    sys.exit(0)