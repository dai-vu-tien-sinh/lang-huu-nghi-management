# Supabase Deployment Guide

## Step-by-Step Deployment Instructions

### 1. Prepare Supabase Database

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Choose region closest to your users
   - Set strong database password

2. **Get Database Connection String**
   - Go to Project Settings > Database
   - Copy the connection string under "Connection string" > "Transaction pooler"
   - Replace `[YOUR-PASSWORD]` with your actual password
   - Format: `postgresql://postgres.xxx:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`

### 2. Set Up Database Schema

1. **Open Supabase SQL Editor**
   - Go to SQL Editor in your Supabase dashboard
   - Create new query

2. **Execute Schema SQL**
   ```sql
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
   ```

### 3. Deploy to Streamlit Cloud

1. **Push Code to GitHub**
   - Create GitHub repository
   - Push all project files including `streamlit_app.py`

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect GitHub account
   - Select your repository
   - Set main file: `streamlit_app.py`

3. **Configure Secrets**
   In Streamlit Cloud secrets section, add:
   ```toml
   DATABASE_URL = "postgresql://postgres.xxx:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres"

   # Optional services (add if needed)
   SENDGRID_API_KEY = "your_sendgrid_key"
   TWILIO_ACCOUNT_SID = "your_twilio_sid"
   TWILIO_AUTH_TOKEN = "your_twilio_token"
   TWILIO_PHONE_NUMBER = "your_twilio_phone"
   ANTHROPIC_API_KEY = "your_anthropic_key"
   ```

### 4. Migrate Data (Optional)

If you have existing data to migrate:

1. **Run Migration Script**
   ```bash
   python deploy.py
   ```

2. **Manual Data Import**
   - Export current data using the deployment script
   - Import using Supabase dashboard or SQL commands

### 5. Test Deployment

1. **Verify Database Connection**
   - Check app logs for database connection errors
   - Test login with default admin account

2. **Test Key Features**
   - User authentication
   - Data creation and retrieval
   - Search functionality
   - Export features

### 6. Post-Deployment Setup

1. **Create Admin User**
   - The app will automatically create initial admin user
   - Login: `admin` / `admin123`

2. **Configure User Accounts**
   - Create additional user accounts as needed
   - Test different role permissions

3. **Set Up Email/SMS (Optional)**
   - Configure SendGrid for email notifications
   - Configure Twilio for SMS notifications

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify connection string format
   - Check Supabase project status
   - Ensure password is correct

2. **Missing Tables**
   - Re-run schema SQL in Supabase
   - Check for SQL execution errors

3. **Permission Errors**
   - Verify user roles are correctly set
   - Check auth.py configuration

4. **Performance Issues**
   - Monitor Supabase dashboard
   - Check query performance
   - Consider upgrading Supabase plan

### Support

For deployment issues:
1. Check Streamlit Cloud logs
2. Monitor Supabase dashboard
3. Test database connection independently
4. Verify all environment variables are set correctly