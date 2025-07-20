# Google Drive Backup Setup for Streamlit Cloud

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create New Project** or select existing project
3. **Enable Google Drive API**:
   - Go to APIs & Services → Library
   - Search for "Google Drive API"
   - Click Enable

## Step 2: Create OAuth 2.0 Credentials

1. **Go to**: APIs & Services → Credentials
2. **Click**: "Create Credentials" → "OAuth 2.0 Client IDs"
3. **Application Type**: Web application
4. **Name**: `Lang Huu Nghi Backup`
5. **Authorized redirect URIs**: Add your Streamlit Cloud URL
   ```
   https://your-app-name.streamlit.app
   ```
6. **Click**: Create
7. **Download** the JSON file (contains Client ID and Secret)

## Step 3: Configure Streamlit Cloud Secrets

### 3.1 Extract Credentials from JSON
Open the downloaded JSON file and find:
```json
{
  "web": {
    "client_id": "1234567890-abcdef.apps.googleusercontent.com",
    "client_secret": "GOCSPX-your-secret-here"
  }
}
```

### 3.2 Add to Streamlit Secrets
In your Streamlit Cloud app settings, add:
```toml
# Google Drive Backup Configuration
GOOGLE_CLIENT_ID = "1234567890-abcdef.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-your-secret-here"
GOOGLE_REDIRECT_URI = "https://your-app-name.streamlit.app"
```

## Step 4: Authenticate in Your App

1. **Go to**: System Management page in your app
2. **Find**: Google Drive backup section
3. **Click**: "Lấy URL xác thực" (Get Auth URL)
4. **Copy** the generated URL
5. **Open** URL in new tab
6. **Login** to Google and grant permissions
7. **Copy** authorization code from the result page
8. **Return** to your app and paste the code
9. **Click**: "Xác thực" (Authenticate)

## Step 5: Test Backup

After successful authentication:
1. **Click**: "Sao lưu ngay" (Backup Now)
2. **Check**: Your Google Drive for "Lang Huu Nghi Database Backups" folder
3. **Verify**: Backup files are created successfully

## Important Notes

### Security
- Never share your Client Secret
- OAuth tokens are stored securely in session state
- Tokens auto-refresh when expired

### Backup Features
- ✅ Manual backup on demand
- ✅ Automatic weekly backups (Sundays 2AM)
- ✅ Maintains 10 most recent backups
- ✅ Works with both PostgreSQL (Supabase) and SQLite
- ✅ Includes metadata and SQL dumps

### Troubleshooting

**"Invalid redirect URI"**
- Ensure redirect URI in Google Console matches your Streamlit Cloud URL exactly
- Include https:// prefix

**"Client ID not found"**
- Double-check GOOGLE_CLIENT_ID in Streamlit secrets
- Ensure no extra spaces or quotes

**"Authentication failed"**
- Try clearing authentication and re-authenticating
- Check if authorization code expired (valid for ~10 minutes)

**"Backup failed"**
- Verify Google Drive API is enabled
- Check app logs for specific error messages
- Ensure sufficient Google Drive storage

Your Vietnamese management system will have reliable Google Drive backups running on Streamlit Cloud!