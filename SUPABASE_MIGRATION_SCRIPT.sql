-- Supabase Migration Script for Làng Hữu Nghị Management System
-- Run this script in Supabase SQL Editor to create all tables and sample data

-- Users table
CREATE TABLE IF NOT EXISTS users (
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
CREATE TABLE IF NOT EXISTS students (
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
CREATE TABLE IF NOT EXISTS veterans (
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
CREATE TABLE IF NOT EXISTS document_files (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20),
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size INTEGER,
    file_data BYTEA,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medical records table
CREATE TABLE IF NOT EXISTS medical_records (
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
CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20),
    teacher_name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student notes table
CREATE TABLE IF NOT EXISTS student_notes (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    note_text TEXT NOT NULL,
    category VARCHAR(50),
    is_important BOOLEAN DEFAULT FALSE,
    teacher_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Insert default admin user
INSERT INTO users (username, password, role, email, full_name, dark_mode) 
VALUES ('admin', 'admin123', 'admin', 'admin@langhuu.vn', 'Administrator', false)
ON CONFLICT (username) DO NOTHING;

-- Insert sample teacher user
INSERT INTO users (username, password, role, email, full_name, dark_mode) 
VALUES ('teacher1', 'teacher123', 'teacher', 'teacher@langhuu.vn', 'Giáo viên chủ nhiệm', false)
ON CONFLICT (username) DO NOTHING;

-- Insert sample doctor user
INSERT INTO users (username, password, role, email, full_name, dark_mode) 
VALUES ('doctor1', 'doctor123', 'doctor', 'doctor@langhuu.vn', 'Bác sĩ', false)
ON CONFLICT (username) DO NOTHING;

-- Insert sample student data
INSERT INTO students (patient_id, name, birth_date, gender, address, phone, house, health_on_admission, initial_characteristics)
VALUES 
('HS001', 'Nguyễn Văn Học', '2010-05-15', 'Nam', 'Hà Nội', '0123456789', 'T3', 'Tình trạng sức khỏe tốt khi nhập học', 'Học sinh hiền lành, ngoan ngoãn, có tinh thần học hỏi tốt'),
('HS002', 'Trần Thị Mai', '2010-08-20', 'Nữ', 'TP.HCM', '0987654321', 'T4', 'Sức khỏe ổn định', 'Học sinh năng động, thích tham gia hoạt động tập thể'),
('HS003', 'Lê Văn Minh', '2009-12-10', 'Nam', 'Đà Nẵng', '0345678901', 'T5', 'Có tiền sử dị ứng nhẹ', 'Học sinh thông minh, có khả năng lãnh đạo tốt')
ON CONFLICT (patient_id) DO NOTHING;

-- Insert sample veteran data
INSERT INTO veterans (patient_id, name, birth_date, gender, address, phone, house, military_unit, rank, service_years, health_on_admission, initial_characteristics)
VALUES 
('CCB001', 'Nguyễn Văn Cường', '1970-03-15', 'Nam', 'Nghệ An', '0912345678', 'T2', 'Trung đoàn 304', 'Trung úy', '1990-2010', 'Có vấn đề về xương khớp', 'Cựu chiến binh có tinh thần trách nhiệm cao'),
('CCB002', 'Phạm Thị Lan', '1975-07-20', 'Nữ', 'Hải Phòng', '0934567890', 'T6', 'Sư đoàn 316', 'Thiếu úy', '1995-2015', 'Sức khỏe tổng thể tốt', 'Nhiệt tình, sẵn sàng giúp đỡ mọi người')
ON CONFLICT (patient_id) DO NOTHING;

-- Insert sample classes
INSERT INTO classes (class_name, academic_year, teacher_name, description)
VALUES 
('Lớp 6A', '2024-2025', 'Cô Nguyễn Thị Hoa', 'Lớp học dành cho học sinh lứa tuổi 12-13'),
('Lớp 7B', '2024-2025', 'Thầy Trần Văn Nam', 'Lớp học trung học cơ sở'),
('Lớp kỹ năng sống', '2024-2025', 'Cô Phạm Thị Lan', 'Lớp học kỹ năng sống cho mọi lứa tuổi')
ON CONFLICT DO NOTHING;

-- Insert sample medical records
INSERT INTO medical_records (patient_id, patient_type, record_date, diagnosis, treatment, medications, follow_up_date, notes, doctor_name)
VALUES 
('HS001', 'student', '2024-01-15', 'Khám sức khỏe định kỳ', 'Không có vấn đề đặc biệt', 'Vitamin tổng hợp', '2024-07-15', 'Học sinh có sức khỏe tốt', 'BS. Nguyễn Văn A'),
('CCB001', 'veteran', '2024-02-20', 'Đau khớp gối', 'Vật lý trị liệu, nghỉ ngơi', 'Thuốc giảm đau, thuốc bổ khớp', '2024-05-20', 'Cần theo dõi tình trạng khớp định kỳ', 'BS. Trần Thị B')
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_students_patient_id ON students(patient_id);
CREATE INDEX IF NOT EXISTS idx_veterans_patient_id ON veterans(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_document_files_patient_id ON document_files(patient_id);
CREATE INDEX IF NOT EXISTS idx_student_notes_student_id ON student_notes(student_id);

-- Enable Row Level Security (RLS) for better security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE veterans ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_notes ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic policies - can be customized later)
CREATE POLICY "Enable all operations for authenticated users" ON users
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON students
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON veterans
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON medical_records
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON document_files
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON classes
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON student_notes
    FOR ALL USING (auth.role() = 'authenticated');

-- Success message
SELECT 'Database schema created successfully! Ready for Làng Hữu Nghị management system.' as status;