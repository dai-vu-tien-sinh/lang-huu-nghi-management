from typing import Dict, Any

# Vietnamese translations only
vi = {
    "navigation": {
        "01_Quan_tri": "Quản trị",
        "02_Y_te": "Y tế",
        "03_Quan_ly_ho_so": "Quản lý hồ sơ",
        "03_Tam_ly": "Y tế",
        "04_Lop_hoc": "Lớp học",
        "05_Tim_kiem_va_In": "Tìm kiếm & In",
        "06_Quan_ly_Database": "Quản lý Dữ liệu", 
        "07_Quan_ly_He_thong": "Quản lý Hệ thống",
        "08_Thong_ke": "Thống kê",
        "main": "Trang chủ"
    },
    
    "app": {
        "title": "Hệ thống quản lý dữ liệu Làng Hữu Nghị",
        "title_full": "Hệ thống quản lý dữ liệu Làng Hữu Nghị - Lang Huu Nghi Management System"
    },
    
    "common": {
        "login": "Đăng nhập",
        "logout": "Đăng xuất",
        "username": "Tên đăng nhập",
        "password": "Mật khẩu",
        "welcome": "Xin chào",
        "role": "Vai trò",
        "submit": "Gửi",
        "cancel": "Hủy",
        "save": "Lưu",
        "add": "Thêm",
        "edit": "Chỉnh sửa",
        "delete": "Xóa",
        "success": "Thành công",
        "error": "Lỗi",
        "search": "Tìm kiếm",
        "back": "Quay lại",
        "next": "Tiếp theo",
        "gender": "Giới tính",
        "male": "Nam",
        "female": "Nữ",
        "other": "Khác",
        "dob": "Ngày sinh",
        "phone": "Số điện thoại",
        "email": "Email",
        "address": "Địa chỉ",
        "status": "Trạng thái",
        "details": "Chi tiết",
        "profile": "Hồ sơ",
        "date": "Ngày",
        "class": "Lớp",
        "assessment": "Đánh giá"
    },
    
    "admin": {
        "title": "Bảng Điều Khiển Quản Trị",
        "user_management": "Quản Lý Người Dùng",
        "interface_customization": "Tùy Chỉnh Giao Diện",
        "reports": "Báo Cáo",
        "system_statistics": "Thống Kê Hệ Thống",
        "add_user": "Thêm Người Dùng Mới",
        "username": "Tên đăng nhập",
        "password": "Mật khẩu",
        "role": "Vai trò",
        "full_name": "Họ và tên",
        "select_student": "Chọn học sinh",
        "add_user_button": "Thêm người dùng",
        "add_success": "Thêm người dùng thành công!",
        "username_exists": "Tên đăng nhập đã tồn tại"
    },
    
    "login": {
        "title": "Đăng nhập",
        "success": "Đăng nhập thành công!",
        "error": "Tên đăng nhập hoặc mật khẩu không đúng"
    },
    
    "groups": {
        "management": "Quản trị hệ thống",
        "support": "Hỗ trợ & Theo dõi",
        "users": "Quản lý người dùng"
    },
    
    "pages": {
        "healthcare": {
            "title": "Quản Lý Hồ Sơ Y Tế",
            "view_records": "📋 Xem Hồ Sơ",
            "add_record": "➕ Thêm Hồ Sơ"
        },
        "classes": {
            "title": "Thông Tin Lớp Học",
            "add_new_class": "➕ Thêm Lớp Mới",
            "add_class_title": "Thêm Lớp Mới",
            "class_name": "Tên lớp",
            "teacher": "Giáo viên chủ nhiệm",
            "academic_year": "Năm học",
            "notes": "Ghi chú",
            "add_class_button": "Thêm lớp"
        },
        "statistics": {
            "title": "Thống Kê và Phân Tích Dữ Liệu",
            "filters": "Bộ lọc",
            "date_range": "Khoảng thời gian",
            "total_students": "Tổng số sinh viên",
            "total_veterans": "Tổng số cựu chiến binh",
            "medical_record_count": "Số hồ sơ y tế",
            "psychological_eval_count": "Số đánh giá tâm lý",
            "chart_customization": "📊 Tùy chỉnh biểu đồ",
            "data_type": "Chọn loại dữ liệu"
        }
    },
    
    "healthcare": {
        "filters": "Bộ lọc",
        "patient_type": "🏥 Loại bệnh nhân",
        "all": "Tất cả",
        "student": "Sinh viên",
        "veteran": "Cựu chiến binh",
        "search_name": "🔍 Tìm theo tên",
        "date_range": "📅 Khoảng thời gian"
    }
}

class Translator:
    def __init__(self):
        self.translations = {
            'vi': vi
        }
        self.current_language = 'vi'  # Vietnamese only

    def set_language(self, language: str):
        # Always set to Vietnamese since we only support Vietnamese
        self.current_language = 'vi'

    def get_text(self, key_path: str, default: str = "") -> str:
        """
        Get translated text using dot notation for nested keys
        Example: translator.get_text('common.login')
        """
        if default is None:
            default = ""
            
        keys = key_path.split('.')
        value = self.translations[self.current_language]
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default if default != "" else key_path
                
        # Make sure we return a string
        if isinstance(value, str):
            return value
        else:
            return str(value) if value is not None else (default if default != "" else key_path)

# Create a global translator instance
translator = Translator()

# Helper function to get current language
def get_current_language() -> str:
    return 'vi'  # Always Vietnamese

# Helper function to set language (does nothing now)
def set_language(language: str):
    # Force Vietnamese only
    translator.set_language('vi')

# Helper function to get text
def get_text(key_path: str, default: str = "") -> str:
    if default is None:
        default = ""
    return translator.get_text(key_path, default)