# How to Get Google Client ID and Client Secret

## Step 1: Access Google Cloud Console

1. **Go to**: https://console.cloud.google.com/
2. **Sign in** with your Google account
3. **Create a new project** (or select existing):
   - Click the project dropdown at the top
   - Click "New Project"
   - Name: `lang-huu-nghi-backup`
   - Click "Create"

## Step 2: Enable Google Drive API

1. **Go to**: APIs & Services → Library
2. **Search for**: "Google Drive API"
3. **Click**: Google Drive API
4. **Click**: "Enable"
5. **Wait**: For API to be enabled (30 seconds)

## Step 3: Create OAuth 2.0 Credentials

### 3.1 Configure OAuth Consent Screen
1. **Go to**: APIs & Services → OAuth consent screen
2. **Choose**: External (for public use)
3. **Fill required fields**:
   - App name: `Làng Hữu Nghị Management`
   - User support email: Your email
   - Developer contact: Your email
4. **Click**: Save and Continue
5. **Skip**: Scopes (click Save and Continue)
6. **Add test users** (your email address)
7. **Click**: Save and Continue

### 3.2 Create Credentials
1. **Go to**: APIs & Services → Credentials
2. **Click**: "+ Create Credentials"
3. **Choose**: "OAuth 2.0 Client IDs"
4. **Application type**: Web application
5. **Name**: `Lang Huu Nghi Backup Client`

### 3.3 Configure Authorized URIs
**Authorized JavaScript origins**:
```
https://your-app-name.streamlit.app
```

**Authorized redirect URIs**:
```
https://your-app-name.streamlit.app
https://your-app-name.streamlit.app/
```

Replace `your-app-name` with your actual Streamlit app name.

6. **Click**: Create

## Step 4: Get Your Credentials

After clicking Create, you'll see a popup with:

```
Client ID: 1234567890-abcdefghijklmnop.apps.googleusercontent.com
Client Secret: GOCSPX-abcdefghijklmnopqrstuvwxyz
```

**Copy both values** - you'll need them for Streamlit Cloud.

## Step 5: Add to Streamlit Cloud

1. **Go to**: Your Streamlit Cloud dashboard
2. **Find your app**: `lang-huu-nghi-management`
3. **Click**: ⋮ → Settings
4. **Go to**: Secrets tab
5. **Add these lines**:

```toml
# Your existing database secrets...
DATABASE_URL = "your-supabase-url"
# ... other database config ...

# Add these new Google Drive secrets:
GOOGLE_CLIENT_ID = "1234567890-abcdefghijklmnop.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-abcdefghijklmnopqrstuvwxyz"
GOOGLE_REDIRECT_URI = "https://your-app-name.streamlit.app"
```

6. **Click**: Save

## Step 6: Test in Your App

1. **Wait**: 2-3 minutes for Streamlit to redeploy
2. **Go to**: Your app → System Management
3. **Find**: Google Drive Backup section
4. **Click**: "Lấy URL xác thực" (Get Auth URL)
5. **Follow**: Authentication flow

## Example with Real Values

If your Streamlit app is `lang-huu-nghi.streamlit.app`, your settings would be:

**In Google Cloud Console**:
- Authorized origins: `https://lang-huu-nghi.streamlit.app`
- Redirect URIs: `https://lang-huu-nghi.streamlit.app`

**In Streamlit Secrets**:
```toml
GOOGLE_CLIENT_ID = "123456789-abc123def456.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-YourActualSecretHere"
GOOGLE_REDIRECT_URI = "https://lang-huu-nghi.streamlit.app"
```

## Troubleshooting

**"redirect_uri_mismatch" error**:
- Ensure URLs in Google Console exactly match your Streamlit app URL
- Include both with and without trailing slash

**"This app isn't verified" warning**:
- Click "Advanced" → "Go to [app name] (unsafe)" 
- This is normal for personal/testing apps

**Can't find the APIs section**:
- Make sure you've selected the correct project in the dropdown
- Try refreshing the Google Cloud Console page

Your Google Drive backup will work once these credentials are configured!