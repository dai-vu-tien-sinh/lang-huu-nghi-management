
#!/usr/bin/env python3
"""
Manual Supabase Keep-Alive Trigger
Run this script to manually keep your Supabase database active
"""

import os
from supabase_keepalive import SupabaseKeepAlive

def main():
    print("🔄 Starting Supabase Keep-Alive...")
    
    try:
        # Create keep-alive service
        keep_alive = SupabaseKeepAlive()
        
        # Run keep-alive once
        success, messages = keep_alive.run_keep_alive()
        
        print("\n📊 Keep-Alive Results:")
        print("=" * 50)
        
        for message in messages:
            print(f"✓ {message}")
        
        print("=" * 50)
        
        if success:
            print("✅ Keep-alive completed successfully!")
        else:
            print("❌ Keep-alive failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Make sure your DATABASE_URL environment variable is set")
        print("   You can set it in Replit Secrets or .env file")

if __name__ == "__main__":
    main()
