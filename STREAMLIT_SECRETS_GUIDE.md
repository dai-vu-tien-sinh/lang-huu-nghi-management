# Streamlit Cloud Secrets Setup Guide

## Step 1: Get Your Supabase Connection Details

1. **Go to your Supabase project dashboard**
2. **Navigate**: Settings → Database
3. **Find**: Connection string section
4. **Copy these values**:

```
Host: aws-0-ap-southeast-1.pooler.supabase.com
Database name: postgres
Port: 6543
User: postgres.abcdefghijklmnop
Password: [your-password-from-setup]
```

## Step 2: Configure Streamlit Cloud Secrets

1. **Go to**: https://share.streamlit.io/
2. **Find your app**: `lang-huu-nghi-management`
3. **Click**: Three dots (⋮) → Settings
4. **Navigate**: Secrets tab

## Step 3: Add Your Database Configuration

**Copy this template and replace with your actual values:**

```toml
# Database connection - REQUIRED
DATABASE_URL = "postgresql://postgres.YOUR_USER_ID:YOUR_PASSWORD@YOUR_HOST.supabase.co:6543/postgres"
PGDATABASE = "postgres"
PGHOST = "YOUR_HOST.supabase.co"
PGPORT = "6543"
PGUSER = "postgres.YOUR_USER_ID"
PGPASSWORD = "YOUR_PASSWORD"
```

## Step 4: Real Example

If your Supabase shows:
- Host: `aws-0-ap-southeast-1.pooler.supabase.com`
- User: `postgres.abcdefghijklmnop`
- Password: `MySecurePass123`

Then paste this:

```toml
DATABASE_URL = "postgresql://postgres.abcdefghijklmnop:MySecurePass123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
PGDATABASE = "postgres"
PGHOST = "aws-0-ap-southeast-1.pooler.supabase.com"
PGPORT = "6543"
PGUSER = "postgres.abcdefghijklmnop"
PGPASSWORD = "MySecurePass123"
```

## Step 5: Save and Deploy

1. **Click**: "Save"
2. **Wait**: 2-3 minutes for automatic redeployment
3. **Visit**: Your app URL
4. **Test**: Login with admin/admin123

## Optional Services (Add if Needed)

```toml
# Google services for backup (optional)
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"

# Email notifications (optional)
SENDGRID_API_KEY = "SG.your-sendgrid-key"

# SMS notifications (optional)
TWILIO_ACCOUNT_SID = "ACyour-account-sid"
TWILIO_AUTH_TOKEN = "your-auth-token"
TWILIO_PHONE_NUMBER = "+1234567890"
```

## Troubleshooting

### App Won't Start
- Check DATABASE_URL format is correct
- Verify password doesn't contain special characters
- Ensure all environment variables are set

### Connection Errors
- Confirm Supabase project is active (not paused)
- Double-check host, user, and password values
- Make sure database tables exist (run migration script)

### Authentication Issues
- Verify admin user exists in users table
- Check user credentials: admin/admin123
- Confirm role permissions are set correctly

Your Vietnamese management system will be live once the secrets are configured!