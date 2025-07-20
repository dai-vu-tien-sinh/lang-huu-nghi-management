
# Add this to your main application (e.g., Trang_chủ.py or database.py)

import atexit
from gdrive_backup import start_automatic_backups, backup_service

# Initialize backup system when app starts
def initialize_app_backup():
    """Initialize backup system for the application"""
    try:
        if start_automatic_backups():
            print("✓ Google Drive backup system initialized - automatic weekly backups enabled")
        else:
            print("⚠ Failed to initialize Google Drive backup system")
    except Exception as e:
        print(f"⚠ Backup system error: {e}")

# Stop backup scheduler when app shuts down
def cleanup_backup():
    """Cleanup backup scheduler on app shutdown"""
    try:
        backup_service.stop_scheduler()
    except:
        pass

# Register cleanup function
atexit.register(cleanup_backup)

# Call initialization
initialize_app_backup()
