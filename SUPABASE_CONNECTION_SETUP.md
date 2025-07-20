# Supabase Database Connection Setup

## Step 1: Create Supabase Project

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Sign in with GitHub or email

2. **Create New Project**
   - Click "New Project"
   - Organization: Choose your organization
   - **Project Name**: `lang-huu-nghi-management`
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to your users (e.g., Southeast Asia)
   - Click "Create new project"
   - Wait 2-3 minutes for setup completion

## Step 2: Get Connection Details

### 2.1 Access Database Settings
1. In your Supabase project dashboard
2. Go to **Settings** (gear icon) → **Database**
3. Scroll down to **Connection string** section

### 2.2 Copy Connection Details
You'll see something like this:

```
Host: aws-0-ap-southeast-1.pooler.supabase.com
Database name: postgres
Port: 6543
User: postgres.abcdefghijklmnop
Password: [YOUR-PASSWORD]
```

### 2.3 Full Connection URL
Copy the **URI** connection string:
```
postgresql://postgres.abcdefghijklmnop:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

## Step 3: Streamlit Cloud Environment Variables

In Streamlit Cloud, add these **exact** values from your Supabase project:

### Required Database Variables:
```
DATABASE_URL = postgresql://postgres.abcdefghijklmnop:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

PGDATABASE = postgres

PGHOST = aws-0-ap-southeast-1.pooler.supabase.com

PGPORT = 6543

PGUSER = postgres.abcdefghijklmnop

PGPASSWORD = [YOUR-ACTUAL-PASSWORD]
```

### Example with Real Values:
If your Supabase shows:
- Host: `aws-0-ap-southeast-1.pooler.supabase.com`
- User: `postgres.abcdefghijklmnop`  
- Password: `MySecurePassword123`

Then set:
```
DATABASE_URL = postgresql://postgres.abcdefghijklmnop:MySecurePassword123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

PGDATABASE = postgres

PGHOST = aws-0-ap-southeast-1.pooler.supabase.com

PGPORT = 6543

PGUSER = postgres.abcdefghijklmnop

PGPASSWORD = MySecurePassword123
```

## Step 4: Set Variables in Streamlit Cloud

### 4.1 Access App Settings
1. Go to your Streamlit Cloud dashboard
2. Find your `lang-huu-nghi-management` app
3. Click the **three dots** menu → **Settings**

### 4.2 Add Secrets
1. Click **Secrets** tab
2. Add each variable in TOML format:

```toml
DATABASE_URL = "postgresql://postgres.abcdefghijklmnop:MySecurePassword123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
PGDATABASE = "postgres"
PGHOST = "aws-0-ap-southeast-1.pooler.supabase.com"
PGPORT = "6543"
PGUSER = "postgres.abcdefghijklmnop"
PGPASSWORD = "MySecurePassword123"
```

### 4.3 Save and Redeploy
1. Click **Save**
2. Streamlit Cloud will automatically redeploy with new environment variables

## Step 5: Create Database Schema

### 5.1 Access SQL Editor
1. In Supabase dashboard, go to **SQL Editor**
2. Click **New query**

### 5.2 Create Tables
Copy and paste this SQL to create all required tables:

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
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

-- Insert admin user
INSERT INTO users (username, password, role, email, full_name, dark_mode) 
VALUES ('admin', 'admin123', 'admin', 'admin@langhuu.vn', 'Administrator', false);

-- Insert sample student
INSERT INTO students (patient_id, name, birth_date, gender, address, phone, house, health_on_admission, initial_characteristics)
VALUES ('HS001', 'Nguyễn Văn Học', '2010-05-15', 'Nam', 'Hà Nội', '0123456789', 'T3', 'Tình trạng sức khỏe tốt khi nhập học', 'Học sinh hiền lành, ngoan ngoãn, có tinh thần học hỏi tốt');
```

### 5.3 Execute Query
1. Click **Run** to create all tables and sample data
2. Check **Table Editor** to verify tables were created successfully

## Step 6: Test Connection

After setting up everything:

1. **Deploy your app** to Streamlit Cloud (if not already)
2. **Visit your app URL** (e.g., `https://lang-huu-nghi-management.streamlit.app`)
3. **Login** with:
   - Username: `admin`
   - Password: `admin123`
4. **Verify** student data loads correctly
5. **Test** adding/editing records

## Common Issues & Solutions

### Connection Refused
- Double-check PASSWORD matches exactly
- Ensure all environment variables are set correctly
- Verify Supabase project is active (not paused)

### Tables Not Found
- Run the SQL schema creation script in Supabase SQL Editor
- Check Table Editor to confirm tables exist

### Authentication Failed
- Verify DATABASE_URL format is correct
- Check username includes the full `postgres.xxxxx` format
- Ensure password doesn't contain special characters that need escaping

Your Vietnamese educational management system will be fully functional with production PostgreSQL database on Supabase!