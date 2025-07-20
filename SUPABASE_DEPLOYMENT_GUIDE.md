# Supabase Database Deployment Guide

## Overview
Deploy your Làng Hữu Nghị management system database to Supabase PostgreSQL for production hosting.

## Step 1: Create Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Choose organization and fill details:
   - **Name**: `lang-huu-nghi-management`
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your users
4. Click "Create new project" (takes 2-3 minutes)

## Step 2: Get Database Connection URL

1. In your Supabase project dashboard
2. Go to **Settings** > **Database**
3. Find **Connection string** section
4. Copy the **URI** (connection pooler):
   ```
   postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-0-xx.pooler.supabase.com:6543/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

## Step 3: Convert SQLite Data to PostgreSQL

Since your current system uses SQLite, you need to migrate to PostgreSQL:

### Option A: Manual Table Creation
1. Go to **SQL Editor** in Supabase dashboard
2. Create tables manually based on your SQLite schema:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    dark_mode BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table  
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) UNIQUE,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(10),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    house VARCHAR(10),
    health_on_admission TEXT,
    initial_characteristics TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Veterans table
CREATE TABLE veterans (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) UNIQUE,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(10),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    house VARCHAR(10),
    military_unit VARCHAR(100),
    rank VARCHAR(50),
    service_years VARCHAR(20),
    health_on_admission TEXT,
    initial_characteristics TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document files table
CREATE TABLE document_files (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20),
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size INTEGER,
    file_data BYTEA,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES students(patient_id) ON DELETE CASCADE
);

-- Medical records table
CREATE TABLE medical_records (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20),
    patient_type VARCHAR(10),
    record_date DATE,
    diagnosis TEXT,
    treatment TEXT,
    medications TEXT,
    follow_up_date DATE,
    notes TEXT,
    doctor_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classes table
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20),
    teacher_name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student notes table
CREATE TABLE student_notes (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    note_text TEXT NOT NULL,
    category VARCHAR(50),
    is_important BOOLEAN DEFAULT FALSE,
    teacher_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
```

### Option B: Use Migration Tool
1. Install `sqlite3` and `psql` on your local machine
2. Export SQLite data and import to PostgreSQL
3. Use tools like `pgloader` for automated migration

## Step 4: Insert Sample Data

Copy your sample data from SQLite to PostgreSQL:

```sql
-- Insert admin user
INSERT INTO users (username, password, role, email, full_name, dark_mode) 
VALUES ('admin', 'admin123', 'admin', 'admin@langhuu.vn', 'Administrator', false);

-- Insert sample students (adjust data as needed)
INSERT INTO students (patient_id, name, birth_date, gender, address, phone, house, health_on_admission, initial_characteristics)
VALUES 
('HS001', 'Nguyễn Văn Học', '2010-05-15', 'Nam', 'Hà Nội', '0123456789', 'T3', 'Tình trạng sức khỏe tốt', 'Học sinh hiền lành, ngoan ngoãn'),
-- Add more students...
;
```

## Step 5: Configure Environment Variables

For your Streamlit deployment, you'll need:

```env
DATABASE_URL=postgresql://postgres.xxx:[PASSWORD]@aws-0-xx.pooler.supabase.com:6543/postgres
PGDATABASE=postgres
PGHOST=aws-0-xx.pooler.supabase.com
PGPORT=6543
PGUSER=postgres.xxx
PGPASSWORD=[YOUR-PASSWORD]
```

## Step 6: Test Connection

Test your database connection:

```python
import psycopg2
import os

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students;")
    count = cursor.fetchone()[0]
    print(f"✅ Connected! Found {count} students")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Step 7: Update Application Code

Your application is already configured for PostgreSQL. Ensure:
- Use `%s` parameter placeholders (not `?`)
- Handle PostgreSQL-specific data types
- Update any SQLite-specific queries

## Security Notes

- Keep database password secure
- Use Row Level Security (RLS) in Supabase for additional protection
- Consider enabling database backups in Supabase dashboard
- Monitor usage in Supabase analytics

Your database will be hosted on Supabase with automatic backups, scaling, and monitoring!