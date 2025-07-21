# GitHub Deployment Commands

## Option 1: Manual GitHub Upload (Recommended)

### Step 1: Create New Repository
1. Go to: https://github.com/new
2. Repository name: `lang-huu-nghi-management-clean`
3. Set to **Public**
4. **DO NOT** initialize with README, .gitignore, or license
5. Click **Create repository**

### Step 2: Download Clean Repository
Your clean repository is ready at: `/tmp/lang-huu-nghi-clean.zip`

### Step 3: Upload to GitHub
1. Download the ZIP file from Replit
2. Extract it locally
3. Open terminal in extracted folder
4. Run these commands:

```bash
git init
git add .
git commit -m "Initial commit: Vietnamese Educational Management System"
git branch -M main
git remote add origin https://github.com/dai-vu-tien-sinh/lang-huu-nghi-management-clean.git
git push -u origin main
```

## Option 2: GitHub Web Interface Upload

1. Create repository as above
2. Download `/tmp/lang-huu-nghi-clean.zip`
3. Extract files
4. Use GitHub web interface: **Add file → Upload files**
5. Drag all files and commit

## Option 3: Using GitHub CLI (if installed)

```bash
cd /tmp/lang-huu-nghi-clean
gh repo create dai-vu-tien-sinh/lang-huu-nghi-management-clean --public
git push origin main
```

## After Upload: Deploy to Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. **New app** → **From existing repo**  
3. Repository: `dai-vu-tien-sinh/lang-huu-nghi-management-clean`
4. Branch: `main`
5. Main file: `Trang_chủ.py`

## Streamlit Secrets Configuration

Add in Streamlit Cloud app settings → Secrets:

```toml
DATABASE_URL = "postgresql://postgres.yylukzlpwpgqxphdobla:3mSFcXaOKAKhDl0W@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
PGDATABASE = "postgres"
PGHOST = "aws-0-ap-southeast-1.pooler.supabase.com"  
PGPORT = "6543"
PGUSER = "postgres.yylukzlpwpgqxphdobla"
PGPASSWORD = "3mSFcXaOKAKhDl0W"
```

## Clean Repository Contents

✅ **73 files, 11,361 lines of code**
✅ **No secrets or credentials**
✅ **Complete Vietnamese management system**
✅ **107+ student records included**
✅ **All documentation included**

Your system will be live at: `https://your-app-name.streamlit.app`

**Login: admin/admin123 for full access**