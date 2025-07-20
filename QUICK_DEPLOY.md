# Quick Supabase Deployment Guide

## 🚀 Deploy in 15 Minutes

### Step 1: Create Supabase Project (3 min)
1. Visit [supabase.com](https://supabase.com) → Sign up/Login
2. Click "New Project"
3. Name: `lang-huu-nghi-management`
4. Region: Singapore (closest to Vietnam)
5. Set database password (save it!)
6. Click "Create new project"

### Step 2: Setup Database (2 min)
1. Once project loads → SQL Editor
2. Click "New query"
3. Copy entire content from `supabase_schema.sql`
4. Paste and click "Run"

### Step 3: Get Connection String (1 min)
1. Settings → Database
2. Copy "Transaction pooler" connection string
3. Replace `[YOUR-PASSWORD]` with your actual password
4. Format: `postgresql://postgres.xxx:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres`

### Step 4: Upload to GitHub (5 min)
1. Create GitHub repository: `lang-huu-nghi-management`
2. Upload these essential files:
   - `streamlit_app.py` (entry point)
   - All `.py` files from your project
   - `pages/` folder (entire folder)
   - `.streamlit/config.toml`
   - `packages.txt`
   - Rename `streamlit_requirements.txt` to `requirements.txt`

### Step 5: Deploy on Streamlit Cloud (4 min)
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub account
3. Select your repository
4. Main file: `streamlit_app.py`
5. Advanced settings → Secrets:
   ```
   DATABASE_URL = "your_complete_supabase_connection_string"
   ```
6. Click "Deploy"

### Step 6: Test (1 min)
- Login: `admin` / `admin123`
- Verify all features work
- Check database connectivity

## Your App Features Ready:
- Role-based access control (6 user types)
- Vietnamese/English support
- Student & veteran management
- Medical & psychological records
- Search, analytics, export capabilities
- Mobile-responsive design

## Live URL
After deployment, your app will be available at:
`https://your-app-name.streamlit.app`

Need help? Check the detailed `DEPLOYMENT_GUIDE.md` file.