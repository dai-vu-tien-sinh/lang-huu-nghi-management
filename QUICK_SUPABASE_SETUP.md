# Quick 10-Minute Supabase Setup

## 🚀 Fast Track Deployment

### 1. Create Supabase Project (2 minutes)
- Go to: https://supabase.com/dashboard  
- New Project → Name: `lang-huu-nghi-management`
- Set strong database password (save it!)
- Region: Southeast Asia
- Click Create

### 2. Setup Database (3 minutes)
- Go to SQL Editor
- Copy entire `SUPABASE_MIGRATION_SCRIPT.sql` content
- Paste and click Run
- Verify success message

### 3. Get Connection Details (1 minute)
- Settings → Database → Connection string
- Copy the URI format connection string
- Note: Host, User, Password

### 4. Configure Streamlit Cloud (3 minutes)
- Go to your Streamlit app settings
- Secrets tab → Add these (replace with your values):

```toml
DATABASE_URL = "postgresql://postgres.YOUR_USER:YOUR_PASS@YOUR_HOST:6543/postgres"
PGDATABASE = "postgres"  
PGHOST = "YOUR_HOST"
PGPORT = "6543"
PGUSER = "postgres.YOUR_USER"
PGPASSWORD = "YOUR_PASS"
```

### 5. Test App (1 minute)
- Save secrets → Auto redeploys
- Visit your Streamlit app URL
- Login: admin / admin123
- Verify student data loads

## ✅ Success Indicators

- Supabase shows 7 tables created
- Streamlit app loads Vietnamese interface  
- Student "Nguyễn Văn Học" appears in data
- No database connection errors

Your production system is live!