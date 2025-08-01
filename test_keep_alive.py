
#!/usr/bin/env python3
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase_keepalive import SupabaseKeepAlive
    
    print("🔄 Testing Supabase Keep-Alive...")
    
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

print("\n🌐 You can also test the web endpoint:")
print("Visit: http://0.0.0.0:5000?keep_alive=true")
