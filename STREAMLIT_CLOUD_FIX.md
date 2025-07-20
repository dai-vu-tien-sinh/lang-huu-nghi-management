# Streamlit Cloud Port Configuration Fix

## Issue Detected
Streamlit Cloud is looking for the app on port 8501 (default), but the configuration was set to port 5000 (Replit-specific).

## Fix Applied
Updated `.streamlit/config.toml`:
- Removed `address = "0.0.0.0"` (not needed for cloud)
- Changed `port = 5000` to `port = 8501` (Streamlit Cloud default)
- Simplified configuration for cloud deployment

## Expected Result
The Streamlit Cloud deployment should now properly connect to your app and complete the health check.

## Next Steps for Deployment

### 1. Push Updated Configuration to GitHub
```bash
git add .streamlit/config.toml
git commit -m "Fix Streamlit Cloud port configuration"
git push origin main
```

### 2. Streamlit Cloud Will Auto-Redeploy
- Streamlit Cloud monitors your GitHub repository
- It will automatically redeploy with the updated configuration
- The health check should now pass

### 3. Database Configuration
After successful deployment, ensure these environment variables are set in Streamlit Cloud:

**Required for database connection:**
```
DATABASE_URL = postgresql://postgres.xxx:[PASSWORD]@aws-0-xx.pooler.supabase.com:6543/postgres
PGDATABASE = postgres
PGHOST = aws-0-xx.pooler.supabase.com
PGPORT = 6543
PGUSER = postgres.xxx
PGPASSWORD = [YOUR-SUPABASE-PASSWORD]
```

### 4. Test Deployment
Once redeployed:
- Access your app at the Streamlit Cloud URL
- Test login with admin/admin123
- Verify database connection and data loading
- Test core functionality (student management, reports)

The configuration is now optimized for Streamlit Cloud hosting.