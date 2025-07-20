# Supabase Keep-Alive Service Integration Guide

## Overview

This guide explains how to prevent your Supabase database from being paused due to inactivity. Supabase free-tier projects are paused after 7 days of inactivity, but this service will automatically keep your database active.

## ✅ What's Been Integrated

### 1. Keep-Alive Service (`supabase_keepalive.py`)
- **Purpose**: Prevents Supabase database from pausing due to inactivity
- **Method**: Makes periodic database queries and manages a small keep-alive table
- **Table**: Creates `keep_alive` table with `name` column for random strings
- **Management**: Automatically inserts/deletes entries to keep table small (max 10 entries)

### 2. API Endpoint Integration (`main.py`)
- **URL**: `https://your-replit-app.replit.app/?keep_alive=true`
- **Method**: GET request returns JSON response
- **Response**: Includes success status, timestamp, and operation messages
- **Logging**: Logs all keep-alive activities for monitoring

### 3. Setup Script (`setup_supabase_keepalive.py`)
- **Purpose**: Test and configure the keep-alive service
- **Features**: Verifies database connection, creates tables, runs test
- **Usage**: `python setup_supabase_keepalive.py`

## 🚀 Quick Start

### Step 1: Test the Service
```bash
# Run the setup script to test everything
python setup_supabase_keepalive.py
```

### Step 2: Find Your API Endpoint
Your keep-alive API endpoint is:
```
https://your-replit-app.replit.app/?keep_alive=true
```
Replace `your-replit-app` with your actual Replit app URL.

### Step 3: Test the API Endpoint
```bash
# Test with curl
curl -X GET 'https://your-replit-app.replit.app/?keep_alive=true'
```

Expected response:
```json
{
  "success": true,
  "timestamp": "2024-01-01T05:00:00",
  "messages": [
    "Queried 'randomstring' from 'keep_alive': 0 results",
    "Inserted 'randomstring' into 'keep_alive'"
  ],
  "status": "Database keep-alive completed successfully",
  "service": "Supabase Keep-Alive",
  "version": "1.0.0"
}
```

## 🕐 Setting Up External Cron Services

### Option 1: UptimeRobot (Recommended)
1. Sign up at [UptimeRobot](https://uptimerobot.com) (Free)
2. Create a new monitor:
   - **Monitor Type**: HTTP(S)
   - **Friendly Name**: Supabase Keep-Alive
   - **URL**: `https://your-replit-app.replit.app/?keep_alive=true`
   - **Monitoring Interval**: 5 minutes
3. Save and activate the monitor

### Option 2: Cron-Job.org
1. Sign up at [Cron-Job.org](https://cron-job.org) (Free)
2. Create a new cron job:
   - **URL**: `https://your-replit-app.replit.app/?keep_alive=true`
   - **Schedule**: `0 5 * * 0,3,5` (Sunday, Wednesday, Friday at 5 AM)
   - **HTTP Method**: GET
3. Save and enable the job

### Option 3: GitHub Actions
Create `.github/workflows/keep-alive.yml`:
```yaml
name: Keep Supabase Alive
on:
  schedule:
    - cron: '0 5 * * 0,3,5'  # Sunday, Wednesday, Friday at 5 AM
  workflow_dispatch:

jobs:
  keep-alive:
    runs-on: ubuntu-latest
    steps:
      - name: Ping keep-alive endpoint
        run: |
          curl -X GET 'https://your-replit-app.replit.app/?keep_alive=true'
```

## 📊 Monitoring

### Check Service Status
```bash
# Run setup script to see current status
python setup_supabase_keepalive.py
```

### Database Table Info
- **Table Name**: `keep_alive`
- **Column**: `name` (stores random strings)
- **Auto-cleanup**: Deletes oldest entries when count exceeds 10
- **Purpose**: Simulates real database activity

### Logs
- All keep-alive activities are logged to console
- Check Replit logs for service activity
- API calls are timestamped for monitoring

## ⚠️ Important Notes

### Database Usage
- Creates a `keep_alive` table in your Supabase database
- Queries count toward your Supabase usage limits
- Table is automatically managed (small footprint)
- No manual cleanup required

### Security
- No sensitive data is stored in keep-alive table
- Service only performs basic SELECT/INSERT/DELETE operations
- API endpoint is publicly accessible (by design)

### Limitations
- Free tier Supabase projects still have usage limits
- Multiple frequent pings may consume API quotas
- Service requires active Replit deployment

## 🔧 Configuration

### Customize Keep-Alive Settings
Edit `supabase_keepalive.py` to modify:
- `table_name`: Default is "keep_alive"
- `column_name`: Default is "name"
- `max_entries`: Default is 10
- `other_endpoints`: Add other services to ping

### Add Multiple Endpoints
```python
other_endpoints = [
    "https://your-other-app.vercel.app/api/keep-alive",
    "https://another-service.com/ping"
]
```

## 🐛 Troubleshooting

### Common Issues

**Error: "Database URL is required"**
- Ensure `DATABASE_URL` environment variable is set
- Check Supabase connection string format

**Error: "Table creation failed"**
- Verify database permissions
- Check if table already exists with different schema

**API endpoint returns error**
- Check if service is properly imported
- Verify database connection is active
- Test with setup script first

### Testing
```bash
# Test database connection
python -c "from supabase_keepalive import create_keep_alive_service; create_keep_alive_service().run_once()"

# Test API endpoint
curl -X GET 'https://your-replit-app.replit.app/?keep_alive=true'
```

## 📝 Success Indicators

✅ **Setup Complete When:**
- Setup script runs without errors
- API endpoint returns success response
- `keep_alive` table exists in database
- External cron service is configured

✅ **Service Working When:**
- Regular API calls return success
- Database shows periodic activity
- No pause notifications from Supabase
- Logs show successful keep-alive operations

---

## 📞 Support

If you encounter issues:
1. Run `python setup_supabase_keepalive.py` for diagnostics
2. Check database connection and permissions
3. Verify API endpoint accessibility
4. Review external cron service configuration

Your Supabase database will now stay active indefinitely! 🎉