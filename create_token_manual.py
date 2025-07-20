#!/usr/bin/env python3
"""
Manual token creation script for Desktop OAuth clients.
This bypasses OAuth Playground and works directly with Desktop application type.
"""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def create_token_manually():
    """Create token.json using Desktop application flow"""
    
    print("🔧 Manual Token Creation for Desktop OAuth Client")
    print("=" * 60)
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        return False
    
    # Load credentials
    with open('credentials.json', 'r') as f:
        creds_data = json.load(f)
    
    client_id = creds_data['installed']['client_id']
    
    print(f"✅ Found Desktop OAuth Client: {client_id[:20]}...")
    print("\n🚀 Starting authentication flow...")
    print("\n" + "=" * 60)
    print("📋 INSTRUCTIONS:")
    print("1. A browser window will open automatically")
    print("2. Sign in with your Google account") 
    print("3. Click 'Allow' to grant permissions")
    print("4. You'll see 'The authentication flow has completed'")
    print("5. You can close the browser window")
    print("6. Token will be saved automatically")
    print("=" * 60)
    
    input("\nPress ENTER to start the authentication flow...")
    
    try:
        # Create flow for Desktop application
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        
        # Run local server flow (works for Desktop apps)
        creds = flow.run_local_server(
            port=8080,
            open_browser=True,
            success_message='✅ Authentication successful! You can close this window.',
            failure_message='❌ Authentication failed. Please try again.'
        )
        
        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("\n✅ Success!")
        print("✅ token.json has been created")
        print("✅ Google Drive backup is now ready!")
        print("\n🔄 You can now use the backup feature in the web interface.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Alternative solutions:")
        print("1. Try running this on a local computer with browser access")
        print("2. Use the OAuth Playground method with Web application type client")
        print("3. Create a new Web application OAuth client in Google Cloud Console")
        
        return False

if __name__ == "__main__":
    create_token_manually()