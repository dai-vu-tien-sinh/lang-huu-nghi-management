
#!/usr/bin/env python3
"""
Database Cleanup Utility
Removes unused records and optimizes the database
"""

import sqlite3
import os
from datetime import datetime, timedelta

class DatabaseCleanup:
    def __init__(self, db_path='lang_huu_nghi.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
    def analyze_unused_records(self):
        """Analyze database for potentially unused records"""
        cursor = self.conn.cursor()
        issues = []
        
        # Check for students without classes
        cursor.execute("SELECT COUNT(*) FROM students WHERE class_id IS NULL OR class_id = 0")
        unassigned_students = cursor.fetchone()[0]
        if unassigned_students > 0:
            issues.append(f"Found {unassigned_students} students not assigned to any class")
        
        # Check for empty document records
        cursor.execute("SELECT COUNT(*) FROM document_files WHERE file_data IS NULL OR LENGTH(file_data) = 0")
        empty_docs = cursor.fetchone()[0]
        if empty_docs > 0:
            issues.append(f"Found {empty_docs} document records with no file data")
        
        # Check for old medical records (older than 5 years)
        five_years_ago = datetime.now() - timedelta(days=5*365)
        cursor.execute("SELECT COUNT(*) FROM medical_records WHERE date < ?", (five_years_ago.isoformat(),))
        old_medical = cursor.fetchone()[0]
        if old_medical > 0:
            issues.append(f"Found {old_medical} medical records older than 5 years")
        
        # Check for orphaned class history records
        cursor.execute("""
            SELECT COUNT(*) FROM student_class_history sch 
            WHERE NOT EXISTS (SELECT 1 FROM students s WHERE s.id = sch.student_id)
        """)
        orphaned_history = cursor.fetchone()[0]
        if orphaned_history > 0:
            issues.append(f"Found {orphaned_history} orphaned class history records")
        
        # Check for duplicate students (same name)
        cursor.execute("""
            SELECT full_name, COUNT(*) as count 
            FROM students 
            GROUP BY full_name 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            issues.append(f"Found {len(duplicates)} sets of duplicate student names")
        
        return issues
    
    def clean_empty_documents(self):
        """Remove document records with no file data"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM document_files WHERE file_data IS NULL OR LENGTH(file_data) = 0")
        deleted = cursor.rowcount
        self.conn.commit()
        return deleted
    
    def clean_orphaned_records(self):
        """Remove orphaned records that reference non-existent parent records"""
        cursor = self.conn.cursor()
        deleted_count = 0
        
        # Remove orphaned class history
        cursor.execute("""
            DELETE FROM student_class_history 
            WHERE student_id NOT IN (SELECT id FROM students)
        """)
        deleted_count += cursor.rowcount
        
        # Remove orphaned student notes
        cursor.execute("""
            DELETE FROM student_notes 
            WHERE student_id NOT IN (SELECT id FROM students)
        """)
        deleted_count += cursor.rowcount
        
        # Remove orphaned medical records
        cursor.execute("""
            DELETE FROM medical_records 
            WHERE patient_type = 'student' AND patient_id NOT IN (SELECT id FROM students)
        """)
        deleted_count += cursor.rowcount
        
        cursor.execute("""
            DELETE FROM medical_records 
            WHERE patient_type = 'veteran' AND patient_id NOT IN (SELECT id FROM veterans)
        """)
        deleted_count += cursor.rowcount
        
        self.conn.commit()
        return deleted_count
    
    def optimize_database(self):
        """Optimize database by running VACUUM"""
        # Get size before optimization
        size_before = os.path.getsize(self.db_path)
        
        cursor = self.conn.cursor()
        cursor.execute("VACUUM")
        self.conn.commit()
        
        # Get size after optimization
        size_after = os.path.getsize(self.db_path)
        
        return size_before, size_after
    
    def run_full_cleanup(self):
        """Run complete database cleanup"""
        print("🧹 Database Cleanup Utility")
        print("=" * 50)
        
        # Analyze issues
        print("🔍 Analyzing database...")
        issues = self.analyze_unused_records()
        
        if not issues:
            print("✅ No issues found in database")
        else:
            print("📋 Found the following issues:")
            for issue in issues:
                print(f"   • {issue}")
        
        # Clean empty documents
        print("\n🗑️ Cleaning empty document records...")
        deleted_docs = self.clean_empty_documents()
        if deleted_docs > 0:
            print(f"   ✅ Removed {deleted_docs} empty document records")
        else:
            print("   ✅ No empty document records found")
        
        # Clean orphaned records
        print("\n🔗 Cleaning orphaned records...")
        deleted_orphaned = self.clean_orphaned_records()
        if deleted_orphaned > 0:
            print(f"   ✅ Removed {deleted_orphaned} orphaned records")
        else:
            print("   ✅ No orphaned records found")
        
        # Optimize database
        print("\n⚡ Optimizing database...")
        size_before, size_after = self.optimize_database()
        size_saved = size_before - size_after
        
        print(f"   📊 Size before: {size_before / 1024:.2f} KB")
        print(f"   📊 Size after: {size_after / 1024:.2f} KB")
        if size_saved > 0:
            print(f"   💾 Space saved: {size_saved / 1024:.2f} KB")
        else:
            print("   ℹ️ No space saved (database was already optimized)")
        
        print("\n✅ Database cleanup completed!")
        
    def close(self):
        """Close database connection"""
        self.conn.close()

if __name__ == "__main__":
    cleanup = DatabaseCleanup()
    try:
        cleanup.run_full_cleanup()
    finally:
        cleanup.close()
