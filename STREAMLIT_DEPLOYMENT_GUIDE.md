# Streamlit Cloud Deployment Guide

## Overview
Deploy your Làng Hữu Nghị management system to Streamlit Cloud for free hosting with automatic GitHub integration.

## Prerequisites
- ✅ GitHub repository: `https://github.com/dai-vu-tien-sinh/lang-huu-nghi-management`
- ✅ Supabase database configured (follow SUPABASE_DEPLOYMENT_GUIDE.md)
- ✅ Clean code without hardcoded credentials

## Step 1: Prepare Repository for Streamlit Cloud

### 1.1 Update requirements.txt
Create/update `requirements.txt` in your repository:

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
psycopg2-binary>=2.9.0
python-docx>=0.8.11
openpyxl>=3.1.0
reportlab>=4.0.0
Pillow>=10.0.0
requests>=2.31.0
python-dotenv>=1.0.0
google-api-python-client>=2.100.0
google-auth>=2.22.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
sendgrid>=6.10.0
twilio>=8.5.0
apscheduler>=3.10.0
schedule>=1.2.0
kaleido==0.2.1
anthropic>=0.3.0
```

### 1.2 Create .streamlit/config.toml
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### 1.3 Update main app file
Ensure your main file is named `Trang_chủ.py` (already done).

## Step 2: Deploy to Streamlit Cloud

### 2.1 Access Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### 2.2 Configure Deployment
1. **Repository**: `dai-vu-tien-sinh/lang-huu-nghi-management`
2. **Branch**: `main`
3. **Main file path**: `Trang_chủ.py`
4. **App URL**: Choose a custom name like `lang-huu-nghi-management`

### 2.3 Add Environment Variables
Click "Advanced settings" and add these secrets:

```
DATABASE_URL = postgresql://postgres.xxx:[PASSWORD]@aws-0-xx.pooler.supabase.com:6543/postgres
PGDATABASE = postgres
PGHOST = aws-0-xx.pooler.supabase.com
PGPORT = 6543
PGUSER = postgres.xxx
PGPASSWORD = [YOUR-SUPABASE-PASSWORD]
```

**Optional (for Google Drive backup):**
```
GOOGLE_CLIENT_ID = your-google-client-id
GOOGLE_CLIENT_SECRET = your-google-client-secret
SENDGRID_API_KEY = your-sendgrid-key
TWILIO_ACCOUNT_SID = your-twilio-sid
TWILIO_AUTH_TOKEN = your-twilio-token
TWILIO_PHONE_NUMBER = your-twilio-phone
```

### 2.4 Deploy
1. Click "Deploy!"
2. Wait for deployment (usually 2-5 minutes)
3. Your app will be available at: `https://lang-huu-nghi-management.streamlit.app`

## Step 3: Post-Deployment Configuration

### 3.1 Test Database Connection
1. Visit your deployed app
2. Try logging in with admin credentials
3. Check if students and data load correctly
4. Test creating/editing records

### 3.2 Configure Google Drive Backup (Optional)
1. Create Google Cloud project and OAuth credentials
2. Download `credentials.json` 
3. Follow the OAuth setup in your app's system management page
4. Test backup functionality

### 3.3 Set Up Custom Domain (Optional)
1. In Streamlit Cloud dashboard, go to app settings
2. Add custom domain if you have one
3. Configure DNS settings as instructed

## Step 4: Monitoring and Maintenance

### 4.1 Monitor App Health
- Check Streamlit Cloud dashboard for app status
- Monitor resource usage and performance
- Set up alerts for downtime

### 4.2 Update Application
- Push changes to GitHub repository
- Streamlit Cloud auto-deploys from `main` branch
- Monitor deployment logs for any issues

### 4.3 Database Maintenance
- Monitor Supabase dashboard for database health
- Set up automated backups in Supabase
- Monitor storage usage and performance

## Troubleshooting

### Common Issues:

**1. Module Import Errors**
- Check `requirements.txt` has all dependencies
- Verify package versions compatibility

**2. Database Connection Errors**
- Verify DATABASE_URL format and credentials
- Check Supabase project is active
- Ensure tables exist in database

**3. File Upload Issues**
- Streamlit Cloud has file size limits
- Large files may need external storage

**4. Performance Issues**
- Optimize database queries
- Use Streamlit caching (@st.cache_data)
- Consider pagination for large datasets

## Security Best Practices

- Never commit secrets to repository
- Use Streamlit Cloud secrets management
- Enable Supabase Row Level Security
- Regularly rotate database passwords
- Monitor access logs

Your Vietnamese educational management system will be live at:
`https://lang-huu-nghi-management.streamlit.app`

With automatic updates from GitHub and PostgreSQL database on Supabase!