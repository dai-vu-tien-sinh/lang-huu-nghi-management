#!/usr/bin/env python3
"""
Local Automatic Backup System
Backs up the database locally on a daily schedule with maximum 10 backups
"""

import os
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import json
import logging
import glob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalBackup:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db_path = 'lang_huu_nghi.db'
        self.backup_dir = 'database_backups'
        self.max_backups = 10  # Keep last 10 backups
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup_filename(self):
        """Generate backup filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"lang_huu_nghi_backup_{timestamp}"
    
    def create_database_backup(self):
        """Create a local backup of the database with compression"""
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"Database file not found: {self.db_path}")
                return None
            
            backup_name = self.create_backup_filename()
            backup_db_path = os.path.join(self.backup_dir, f"{backup_name}.db")
            backup_zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            # Create database copy
            shutil.copy2(self.db_path, backup_db_path)
            
            # Create compressed backup
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_db_path, f"{backup_name}.db")
                
                # Add metadata
                metadata = {
                    'created': datetime.now().isoformat(),
                    'original_size': os.path.getsize(self.db_path),
                    'compressed_size': os.path.getsize(backup_zip_path),
                    'version': '1.0'
                }
                zipf.writestr('backup_info.json', json.dumps(metadata, indent=2))
            
            # Remove uncompressed copy
            os.remove(backup_db_path)
            
            # Automatically cleanup old backups to maintain limit
            self.cleanup_old_backups()
            
            logger.info(f"Created backup: {backup_zip_path}")
            return backup_zip_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            # Get all backup files
            backup_pattern = os.path.join(self.backup_dir, "lang_huu_nghi_backup_*.zip")
            backup_files = glob.glob(backup_pattern)
            
            # Sort by modification time (newest first)
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            # Remove old files beyond the limit
            if len(backup_files) > self.max_backups:
                files_to_delete = backup_files[self.max_backups:]
                for file_path in files_to_delete:
                    os.remove(file_path)
                    logger.info(f"Deleted old backup: {os.path.basename(file_path)}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def get_backup_info(self):
        """Get information about existing backups"""
        try:
            backup_pattern = os.path.join(self.backup_dir, "lang_huu_nghi_backup_*.zip")
            backup_files = glob.glob(backup_pattern)
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            backups = []
            for file_path in backup_files:
                try:
                    file_stat = os.stat(file_path)
                    size_mb = file_stat.st_size / (1024 * 1024)
                    
                    # Extract timestamp from filename
                    filename = os.path.basename(file_path)
                    # Extract timestamp: lang_huu_nghi_backup_YYYYMMDD_HHMMSS.zip
                    timestamp_str = filename.replace('lang_huu_nghi_backup_', '').replace('.zip', '')
                    
                    try:
                        # Parse timestamp from filename
                        backup_datetime = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        display_date = backup_datetime.strftime('%d/%m/%Y lúc %H:%M')
                        sort_date = backup_datetime
                    except ValueError:
                        # Fallback to file modification time if filename parsing fails
                        sort_date = datetime.fromtimestamp(file_stat.st_mtime)
                        display_date = sort_date.strftime('%d/%m/%Y lúc %H:%M')
                    
                    # Try to read metadata from zip
                    metadata = {}
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zipf:
                            if 'backup_info.json' in zipf.namelist():
                                metadata = json.loads(zipf.read('backup_info.json').decode())
                    except:
                        pass
                    
                    backup_info = {
                        'filename': filename,
                        'path': file_path,
                        'size': f"{size_mb:.2f} MB",
                        'created': display_date,
                        'created_datetime': sort_date,
                        'metadata': metadata
                    }
                    backups.append(backup_info)
                except Exception as e:
                    logger.warning(f"Failed to read backup info for {file_path}: {e}")
                    continue
            
            # Sort by actual creation time
            backups.sort(key=lambda x: x['created_datetime'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return []
    
    def create_pre_restore_backup(self):
        """Create a special backup before restore for revert purposes"""
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"Database file not found: {self.db_path}")
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pre_restore_name = f"pre_restore_backup_{timestamp}"
            backup_db_path = os.path.join(self.backup_dir, f"{pre_restore_name}.db")
            backup_zip_path = os.path.join(self.backup_dir, f"{pre_restore_name}.zip")
            
            # Create database copy
            shutil.copy2(self.db_path, backup_db_path)
            
            # Create compressed backup
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_db_path, f"{pre_restore_name}.db")
                
                # Add metadata
                metadata = {
                    'created': datetime.now().isoformat(),
                    'original_size': os.path.getsize(self.db_path),
                    'compressed_size': os.path.getsize(backup_zip_path),
                    'version': '1.0',
                    'type': 'pre_restore'
                }
                zipf.writestr('backup_info.json', json.dumps(metadata, indent=2))
            
            # Remove uncompressed copy
            os.remove(backup_db_path)
            
            logger.info(f"Created pre-restore backup: {backup_zip_path}")
            return backup_zip_path
            
        except Exception as e:
            logger.error(f"Failed to create pre-restore backup: {e}")
            return None

    def restore_backup(self, backup_path):
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Handle both .zip and .db files
            if backup_path.endswith('.zip'):
                # Extract and restore from zip
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # Find the database file in the zip
                    db_files = [name for name in zipf.namelist() if name.endswith('.db')]
                    if not db_files:
                        logger.error("No database file found in backup")
                        return False
                    
                    # Extract database file
                    zipf.extract(db_files[0], self.backup_dir)
                    extracted_path = os.path.join(self.backup_dir, db_files[0])
                    
                    # Replace current database
                    shutil.move(extracted_path, self.db_path)
            
            elif backup_path.endswith('.db'):
                # Direct database file restore
                shutil.copy2(backup_path, self.db_path)
            
            else:
                logger.error(f"Unsupported backup file format: {backup_path}")
                return False
                
            logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def perform_backup(self):
        """Perform complete backup process"""
        logger.info("Starting automatic database backup...")
        
        try:
            # Create backup
            backup_path = self.create_database_backup()
            if not backup_path:
                logger.error("Failed to create backup")
                return False
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            # Save backup metadata
            self.save_backup_metadata(backup_path)
            
            logger.info("Database backup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Backup process failed: {e}")
            return False
    
    def save_backup_metadata(self, backup_path):
        """Save backup metadata for tracking"""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'backup_path': backup_path,
            'backup_dir': self.backup_dir
        }
        
        with open('last_backup.json', 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def start_scheduler(self):
        """Start the daily backup scheduler"""
        try:
            # Schedule backup every day at 2 AM
            self.scheduler.add_job(
                func=self.perform_backup,
                trigger="cron",
                hour=2,
                minute=0,
                id='daily_backup'
            )
            
            self.scheduler.start()
            logger.info("Backup scheduler started - backups will run daily at 2:00 AM")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    def stop_scheduler(self):
        """Stop the backup scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Backup scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def manual_backup(self):
        """Perform immediate manual backup"""
        logger.info("Performing manual backup...")
        return self.perform_backup()

# Global backup instance
backup_service = LocalBackup()

def start_automatic_backups():
    """Start automatic daily backups"""
    backup_service.start_scheduler()
    return True

def perform_manual_backup():
    """Perform manual backup"""
    return backup_service.manual_backup()

def get_backup_list():
    """Get list of available backups"""
    return backup_service.get_backup_info()

def restore_from_backup(backup_path):
    """Restore database from backup"""
    return backup_service.restore_backup(backup_path)

if __name__ == "__main__":
    # For testing
    result = backup_service.manual_backup()
    print(f"Backup result: {result}")