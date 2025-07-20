# Google OAuth Setup Guide - Missing Redirect URIs

## Problem
You don't see "Authorized redirect URIs" section in Google Cloud Console OAuth configuration.

## Solution
The "Authorized redirect URIs" section only appears for **Web application** type OAuth clients, not for **Desktop application** type.

### Option 1: Convert to Web Application (Recommended)
1. Go to [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials)
2. Find your OAuth 2.0 client ID
3. Click **Delete** to remove the current client
4. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client ID**
5. Choose **Application type: Web application**
6. Name it "Lang Huu Nghi Backup - Web"
7. Add these Authorized redirect URIs:
   - `http://localhost:8080/`
   - `http://localhost:8080`
   - `urn:ietf:wg:oauth:2.0:oob`
8. Click **Create**
9. Download the new credentials.json
10. Replace the old credentials.json in your project

### Option 2: Use OAuth Playground (Faster)
Since your current setup is Desktop application type, use the OAuth Playground method:

1. **Go to**: https://developers.google.com/oauthplayground/
2. **Configure credentials** (click ⚙️ settings):
   - Check ✅ "Use your own OAuth credentials"
   - Client ID: `YOUR_GOOGLE_CLIENT_ID` (get from Google Cloud Console)
   - Client Secret: `YOUR_GOOGLE_CLIENT_SECRET` (get from Google Cloud Console)
3. **Select APIs**:
   - Choose "Drive API v3" 
   - Select: `https://www.googleapis.com/auth/drive.file`
   - Click "Authorize APIs"
4. **Sign in** with your Google account and grant permissions
5. **Exchange code**: Click "Exchange authorization code for tokens"
6. **Copy tokens**: You'll get `access_token` and `refresh_token`
7. **Use in app**: Go to the backup section, click "🔧 Xác thực thủ công", expand OAuth Playground section, and paste tokens

### Option 3: Create New Web Application Client
If you want to keep the existing client:

1. Go to [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client ID** 
3. Select **Web application**
4. Add Authorized redirect URIs:
   - `http://localhost:8080/`
   - `http://localhost:8080` 
   - `urn:ietf:wg:oauth:2.0:oob`
5. Download credentials.json and update your project

## Why This Happens
- **Desktop application**: No redirect URIs needed (uses local server)
- **Web application**: Requires specific redirect URIs for security

The OAuth Playground method (Option 2) is fastest since it works with your current Desktop application setup.