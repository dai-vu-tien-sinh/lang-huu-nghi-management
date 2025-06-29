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
    health_status: str = "Bình thường"
    academic_status: str = "Chưa đánh giá"
    psychological_status: str = ""
    profile_image: Optional[bytes] = None
    gender: Optional[str] = ""
    phone: Optional[str] = ""
    year: Optional[str] = ""
    parent_name: Optional[str] = ""

@dataclass
class Veteran:
    id: int
    full_name: str
    birth_date: datetime
    service_period: str
    health_condition: str
    address: str
    email: str
    contact_info: str
    profile_image: Optional[bytes] = None

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