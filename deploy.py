#!/usr/bin/env python3
"""
Deployment script for Làng Hữu Nghị Management System
This script helps migrate data from current database to Supabase
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

def export_current_database():
    """Export current database to JSON for migration"""
    try:
        # Connect to current SQLite database
        conn = sqlite3.connect('lang_huu_nghi.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        export_data = {}
        
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            export_data[table] = [dict(row) for row in rows]
        
        # Save to JSON file
        with open('database_export.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        conn.close()
        print(f"Database exported successfully. Found {len(tables)} tables.")
        return True
        
    except Exception as e:
        print(f"Error exporting database: {e}")
        return False

def import_to_supabase(database_url):
    """Import data to Supabase database"""
    try:
        # Connect to Supabase PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Load exported data
        with open('database_export.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Starting data import to Supabase...")
        
        # Import data table by table
        for table_name, rows in data.items():
            if not rows:
                continue
                
            print(f"Importing {len(rows)} records to {table_name}...")
            
            # Get column names
            columns = list(rows[0].keys())
            
            # Create INSERT statement
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert data
            for row in rows:
                values = [row[col] for col in columns]
                cursor.execute(insert_sql, values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Data import completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error importing to Supabase: {e}")
        return False

def create_tables_sql():
    """Generate SQL for creating tables in Supabase"""
    sql = """
-- Create tables for Làng Hữu Nghị Management System

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    family_student_id INTEGER,
    theme_preference VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classes table
CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    teacher_id INTEGER REFERENCES users(id),
    academic_year VARCHAR(20),
    notes TEXT
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    birth_date DATE,
    address TEXT,
    email VARCHAR(200),
    admission_date DATE,
    class_id INTEGER REFERENCES classes(id),
    health_status VARCHAR(100) DEFAULT 'Bình thường',
    academic_status VARCHAR(100) DEFAULT 'Chưa đánh giá',
    psychological_status TEXT,
    profile_image BYTEA,
    gender VARCHAR(10),
    phone VARCHAR(20),
    year VARCHAR(10),
    parent_name VARCHAR(200)
);

-- Veterans table
CREATE TABLE IF NOT EXISTS veterans (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    birth_date DATE NOT NULL,
    service_period VARCHAR(100),
    health_condition VARCHAR(200),
    address TEXT,
    email VARCHAR(200),
    contact_info TEXT,
    profile_image BYTEA
);

-- Medical records table
CREATE TABLE IF NOT EXISTS medical_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    patient_type VARCHAR(20) NOT NULL,
    diagnosis TEXT NOT NULL,
    treatment TEXT NOT NULL,
    doctor_id INTEGER REFERENCES users(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    notification_sent BOOLEAN DEFAULT FALSE
);

-- Psychological evaluations table
CREATE TABLE IF NOT EXISTS psychological_evaluations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluator_id INTEGER REFERENCES users(id),
    assessment TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    follow_up_date DATE,
    notification_sent BOOLEAN DEFAULT FALSE
);

-- Sidebar preferences table
CREATE TABLE IF NOT EXISTS sidebar_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    page_order TEXT,
    hidden_pages TEXT
);

-- Student class history table
CREATE TABLE IF NOT EXISTS student_class_history (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    from_class_id INTEGER,
    to_class_id INTEGER REFERENCES classes(id),
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by INTEGER REFERENCES users(id),
    reason TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_students_class_id ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id, patient_type);
CREATE INDEX IF NOT EXISTS idx_psychological_evaluations_student ON psychological_evaluations(student_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
"""
    return sql

def main():
    print("Làng Hữu Nghị Management System - Deployment Script")
    print("=" * 60)
    
    # Step 1: Export current database
    print("Step 1: Exporting current database...")
    if export_current_database():
        print("✓ Database exported successfully")
    else:
        print("✗ Failed to export database")
        return
    
    # Step 2: Display SQL for manual execution
    print("\nStep 2: Database schema SQL")
    print("Copy and execute this SQL in your Supabase SQL editor:")
    print("-" * 60)
    print(create_tables_sql())
    print("-" * 60)
    
    # Step 3: Import data (if database URL provided)
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgresql'):
        print("\nStep 3: Importing data to Supabase...")
        if import_to_supabase(database_url):
            print("✓ Data imported successfully")
        else:
            print("✗ Failed to import data")
    else:
        print("\nStep 3: Set DATABASE_URL environment variable and run script again to import data")
    
    print("\nDeployment preparation completed!")
    print("Next steps:")
    print("1. Create a Supabase project")
    print("2. Execute the SQL schema in Supabase SQL editor")
    print("3. Set DATABASE_URL and run this script again to import data")
    print("4. Deploy to Streamlit Cloud with your Supabase connection string")

if __name__ == "__main__":
    main()