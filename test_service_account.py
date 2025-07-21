#!/usr/bin/env python3
"""
Test script to validate Google Service Account configuration
"""
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_service_account():
    """Test Google Service Account authentication and permissions"""
    print("🔍 Testing Google Service Account configuration...")
    
    # Get Service Account JSON from environment
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if not service_account_json:
        print("❌ GOOGLE_SERVICE_ACCOUNT_JSON not found in environment")
        return False
    
    try:
        # Parse JSON
        credentials_info = json.loads(service_account_json)
        print(f"✅ JSON format valid")
        print(f"   Project: {credentials_info.get('project_id')}")
        print(f"   Email: {credentials_info.get('client_email')}")
        
        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, 
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        print("✅ Credentials created successfully")
        
        # Build Drive service
        service = build('drive', 'v3', credentials=credentials)
        print("✅ Google Drive service built successfully")
        
        # Test API access
        try:
            about = service.about().get(fields="user").execute()
            user_email = about.get('user', {}).get('emailAddress', 'Unknown')
            print(f"✅ API access successful - authenticated as: {user_email}")
            
            # Try to list files (should work even if empty)
            results = service.files().list(pageSize=1, fields="files(id, name)").execute()
            print(f"✅ Drive API working - can access files")
            
            return True
            
        except HttpError as e:
            if e.resp.status == 403:
                print("❌ Google Drive API not enabled or insufficient permissions")
                print("   Solution: Enable Google Drive API in Google Cloud Console")
                print("   Go to: APIs & Services → Library → Google Drive API → Enable")
            else:
                print(f"❌ API Error: {e}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    success = test_service_account()
    if success:
        print("\n🎉 Service Account configuration is working perfectly!")
        print("   Google Drive backup should work now.")
    else:
        print("\n🔧 Service Account needs configuration fixes.")
        print("   Check the error messages above for solutions.")