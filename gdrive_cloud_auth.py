"""
Google Drive Cloud Authentication for Streamlit Cloud
Handles OAuth authentication using environment variables instead of local files
"""

import os
import json
import streamlit as st
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
import tempfile


class CloudGoogleAuth:
    """Handle Google Drive authentication for cloud deployment"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8080')
        
    def has_credentials(self):
        """Check if environment credentials are available"""
        return bool(self.client_id and self.client_secret)
    
    def create_credentials_dict(self):
        """Create credentials dictionary for OAuth flow"""
        return {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
    
    def get_authorization_url(self):
        """Get authorization URL for OAuth flow"""
        if not self.has_credentials():
            return None
            
        # Create temporary credentials file
        creds_dict = self.create_credentials_dict()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(creds_dict, f)
            temp_creds_path = f.name
        
        try:
            flow = Flow.from_client_secrets_file(
                temp_creds_path,
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return auth_url
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_creds_path):
                os.unlink(temp_creds_path)
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        if not self.has_credentials():
            return None
            
        creds_dict = self.create_credentials_dict()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(creds_dict, f)
            temp_creds_path = f.name
        
        try:
            flow = Flow.from_client_secrets_file(
                temp_creds_path,
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=authorization_code)
            
            return flow.credentials
            
        except Exception as e:
            st.error(f"Lỗi xác thực: {str(e)}")
            return None
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_creds_path):
                os.unlink(temp_creds_path)
    
    def get_stored_credentials(self):
        """Get stored credentials from session state"""
        if 'google_credentials' in st.session_state:
            creds_data = st.session_state['google_credentials']
            
            if creds_data:
                creds = Credentials.from_authorized_user_info(creds_data, self.SCOPES)
                
                # Refresh if expired
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        # Update session state with refreshed token
                        st.session_state['google_credentials'] = {
                            'token': creds.token,
                            'refresh_token': creds.refresh_token,
                            'token_uri': creds.token_uri,
                            'client_id': creds.client_id,
                            'client_secret': creds.client_secret,
                            'scopes': creds.scopes
                        }
                    except Exception as e:
                        st.error(f"Lỗi làm mới token: {str(e)}")
                        return None
                
                return creds
        
        return None
    
    def store_credentials(self, credentials):
        """Store credentials in session state"""
        if credentials:
            st.session_state['google_credentials'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            return True
        return False
    
    def clear_credentials(self):
        """Clear stored credentials"""
        if 'google_credentials' in st.session_state:
            del st.session_state['google_credentials']
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        creds = self.get_stored_credentials()
        return creds is not None and creds.valid