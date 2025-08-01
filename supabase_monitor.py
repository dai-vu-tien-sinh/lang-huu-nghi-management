
#!/usr/bin/env python3
"""
Supabase Health Monitor
Provides detailed health checks and monitoring for Supabase connection
"""

import os
import time
import psycopg2
from datetime import datetime, timedelta
from supabase_keepalive import SupabaseKeepAlive

class SupabaseMonitor:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
    
    def check_connection(self):
        """Check basic database connection"""
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version(), current_timestamp")
                    version, timestamp = cursor.fetchone()
                    return {
                        "status": "healthy",
                        "version": version,
                        "timestamp": timestamp,
                        "latency_ms": self._measure_latency()
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _measure_latency(self):
        """Measure database query latency"""
        try:
            start_time = time.time()
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            end_time = time.time()
            return round((end_time - start_time) * 1000, 2)
        except:
            return None
    
    def check_keep_alive_table(self):
        """Check keep-alive table status"""
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    # Check if table exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'keep_alive'
                        )
                    """)
                    table_exists = cursor.fetchone()[0]
                    
                    if not table_exists:
                        return {"status": "missing", "message": "Keep-alive table not found"}
                    
                    # Check table contents
                    cursor.execute("SELECT COUNT(*) FROM keep_alive")
                    count = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT created_at FROM keep_alive 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                    last_entry = cursor.fetchone()
                    
                    return {
                        "status": "healthy",
                        "entry_count": count,
                        "last_entry": last_entry[0] if last_entry else None
                    }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_comprehensive_check(self):
        """Run all health checks"""
        print("🔍 Supabase Health Monitor")
        print("=" * 50)
        
        # Connection check
        print("1️⃣ Database Connection:")
        conn_status = self.check_connection()
        if conn_status["status"] == "healthy":
            print(f"   ✅ Connected successfully")
            print(f"   📊 Latency: {conn_status['latency_ms']}ms")
            print(f"   🕐 Server time: {conn_status['timestamp']}")
        else:
            print(f"   ❌ Connection failed: {conn_status['error']}")
            return False
        
        # Keep-alive table check
        print("\n2️⃣ Keep-Alive Table:")
        table_status = self.check_keep_alive_table()
        if table_status["status"] == "healthy":
            print(f"   ✅ Table exists and accessible")
            print(f"   📝 Entry count: {table_status['entry_count']}")
            if table_status['last_entry']:
                print(f"   🕐 Last entry: {table_status['last_entry']}")
        else:
            print(f"   ❌ Table check failed: {table_status.get('error', table_status.get('message'))}")
        
        # Keep-alive service test
        print("\n3️⃣ Keep-Alive Service:")
        try:
            keep_alive = SupabaseKeepAlive()
            success, messages = keep_alive.run_keep_alive()
            if success:
                print("   ✅ Keep-alive service working")
                for msg in messages:
                    print(f"   📝 {msg}")
            else:
                print("   ❌ Keep-alive service failed")
                for msg in messages:
                    print(f"   ❌ {msg}")
        except Exception as e:
            print(f"   ❌ Keep-alive service error: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Health check completed")
        return True

if __name__ == "__main__":
    try:
        monitor = SupabaseMonitor()
        monitor.run_comprehensive_check()
    except Exception as e:
        print(f"❌ Monitor failed to start: {e}")
