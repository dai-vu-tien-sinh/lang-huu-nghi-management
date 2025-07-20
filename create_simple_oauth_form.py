#!/usr/bin/env python3
"""
Simple script to replace the complex OAuth form in the system management page
This will create a clean, no-refresh token input form
"""

def get_simple_oauth_section():
    return '''
            st.error("Google Verification Required")
            st.markdown("**Fix:** Add your email as test user in [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent)")
            st.markdown("Test users → + ADD USERS → langtrehuunghivietnam@gmail.com → Save")
            
            st.markdown("---")
            
            # Get credentials
            try:
                import json
                with open('credentials.json', 'r') as f:
                    creds = json.load(f)
                client_id = creds['web']['client_id']
                client_secret = creds['web']['client_secret']
            except:
                # Use environment variables or placeholder values
                import os
                client_id = os.getenv('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
                client_secret = os.getenv('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET')
            
            st.markdown("**OAuth Playground:** https://developers.google.com/oauthplayground/")
            st.code(f"Client ID: {client_id}")
            st.code(f"Client Secret: {client_secret}")
            
            # Simple token form
            st.markdown("**Paste tokens here:**")
            
            # Use unique keys to prevent refresh
            access_token = st.text_area("Access Token", key="oauth_access_token", height=80)
            refresh_token = st.text_area("Refresh Token", key="oauth_refresh_token", height=80)
            
            if st.button("Create token.json", key="create_token_btn"):
                if access_token.strip() and refresh_token.strip():
                    try:
                        token_data = {
                            "token": access_token.strip(),
                            "refresh_token": refresh_token.strip(), 
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "scopes": ["https://www.googleapis.com/auth/drive.file"]
                        }
                        
                        import json
                        with open('token.json', 'w') as f:
                            json.dump(token_data, f, indent=2)
                        
                        st.success("Token created! Google Drive backup ready.")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter both tokens")
    '''

if __name__ == "__main__":
    print("This generates the simple OAuth form code")
    print(get_simple_oauth_section())