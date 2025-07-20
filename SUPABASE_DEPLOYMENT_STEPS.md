# Complete Supabase Deployment Guide

## Phase 1: Create Supabase Project

### Step 1: Sign up and Create Project
1. **Go to**: https://supabase.com/dashboard
2. **Sign in** with GitHub or create account
3. **Click**: "New Project"
4. **Fill details**:
   - Organization: Choose/create organization
   - Project name: `lang-huu-nghi-management`
   - Database password: **Create strong password and save it!**
   - Region: Southeast Asia (Singapore) or closest to Vietnam
5. **Click**: "Create new project"
6. **Wait**: 2-3 minutes for project setup

### Step 2: Get Connection Details
1. **Navigate**: Settings → Database
2. **Find**: Connection string section
3. **Copy these values**:
   ```
   Host: aws-0-ap-southeast-1.pooler.supabase.com
   Database: postgres
   Port: 6543
   User: postgres.abcdefghijklmnop
   Password: [Your password from Step 1]
   ```

## Phase 2: Setup Database Schema

### Step 3: Run Migration Script
1. **Go to**: SQL Editor in Supabase dashboard
2. **Click**: "New query"
3. **Copy and paste**: The entire content from `SUPABASE_MIGRATION_SCRIPT.sql`
4. **Click**: "Run" button
5. **Verify**: Success message appears

### Step 4: Verify Tables Created
1. **Go to**: Table Editor
2. **Check**: These tables exist:
   - users (4 columns)
   - students (11 columns) 
   - veterans (13 columns)
   - medical_records (10 columns)
   - document_files (6 columns)
   - classes (5 columns)
   - student_notes (7 columns)

## Phase 3: Configure Streamlit Cloud

### Step 5: Setup Environment Variables
1. **Go to**: Your Streamlit Cloud app dashboard
2. **Click**: Three dots → Settings
3. **Navigate**: Secrets tab
4. **Add these variables** (replace with your actual values):

```toml
# Database Connection
DATABASE_URL = "postgresql://postgres.YOUR_USER_ID:YOUR_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
PGDATABASE = "postgres"
PGHOST = "aws-0-ap-southeast-1.pooler.supabase.com"
PGPORT = "6543"
PGUSER = "postgres.YOUR_USER_ID"
PGPASSWORD = "YOUR_PASSWORD"

# Optional: Google Services (for backup features)
GOOGLE_CLIENT_ID = "your-google-client-id"
GOOGLE_CLIENT_SECRET = "your-google-client-secret"

# Optional: Email notifications
SENDGRID_API_KEY = "your-sendgrid-key"

# Optional: SMS notifications  
TWILIO_ACCOUNT_SID = "your-twilio-sid"
TWILIO_AUTH_TOKEN = "your-twilio-token"
TWILIO_PHONE_NUMBER = "your-twilio-phone"
```

### Step 6: Save and Deploy
1. **Click**: "Save"
2. **Wait**: For automatic redeployment
3. **Monitor**: Deployment logs for any issues

## Phase 4: Test Your Deployment

### Step 7: Access Your App
1. **Visit**: `https://YOUR_APP_NAME.streamlit.app`
2. **Login** with sample accounts:
   - Admin: username=`admin`, password=`admin123`
   - Teacher: username=`teacher1`, password=`teacher123`
   - Doctor: username=`doctor1`, password=`doctor123`

### Step 8: Verify Functionality
Test these features:
- [ ] **Login**: All user roles work
- [ ] **Students**: View Nguyễn Văn Học, Trần Thị Mai, Lê Văn Minh
- [ ] **Veterans**: View Nguyễn Văn Cường, Phạm Thị Lan
- [ ] **Add/Edit**: Create new student record
- [ ] **Medical Records**: View and add medical data
- [ ] **Classes**: View sample classes
- [ ] **Statistics**: Charts load correctly
- [ ] **Reports**: Generate Word documents
- [ ] **File Upload**: Test document attachments

## Phase 5: Production Setup

### Step 9: Security Configuration
1. **In Supabase**: Authentication → Settings
2. **Disable**: Sign up if not needed
3. **Configure**: Password policies
4. **Setup**: Email templates (optional)

### Step 10: Backup Configuration
1. **In Supabase**: Settings → Database
2. **Enable**: Point-in-time recovery
3. **Configure**: Automated backups

## Your Live URLs

After successful deployment:
- **App**: `https://lang-huu-nghi-management.streamlit.app`
- **Database**: Supabase dashboard for admin access
- **GitHub**: `https://github.com/dai-vu-tien-sinh/lang-huu-nghi-management`

## Default Login Credentials

- **Admin**: admin / admin123
- **Teacher**: teacher1 / teacher123  
- **Doctor**: doctor1 / doctor123

## Support & Monitoring

- **Supabase**: Built-in monitoring and logs
- **Streamlit**: App health monitoring
- **Performance**: Auto-scaling included
- **Uptime**: 99.9% guaranteed by both platforms

Your Vietnamese educational management system is now production-ready with professional cloud infrastructure!