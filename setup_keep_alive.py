
#!/usr/bin/env python3
"""
Supabase Keep-Alive Setup and Test
Sets up automatic keep-alive scheduling
"""

import os
import time
from threading import Thread
from supabase_keepalive import SupabaseKeepAlive

def start_keep_alive_scheduler():
    """Start the keep-alive scheduler in background"""
    try:
        print("🚀 Starting Supabase Keep-Alive Scheduler...")
        
        keep_alive = SupabaseKeepAlive()
        
        # Test connection first
        print("🔍 Testing database connection...")
        success, messages = keep_alive.run_keep_alive()
        
        if success:
            print("✅ Database connection successful!")
            print("⏰ Starting automatic scheduler...")
            
            # Start scheduler in background thread
            scheduler_thread = Thread(target=keep_alive.start_scheduled_task, daemon=True)
            scheduler_thread.start()
            
            print("🎯 Scheduler started! Keep-alive will run:")
            print("   - Sunday at 5:00 AM")
            print("   - Wednesday at 5:00 AM") 
            print("   - Friday at 5:00 AM")
            
            return True
        else:
            print("❌ Database connection failed!")
            for message in messages:
                print(f"   {message}")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return False

def test_keep_alive_endpoint():
    """Test the keep-alive endpoint"""
    import requests
    
    try:
        # Get the current app URL
        base_url = "http://0.0.0.0:5000"  # Local development
        endpoint = f"{base_url}?keep_alive=true"
        
        print(f"🌐 Testing keep-alive endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=30)
        
        if response.status_code == 200:
            print("✅ Keep-alive endpoint is working!")
            return True
        else:
            print(f"❌ Endpoint returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Endpoint test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Supabase Keep-Alive Setup")
    print("=" * 40)
    
    # Check environment
    if not os.environ.get('DATABASE_URL'):
        print("⚠️  DATABASE_URL not found in environment variables")
        print("   Please set it in Replit Secrets or your .env file")
        exit(1)
    
    # Test keep-alive
    print("\n1️⃣ Testing Keep-Alive Service...")
    if start_keep_alive_scheduler():
        print("\n2️⃣ Testing Web Endpoint...")
        test_keep_alive_endpoint()
        
        print("\n✅ Setup complete!")
        print("💡 Your Supabase database will stay active automatically")
        
        # Keep the script running to maintain scheduler
        print("\n⏳ Keeping scheduler alive... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Keep-alive scheduler stopped")
    else:
        print("\n❌ Setup failed - please check your configuration")
