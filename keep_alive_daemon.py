
#!/usr/bin/env python3
"""
Keep-Alive Daemon Service
Runs continuously in deployed environments to keep Supabase active
"""

import os
import time
import threading
from datetime import datetime
from supabase_keepalive import SupabaseKeepAlive

class KeepAliveDaemon:
    def __init__(self, interval_hours=6):
        """
        Initialize daemon with configurable interval
        Args:
            interval_hours: Hours between keep-alive operations (default: 6)
        """
        self.interval_hours = interval_hours
        self.interval_seconds = interval_hours * 3600
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the daemon in a background thread"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_daemon, daemon=True)
        self.thread.start()
        print(f"🚀 Keep-alive daemon started (every {self.interval_hours} hours)")
        
    def stop(self):
        """Stop the daemon"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("🛑 Keep-alive daemon stopped")
        
    def _run_daemon(self):
        """Main daemon loop with retry logic"""
        retry_count = 0
        max_retries = 3
        
        while self.running:
            try:
                keep_alive = SupabaseKeepAlive()
                print(f"🔄 Running keep-alive at {datetime.now()}")
                success, messages = keep_alive.run_keep_alive()
                
                if success:
                    print("✅ Keep-alive successful")
                    retry_count = 0  # Reset retry count on success
                else:
                    print("❌ Keep-alive failed")
                    for msg in messages:
                        print(f"   {msg}")
                    
                    # Retry logic
                    retry_count += 1
                    if retry_count <= max_retries:
                        print(f"🔄 Retrying in 5 minutes... (attempt {retry_count}/{max_retries})")
                        time.sleep(300)  # Wait 5 minutes before retry
                        continue
                    else:
                        print(f"❌ Max retries ({max_retries}) reached, waiting for next interval")
                        retry_count = 0
                        
            except Exception as e:
                print(f"❌ Keep-alive daemon error: {e}")
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"🔄 Retrying in 5 minutes due to error... (attempt {retry_count}/{max_retries})")
                    time.sleep(300)
                    continue
                else:
                    print(f"❌ Max retries ({max_retries}) reached after error, waiting for next interval")
                    retry_count = 0
                
            # Wait for next interval
            time.sleep(self.interval_seconds)

# Global daemon instance
daemon = KeepAliveDaemon(interval_hours=6)

def start_keep_alive_daemon():
    """Start the keep-alive daemon (for deployed environments)"""
    if os.environ.get('REPLIT_DEPLOYMENT'):
        daemon.start()
        return True
    return False

if __name__ == "__main__":
    print("🔧 Starting Keep-Alive Daemon...")
    daemon.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        daemon.stop()
