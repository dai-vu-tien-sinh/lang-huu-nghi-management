# Complete Google Drive Backup Setup for Streamlit Cloud

## Current Status
✅ **Environment Variables Configured**: You have GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET set
⏳ **OAuth Flow Required**: Need to complete one-time authentication to get access token

## Why You're Getting Authentication Errors
The backup system requires **two parts**:
1. ✅ **API Keys** (Client ID + Secret) - You have these in Streamlit Cloud
2. ⏳ **OAuth Token** - You need to complete this step

## Step-by-Step Solution

### 1. Access Your Streamlit App
Go to your deployed app: `https://your-app-name.streamlit.app`

### 2. Login and Navigate
- Login with: `admin` / `admin123`
- Go to: **Quản lý Hệ thống** (System Management)
- Find: **💾 Sao lưu Google Drive** section

### 3. Complete OAuth Flow
You should see:
```
🔧 Cần xác thực Google Drive
Google Drive Credentials đã được cấu hình, cần xác thực:
✅ Client ID và Secret đã có trong environment variables
⏳ Cần thực hiện xác thực OAuth một lần
✅ Sau đó sao lưu sẽ hoạt động tự động
```

**Follow these steps:**
1. Click **🔗 Lấy URL xác thực** (Get Auth URL)
2. Copy the generated URL
3. Open URL in new tab
4. Login to Google and grant permissions
5. Copy the authorization code from the URL
6. Paste code back in your app
7. Click **✅ Xác thực** (Authenticate)

### 4. Test Backup
After authentication:
- Click **🔄 Sao lưu ngay** (Backup Now)
- Should show: ✅ Sao lưu thành công lên Google Drive!

## Expected Error Flow

**Before OAuth (Current State):**
```
ERROR:gdrive_backup:No valid credentials found. Please authenticate first.
ERROR:gdrive_backup:Authentication failed, backup aborted
```

**After OAuth (Target State):**
```
INFO:gdrive_backup:Using cloud-based Google Drive authentication
INFO:gdrive_backup:Database backup completed successfully
```

## Troubleshooting

### If OAuth URL Generation Fails:
- Check GOOGLE_CLIENT_ID is correctly set
- Check GOOGLE_CLIENT_SECRET is correctly set
- Restart your Streamlit Cloud app

### If Authentication Code Fails:
- Make sure you copied the full code
- Check redirect URI in Google Cloud Console matches your app URL
- Try generating a new auth URL

### If Still Getting Errors:
The authentication system is working correctly - errors are normal until OAuth is completed.

## After Successful Setup

**Backup Features Available:**
- ✅ Manual backup on demand
- ✅ Automatic weekly backups (Sundays 2AM)
- ✅ View backup history
- ✅ Supabase PostgreSQL backup support

**Files Backed Up:**
- Complete database dump (SQL format)
- Student records and medical data
- User accounts and permissions
- Class and document metadata

Your Vietnamese management system will have full Google Drive backup capability once OAuth is completed!