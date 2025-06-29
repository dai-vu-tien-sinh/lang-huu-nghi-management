-- Làng Hữu Nghị Management System Database Schema for Supabase

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

-- Insert initial admin user
INSERT INTO users (username, password_hash, role, full_name, email) 
VALUES ('admin', 'pbkdf2:sha256:600000$salt$hash', 'admin', 'System Administrator', 'admin@langhuunghi.vn')
ON CONFLICT (username) DO NOTHING;