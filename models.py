from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: str
    full_name: str
    email: Optional[str]
    family_student_id: Optional[int]
    theme_preference: Optional[str]
    created_at: datetime

@dataclass
class Family:
    id: int
    student_id: int
    guardian_name: str
    relationship: str
    occupation: str
    address: str
    phone: str
    household_status: str  # Hoàn cảnh gia đình
    support_status: str    # Chế độ chính sách

@dataclass
class Class:
    id: int
    name: str
    teacher_id: int
    academic_year: str
    notes: Optional[str]

@dataclass
class Student:
    id: int
    full_name: str
    birth_date: Optional[datetime] = None
    address: str = ""
    email: str = ""
    admission_date: Optional[datetime] = None
    class_id: Optional[int] = None
    profile_image: Optional[bytes] = None
    gender: Optional[str] = ""
    phone: Optional[str] = ""
    year: Optional[str] = ""
    parent_name: Optional[str] = ""
    # Thông tin hành chính mới
    decision_number: Optional[str] = ""  # Số quyết định
    nha_chu_t_info: Optional[str] = ""   # Thông tin nhà chữ T
    # Y tế mở rộng
    health_on_admission: Optional[str] = ""      # Tình trạng sức khỏe khi vào làng
    initial_characteristics: Optional[str] = ""  # Đặc điểm sơ bộ của bệnh nhân khi vào làng

@dataclass
class Veteran:
    id: int
    full_name: str
    birth_date: Optional[datetime] = None
    gender: Optional[str] = ""
    address: Optional[str] = ""
    email: Optional[str] = ""
    admission_date: Optional[datetime] = None
    profile_image: Optional[bytes] = None
    initial_characteristics: Optional[str] = ""
    service_period: Optional[str] = ""
    health_condition: Optional[str] = ""
    contact_info: Optional[str] = ""

@dataclass
class PeriodicAssessment:
    id: int
    student_id: int
    assessment_date: datetime
    academic_performance: str
    health_condition: str
    social_behavior: str
    teacher_notes: str
    doctor_notes: Optional[str]
    counselor_notes: Optional[str]

@dataclass
class Support:
    id: int
    student_id: int
    support_type: str  # Loại hỗ trợ
    amount: float     # Số tiền/giá trị hỗ trợ
    start_date: datetime
    end_date: Optional[datetime]
    approval_status: str
    approved_by: int  # User ID
    notes: str

@dataclass
class MedicalRecord:
    id: int
    patient_id: int
    patient_type: str  # 'student' or 'veteran'
    diagnosis: str
    treatment: str
    doctor_id: int
    date: datetime
    notes: Optional[str]
    notification_sent: bool
    # Mở rộng cho y tế không đánh giá định kỳ
    is_routine_checkup: bool = False    # False = chỉ khi gia đình yêu cầu hoặc phát sinh
    requested_by_family: bool = False   # Gia đình yêu cầu
    emergency_case: bool = False        # Trường hợp phát sinh

@dataclass 
class DocumentFile:
    id: int
    student_id: int
    file_name: str
    file_type: str  # 'word', 'pdf', 'image', etc.
    file_data: bytes
    upload_date: datetime
    uploaded_by: int
    description: Optional[str] = ""
    category: str = "profile"  # 'profile', 'medical', 'academic', etc.

@dataclass
class PsychologicalEvaluation:
    id: int
    student_id: int
    evaluation_date: datetime
    evaluator_id: int
    assessment: str
    recommendations: str
    follow_up_date: Optional[datetime]
    notification_sent: bool