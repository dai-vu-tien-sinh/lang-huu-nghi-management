# Security Fix: Removed Google OAuth Credentials

## Issue Fixed
GitHub blocked the push because Google OAuth credentials were hardcoded in the source code. This is a security violation.

## Changes Made
✅ Removed hardcoded Google Client ID and Client Secret from:
- `create_simple_oauth_form.py`
- `pages/01_Quản_lý_Hệ_thống.py`
- `GOOGLE_OAUTH_SETUP.md`

✅ Replaced with environment variables and placeholders:
- `GOOGLE_CLIENT_ID` environment variable
- `GOOGLE_CLIENT_SECRET` environment variable

## How to Setup Google OAuth (Post-Deployment)

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Google Drive API

### 2. Create OAuth Credentials
1. Go to APIs & Services > Credentials
2. Create OAuth 2.0 Client ID (Web Application type)
3. Add authorized redirect URIs:
   - `http://localhost:8080/`
   - `https://your-deployment-url.replit.app/`

### 3. Set Environment Variables
In your deployment environment, set:
```bash
export GOOGLE_CLIENT_ID="your-actual-client-id"
export GOOGLE_CLIENT_SECRET="your-actual-client-secret"
```

### 4. Download credentials.json
- Download the credentials file from Google Cloud Console
- Place it in your project root as `credentials.json`
- Add `credentials.json` to `.gitignore` (already done)

## Push to GitHub
Now you can safely push to GitHub:

```bash
git add .
git commit -m "Security fix: Remove hardcoded OAuth credentials

- Replace Google OAuth credentials with environment variables
- Use placeholders for sensitive data
- Add security documentation
- Ready for secure deployment"

git push origin main --force
```

The repository will now pass GitHub's security scan and can be safely deployed.