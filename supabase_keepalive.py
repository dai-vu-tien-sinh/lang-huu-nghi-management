"""
Supabase Keep Alive Service
Prevents Supabase projects from getting paused due to inactivity
"""

import os
import time
import random
import string
import psycopg2
from datetime import datetime, timedelta
import requests
from threading import Thread
import schedule
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseKeepAlive:
    def __init__(self, database_url=None, table_name="keep_alive", column_name="name", 
                 max_entries=10, other_endpoints=None):
        """
        Initialize the Supabase Keep Alive service
        
        Args:
            database_url (str): Database connection URL
            table_name (str): Table name to use for keep-alive operations
            column_name (str): Column name to store random strings
            max_entries (int): Maximum entries before deletion starts
            other_endpoints (list): List of other endpoints to ping
        """
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        self.table_name = table_name
        self.column_name = column_name
        self.max_entries = max_entries
        self.other_endpoints = other_endpoints or []
        
        if not self.database_url:
            raise ValueError("Database URL is required")
            
        self.setup_table()
    
    def setup_table(self):
        """Create the keep-alive table if it doesn't exist"""
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {self.table_name} (
                            id SERIAL PRIMARY KEY,
                            {self.column_name} TEXT UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    conn.commit()
                    logger.info(f"Keep-alive table '{self.table_name}' is ready")
        except Exception as e:
            logger.error(f"Error setting up table: {e}")
            raise
    
    def generate_random_string(self, length=12):
        """Generate a random string of specified length"""
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))
    
    def query_random_string(self):
        """Query the database with a random string"""
        random_string = self.generate_random_string()
        
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT * FROM {self.table_name} 
                        WHERE {self.column_name} = %s
                    """, (random_string,))
                    result = cursor.fetchall()
                    
                    message = f"Queried '{random_string}' from '{self.table_name}': {len(result)} results"
                    logger.info(message)
                    return True, message
        except Exception as e:
            error_msg = f"Error querying random string: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_entry_count(self):
        """Get the current number of entries in the table"""
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                    count = cursor.fetchone()[0]
                    return count
        except Exception as e:
            logger.error(f"Error getting entry count: {e}")
            return 0
    
    def insert_random_entry(self):
        """Insert a random entry into the table"""
        random_string = self.generate_random_string()
        
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        INSERT INTO {self.table_name} ({self.column_name})
                        VALUES (%s)
                        ON CONFLICT ({self.column_name}) DO NOTHING
                    """, (random_string,))
                    conn.commit()
                    
                    message = f"Inserted '{random_string}' into '{self.table_name}'"
                    logger.info(message)
                    return True, message
        except Exception as e:
            error_msg = f"Error inserting random entry: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_oldest_entry(self):
        """Delete the oldest entry from the table"""
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        DELETE FROM {self.table_name}
                        WHERE id = (
                            SELECT id FROM {self.table_name}
                            ORDER BY created_at ASC
                            LIMIT 1
                        )
                        RETURNING {self.column_name}
                    """)
                    deleted_entry = cursor.fetchone()
                    conn.commit()
                    
                    if deleted_entry:
                        message = f"Deleted '{deleted_entry[0]}' from '{self.table_name}'"
                        logger.info(message)
                        return True, message
                    else:
                        message = f"No entries to delete from '{self.table_name}'"
                        logger.info(message)
                        return True, message
        except Exception as e:
            error_msg = f"Error deleting oldest entry: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def manage_entries(self):
        """Manage entries - insert or delete based on current count"""
        current_count = self.get_entry_count()
        
        if current_count >= self.max_entries:
            return self.delete_oldest_entry()
        else:
            return self.insert_random_entry()
    
    def ping_other_endpoints(self):
        """Ping other endpoints to keep them alive"""
        results = []
        
        for endpoint in self.other_endpoints:
            try:
                response = requests.get(endpoint, timeout=30)
                status = "Passed" if response.status_code == 200 else "Failed"
                result = f"{endpoint} - {status}"
                results.append(result)
                logger.info(result)
            except Exception as e:
                result = f"{endpoint} - Failed: {str(e)}"
                results.append(result)
                logger.error(result)
        
        return results
    
    def run_keep_alive(self):
        """Run the complete keep-alive process"""
        logger.info("Starting keep-alive process...")
        
        success_count = 0
        total_operations = 0
        messages = []
        
        # 1. Query with random string
        total_operations += 1
        success, message = self.query_random_string()
        if success:
            success_count += 1
        messages.append(message)
        
        # 2. Manage entries (insert/delete)
        total_operations += 1
        success, message = self.manage_entries()
        if success:
            success_count += 1
        messages.append(message)
        
        # 3. Ping other endpoints
        if self.other_endpoints:
            endpoint_results = self.ping_other_endpoints()
            messages.extend(endpoint_results)
        
        # Log summary
        logger.info(f"Keep-alive completed: {success_count}/{total_operations} operations successful")
        
        return success_count == total_operations, messages
    
    def start_scheduled_task(self, cron_schedule="0 5 */3 * *"):
        """
        Start the scheduled keep-alive task
        
        Args:
            cron_schedule (str): Cron-like schedule (currently uses simple schedule)
        """
        # Run every 3 days to ensure database stays active
        schedule.every(3).days.at("05:00").do(self.run_keep_alive)
        
        # Also run daily at different times for extra safety
        schedule.every().day.at("12:00").do(self.run_keep_alive)
        schedule.every().day.at("18:00").do(self.run_keep_alive)
        
        logger.info("Scheduled keep-alive task started (every 3 days at 5:00 AM + daily at 12:00 PM and 6:00 PM)")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self):
        """Run keep-alive once for testing"""
        return self.run_keep_alive()


def create_keep_alive_service():
    """Factory function to create a keep-alive service"""
    # You can customize these settings
    other_endpoints = [
        # Add your other project URLs here
        # "https://your-other-app.vercel.app/api/keep-alive",
    ]
    
    return SupabaseKeepAlive(
        table_name="keep_alive",
        column_name="name",
        max_entries=10,
        other_endpoints=other_endpoints
    )


if __name__ == "__main__":
    # Create and run the keep-alive service
    keep_alive = create_keep_alive_service()
    
    # Run once for testing
    success, messages = keep_alive.run_once()
    
    for message in messages:
        print(message)
    
    print(f"\nKeep-alive {'successful' if success else 'failed'}")