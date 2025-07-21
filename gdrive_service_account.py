"""
Google Drive backup using Service Account - simpler and more reliable for production
"""
import os
import json
import logging
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveServiceAccount:
    """Google Drive backup using Service Account authentication"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.service = None
        self.backup_folder_id = None
        self.backup_folder_name = 'Lang Huu Nghi Database Backups'
        self.max_backups = 10
        
        # Database connection info
        self.db_url = os.environ.get('DATABASE_URL')
        if self.db_url:
            self.db_mode = 'postgresql'
        else:
            self.db_mode = 'sqlite'
            
    def authenticate(self):
        """Authenticate using Service Account JSON from environment variable"""
        try:
            # Get service account JSON from environment
            service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            
            if not service_account_json:
                logger.error("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not found")
                return False
                
            # Parse JSON credentials
            try:
                credentials_info = json.loads(service_account_json)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
                return False
                
            # Create credentials from service account info
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info, scopes=self.SCOPES
            )
            
            # Build the Drive service
            self.service = build('drive', 'v3', credentials=credentials)
            
            # Test the connection
            try:
                about = self.service.about().get(fields="user").execute()
                user_email = about.get('user', {}).get('emailAddress', 'Service Account')
                logger.info(f"Successfully authenticated as: {user_email}")
                return True
            except HttpError as e:
                if e.resp.status == 403:
                    logger.error("Google Drive API not enabled or insufficient permissions")
                    logger.error("Solution: Enable Google Drive API in Google Cloud Console")
                else:
                    logger.error(f"API test failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Service Account authentication failed: {e}")
            return False
    
    def find_or_create_backup_folder(self):
        """Find existing backup folder or create new one"""
        try:
            # Search for existing folder
            query = f"name='{self.backup_folder_name}' and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get('files', [])
            
            if folders:
                self.backup_folder_id = folders[0]['id']
                logger.info(f"Found existing backup folder: {self.backup_folder_id}")
                return True
            
            # Create new folder
            folder_metadata = {
                'name': self.backup_folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(body=folder_metadata).execute()
            self.backup_folder_id = folder.get('id')
            logger.info(f"Created new backup folder: {self.backup_folder_id}")
            
            return True
            
        except HttpError as e:
            logger.error(f"Failed to find/create backup folder: {e}")
            return False
    
    def create_database_backup(self):
        """Create database backup file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if self.db_mode == 'postgresql':
                # PostgreSQL backup using SQL dump
                return self._create_postgresql_backup(timestamp)
            else:
                # SQLite backup
                return self._create_sqlite_backup(timestamp)
                
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return None
    
    def _create_postgresql_backup(self, timestamp):
        """Create PostgreSQL backup using custom SQL export"""
        try:
            from database import Database
            
            db = Database()
            
            # Create SQL dump
            backup_content = f"""-- Lang Huu Nghi Database Backup
-- Created: {datetime.now().isoformat()}
-- Database: PostgreSQL

"""
            
            # Export all tables
            tables = ['users', 'students', 'veterans', 'medical_records', 'student_notes', 'documents']
            
            for table in tables:
                try:
                    backup_content += f"\n-- Table: {table}\n"
                    
                    # Get table data  
                    rows = db.execute_query(f"SELECT * FROM {table}")
                    
                    if rows:
                        # Get column names
                        first_row = db.execute_query(f"SELECT * FROM {table} LIMIT 1")
                        if first_row:
                            columns = list(first_row[0].keys()) if first_row and hasattr(first_row[0], 'keys') else []
                        else:
                            columns = []
                        
                        if columns:
                            backup_content += f"-- Columns: {', '.join(columns)}\n"
                            
                            for row in rows:
                                values = []
                                for value in row:
                                    if value is None:
                                        values.append('NULL')
                                    elif isinstance(value, str):
                                        # Escape single quotes
                                        escaped = value.replace("'", "''")
                                        values.append(f"'{escaped}'")
                                    else:
                                        values.append(str(value))
                                
                                backup_content += f"INSERT INTO {table} VALUES ({', '.join(values)});\n"
                    
                    backup_content += f"-- End of {table}\n\n"
                    
                except Exception as table_error:
                    logger.warning(f"Could not backup table {table}: {table_error}")
                    backup_content += f"-- Error backing up {table}: {table_error}\n\n"
            
            # Save to temporary file
            backup_filename = f"lang_huu_nghi_backup_{timestamp}.sql"
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8')
            temp_file.write(backup_content)
            temp_file.close()
            
            return temp_file.name, backup_filename
            
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            return None
    
    def _create_sqlite_backup(self, timestamp):
        """Create SQLite backup by copying database file"""
        try:
            db_path = 'lang_huu_nghi.db'
            if not os.path.exists(db_path):
                logger.error("SQLite database file not found")
                return None
                
            backup_filename = f"lang_huu_nghi_backup_{timestamp}.db"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
            temp_file.close()
            
            # Copy database file
            import shutil
            shutil.copy2(db_path, temp_file.name)
            
            return temp_file.name, backup_filename
            
        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            return None
    
    def upload_backup(self, file_path, filename):
        """Upload backup file to Google Drive"""
        try:
            file_metadata = {
                'name': filename,
                'parents': [self.backup_folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size'
            ).execute()
            
            logger.info(f"Backup uploaded successfully: {filename} ({file.get('size')} bytes)")
            return file.get('id')
            
        except HttpError as e:
            logger.error(f"Failed to upload backup: {e}")
            return None
        finally:
            # Clean up temporary file
            try:
                os.unlink(file_path)
            except:
                pass
    
    def cleanup_old_backups(self):
        """Remove old backups, keeping only the latest N backups"""
        try:
            # Get all backup files in folder
            query = f"'{self.backup_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                orderBy='createdTime desc',
                fields="files(id, name, createdTime)"
            ).execute()
            
            files = results.get('files', [])
            
            if len(files) > self.max_backups:
                files_to_delete = files[self.max_backups:]
                
                for file in files_to_delete:
                    try:
                        self.service.files().delete(fileId=file['id']).execute()
                        logger.info(f"Deleted old backup: {file['name']}")
                    except HttpError as e:
                        logger.warning(f"Could not delete {file['name']}: {e}")
                        
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def create_backup(self):
        """Main backup method"""
        try:
            # Authenticate
            if not self.authenticate():
                return False
                
            # Find/create backup folder
            if not self.find_or_create_backup_folder():
                return False
                
            # Create database backup
            backup_result = self.create_database_backup()
            if not backup_result:
                return False
                
            file_path, filename = backup_result
            
            # Upload to Google Drive
            file_id = self.upload_backup(file_path, filename)
            if not file_id:
                return False
                
            # Cleanup old backups
            self.cleanup_old_backups()
            
            logger.info("Backup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        try:
            if not self.authenticate():
                return []
                
            if not self.find_or_create_backup_folder():
                return []
                
            query = f"'{self.backup_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                orderBy='createdTime desc',
                fields="files(id, name, createdTime, size)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []