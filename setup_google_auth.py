#!/usr/bin/env python3
"""
Simple Google Drive authentication setup for Replit environment.
This script helps users set up Google Drive authentication manually.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def setup_authentication():
    """Set up Google Drive authentication interactively"""
    
    print("🔧 Google Drive Authentication Setup")
    print("=" * 50)
    
    # Check for credentials.json
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json not found!")
        print("\nPlease follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download the JSON file and rename it to 'credentials.json'")
        print("6. Place it in the project root directory")
        return False
    
    print("✅ Found credentials.json")
    
    # Check if we already have a token
    if os.path.exists('token.json'):
        print("✅ Existing authentication found")
        
        # Verify the token
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds and creds.valid:
            print("✅ Authentication is valid and ready to use!")
            return True
        elif creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ Token refreshed successfully!")
            return True
    
    print("\n🔑 Starting new authentication...")
    
    # Create flow with correct redirect URI matching credentials.json
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = 'http://localhost'
    
    # Get the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print("\n" + "=" * 80)
    print("📋 AUTHENTICATION INSTRUCTIONS")
    print("=" * 80)
    print(f"1. Open this URL in your browser:")
    print(f"   {auth_url}")
    print("\n2. Sign in with your Google account")
    print("3. Grant permissions to the application")
    print("4. You will see a page saying 'The authentication flow has completed'")
    print("5. Copy the FULL URL from your browser's address bar")
    print("6. Paste it below when prompted")
    print("=" * 80)
    
    # Get the authorization response URL
    try:
        auth_response = input("\nPaste the full URL here: ").strip()
        
        # Extract code from URL
        if 'code=' in auth_response:
            # Parse the URL to get the code
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(auth_response)
            code = parse_qs(parsed.query).get('code', [None])[0]
            
            if code:
                # Exchange code for token
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                # Save credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                
                print("\n✅ Authentication successful!")
                print("✅ Credentials saved to token.json")
                print("✅ Google Drive backup is now ready to use!")
                return True
            else:
                print("❌ Could not extract authorization code from URL")
                return False
        else:
            print("❌ Invalid URL format. Please make sure you copied the complete URL.")
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Authentication cancelled")
        return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

if __name__ == '__main__':
    success = setup_authentication()
    if success:
        print("\n🎉 Setup complete! You can now use Google Drive backup features.")
    else:
        print("\n❌ Setup failed. Please try again or check the documentation.")