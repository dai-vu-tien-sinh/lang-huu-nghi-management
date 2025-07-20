#!/usr/bin/env python3
"""
Setup script for Supabase Keep-Alive service
This script will help you configure the keep-alive service for your Supabase database
"""

import os
import sys
from supabase_keepalive import create_keep_alive_service

def main():
    print("🔄 Supabase Keep-Alive Service Setup")
    print("=" * 50)
    
    # Check if DATABASE_URL exists
    if not os.environ.get('DATABASE_URL'):
        print("❌ ERROR: DATABASE_URL environment variable not found!")
        print("Please set your Supabase database URL in the environment variables.")
        sys.exit(1)
    
    print("✅ DATABASE_URL found")
    
    try:
        # Create keep-alive service
        print("\n🔧 Creating keep-alive service...")
        keep_alive = create_keep_alive_service()
        
        # Test the service
        print("🧪 Testing keep-alive service...")
        success, messages = keep_alive.run_once()
        
        if success:
            print("✅ Keep-alive service test PASSED!")
            print("\n📋 Test Results:")
            for message in messages:
                print(f"  • {message}")
        else:
            print("❌ Keep-alive service test FAILED!")
            print("\n📋 Error Messages:")
            for message in messages:
                print(f"  • {message}")
            sys.exit(1)
        
        # Display setup information
        print("\n" + "=" * 50)
        print("🎉 SETUP COMPLETE!")
        print("=" * 50)
        
        print("\n📡 API Endpoint:")
        print("Your keep-alive API endpoint is:")
        print("https://your-replit-app.replit.app/?keep_alive=true")
        print("(Replace 'your-replit-app' with your actual Replit app URL)")
        
        print("\n🕐 Recommended External Cron Services:")
        print("1. **UptimeRobot** (Free): https://uptimerobot.com")
        print("   - Set up HTTP monitoring")
        print("   - Check interval: Every 5 minutes")
        print("   - URL: Your API endpoint")
        
        print("\n2. **Cron-Job.org** (Free): https://cron-job.org")
        print("   - Create a cron job")
        print("   - Schedule: '0 5 * * 0,3,5' (Sunday, Wednesday, Friday at 5 AM)")
        print("   - URL: Your API endpoint")
        
        print("\n3. **GitHub Actions** (Free):")
        print("   - Create a workflow that runs on schedule")
        print("   - Use 'curl' to ping your endpoint")
        
        print("\n📊 Database Table Info:")
        print(f"  • Table: keep_alive")
        print(f"  • Column: name")
        print(f"  • Current entries: {keep_alive.get_entry_count()}")
        print(f"  • Max entries before cleanup: {keep_alive.max_entries}")
        
        print("\n⚠️  Important Notes:")
        print("  • The service creates a 'keep_alive' table in your database")
        print("  • It automatically manages entries to keep the table small")
        print("  • Database queries count toward your Supabase usage limits")
        print("  • Free tier projects pause after 7 days of inactivity")
        
        print("\n🔍 To test the API endpoint:")
        print("curl -X GET 'https://your-replit-app.replit.app/?keep_alive=true'")
        
    except Exception as e:
        print(f"❌ SETUP FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()