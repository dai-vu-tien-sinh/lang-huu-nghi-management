#!/usr/bin/env python3
"""
Alternative Google Drive authentication setup for environments where the standard flow doesn't work.
This script provides manual token generation instructions.
"""

import json
import os

def fix_google_oauth():
    """Provide manual instructions for Google OAuth setup"""
    
    print("🔧 Google Drive Authentication Fix")
    print("=" * 60)
    
    # Check credentials
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        return False
    
    with open('credentials.json', 'r') as f:
        creds = json.load(f)
    
    client_id = creds['installed']['client_id']
    
    print("The current OAuth setup is having redirect URI issues.")
    print("Here's how to fix it manually:")
    print()
    print("OPTION 1: Update Google Cloud Console Settings")
    print("=" * 50)
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print(f"2. Find your OAuth 2.0 client (ID: {client_id})")
    print("3. Click 'Edit' on your OAuth client")
    print("4. In 'Authorized redirect URIs', add these URLs:")
    print("   - http://localhost:8080/")
    print("   - http://localhost:8080")  
    print("   - urn:ietf:wg:oauth:2.0:oob")
    print("5. Save the changes")
    print("6. Download the updated credentials.json")
    print("7. Replace the existing credentials.json with the new one")
    print("8. Run: python setup_google_auth.py")
    print()
    
    print("OPTION 2: Use OAuth Playground (Advanced)")
    print("=" * 50)
    print("1. Go to: https://developers.google.com/oauthplayground/")
    print("2. Click the settings gear in top-right")
    print("3. Check 'Use your own OAuth credentials'")
    print(f"4. Enter Client ID: {client_id}")
    print(f"5. Enter Client Secret: {creds['installed']['client_secret']}")
    print("6. In Step 1, select 'Drive API v3' and scope:")
    print("   https://www.googleapis.com/auth/drive.file")
    print("7. Click 'Authorize APIs'")
    print("8. Complete Google sign-in")
    print("9. In Step 2, click 'Exchange authorization code for tokens'")
    print("10. Copy the refresh_token and access_token")
    print("11. Create token.json manually with this format:")
    print()
    
    token_format = {
        "token": "YOUR_ACCESS_TOKEN",
        "refresh_token": "YOUR_REFRESH_TOKEN", 
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": client_id,
        "client_secret": creds['installed']['client_secret'],
        "scopes": ["https://www.googleapis.com/auth/drive.file"]
    }
    
    print(json.dumps(token_format, indent=2))
    print()
    print("OPTION 3: Simplified Manual Setup")
    print("=" * 50)
    print("If both options above are too complex, you can:")
    print("1. Use a local computer with proper browser access")
    print("2. Run the same authentication script there")
    print("3. Copy the generated token.json file to this project")
    print()
    
    return True

if __name__ == "__main__":
    fix_google_oauth()