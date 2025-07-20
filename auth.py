import streamlit as st
import hashlib
from database import Database

def init_auth():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

def login(username: str, password: str) -> bool:
    db = Database()
    user = db.get_user_by_username(username)
    if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
        # Store the actual password for admin viewing when user successfully logs in
        db.update_user_original_password(user.id, password)
        st.session_state.user = user
        st.session_state.authenticated = True
        st.session_state.user_role = user.role
        return True
    return False

def logout():
    st.session_state.user = None
    st.session_state.authenticated = False
    st.session_state.user_role = None

def check_auth():
    if not st.session_state.authenticated:
        st.warning("Please log in to access this page")
        st.stop()
    
    # Ensure user_role is set in session state
    if hasattr(st.session_state, 'user') and st.session_state.user:
        st.session_state.user_role = st.session_state.user.role
    else:
        st.session_state.user_role = None
    
    return True

def check_role(allowed_roles):
    """Check if current user has permission to access the page"""
    # Admin và hành chính có toàn quyền
    if st.session_state.user.role in ['admin', 'administrative']:
        return True

    # Define page access for each role
    role_allowed_pages = {
        # Giáo viên: quản lý lớp học, hồ sơ học sinh, tìm kiếm và in, thống kê
        'teacher': [
            "03_Quan_ly_ho_so", # Hồ sơ học sinh
            "04_Lop_hoc",       # Lớp học
            "05_Tim_kiem_va_In", # Tìm kiếm và in
            "07_Thong_ke"       # Thống kê
        ],
        
        # Bác sĩ: y tế, hồ sơ học sinh, tìm kiếm và in, thống kê
        'doctor': [
            "02_Y_te",          # Y tế
            "03_Quan_ly_ho_so", # Hồ sơ học sinh và cựu chiến binh
            "05_Tim_kiem_va_In", # Tìm kiếm và in
            "07_Thong_ke"       # Thống kê
        ],
        

        
        # Phụ huynh: chỉ xem thông tin của con mình, thống kê
        'family': [
            "03_Quan_ly_ho_so", # Hồ sơ học sinh (chỉ xem con mình)
            "04_Lop_hoc",       # Lớp học (chỉ xem thông tin lớp của con mình)
            "07_Thong_ke"       # Thống kê (chỉ xem thống kê chung)
        ]
    }
    
    # Kiểm tra quyền truy cập dựa trên vai trò
    user_role = st.session_state.user.role
    current_page = st.session_state.get("current_page", "")
    
    # Nếu không tìm thấy vai trò trong danh sách hoặc trang không được phép
    if user_role not in role_allowed_pages or (current_page not in role_allowed_pages.get(user_role, [])):
        st.error("Bạn không có quyền truy cập trang này")
        st.stop()
    
    # Nếu cần kiểm tra quyền cụ thể theo tham số allowed_roles
    if not st.session_state.user or st.session_state.user.role not in allowed_roles:
        st.error("Bạn không có quyền thực hiện thao tác này")
        st.stop()
    
    return True

def check_student_access(student_id):
    """Check if current user has access to view/edit student information"""
    if not st.session_state.authenticated:
        return False

    if st.session_state.user.role in ['admin', 'administrative']:
        return True

    if st.session_state.user.role == 'family':
        return student_id == st.session_state.user.family_student_id

    # Only certain roles can access student information
    return st.session_state.user.role in ['teacher', 'doctor', 'counselor', 'nurse']

def can_edit_student_info():
    """Check if current user has permission to edit student information"""
    if not st.session_state.authenticated:
        return False

    # Family users cannot edit information
    if st.session_state.user.role == 'family':
        return False
        
    # Y tá chỉ có thể cập nhật thông tin sức khỏe, không thể sửa thông tin cá nhân
    if st.session_state.user.role == 'nurse':
        return False

    # Administrative chỉ có thể cập nhật thông tin cơ bản, không thể sửa thông tin y tế/tâm lý
    if st.session_state.user.role == 'administrative':
        return True
        
    # Các vai trò khác có quyền chỉnh sửa thông tin học sinh
    return st.session_state.user.role in ['admin', 'teacher', 'doctor', 'counselor']

def can_edit_veteran_info():
    """Check if current user has permission to edit veteran information"""
    if not st.session_state.authenticated:
        return False

    # Admin, nhân viên hành chính, và bác sĩ có thể chỉnh sửa thông tin cựu chiến binh
    return st.session_state.user.role in ['admin', 'administrative', 'doctor']

def can_manage_data():
    """Check if user has permission to manage data (import/export/database)"""
    if not st.session_state.authenticated:
        return False

    # Admin, bác sĩ và giáo viên có thể quản lý dữ liệu
    return st.session_state.user.role in ['admin', 'doctor', 'teacher', 'administrative']

def get_user_accessible_students():
    """Get list of student IDs that the current user can access"""
    if not st.session_state.authenticated:
        return []

    if st.session_state.user.role in ['admin', 'administrative']:
        return None  # None means all students

    if st.session_state.user.role == 'family':
        return [st.session_state.user.family_student_id]

    return None  # Other authorized roles can see all students

def is_search_allowed():
    """Check if user has permission to use search functionality"""
    if not st.session_state.authenticated:
        return False

    # Family users cannot use search
    if st.session_state.user.role == 'family':
        return False
        
    # Mọi vai trò khác đều có thể sử dụng tìm kiếm nhưng với phạm vi hạn chế
    return True

def is_print_allowed():
    """Check if user has permission to print profiles"""
    if not st.session_state.authenticated:
        return False

    # Family users cannot print profiles
    if st.session_state.user.role == 'family':
        return False
        
    # Các vai trò khác đều có thể in (bao gồm y tá)
    return True
    
def get_role_based_search_types():
    """Trả về danh sách loại tìm kiếm mà vai trò hiện tại có thể thực hiện"""
    if not st.session_state.authenticated:
        return []
        
    # Admin và nhân viên hành chính có thể tìm kiếm tất cả
    if st.session_state.user.role in ['admin', 'administrative']:
        return ['students', 'veterans', 'medical_records', 'psychological_evaluations']
        
    # Vai trò y tế tìm kiếm y tế và học sinh, cựu chiến binh
    if st.session_state.user.role == 'doctor':
        return ['students', 'veterans', 'medical_records']
        
    # Y tá có thể tìm kiếm học sinh, cựu chiến binh và hồ sơ y tế
    if st.session_state.user.role == 'nurse':
        return ['students', 'veterans', 'medical_records']
        
    # Tư vấn tâm lý có thể tìm kiếm học sinh và đánh giá tâm lý
    if st.session_state.user.role == 'counselor':
        return ['students', 'psychological_evaluations']
        
    # Giáo viên tìm kiếm học sinh và đánh giá tâm lý
    if st.session_state.user.role == 'teacher':
        return ['students', 'psychological_evaluations']
        
    # Phụ huynh không được tìm kiếm
    return []

def check_page_access(page_id: str) -> bool:
    """Check if current user has access to a specific page"""
    if not st.session_state.authenticated:
        return False
    
    from database import Database
    db = Database()
    available_pages = db.get_available_pages(st.session_state.user.role)
    
    # Check if page is in user's available pages
    for page in available_pages:
        if page['id'] == page_id:
            return True
    
    return False

def get_user_accessible_pages():
    """Get list of pages accessible to current user"""
    if not st.session_state.authenticated:
        return []
    
    from database import Database
    db = Database()
    return db.get_available_pages(st.session_state.user.role)