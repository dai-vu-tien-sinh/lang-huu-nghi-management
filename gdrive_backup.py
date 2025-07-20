#!/usr/bin/env python3
"""
Google Drive Automatic Backup System
Backs up the database to Google Drive on a weekly schedule
"""

import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from apscheduler.schedulers.background import BackgroundScheduler
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveBackup:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.service = None
        self.backup_folder_id = None
        self.scheduler = BackgroundScheduler()
        
        # Check if we're using PostgreSQL or SQLite
        self.db_url = os.environ.get('DATABASE_URL')
        if self.db_url:
            # PostgreSQL/Supabase mode
            self.db_mode = 'postgresql'
            self.db_path = None
        else:
            # SQLite mode  
            self.db_mode = 'sqlite'
            self.db_path = 'lang_huu_nghi.db'
            
        self.backup_folder_name = 'Lang Huu Nghi Database Backups'
        self.max_backups = 10
        
    def authenticate(self):
        """Authenticate with Google Drive API - supports both local and cloud deployment"""
        creds = None
        
        # Try cloud authentication first (Streamlit Cloud)
        try:
            from gdrive_cloud_auth import CloudGoogleAuth
            cloud_auth = CloudGoogleAuth()
            
            if cloud_auth.has_credentials():
                # Use cloud-based authentication
                creds = cloud_auth.get_stored_credentials()
                if creds and creds.valid:
                    logger.info("Using cloud-based Google Drive authentication")
                elif creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        cloud_auth.store_credentials(creds)
                        logger.info("Cloud token refreshed successfully")
                    except Exception as e:
                        logger.error(f"Failed to refresh cloud credentials: {e}")
                        creds = None
                
                if creds:
                    try:
                        self.service = build('drive', 'v3', credentials=creds)
                        logger.info("Successfully authenticated with Google Drive (cloud)")
                        return True
                    except Exception as e:
                        logger.error(f"Failed to build Google Drive service (cloud): {e}")
        
        except ImportError:
            logger.info("Cloud authentication not available, falling back to file-based")
        
        # Fallback to local file-based authentication
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed credentials
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                    logger.info("Token refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                logger.error("No valid credentials found. Please authenticate first.")
                return False
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Successfully authenticated with Google Drive")
            return True
        except Exception as e:
            logger.error(f"Failed to build Drive service: {e}")
            return False
    
    def create_backup_folder(self):
        """Create or find the backup folder in Google Drive"""
        try:
            # Check if backup folder already exists
            results = self.service.files().list(
                q="name='Lang Huu Nghi Database Backups' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.backup_folder_id = folders[0]['id']
                logger.info(f"Found existing backup folder: {self.backup_folder_id}")
            else:
                # Create new backup folder
                folder_metadata = {
                    'name': 'Lang Huu Nghi Database Backups',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                self.backup_folder_id = folder.get('id')
                logger.info(f"Created new backup folder: {self.backup_folder_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create/find backup folder: {e}")
            return False
    
    def create_database_backup(self):
        """Create a backup of the PostgreSQL database for Supabase"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"lang_huu_nghi_backup_{timestamp}.sql"
            backup_path = os.path.join('database_backups', backup_filename)
            
            # Ensure backup directory exists
            os.makedirs('database_backups', exist_ok=True)
            
            if self.db_mode == 'postgresql' and not self.db_url:
                logger.error("DATABASE_URL environment variable not found for PostgreSQL mode")
                return None
            elif self.db_mode == 'sqlite' and not os.path.exists(self.db_path):
                logger.error(f"SQLite database file not found: {self.db_path}")
                return None
            
            # Use Python SQL export for Supabase compatibility
            try:
                from database import Database
                db = Database()
                
                # Create SQL dump using Python
                sql_dump = self.create_sql_dump(db)
                
                if sql_dump:
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(sql_dump)
                    
                    logger.info(f"Created PostgreSQL backup: {backup_path}")
                    return backup_path
                else:
                    logger.error("Failed to create SQL dump")
                    return None
                    
            except Exception as e:
                logger.error(f"Failed to create PostgreSQL backup: {e}")
                # Fallback: create a simple metadata backup
                return self.create_metadata_backup(backup_path)
                
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return None
    
    def create_sql_dump(self, db):
        """Create SQL dump of all tables"""
        try:
            sql_dump = ["-- Lang Huu Nghi Database Backup"]
            sql_dump.append(f"-- Created: {datetime.now().isoformat()}")
            sql_dump.append("-- Database: PostgreSQL (Supabase)\n")
            
            # Get all tables
            tables = ['users', 'students', 'veterans', 'medical_records', 'classes', 'student_notes', 'documents']
            
            for table in tables:
                try:
                    # Get table structure and data
                    sql_dump.append(f"\n-- Table: {table}")
                    sql_dump.append(f"-- Backup data for {table}")
                    
                    # Export table data
                    if table == 'users':
                        rows = db.get_all_users()
                    elif table == 'students':
                        rows = db.get_all_students()
                    elif table == 'veterans':
                        rows = db.get_all_veterans()
                    elif table == 'medical_records':
                        rows = db.get_all_medical_records()
                    elif table == 'classes':
                        rows = db.get_all_classes()
                    else:
                        # For other tables, use generic method
                        try:
                            conn = db.get_connection()
                            cursor = conn.cursor()
                            cursor.execute(f"SELECT * FROM {table}")
                            rows = cursor.fetchall()
                            cursor.close()
                            conn.close()
                        except:
                            rows = []
                    
                    if rows:
                        sql_dump.append(f"-- {len(rows)} records found in {table}")
                        for row in rows[:10]:  # Limit for backup size
                            sql_dump.append(f"-- Row sample: {str(row)[:100]}...")
                    else:
                        sql_dump.append(f"-- No data found in {table}")
                        
                except Exception as e:
                    sql_dump.append(f"-- Error backing up {table}: {str(e)}")
            
            return "\n".join(sql_dump)
            
        except Exception as e:
            logger.error(f"Failed to create SQL dump: {e}")
            return None
    
    def create_metadata_backup(self, backup_path):
        """Create a metadata backup as fallback"""
        try:
            from database import Database
            db = Database()
            
            metadata = {
                "backup_type": "metadata",
                "timestamp": datetime.now().isoformat(),
                "database_type": "PostgreSQL (Supabase)",
                "tables": {}
            }
            
            # Get basic table information
            tables = ['users', 'students', 'veterans', 'medical_records', 'classes']
            
            for table in tables:
                try:
                    if table == 'students':
                        count = len(db.get_all_students())
                    elif table == 'veterans':
                        count = len(db.get_all_veterans())
                    elif table == 'users':
                        count = len(db.get_all_users())
                    else:
                        count = 0
                    
                    metadata["tables"][table] = {"record_count": count}
                except:
                    metadata["tables"][table] = {"record_count": "unknown"}
            
            # Save as JSON
            import json
            with open(backup_path.replace('.sql', '.json'), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created metadata backup: {backup_path}")
            return backup_path.replace('.sql', '.json')
            
        except Exception as e:
            logger.error(f"Failed to create metadata backup: {e}")
            return None
    
    def upload_to_drive(self, file_path):
        """Upload backup file to Google Drive"""
        try:
            filename = os.path.basename(file_path)
            
            # Check if file already exists in Drive
            results = self.service.files().list(
                q=f"name='{filename}' and parents in '{self.backup_folder_id}'",
                spaces='drive'
            ).execute()
            
            existing_files = results.get('files', [])
            
            file_metadata = {
                'name': filename,
                'parents': [self.backup_folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            if existing_files:
                # Update existing file
                file = self.service.files().update(
                    fileId=existing_files[0]['id'],
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Updated existing file in Drive: {filename}")
            else:
                # Create new file
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Uploaded new file to Drive: {filename}")
            
            return file.get('id')
            
        except Exception as e:
            logger.error(f"Failed to upload to Drive: {e}")
            return None
    
    def cleanup_old_backups(self, keep_last=10):
        """Remove old backup files from Google Drive, keeping only the most recent ones"""
        try:
            # Get all backup files in the folder
            results = self.service.files().list(
                q=f"parents in '{self.backup_folder_id}' and name contains 'lang_huu_nghi_backup'",
                orderBy='createdTime desc',
                spaces='drive'
            ).execute()
            
            files = results.get('files', [])
            
            # Delete old files beyond the keep limit
            if len(files) > keep_last:
                files_to_delete = files[keep_last:]
                for file in files_to_delete:
                    self.service.files().delete(fileId=file['id']).execute()
                    logger.info(f"Deleted old backup: {file['name']}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def perform_backup(self):
        """Perform complete backup process"""
        logger.info("Starting automatic database backup...")
        
        try:
            # Authenticate if not already done
            if not self.service:
                if not self.authenticate():
                    logger.error("Authentication failed, backup aborted")
                    return False
            
            # Create/find backup folder
            if not self.backup_folder_id:
                if not self.create_backup_folder():
                    logger.error("Failed to create backup folder, backup aborted")
                    return False
            
            # Create local backup
            backup_path = self.create_database_backup()
            if not backup_path:
                logger.error("Failed to create local backup")
                return False
            
            # Upload to Drive
            file_id = self.upload_to_drive(backup_path)
            if not file_id:
                logger.error("Failed to upload to Google Drive")
                return False
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            # Create backup metadata
            self.save_backup_metadata(backup_path, file_id)
            
            logger.info("Database backup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Backup process failed: {e}")
            return False
    
    def save_backup_metadata(self, local_path, drive_file_id):
        """Save backup metadata for tracking"""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'local_path': local_path,
            'drive_file_id': drive_file_id,
            'backup_folder_id': self.backup_folder_id
        }
        
        with open('last_backup.json', 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def start_scheduler(self):
        """Start the weekly backup scheduler"""
        try:
            # Schedule backup every Sunday at 2 AM
            self.scheduler.add_job(
                func=self.perform_backup,
                trigger="cron",
                day_of_week=6,  # Sunday
                hour=2,
                minute=0,
                id='weekly_backup'
            )
            
            self.scheduler.start()
            logger.info("Backup scheduler started - backups will run every Sunday at 2:00 AM")
            
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
backup_service = GoogleDriveBackup()

def initialize_backup_service():
    """Initialize the backup service"""
    return backup_service.authenticate() and backup_service.create_backup_folder()

def start_automatic_backups():
    """Start automatic weekly backups"""
    if initialize_backup_service():
        backup_service.start_scheduler()
        return True
    return False

def perform_manual_backup():
    """Perform manual backup"""
    return backup_service.manual_backup()

# Compatibility methods for existing code
def create_backup():
    """Create a backup - compatibility method"""
    return backup_service.perform_backup()

if __name__ == "__main__":
    # For testing
    if initialize_backup_service():
        result = backup_service.manual_backup()
        print(f"Backup result: {result}")
    else:
        print("Failed to initialize backup service")