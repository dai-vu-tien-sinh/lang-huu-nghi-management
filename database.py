import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
import os
import shutil
import json
from models import User, Student, Veteran, MedicalRecord, PsychologicalEvaluation, Family, Class, PeriodicAssessment, Support
from translations import get_current_language

# Bảng chuyển đổi các giá trị tiếng Việt sang tiếng Anh
TRANSLATIONS = {
    # Giới tính
    "Nam": "Male",
    "Nữ": "Female",
    
    # Tình trạng sức khỏe
    "Tốt": "Good",
    "Bình thường": "Normal",
    "Cần chú ý": "Needs Attention",
    
    # Tình trạng học tập
    "Xuất sắc": "Excellent",
    "Tốt": "Good",
    "Trung bình": "Average",
    "Cần cải thiện": "Needs Improvement",
    
    # Tình trạng tâm lý
    "Ổn định": "Stable",
    "Tốt": "Good",
    "Cần theo dõi": "Needs Monitoring",
    
    # Vai trò
    "admin": "Admin",
    "teacher": "Teacher",
    "doctor": "Doctor",
    "nurse": "Nurse",
    "counselor": "Counselor",
    "family": "Family",
    
    # Các giá trị lịch sử lớp
    "Hiện tại": "Current"
}

def translate_value(value: Any) -> Any:
    """Dịch giá trị tiếng Việt sang tiếng Anh dựa trên ngôn ngữ hiện tại"""
    if get_current_language() != 'en':
        return value
        
    if not isinstance(value, str):
        return value
    
    return TRANSLATIONS.get(value, value)

class SidebarPreference:
    def __init__(self, id: int, user_id: int, page_order: str, hidden_pages: str):
        self.id = id
        self.user_id = user_id
        self.page_order = json.loads(page_order) if page_order else []
        self.hidden_pages = json.loads(hidden_pages) if hidden_pages else []

class Database:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Database._initialized:
            return
            
        print("Initializing database...")
        self.db_path = 'lang_huu_nghi.db'
        self.backup_dir = 'database_backups'
        os.makedirs(self.backup_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        print("Creating tables...")
        self.create_tables()
        print("Creating initial admin...")
        self.create_initial_admin()
        print("Creating sample data...")
        success = self.create_sample_data()
        if success:
            print("Sample data created successfully")
        else:
            print("Sample data already exists")
        
        Database._initialized = True

    def create_tables(self):
        cursor = self.conn.cursor()

        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            family_student_id INTEGER,
            theme_preference TEXT DEFAULT 'Chính thức',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (family_student_id) REFERENCES students (id)
        )
        ''')

        # Execute the ALTER TABLE statement within a try-except block
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN family_student_id INTEGER REFERENCES students(id)")
            cursor.execute("ALTER TABLE users ADD COLUMN theme_preference TEXT DEFAULT 'Chính thức'")
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            cursor.execute("ALTER TABLE users ADD COLUMN dark_mode BOOLEAN DEFAULT FALSE")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"Note: {str(e)}")

        # Classes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            academic_year TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
        ''')

        # Students table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            birth_date DATE,
            gender TEXT,
            phone TEXT,
            address TEXT,
            email TEXT,
            admission_date DATE,
            class_id INTEGER,
            year TEXT,
            parent_name TEXT,
            profile_image BLOB,
            decision_number TEXT,
            nha_chu_t_info TEXT,
            health_on_admission TEXT,
            initial_characteristics TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
        ''')

        # Family information table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS families (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            guardian_name TEXT NOT NULL,
            relationship TEXT NOT NULL,
            occupation TEXT,
            address TEXT,
            phone TEXT,
            household_status TEXT,
            support_status TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
        ''')

        # Veterans table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS veterans (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            birth_date DATE NOT NULL,
            service_period TEXT,
            health_condition TEXT,
            address TEXT,
            email TEXT,
            contact_info TEXT,
            profile_image BLOB,
            initial_characteristics TEXT
        )
        ''')

        # Periodic assessments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS periodic_assessments (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            academic_performance TEXT,
            health_condition TEXT,
            social_behavior TEXT,
            teacher_notes TEXT,
            doctor_notes TEXT,
            counselor_notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
        ''')

        # Support records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS supports (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            support_type TEXT NOT NULL,
            amount REAL,
            start_date DATE NOT NULL,
            end_date DATE,
            approval_status TEXT NOT NULL,
            approved_by INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
        ''')

        # Medical records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            patient_type TEXT NOT NULL,
            diagnosis TEXT,
            treatment TEXT,
            doctor_id INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            notification_sent BOOLEAN DEFAULT FALSE,
            is_routine_checkup BOOLEAN DEFAULT FALSE,
            requested_by_family BOOLEAN DEFAULT FALSE,
            emergency_case BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
        ''')

        # Psychological evaluations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS psychological_evaluations (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            evaluator_id INTEGER NOT NULL,
            assessment TEXT,
            recommendations TEXT,
            follow_up_date DATE,
            notification_sent BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (evaluator_id) REFERENCES users (id)
        )
        ''')

        # Sidebar preferences table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sidebar_preferences (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            page_order TEXT,  -- JSON array of page names in order
            hidden_pages TEXT, -- JSON array of hidden page names
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Add student class history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_class_history (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
        ''')

        # Student notes table for teacher notes about students
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_notes (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            class_id INTEGER,
            content TEXT NOT NULL,
            note_type TEXT DEFAULT 'Khác',
            is_important BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (teacher_id) REFERENCES users (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
        ''')

        # Document files table for hồ sơ quá trình
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_files (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_data BLOB NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by INTEGER NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'profile',
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
        ''')

        # Add new columns to existing tables
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN decision_number TEXT")
            cursor.execute("ALTER TABLE students ADD COLUMN nha_chu_t_info TEXT")
            cursor.execute("ALTER TABLE students ADD COLUMN health_on_admission TEXT")

            cursor.execute("ALTER TABLE students ADD COLUMN initial_characteristics TEXT")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"Note: {str(e)}")

        # Add original_password column to users table for admin viewing
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN original_password TEXT")
            
            # Don't set default passwords - they will be captured on next login
            print("Added original_password column. Passwords will be captured on user login.")
            
            self.conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"Note: {str(e)}")

        try:
            cursor.execute("ALTER TABLE medical_records ADD COLUMN is_routine_checkup BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE medical_records ADD COLUMN requested_by_family BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE medical_records ADD COLUMN emergency_case BOOLEAN DEFAULT FALSE")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"Note: {str(e)}")

        self.conn.commit()

    def backup_database(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of the current database"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_name or f"backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_file)

            # Close current connection
            self.conn.close()

            # Copy database file
            shutil.copy2(self.db_path, backup_path)

            # Reopen connection
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)

            return backup_path
        except Exception as e:
            print(f"Backup error: {str(e)}")
            # Ensure connection is reopened even if backup fails
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            raise e

    def restore_database(self, backup_path: str) -> bool:
        """Restore database from a backup file"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError("Backup file not found")

            # Close current connection
            self.conn.close()

            # Replace current database with backup
            shutil.copy2(backup_path, self.db_path)

            # Reopen connection
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)

            return True
        except Exception as e:
            print(f"Restore error: {str(e)}")
            # Ensure connection is reopened even if restore fails
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            raise e

    def get_available_backups(self) -> List[tuple]:
        """Get list of available database backups"""
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.db'):
                    path = os.path.join(self.backup_dir, file)
                    timestamp = datetime.fromtimestamp(os.path.getctime(path))
                    size = os.path.getsize(path) / (1024 * 1024)  # Size in MB
                    backups.append((file, timestamp, f"{size:.2f} MB"))
            return sorted(backups, key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"Error listing backups: {str(e)}")
            return []

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, username, password_hash, role, full_name, email, 
                       COALESCE(family_student_id, NULL) as family_student_id,
                       COALESCE(theme_preference, 'Chính thức') as theme_preference,
                       COALESCE(created_at, CURRENT_TIMESTAMP) as created_at
                FROM users WHERE username = ?
            """, (username,))
            result = cursor.fetchone()
            return User(*result) if result else None
        except sqlite3.OperationalError as e:
            print(f"Database error in get_user_by_username: {e}")
            # Return minimal user object if columns are missing
            cursor.execute("SELECT id, username, password_hash, role, full_name, email FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    password_hash=result[2],
                    role=result[3],
                    full_name=result[4],
                    email=result[5],
                    family_student_id=None,
                    theme_preference='Chính thức',
                    created_at=datetime.now()
                )
            return None

    def add_user(self, username: str, password: str, role: str, full_name: str, family_student_id: Optional[int] = None) -> bool:
        try:
            cursor = self.conn.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Store both the hash and original password for admin viewing
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, full_name, family_student_id, original_password) VALUES (?, ?, ?, ?, ?, ?)",
                (username, password_hash, role, full_name, family_student_id, password)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_students(self, user_role: Optional[str] = None, family_student_id: Optional[int] = None) -> List[Student]:
        """Get list of students with role-based access control"""
        cursor = self.conn.cursor()

        if user_role == 'family' and family_student_id:
            # Family users can only see their assigned student
            cursor.execute("SELECT * FROM students WHERE id = ?", (family_student_id,))
        else:
            # Other roles can see all students
            cursor.execute("SELECT * FROM students")
            
        # In ra thông tin của column names để debug
        column_names = [description[0] for description in cursor.description]
        print(f"DB Columns: {column_names}")
        
        # Lấy tất cả các hàng
        rows = cursor.fetchall()
        
        # Tạo danh sách học sinh
        students = []
        for row in rows:
            # Tạo một map để truy cập dữ liệu theo tên cột
            row_data = dict(zip(column_names, row))
            
            # Chuyển đổi ngôn ngữ nếu cần
            if get_current_language() == 'en':
                # Dịch gender
                if row_data['gender']:
                    row_data['gender'] = translate_value(row_data['gender'])
            
            # Tạo đối tượng Student với các tham số đúng theo thứ tự khai báo trong class
            student = Student(
                id=row_data['id'],
                full_name=row_data['full_name'],
                birth_date=row_data['birth_date'],
                address=row_data['address'],
                email=row_data['email'],
                admission_date=row_data['admission_date'],
                class_id=row_data['class_id'],
                profile_image=row_data['profile_image'],
                gender=row_data['gender'],
                phone=row_data['phone'],
                year=row_data['year'],
                parent_name=row_data['parent_name']
            )
            
            # Thêm các trường mới vào đối tượng student
            student.decision_number = row_data.get('decision_number', '')
            student.nha_chu_t_info = row_data.get('nha_chu_t_info', '')
            student.health_on_admission = row_data.get('health_on_admission', '')
            student.initial_characteristics = row_data.get('initial_characteristics', '')
            

            
            students.append(student)
        
        return students

    def get_veterans(self) -> List[Veteran]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM veterans")
        
        # Chuyển đổi dữ liệu nếu ngôn ngữ là tiếng Anh
        if get_current_language() == 'en':
            veterans = []
            for row in cursor.fetchall():
                # Tạo danh sách mới với các giá trị đã được dịch
                translated_row = list(row)
                # Dịch health_condition (index 4)
                if row[4]:
                    translated_row[4] = translate_value(row[4])
                veterans.append(Veteran(*translated_row))
            return veterans
        else:
            return [Veteran(*row) for row in cursor.fetchall()]

    def get_students_for_selection(self, user_role: Optional[str] = None, family_student_id: Optional[int] = None) -> List[tuple]:
        """Get a list of students with their IDs for selection"""
        cursor = self.conn.cursor()

        if user_role == 'family' and family_student_id:
            # Family users can only select their assigned student
            cursor.execute(
                "SELECT id, full_name FROM students WHERE id = ? ORDER BY full_name",
                (family_student_id,)
            )
        else:
            # Other roles can select any student
            cursor.execute("SELECT id, full_name FROM students ORDER BY full_name")

        return cursor.fetchall()

    def get_veterans_for_selection(self) -> List[tuple]:
        """Get a list of veterans with their IDs for selection"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, full_name FROM veterans ORDER BY full_name")
        return cursor.fetchall()

    def add_medical_record(self, record_data: dict) -> Optional[int]:
        """Add a new medical record to the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO medical_records (
                    patient_id, patient_type, diagnosis, treatment,
                    doctor_id, notes, is_routine_checkup, 
                    requested_by_family, emergency_case
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_data["patient_id"],
                record_data["patient_type"],
                record_data["diagnosis"],
                record_data["treatment"],
                record_data["doctor_id"],
                record_data.get("notes"),
                record_data.get("is_routine_checkup", False),
                record_data.get("requested_by_family", False),
                record_data.get("emergency_case", False)
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding medical record: {e}")
            self.conn.rollback()
            raise e

    def add_psychological_evaluation(self, eval_data) -> int:
        """Add a new psychological evaluation record.
        Accepts either a PsychologicalEvaluation object or a dictionary with evaluation data.
        """
        cursor = self.conn.cursor()
        try:
            # Check if eval_data is a dictionary or a PsychologicalEvaluation object
            if isinstance(eval_data, dict):
                student_id = eval_data["student_id"]
                evaluator_id = eval_data["evaluator_id"]
                assessment = eval_data["assessment"]
                recommendations = eval_data["recommendations"]
                follow_up_date = eval_data["follow_up_date"]
            else:
                # Assume it's a PsychologicalEvaluation object
                student_id = eval_data.student_id
                evaluator_id = eval_data.evaluator_id
                assessment = eval_data.assessment
                recommendations = eval_data.recommendations
                follow_up_date = eval_data.follow_up_date
            
            cursor.execute(
                """INSERT INTO psychological_evaluations 
                (student_id, evaluator_id, assessment, recommendations, follow_up_date)
                VALUES (?, ?, ?, ?, ?)""",
                (student_id, evaluator_id, assessment, recommendations, follow_up_date)
            )
            self.conn.commit()
            last_id = cursor.lastrowid
            if last_id is None:
                return 0  # Trả về 0 nếu không thể lấy được ID (trường hợp lỗi)
            return last_id
        except Exception as e:
            print(f"Error adding psychological evaluation: {e}")
            self.conn.rollback()
            raise e

    def send_medical_record_notification(self, record_id: int) -> bool:
        """Send notification for medical record and update notification status."""
        cursor = self.conn.cursor()
        try:
            # Get record details
            cursor.execute("""
                SELECT mr.*, u.full_name as doctor_name,
                CASE 
                    WHEN mr.patient_type = 'student' THEN s.email
                    WHEN mr.patient_type = 'veteran' THEN v.email
                END as patient_email
                FROM medical_records mr
                JOIN users u ON mr.doctor_id = u.id
                LEFT JOIN students s ON mr.patient_id = s.id AND mr.patient_type = 'student'
                LEFT JOIN veterans v ON mr.patient_id = v.id AND mr.patient_type = 'veteran'
                WHERE mr.id = ?
            """, (record_id,))
            record = cursor.fetchone()

            if record and record[-1]:  # If we have patient email
                from email_utils import send_medical_notification
                
                # Convert string to datetime if needed for date formatting
                appointment_date = record[6]  # This is the date field
                if isinstance(appointment_date, str):
                    try:
                        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d')
                        except ValueError:
                            appointment_date = datetime.now()  # Fallback to current time
                
                formatted_date = appointment_date.strftime("%Y-%m-%d %H:%M") if hasattr(appointment_date, 'strftime') else str(appointment_date)
                
                success = send_medical_notification(
                    patient_email=record[-1],
                    appointment_date=formatted_date,
                    doctor_name=record[-2]
                )
                if success:
                    cursor.execute(
                        "UPDATE medical_records SET notification_sent = TRUE WHERE id = ?",
                        (record_id,)
                    )
                    self.conn.commit()
                return success
        except Exception as e:
            print(f"Error sending medical notification: {e}")
            return False
        return False

    def send_psychological_evaluation_notification(self, eval_id: int) -> bool:
        """Send notification for psychological evaluation and update notification status."""
        cursor = self.conn.cursor()
        try:
            # Get evaluation details
            cursor.execute("""
                SELECT pe.*, u.full_name as counselor_name, s.email as student_email
                FROM psychological_evaluations pe
                JOIN users u ON pe.evaluator_id = u.id
                JOIN students s ON pe.student_id = s.id
                WHERE pe.id = ?
            """, (eval_id,))
            eval_record = cursor.fetchone()

            if eval_record and eval_record[-1]:  # If we have student email
                from email_utils import send_psychological_notification

                # Convert string to datetime if needed
                evaluation_date = eval_record[2]
                if isinstance(evaluation_date, str):
                    evaluation_date = datetime.strptime(evaluation_date, '%Y-%m-%d %H:%M:%S')

                success = send_psychological_notification(
                    student_email=eval_record[-1],
                    evaluation_date=evaluation_date.strftime("%Y-%m-%d %H:%M"),
                    counselor_name=eval_record[-2]
                )
                if success:
                    cursor.execute(
                        "UPDATE psychological_evaluations SET notification_sent = TRUE WHERE id = ?",
                        (eval_id,)
                    )
                    self.conn.commit()
                return success
        except Exception as e:
            print(f"Error sending psychological notification: {e}")
            return False
        return False

    def create_initial_admin(self):
        """Create an initial admin user if no users exist."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            # Create default admin user
            username = "admin"
            password = "admin123"
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, "admin", "System Administrator", "admin@langhunghi.edu.vn"))
            self.conn.commit()
            return True
        return False

    def create_sample_data(self):
        """Create sample data for testing and demonstration."""
        cursor = self.conn.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 1:  # If we have more than just admin
            print("Sample data already exists")
            return False

        try:
            print("Creating sample users...")
            # Create sample users first
            users = [
                # Teachers
                ("giaovien1", "password123", "teacher", "Giáo viên Nguyễn Văn A", "giaovien1@langhunghi.edu.vn"),
                ("giaovien2", "password123", "teacher", "Giáo viên Trần Thị B", "giaovien2@langhunghi.edu.vn"),
                ("giaovien3", "password123", "teacher", "Giáo viên Lê Văn C", "giaovien3@langhunghi.edu.vn"),

                # Doctors
                ("bacsi1", "password123", "doctor", "Bác sĩ Phạm Thị D", "bacsi1@langhunghi.edu.vn"),
                ("bacsi2", "password123", "doctor", "Bác sĩ Hoàng Văn E", "bacsi2@langhunghi.edu.vn"),

                # Nurses
                ("yta1", "password123", "nurse", "Y tá Vũ Thị F", "yta1@langhunghi.edu.vn"),
                ("yta2", "password123", "nurse", "Y tá Đỗ Văn G", "yta2@langhunghi.edu.vn"),

                # Counselors
                ("tuvan1", "password123", "counselor", "Tư vấn Trịnh Thị H", "tuvan1@langhunghi.edu.vn"),
                ("tuvan2", "password123", "counselor", "Tư vấn Mai Văn I", "tuvan2@langhunghi.edu.vn"),

                # Administrative staff
                ("vanphong1", "password123", "administrative", "Nhân viên Bùi Thị K", "vanphong1@langhunghi.edu.vn"),
                ("vanphong2", "password123", "administrative", "Nhân viên Ngô Văn L", "vanphong2@langhunghi.edu.vn")
            ]

            for username, password, role, full_name, email in users:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, full_name, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, password_hash, role, full_name, email))

            print("Creating sample classes...")
            # Create sample classes
            classes = [
                ("Lớp 10A", 1, "2023-2024", "Lớp chất lượng cao"),
                ("Lớp 10B", 2, "2023-2024", "Lớp thường"),
                ("Lớp 11A", 3, "2023-2024", "Lớp chuyên Anh")
            ]

            for name, teacher_id, year, notes in classes:
                cursor.execute("""
                    INSERT INTO classes (name, teacher_id, academic_year, notes)
                    VALUES (?, ?, ?, ?)
                """, (name, teacher_id, year, notes))

            print("Creating sample students...")
            # Create sample students
            students = [
                ("Nguyễn Văn Học", "2000-01-15", "Hà Nội", "student1@langhunghi.edu.vn", "2023-09-01", 1, "Tốt", "Xuất sắc", "Ổn định"),
                ("Trần Thị Mai", "2001-03-20", "Hải Phòng", "student2@langhunghi.edu.vn", "2023-09-01", 1, "Bình thường", "Tốt", "Tốt"),
                ("Lê Văn Nam", "2000-07-10", "Đà Nẵng", "student3@langhunghi.edu.vn", "2023-09-01", 2, "Cần chú ý", "Trung bình", "Cần theo dõi"),
                ("Phạm Thị Hoa", "2001-05-25", "Huế", "student4@langhunghi.edu.vn", "2023-09-01", 2, "Tốt", "Khá", "Ổn định"),
                ("Hoàng Văn Thành", "2000-11-30", "Nghệ An", "student5@langhunghi.edu.vn", "2023-09-01", 3, "Bình thường", "Xuất sắc", "Tốt")
            ]

            for name, birth, addr, email, admission, class_id in [(s[0], s[1], s[2], s[3], s[4], s[5]) for s in students]:
                cursor.execute("""
                    INSERT INTO students (
                        full_name, birth_date, address, email,
                        admission_date, class_id
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (name, birth, addr, email, admission, class_id))

            print("Creating sample family users...")
            # Create family users linked to students
            family_users = [
                ("phuhuynh1", "123456", "Phụ huynh Nguyễn Văn Học", 1),
                ("phuhuynh2", "123456", "Phụ huynh Trần Thị Mai", 2),
                ("phuhuynh3", "123456", "Phụ huynh Lê Văn Nam", 3)
            ]

            for username, password, full_name, student_id in family_users:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, full_name, family_student_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, password_hash, "family", full_name, student_id))

            print("Committing changes...")
            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error creating sample data: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False

    def save_student_image(self, student_id: int, image_data: bytes) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE students SET profile_image = ? WHERE id = ?",
                (image_data, student_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving student image: {e}")
            return False

    def save_veteran_image(self, veteran_id: int, image_data: bytes) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE veterans SET profile_image = ? WHERE id = ?",
                (image_data, veteran_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving veteran image: {e}")
            return False

    def get_student_image(self, student_id: int) -> Optional[bytes]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT profile_image FROM students WHERE id = ?", (student_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_veteran_image(self, veteran_id: int) -> Optional[bytes]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT profile_image FROM veterans WHERE id = ?", (veteran_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def search_students(self, query: dict) -> List[Student]:
        """Search students with filters"""
        try:
            # Chỉ định rõ các cột cần lấy thay vì SELECT *
            sql = """SELECT 
                id, full_name, birth_date, address, email, 
                admission_date, class_id, gender, phone, year, parent_name
                FROM students WHERE 1=1"""
            params = []

            if query.get('name'):
                sql += " AND full_name LIKE ?"
                params.append(f"%{query['name']}%")
                
            if query.get('address'):
                sql += " AND address LIKE ?"
                params.append(f"%{query['address']}%")
                
            if query.get('phone'):
                sql += " AND phone LIKE ?"
                params.append(f"%{query['phone']}%")
                
            if query.get('email'):
                sql += " AND email LIKE ?"
                params.append(f"%{query['email']}%")
                
            if query.get('gender') and query['gender'] != "Tất cả":
                sql += " AND gender = ?"
                params.append(query['gender'])
                
            if query.get('year'):
                sql += " AND year LIKE ?"
                params.append(f"%{query['year']}%")
                
            if query.get('parent_name'):
                sql += " AND parent_name LIKE ?"
                params.append(f"%{query['parent_name']}%")

            if query.get('class_id'):
                sql += " AND class_id = ?"
                params.append(query['class_id'])




            if query.get('from_date'):
                sql += " AND date(admission_date) >= date(?)"
                params.append(str(query['from_date']))

            if query.get('to_date'):
                sql += " AND date(admission_date) <= date(?)"
                params.append(str(query['to_date']))
                
            if query.get('birth_date_from'):
                sql += " AND date(birth_date) >= date(?)"
                params.append(str(query['birth_date_from']))
                
            if query.get('birth_date_to'):
                sql += " AND date(birth_date) <= date(?)"
                params.append(str(query['birth_date_to']))

            sql += " ORDER BY full_name"

            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            
            # Chuyển đổi dữ liệu nếu ngôn ngữ là tiếng Anh
            if get_current_language() == 'en':
                students = []
                for row in cursor.fetchall():
                    # Tạo danh sách mới với các giá trị đã được dịch
                    translated_row = list(row)
                    # Dịch gender
                    if row[2]:
                        translated_row[2] = translate_value(row[2]) 
                        translated_row[10] = translate_value(row[10])
                    students.append(Student(*translated_row))
                return students
            else:
                return [Student(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Search students error: {str(e)}")
            return []

    def search_veterans(self, query: dict) -> List[Veteran]:
        """Search veterans with filters"""
        try:
            # Chỉ định rõ các cột cần lấy thay vì SELECT *
            sql = """SELECT 
                id, full_name, birth_date, service_period, 
                health_condition, address, email, contact_info, profile_image, initial_characteristics
                FROM veterans WHERE 1=1"""
            params = []

            if query.get('name'):
                sql += " AND full_name LIKE ?"
                params.append(f"%{query['name']}%")
                
            if query.get('address'):
                sql += " AND address LIKE ?"
                params.append(f"%{query['address']}%")
                
            if query.get('email'):
                sql += " AND email LIKE ?"
                params.append(f"%{query['email']}%")
                
            if query.get('contact_info'):
                sql += " AND contact_info LIKE ?"
                params.append(f"%{query['contact_info']}%")

            if query.get('health_condition'):
                sql += " AND health_condition LIKE ?"
                params.append(f"%{query['health_condition']}%")

            if query.get('service_period'):
                sql += " AND service_period LIKE ?"
                params.append(f"%{query['service_period']}%")
                
            if query.get('birth_date_from'):
                sql += " AND date(birth_date) >= date(?)"
                params.append(str(query['birth_date_from']))
                
            if query.get('birth_date_to'):
                sql += " AND date(birth_date) <= date(?)"
                params.append(str(query['birth_date_to']))

            sql += " ORDER BY full_name"

            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            
            # Chuyển đổi dữ liệu nếu ngôn ngữ là tiếng Anh
            if get_current_language() == 'en':
                veterans = []
                for row in cursor.fetchall():
                    # Tạo danh sách mới với các giá trị đã được dịch
                    translated_row = list(row)
                    # Dịch health_condition (index 4)
                    if row[4]:
                        translated_row[4] = translate_value(row[4])
                    veterans.append(Veteran(*translated_row))
                return veterans
            else:
                return [Veteran(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Search veterans error: {str(e)}")
            return []

    def search_medical_records(self, query: dict) -> List[dict]:
        """Search medical records with filters"""
        try:
            sql = """
                SELECT mr.*, 
                    u.full_name as doctor_name,
                    CASE 
                        WHEN mr.patient_type = 'student' THEN s.full_name
                        WHEN mr.patient_type = 'veteran' THEN v.full_name
                    END as patient_name
                FROM medical_records mr
                JOIN users u ON mr.doctor_id = u.id
                LEFT JOIN students s ON mr.patient_id = s.id AND mr.patient_type = 'student'
                LEFT JOIN veterans v ON mr.patient_id = v.id AND mr.patient_type = 'veteran'
                WHERE 1=1
            """
            params = []

            if query.get('patient_name'):
                sql += """ AND (
                    (mr.patient_type = 'student' AND s.full_name LIKE ?) OR
                    (mr.patient_type = 'veteran' AND v.full_name LIKE ?)
                )"""
                params.extend([f"%{query['patient_name']}%"] * 2)

            if query.get('diagnosis'):
                sql += " AND mr.diagnosis LIKE ?"
                params.append(f"%{query['diagnosis']}%")

            if query.get('from_date'):
                sql += " AND date(mr.date) >= date(?)"
                params.append(str(query['from_date']))

            if query.get('to_date'):
                sql += " AND date(mr.date) <= date(?)"
                params.append(str(query['to_date']))

            if query.get('doctor_id'):
                sql += " AND mr.doctor_id = ?"
                params.append(query['doctor_id'])

            sql += " ORDER BY mr.date DESC"

            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"Search medical records error: {str(e)}")
            return []

    def search_psychological_evaluations(self, query: dict) -> List[dict]:
        """Search psychological evaluations with filters"""
        try:
            sql = """
                SELECT pe.*, u.full_name as evaluator_name, s.full_name as student_name
                FROM psychological_evaluations pe
                JOIN users u ON pe.evaluator_id = u.id
                JOIN students s ON pe.student_id = s.id
                WHERE 1=1
            """
            params = []

            if query.get('student_name'):
                sql += " AND s.full_name LIKE ?"
                params.append(f"%{query['student_name']}%")

            if query.get('assessment'):
                sql += " AND pe.assessment LIKE ?"
                params.append(f"%{query['assessment']}%")

            if query.get('from_date'):
                sql += " AND date(pe.evaluation_date) >= date(?)"
                params.append(str(query['from_date']))

            if query.get('to_date'):
                sql += " AND date(pe.evaluation_date) <= date(?)"
                params.append(str(query['to_date']))

            if query.get('evaluator_id'):
                sql += " AND pe.evaluator_id = ?"
                params.append(query['evaluator_id'])

            sql += " ORDER BY pe.evaluation_date DESC"

            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"Search psychological evaluations error: {str(e)}")
            return []

    def add_student(self, student_data: dict) -> int:
        """Add a new student to the database"""
        try:
            cursor = self.conn.cursor()

            # Set default admission date to today if not provided
            if not student_data.get("admission_date"):
                student_data["admission_date"] = datetime.now().strftime("%Y-%m-%d")

            # Validate and format birth date if provided
            birth_date = student_data.get("birth_date")
            if birth_date and isinstance(birth_date, str):
                try:
                    # Try different date formats
                    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%Y"]:
                        try:
                            parsed_date = datetime.strptime(birth_date, fmt)
                            if fmt == "%Y":
                                # If only year provided, set to January 1st
                                parsed_date = parsed_date.replace(month=1, day=1)
                            student_data["birth_date"] = parsed_date.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                    # Only raise error if birth_date was provided but invalid
                    if birth_date and not student_data.get("birth_date"):
                        raise ValueError(f"Không thể nhận dạng định dạng ngày sinh: {birth_date}. Vui lòng sử dụng một trong các định dạng: DD/MM/YYYY, YYYY-MM-DD, hoặc YYYY.")
                except Exception as e:
                    raise ValueError(f"Lỗi khi xử lý ngày sinh: {str(e)}")
            # Allow birth_date to be None (empty)
            
            # Kiểm tra xem học sinh có tồn tại chưa (dựa vào tên)
            student_name = student_data.get("full_name")
            cursor.execute("SELECT id FROM students WHERE full_name = ?", (student_name,))
            existing_student = cursor.fetchone()
            
            if existing_student:
                # Nếu học sinh đã tồn tại, xóa bản ghi cũ và thêm mới
                student_id = existing_student[0]
                print(f"Tìm thấy học sinh trùng tên: {student_name} (ID: {student_id}). Cập nhật thông tin mới.")
                
                # Xóa bản ghi cũ
                cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))

            # In ra thứ tự trường dữ liệu khi thêm mới
            print("INSERT students order:")
            print("1. full_name:", student_data["full_name"])
            print("2. birth_date:", student_data.get("birth_date"))
            print("3. address:", student_data.get("address", ""))
            print("4. email:", student_data.get("email", ""))
            print("5. admission_date:", student_data["admission_date"])
            print("6. class_id:", student_data.get("class_id"))

            print("10. profile_image:", None)
            print("11. gender:", student_data.get("gender", ""))
            print("12. phone:", student_data.get("phone", ""))
            print("13. year:", student_data.get("year", ""))
            print("14. parent_name:", student_data.get("parent_name", ""))
            
            # Thêm học sinh mới (hoặc bản ghi cập nhật)
            cursor.execute("""
                INSERT INTO students (
                    full_name, birth_date, address, email,
                    admission_date, class_id, profile_image,
                    gender, phone, year, parent_name,
                    decision_number, nha_chu_t_info, health_on_admission,
                    initial_characteristics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_data["full_name"],
                student_data.get("birth_date"),  # Now can be None
                student_data.get("address", ""),
                student_data.get("email", ""),
                student_data["admission_date"],
                student_data.get("class_id"),

                None,  # profile_image
                student_data.get("gender", ""),
                student_data.get("phone", ""),
                student_data.get("year", ""),
                student_data.get("parent_name", ""),
                student_data.get("decision_number", ""),
                student_data.get("nha_chu_t_info", ""),
                student_data.get("health_on_admission", ""),
                student_data.get("initial_characteristics", "")
            ))
            self.conn.commit()
            # Trả về ID của bản ghi mới thêm, đảm bảo không trả về None
            new_id = cursor.lastrowid
            return new_id if new_id is not None else 0
        except Exception as e:
            print(f"Error adding student: {e}")
            self.conn.rollback()
            raise e

    def get_class(self, class_id: int) -> Optional[Class]:
        """Get class information by ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, teacher_id, academic_year, notes 
            FROM classes WHERE id = ?
        """, (class_id,))
        result = cursor.fetchone()
        return Class(*result) if result else None

    def get_classes(self) -> List[Class]:
        """Get all classes"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, teacher_id, academic_year, notes 
            FROM classes ORDER BY name
        """)
        return [Class(*row) for row in cursor.fetchall()]

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, username, password_hash, role, full_name, email, 
                       COALESCE(family_student_id, NULL) as family_student_id,
                       COALESCE(theme_preference, 'Chính thức') as theme_preference,
                       COALESCE(created_at, CURRENT_TIMESTAMP) as created_at
                FROM users WHERE id = ?
            """, (user_id,))
            result = cursor.fetchone()
            return User(*result) if result else None
        except sqlite3.OperationalError as e:
            print(f"Database error in get_user_by_id: {e}")
            # Return minimal user object if columns are missing
            cursor.execute("SELECT id, username, password_hash, role, full_name, email FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    password_hash=result[2],
                    role=result[3],
                    full_name=result[4],
                    email=result[5],
                    family_student_id=None,
                    theme_preference='Chính thức',
                    created_at=datetime.now()
                )
            return None

    def get_students_by_class(self, class_id: int) -> List[Student]:
        """Get all students in a class"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                id, full_name, birth_date, address, email, 
                admission_date, class_id, profile_image, gender, phone, year, parent_name,
                decision_number, nha_chu_t_info, health_on_admission, initial_characteristics
            FROM students 
            WHERE class_id = ? 
            ORDER BY full_name
        """, (class_id,))
        
        # In ra thông tin của column names để debug
        column_names = [description[0] for description in cursor.description]
        print(f"DB Columns (get_students_by_class): {column_names}")
        
        # Lấy tất cả các hàng
        rows = cursor.fetchall()
        
        # Tạo danh sách học sinh
        students = []
        for row in rows:
            # Tạo một map để truy cập dữ liệu theo tên cột
            row_data = dict(zip(column_names, row))
            
            # Chuyển đổi ngôn ngữ nếu cần
            if get_current_language() == 'en':
                # Dịch gender
                if row_data['gender']:
                    row_data['gender'] = translate_value(row_data['gender'])
            
            # Tạo đối tượng Student với các tham số đúng theo thứ tự khai báo trong class
            student = Student(
                id=row_data['id'],
                full_name=row_data['full_name'],
                birth_date=row_data['birth_date'],
                address=row_data['address'],
                email=row_data['email'],
                admission_date=row_data['admission_date'],
                class_id=row_data['class_id'],
                profile_image=row_data['profile_image'],
                gender=row_data['gender'],
                phone=row_data['phone'],
                year=row_data['year'],
                parent_name=row_data['parent_name'],
                decision_number=row_data['decision_number'],
                nha_chu_t_info=row_data['nha_chu_t_info'],
                health_on_admission=row_data['health_on_admission'],
                initial_characteristics=row_data['initial_characteristics']
            )
            students.append(student)
        
        return students
    
    def update_student(self, student_id: int, student_data: dict) -> bool:
        """Update student information"""
        try:
            cursor = self.conn.cursor()
            update_fields = []
            params = []

            # Build update query dynamically based on provided fields
            if "full_name" in student_data:
                update_fields.append("full_name = ?")
                params.append(student_data["full_name"])
            if "birth_date" in student_data:
                update_fields.append("birth_date = ?")
                params.append(student_data["birth_date"])
            if "gender" in student_data:
                update_fields.append("gender = ?")
                params.append(student_data["gender"])
            if "phone" in student_data:
                update_fields.append("phone = ?")
                params.append(student_data["phone"])
            if "address" in student_data:
                update_fields.append("address = ?")
                params.append(student_data["address"])
            if "email" in student_data:
                update_fields.append("email = ?")
                params.append(student_data["email"])
            if "admission_date" in student_data:
                update_fields.append("admission_date = ?")
                params.append(student_data["admission_date"])
            if "class_id" in student_data:
                update_fields.append("class_id = ?")
                params.append(student_data["class_id"])

            if "year" in student_data:
                update_fields.append("year = ?")
                params.append(student_data["year"])
            if "parent_name" in student_data:
                update_fields.append("parent_name = ?")
                params.append(student_data["parent_name"])
            if "decision_number" in student_data:
                update_fields.append("decision_number = ?")
                params.append(student_data["decision_number"])
            if "nha_chu_t_info" in student_data:
                update_fields.append("nha_chu_t_info = ?")
                params.append(student_data["nha_chu_t_info"])
            if "health_on_admission" in student_data:
                update_fields.append("health_on_admission = ?")
                params.append(student_data["health_on_admission"])
            if "initial_characteristics" in student_data:
                update_fields.append("initial_characteristics = ?")
                params.append(student_data["initial_characteristics"])

            if not update_fields:
                return False

            query = f"UPDATE students SET {', '.join(update_fields)} WHERE id = ?"
            params.append(student_id)

            cursor.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            self.conn.rollback()
            return False

    def update_veteran(self, veteran_id: int, veteran_data: dict) -> bool:
        """Update veteran information"""
        try:
            cursor = self.conn.cursor()
            update_fields = []
            params = []

            # Build update query dynamically based on provided fields
            if "full_name" in veteran_data:
                update_fields.append("full_name = ?")
                params.append(veteran_data["full_name"])
            if "birth_date" in veteran_data:
                update_fields.append("birth_date = ?")
                params.append(veteran_data["birth_date"])
            if "service_period" in veteran_data:
                update_fields.append("service_period = ?")
                params.append(veteran_data["service_period"])
            if "health_condition" in veteran_data:
                update_fields.append("health_condition= ?")
                params.append(veteran_data["health_condition"])
            if "address" in veteran_data:
                update_fields.append("address = ?")
                params.append(veteran_data["address"])
            if "email" in veteran_data:
                update_fields.append("email = ?")
                params.append(veteran_data["email"])
            if "contact_info" in veteran_data:
                update_fields.append("contact_info = ?")
                params.append(veteran_data["contact_info"])
            if "initial_characteristics" in veteran_data:
                update_fields.append("initial_characteristics = ?")
                params.append(veteran_data["initial_characteristics"])

            if not update_fields:
                return False

            query = f"UPDATE veterans SET {', '.join(update_fields)} WHERE id = ?"
            params.append(veteran_id)

            cursor.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating veteran: {e}")
            self.conn.rollback()
            return False

    def add_veteran(self, veteran_data: dict) -> int:
        """Add a new veteran to the database and return their ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO veterans (
                    full_name, birth_date, service_period,
                    health_condition, address, email, contact_info, initial_characteristics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                veteran_data["full_name"],
                veteran_data["birth_date"],
                veteran_data["service_period"],
                veteran_data["health_condition"],
                veteran_data["address"],
                veteran_data["email"],
                veteran_data["contact_info"],
                veteran_data.get("initial_characteristics", "")
            ))
            self.conn.commit()
            # Đảm bảo không trả về None
            new_id = cursor.lastrowid
            return new_id if new_id is not None else 0
        except Exception as e:
            print(f"Error adding veteran: {e}")
            self.conn.rollback()
            return 0

    def get_user_sidebar_preferences(self, user_id: int) -> Optional[SidebarPreference]:
        """Get user's sidebar preferences"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, user_id, page_order, hidden_pages FROM sidebar_preferences WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return SidebarPreference(*result) if result else None

    def save_user_sidebar_preferences(self, user_id: int, page_order: List[str], hidden_pages: List[str]) -> bool:
        """Save or update user's sidebar preferences"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sidebar_preferences (user_id, page_order, hidden_pages)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    page_order = excluded.page_order,
                    hidden_pages = excluded.hidden_pages
            """, (
                user_id,
                json.dumps(page_order),
                json.dumps(hidden_pages)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving sidebar preferences: {e}")
            return False

    def get_available_pages(self, user_role: str) -> List[Dict[str, str]]:
        """Get list of available pages based on user role"""
        from translations import get_text, get_current_language
        pages = []

        # Translation keys for groups
        group_management = get_text("groups.management", "Quản trị hệ thống")
        group_support = get_text("groups.support", "Hỗ trợ & Theo dõi")
        group_users = get_text("groups.users", "Quản lý người dùng")
        
        # Pages based on user roles - dynamically filtered
        if user_role in ['admin', 'administrative']:
            # Admin users have access to all pages
            pages.extend([
                {"id": "01_Quản_lý_Hệ_thống", "name": "Quản lý Hệ thống", "group": group_management, "path": "pages/01_Quản_lý_Hệ_thống.py"},
                {"id": "02_Quản_lý_hồ_sơ", "name": "Quản lý hồ sơ", "group": group_users, "path": "pages/02_Quản_lý_hồ_sơ.py"},
                {"id": "03_Y_tế", "name": "Y tế", "group": group_support, "path": "pages/03_Y_tế.py"},
                {"id": "04_Lớp_học", "name": "Lớp học", "group": group_users, "path": "pages/04_Lớp_học.py"},
            ])
        
        elif user_role == 'teacher':
            # Teachers can access class management and student profiles
            pages.extend([
                {"id": "02_Quản_lý_hồ_sơ", "name": "Quản lý hồ sơ", "group": group_users, "path": "pages/02_Quản_lý_hồ_sơ.py"},
                {"id": "04_Lớp_học", "name": "Lớp học", "group": group_users, "path": "pages/04_Lớp_học.py"},
            ])
        
        elif user_role in ['doctor', 'nurse']:
            # Medical staff can access medical records and student profiles
            pages.extend([
                {"id": "02_Quản_lý_hồ_sơ", "name": "Quản lý hồ sơ", "group": group_users, "path": "pages/02_Quản_lý_hồ_sơ.py"},
                {"id": "03_Y_tế", "name": "Y tế", "group": group_support, "path": "pages/03_Y_tế.py"},
            ])
        
        elif user_role == 'counselor':
            # Counselors can access student profiles for psychological evaluations
            pages.extend([
                {"id": "02_Quản_lý_hồ_sơ", "name": "Quản lý hồ sơ", "group": group_users, "path": "pages/02_Quản_lý_hồ_sơ.py"},
            ])
        
        elif user_role == 'family':
            # Family users only see their child's class information
            pages.extend([
                {"id": "04_Lớp_học", "name": "Lớp học", "group": group_users, "path": "pages/04_Lớp_học.py"},
            ])
        
        return pages

    def update_class(self, class_id: int, class_data: dict) -> bool:
        """Update class information"""
        try:
            cursor = self.conn.cursor()
            update_fields = []
            params = []

            # Build update query dynamically based on provided fields
            if "name" in class_data:
                update_fields.append("name = ?")
                params.append(class_data["name"])
            if "teacher_id" in class_data:
                update_fields.append("teacher_id = ?")
                params.append(class_data["teacher_id"])
            if "academic_year" in class_data:
                update_fields.append("academic_year = ?")
                params.append(class_data["academic_year"])
            if "notes" in class_data:
                update_fields.append("notes = ?")
                params.append(class_data["notes"])

            if not update_fields:
                return False

            query = f"UPDATE classes SET {', '.join(update_fields)} WHERE id = ?"
            params.append(class_id)

            cursor.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating class: {e}")
            self.conn.rollback()
            return False

    def add_class(self, class_data: dict) -> int:
        """Add a new class"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO classes (name, teacher_id, academic_year, notes)
                VALUES (?, ?, ?, ?)
            """, (
                class_data["name"],
                class_data["teacher_id"],
                class_data["academic_year"],
                class_data.get("notes", "")
            ))
            self.conn.commit()
            # Trả về ID của lớp mới thêm, đảm bảo không trả về None
            new_id = cursor.lastrowid
            return new_id if new_id is not None else 0
        except Exception as e:
            print(f"Error adding class: {e}")
            self.conn.rollback()
            raise e

    def get_teachers(self) -> List[User]:
        """Get list of teachers"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, username, password_hash, role, full_name, email,
                       COALESCE(family_student_id, NULL) as family_student_id,
                       COALESCE(theme_preference, 'Chính thức') as theme_preference,
                       COALESCE(created_at, CURRENT_TIMESTAMP) as created_at
                FROM users WHERE role = 'teacher'
            """)
            return [User(*row) for row in cursor.fetchall()]
        except sqlite3.OperationalError as e:
            print(f"Database error in get_teachers: {e}")
            # Return minimal user objects if columns are missing
            cursor.execute("SELECT id, username, password_hash, role, full_name, email FROM users WHERE role = 'teacher'")
            results = cursor.fetchall()
            return [
                User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    role=row[3],
                    full_name=row[4],
                    email=row[5],
                    family_student_id=None,
                    theme_preference='Chính thức',
                    created_at=datetime.now()
                ) for row in results
            ]

    def update_student_class(self, student_id: int, new_class_id: Optional[int]) -> bool:
        """Update a student's class assignment and record the change in history"""
        try:
            cursor = self.conn.cursor()

            # Get current class
            cursor.execute(
                "SELECT class_id FROM students WHERE id = ?",
                (student_id,)
            )
            current_class = cursor.fetchone()
            current_class_id = current_class[0] if current_class else None

            # If there's a current class, close its history record
            if current_class_id:
                cursor.execute("""
                    UPDATE student_class_history 
                    SET end_date = date('now')
                    WHERE student_id = ? AND class_id = ? AND end_date IS NULL
                """, (student_id, current_class_id))

            # If assigning to a new class, create history record
            if new_class_id:
                cursor.execute("""
                    INSERT INTO student_class_history (
                        student_id, class_id, start_date
                    ) VALUES (?, ?, date('now'))
                """, (student_id, new_class_id))

            # Update current class
            cursor.execute(
                "UPDATE students SET class_id = ? WHERE id = ?",
                (new_class_id, student_id)
            )

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating student class: {e}")
            self.conn.rollback()
            return False

    def get_student_class_history(self, student_id: int) -> List[Dict]:
        """Get a student's class history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    sch.start_date,
                    sch.end_date,
                    c.name as class_name,
                    c.academic_year,
                    u.full_name as teacher_name
                FROM student_class_history sch
                JOIN classes c ON sch.class_id = c.id
                JOIN users u ON c.teacher_id = u.id
                WHERE sch.student_id = ?
                ORDER BY sch.start_date DESC
            """, (student_id,))

            history = []
            for row in cursor.fetchall():
                # Sử dụng translate_value để dịch 'Hiện tại' nếu language là tiếng Anh
                current_label = 'Hiện tại'
                if get_current_language() == 'en':
                    current_label = translate_value(current_label)
                    
                history.append({
                    'start_date': row[0],
                    'end_date': row[1] if row[1] else current_label,
                    'class_name': row[2],
                    'academic_year': row[3],
                    'teacher_name': row[4]
                })
            return history
        except Exception as e:
            print(f"Error getting student class history: {e}")
            return []

    def add_student_to_class(self, student_id: int, class_id: int, reason: str = "Thêm mới vào lớp") -> bool:
        """Add a student to a class with history tracking"""
        return self.update_student_class(student_id, class_id)

    def remove_student_from_class(self, student_id: int, reason: str = "Rời khỏi lớp") -> bool:
        """Remove a student from their current class"""
        try:
            cursor = self.conn.cursor()
            
            # Get current class to close history record
            cursor.execute("SELECT class_id FROM students WHERE id = ?", (student_id,))
            current_class = cursor.fetchone()
            
            if current_class and current_class[0]:
                # Close current class history record
                cursor.execute("""
                    UPDATE student_class_history 
                    SET end_date = date('now')
                    WHERE student_id = ? AND class_id = ? AND end_date IS NULL
                """, (student_id, current_class[0]))
                
                # Remove from current class
                cursor.execute("UPDATE students SET class_id = NULL WHERE id = ?", (student_id,))
                
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error removing student from class: {e}")
            self.conn.rollback()
            return False

    def get_unassigned_students(self) -> List[Student]:
        """Get students who are not assigned to any class"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, full_name, birth_date, gender, phone, address, email, 
                   admission_date, class_id, year, parent_name, profile_image,
                   decision_number, nha_chu_t_info, health_on_admission, initial_characteristics
            FROM students 
            WHERE class_id IS NULL OR class_id = 0
            ORDER BY full_name
        """)
        
        results = cursor.fetchall()
        return [Student(*row) for row in results]

    def add_student_note(self, note_data: dict) -> bool:
        """Add a note for a student"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO student_notes (
                    student_id, teacher_id, class_id, content, note_type, is_important, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                note_data['student_id'],
                note_data['teacher_id'], 
                note_data['class_id'],
                note_data['content'],
                note_data['note_type'],
                note_data['is_important'],
                note_data['created_at']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding student note: {e}")
            self.conn.rollback()
            return False

    def get_student_notes(self, student_id: int, class_id: int = None) -> List[Dict]:
        """Get notes for a student"""
        try:
            cursor = self.conn.cursor()
            if class_id:
                cursor.execute("""
                    SELECT sn.id, sn.student_id, sn.teacher_id, sn.class_id, sn.content, 
                           sn.note_type, sn.is_important, sn.created_at, u.full_name as teacher_name
                    FROM student_notes sn
                    LEFT JOIN users u ON sn.teacher_id = u.id
                    WHERE sn.student_id = ? AND sn.class_id = ?
                    ORDER BY sn.created_at DESC
                """, (student_id, class_id))
            else:
                cursor.execute("""
                    SELECT sn.id, sn.student_id, sn.teacher_id, sn.class_id, sn.content, 
                           sn.note_type, sn.is_important, sn.created_at, u.full_name as teacher_name
                    FROM student_notes sn
                    LEFT JOIN users u ON sn.teacher_id = u.id
                    WHERE sn.student_id = ?
                    ORDER BY sn.created_at DESC
                """, (student_id,))
            
            results = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'student_id': row[1],
                    'teacher_id': row[2],
                    'class_id': row[3],
                    'content': row[4],
                    'note_type': row[5],
                    'is_important': bool(row[6]),
                    'created_at': row[7],
                    'teacher_name': row[8]
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting student notes: {e}")
            return []

    def delete_student_note(self, note_id: int) -> bool:
        """Delete a student note"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM student_notes WHERE id = ?", (note_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting student note: {e}")
            self.conn.rollback()
            return False

    def get_all_users(self) -> List[User]:
        """Get all users in the system"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, username, password_hash, role, full_name, email,
                       COALESCE(family_student_id, NULL) as family_student_id,
                       COALESCE(theme_preference, 'Chính thức') as theme_preference,
                       COALESCE(created_at, CURRENT_TIMESTAMP) as created_at
                FROM users ORDER BY id
            """)
            return [User(*row) for row in cursor.fetchall()]
        except sqlite3.OperationalError as e:
            print(f"Database error in get_all_users: {e}")
            # Return minimal user objects if columns are missing
            cursor.execute("SELECT id, username, password_hash, role, full_name, email FROM users ORDER BY id")
            results = cursor.fetchall()
            return [
                User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    role=row[3],
                    full_name=row[4],
                    email=row[5],
                    family_student_id=None,
                    theme_preference='Chính thức',
                    created_at=datetime.now()
                ) for row in results
            ]

    def update_user_original_password(self, user_id: int, password: str) -> bool:
        """Update the original password for a user when they successfully log in"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET original_password = ? WHERE id = ?",
                (password, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating original password: {e}")
            return False

    def get_user_passwords(self) -> dict:
        """Get all user passwords for admin viewing (admin only feature)"""
        cursor = self.conn.cursor()
        try:
            # Get original password from original_password field
            cursor.execute("""
                SELECT id, username, COALESCE(original_password, 'N/A') as password, full_name, role
                FROM users ORDER BY id
            """)
            password_dict = {}
            for row in cursor.fetchall():
                user_id, username, password, full_name, role = row
                password_dict[user_id] = {
                    'username': username,
                    'password': password if password != 'N/A' else 'Chưa đăng nhập hoặc tài khoản cũ',
                    'full_name': full_name,
                    'role': role
                }
            return password_dict
        except Exception as e:
            print(f"Error getting user passwords: {e}")
            return {}

    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the system"""
        try:
            cursor = self.conn.cursor()
            
            # Don't allow deleting admin user (ID=1)
            if user_id == 1:
                return False
                
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            self.conn.rollback()
            return False
    def search_student_class_history(self, student_id: Optional[int] = None, 
                                   student_name: Optional[str] = None,
                                   from_date: Optional[str] = None,
                                   to_date: Optional[str] = None) -> List[Dict]:
        """Tìm kiếm lịch sử lớp học của học sinh"""
        try:
            cursor = self.conn.cursor()
            sql = """
                SELECT 
                    s.full_name as student_name,
                    sch.start_date,
                    sch.end_date,
                    c.name as class_name,
                    c.academic_year,
                    u.full_name as teacher_name
                FROM student_class_history sch
                JOIN students s ON sch.student_id = s.id
                JOIN classes c ON sch.class_id = c.id
                JOIN users u ON c.teacher_id = u.id
                WHERE 1=1
            """
            params = []

            if student_id:
                sql += " AND sch.student_id = ?"
                params.append(student_id)

            if student_name:
                sql += " AND s.full_name LIKE ?"
                params.append(f"%{student_name}%")

            if from_date:
                sql += " AND date(sch.start_date) >= date(?)"
                params.append(from_date)

            if to_date:
                sql += " AND (sch.end_date IS NULL OR date(sch.end_date) <= date(?))"
                params.append(to_date)

            sql += " ORDER BY sch.start_date DESC"

            cursor.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                # Sử dụng translate_value để dịch 'Hiện tại' nếu language là tiếng Anh
                current_label = 'Hiện tại'
                if get_current_language() == 'en':
                    current_label = translate_value(current_label)
                    
                results.append({
                    'student_name': row[0],
                    'start_date': row[1],
                    'end_date': row[2] if row[2] else current_label,
                    'class_name': row[3],
                    'academic_year': row[4],
                    'teacher_name': row[5]
                })
            return results
        except Exception as e:
            print(f"Error searching student class history: {e}")
            return []
    def update_user_theme(self, user_id: int, theme_name: str) -> bool:
        """Update user's theme preference"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET theme_preference = ? WHERE id = ?",
                (theme_name, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user theme: {e}")
            return False

    def get_user_theme(self, user_id: int) -> str:
        """Get user's theme preference"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT theme_preference FROM users WHERE id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 'Chính thức'
        except Exception as e:
            print(f"Error getting user theme: {e}")
            return 'Chính thức'
    
    # Document management methods
    def upload_document(self, student_id: int, file_name: str, file_type: str, 
                       file_data: bytes, uploaded_by: int, description: str = "", 
                       category: str = "profile") -> int:
        """Upload a document file for a student"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO document_files 
                (student_id, file_name, file_type, file_data, uploaded_by, description, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, file_name, file_type, file_data, uploaded_by, description, category))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error uploading document: {e}")
            return 0

    def get_student_documents(self, student_id: int) -> List[dict]:
        """Get all documents for a student"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT df.*, u.full_name as uploaded_by_name
                FROM document_files df
                JOIN users u ON df.uploaded_by = u.id
                WHERE df.student_id = ?
                ORDER BY df.upload_date DESC
            """, (student_id,))
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'id': row[0],
                    'student_id': row[1],
                    'file_name': row[2],
                    'file_type': row[3],
                    'upload_date': row[5],
                    'uploaded_by': row[6],
                    'description': row[7],
                    'category': row[8],
                    'uploaded_by_name': row[9]
                })
            return documents
        except Exception as e:
            print(f"Error getting student documents: {e}")
            return []

    def download_document(self, document_id: int) -> Optional[tuple]:
        """Download a document by ID, returns (file_name, file_data)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT file_name, file_data, file_type
                FROM document_files
                WHERE id = ?
            """, (document_id,))
            result = cursor.fetchone()
            return result if result else None
        except Exception as e:
            print(f"Error downloading document: {e}")
            return None

    def delete_document(self, document_id: int) -> bool:
        """Delete a document by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM document_files WHERE id = ?", (document_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def get_documents(self, student_id: int = None, category: str = None, date_filter: str = None) -> List[dict]:
        """Get documents with optional filters"""
        try:
            cursor = self.conn.cursor()
            
            # Build query with filters
            query = """
                SELECT df.*, u.full_name as uploaded_by_name, s.full_name as student_name
                FROM document_files df
                JOIN users u ON df.uploaded_by = u.id
                JOIN students s ON df.student_id = s.id
                WHERE 1=1
            """
            params = []
            
            if student_id:
                query += " AND df.student_id = ?"
                params.append(student_id)
            
            if category:
                query += " AND df.category = ?"
                params.append(category)
            
            if date_filter:
                if date_filter == "today":
                    query += " AND DATE(df.upload_date) = DATE('now')"
                elif date_filter == "week":
                    query += " AND df.upload_date >= DATE('now', '-7 days')"
                elif date_filter == "month":
                    query += " AND df.upload_date >= DATE('now', '-30 days')"
                elif date_filter == "year":
                    query += " AND df.upload_date >= DATE('now', '-365 days')"
            
            query += " ORDER BY df.upload_date DESC"
            
            cursor.execute(query, params)
            
            documents = []
            for row in cursor.fetchall():
                from datetime import datetime
                upload_date = datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S') if row[5] else None
                
                # Create document object
                doc = type('Document', (), {
                    'id': row[0],
                    'student_id': row[1],
                    'file_name': row[2],
                    'file_type': row[3],
                    'upload_date': upload_date,
                    'uploaded_by': row[6],
                    'description': row[7],
                    'category': row[8],
                    'uploaded_by_name': row[9],
                    'student_name': row[10]
                })()
                
                documents.append(doc)
            
            return documents
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []