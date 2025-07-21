#!/usr/bin/env python3
"""
Script to enable Google Drive API and test Service Account
"""
import os
import json
import subprocess
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def enable_drive_api():
    """Enable Google Drive API for the project"""
    print("🔧 Enabling Google Drive API...")
    
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        print("❌ GOOGLE_SERVICE_ACCOUNT_JSON not found")
        return False
        
    try:
        credentials_info = json.loads(service_account_json)
        project_id = credentials_info.get('project_id')
        
        print(f"📋 Project ID: {project_id}")
        
        # Use gcloud to enable the API
        enable_cmd = f"gcloud services enable drive.googleapis.com --project={project_id}"
        print(f"🔧 Running: {enable_cmd}")
        
        # Alternative: Use the Service Usage API to enable Drive API
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/service.management']
        )
        
        # Build Service Usage API client
        service_usage = build('serviceusage', 'v1', credentials=credentials)
        
        # Enable Google Drive API
        service_name = f"projects/{project_id}/services/drive.googleapis.com"
        
        try:
            operation = service_usage.services().enable(name=service_name).execute()
            print(f"✅ API enable operation started: {operation.get('name', 'Unknown')}")
            return True
        except HttpError as e:
            if e.resp.status == 403:
                print("❌ Insufficient permissions to enable API programmatically")
                print("💡 Please enable manually in Google Cloud Console:")
                print(f"   1. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com?project={project_id}")
                print("   2. Click 'ENABLE'")
                return False
            else:
                print(f"❌ Error enabling API: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to enable API: {e}")
        return False

def test_drive_access():
    """Test Google Drive API access"""
    print("\n🧪 Testing Google Drive API access...")
    
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        return False
        
    try:
        credentials_info = json.loads(service_account_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        # Test basic API access
        about = service.about().get(fields="user").execute()
        user_email = about.get('user', {}).get('emailAddress', 'Service Account')
        print(f"✅ Authenticated as: {user_email}")
        
        # Test file listing
        results = service.files().list(pageSize=1).execute()
        print("✅ Drive API working correctly")
        
        return True
        
    except HttpError as e:
        if e.resp.status == 403:
            print("❌ Google Drive API not enabled")
            return False
        else:
            print(f"❌ API Error: {e}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Google Drive API Setup and Test")
    print("=" * 50)
    
    # Try to enable API
    api_enabled = enable_drive_api()
    
    # Test access
    access_working = test_drive_access()
    
    if access_working:
        print("\n🎉 SUCCESS: Google Drive API is working!")
        print("   Your backup system should work now.")
    else:
        print("\n⚠️ ACTION REQUIRED:")
        print("   1. Go to Google Cloud Console")
        print("   2. Navigate to APIs & Services → Library")
        print("   3. Search 'Google Drive API'")
        print("   4. Click 'ENABLE'")
        print("   5. Wait 1-2 minutes for propagation")