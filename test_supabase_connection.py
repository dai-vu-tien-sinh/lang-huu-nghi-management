#!/usr/bin/env python3
"""
Test Supabase Connection and Keep-Alive
"""

import os
import sys
from datetime import datetime

def test_database_connection():
    """Test the database connection"""
    print("🔍 Testing Supabase Connection...")
    print("=" * 50)
    
    # Check environment variables
    database_url = os.environ.get('DATABASE_URL')
    print(f"DATABASE_URL set: {'✅ Yes' if database_url else '❌ No'}")
    
    if not database_url:
        print("\n⚠️  DATABASE_URL not found!")
        print("   Please set it in Replit Secrets:")
        print("   Key: DATABASE_URL")
        print("   Value: postgresql://postgres:[YOUR-PASSWORD]@db.yylukzlpwpgqxphdobla.supabase.co:5432/postgres")
        return False
    
    # Check psycopg2 dependency
    try:
        import psycopg2
        print("✅ psycopg2 is installed")
    except ImportError:
        print("❌ psycopg2 not installed")
        print("   Run: pip install psycopg2-binary")
        return False
    
    # Test basic connection
    try:
        print(f"\n🔗 Testing connection to: {database_url[:50]}...")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version[:50]}...")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_keep_alive_service():
    """Test the keep-alive service"""
    print(f"\n🚀 Testing Keep-Alive Service...")
    print("=" * 50)
    
    try:
        from supabase_keepalive import SupabaseKeepAlive
        
        keep_alive = SupabaseKeepAlive()
        print("✅ SupabaseKeepAlive instance created")
        
        # Test keep-alive operation
        print("\n🔄 Running keep-alive operation...")
        success, messages = keep_alive.run_keep_alive()
        
        print(f"\nResults:")
        print(f"Success: {'✅' if success else '❌'}")
        
        for i, message in enumerate(messages, 1):
            print(f"{i}. {message}")
        
        return success
        
    except Exception as e:
        print(f"❌ Keep-alive test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Supabase Connection & Keep-Alive Test")
    print("=" * 50)
    
    # Test database connection
    connection_ok = test_database_connection()
    
    if connection_ok:
        # Test keep-alive service
        keep_alive_ok = test_keep_alive_service()
        
        if keep_alive_ok:
            print(f"\n🎉 All tests PASSED!")
            print("Your Supabase keep-alive system is working correctly.")
        else:
            print(f"\n⚠️  Keep-alive test FAILED")
    else:
        print(f"\n❌ Connection test FAILED")
        print("Please fix the connection issues first.")