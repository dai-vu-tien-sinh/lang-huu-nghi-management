from typing import Dict, Any

# Vietnamese translations
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
    
    "database_management": {
        "title": "Quản lý Database",
        "view_tables": "Xem và Chỉnh sửa Bảng",
        "export": "Xuất dữ liệu",
        "import": "Nhập dữ liệu",
        "select_table": "Chọn bảng",
        "table_info": "Thông tin bảng",
        "rows": "Số hàng",
        "columns": "Số cột",
        "edit_data": "Chỉnh sửa dữ liệu",
        "rows_per_page": "Số hàng mỗi trang",
        "page_number": "Trang",
        "save_changes": "Lưu thay đổi",
        "saved_successfully": "Đã lưu thay đổi thành công!",
        "save_error": "Lỗi khi lưu thay đổi",
        "no_data": "Không có dữ liệu trong bảng này",
        "export_data": "Xuất dữ liệu",
        "select_table_export": "Chọn bảng để xuất",
        "preview": "Xem trước",
        "first_rows": "hàng đầu tiên",
        "export_csv": "Xuất ra CSV",
        "export_excel": "Xuất ra Excel",
        "import_data": "Nhập dữ liệu",
        "select_table_import": "Chọn bảng để nhập dữ liệu",
        "upload_file": "Tải lên file (CSV hoặc Excel)",
        "preview_import": "Xem trước dữ liệu nhập",
        "import_options": "Tùy chọn nhập",
        "append": "Thêm vào bảng hiện tại",
        "replace": "Thay thế bảng hiện tại (Xóa dữ liệu cũ)",
        "import_button": "Nhập dữ liệu",
        "imported_successfully": "Đã nhập dữ liệu thành công! Số hàng đã nhập",
        "import_error": "Lỗi khi nhập dữ liệu",
        "file_read_error": "Lỗi khi đọc file",
        "no_matching_columns": "Không có cột nào trong file khớp với cột trong bảng",
        "tables": {
            "users": "Người dùng",
            "classes": "Lớp học",
            "families": "Gia đình",
            "veterans": "Cựu chiến binh",
            "periodic_assessments": "Đánh giá định kỳ",
            "supports": "Hỗ trợ",
            "medical_records": "Hồ sơ y tế",
            "psychological_evaluations": "Đánh giá tâm lý",
            "students": "Học sinh",
            "student_class_history": "Lịch sử lớp học"
        }
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
        "edit": "Sửa",
        "delete": "Xóa",
        "success": "Thành công",
        "error": "Lỗi",
        "select_language": "Chọn ngôn ngữ",
        "home": "Trang chủ",
        "login_required": "Vui lòng đăng nhập để sử dụng chức năng này",
        "no_permission": "Bạn không có quyền sử dụng chức năng này",
        "not_updated": "Chưa cập nhật",
        "not_evaluated": "Chưa đánh giá",
        "theme": "Giao diện",
        "choose_theme": "Chọn giao diện",
        "dark_mode": "Chế độ tối"
    },
    "login": {
        "title": "Đăng nhập",
        "success": "Đăng nhập thành công!",
        "error": "Tên đăng nhập hoặc mật khẩu không đúng"
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
        "username_exists": "Tên đăng nhập đã tồn tại",
        "customize_sidebar": "Tùy Chỉnh Thanh Menu",
        "drag_drop": "Kéo và thả để sắp xếp lại thứ tự các trang:",
        "show": "Hiển thị",
        "save_customization": "Lưu Tùy Chỉnh",
        "save_success": "Đã lưu tùy chỉnh thành công!",
        "save_error": "Không thể lưu tùy chỉnh",
        "create_report": "Tạo Báo Cáo",
        "report_type": "Loại báo cáo",
        "generate_pdf": "Tạo báo cáo PDF",
        "download_report": "Tải xuống báo cáo",
        "system_stats": "Thống Kê Hệ Thống",
        "total_students": "Tổng số học sinh",
        "total_veterans": "Tổng số cựu chiến binh"
    },
    "dashboard": {
        "admin": {
            "title": "Bảng Điều Khiển Quản Trị",
            "welcome": "Chào mừng đến với bảng điều khiển quản trị. Sử dụng thanh bên để điều hướng đến các phần khác nhau."
        },
        "doctor": {
            "title": "Bảng Điều Khiển Y Tế",
            "welcome": "Truy cập hồ sơ y tế và thông tin bệnh nhân thông qua menu bên."
        },
        "teacher": {
            "title": "Bảng Điều Khiển Giáo Viên",
            "welcome": "Xem và quản lý thông tin sinh viên bằng menu bên."
        },
        "counselor": {
            "title": "Bảng Điều Khiển Tư Vấn",
            "welcome": "Truy cập đánh giá tâm lý và thông tin hỗ trợ sinh viên."
        }
    },
    "pages": {
        "psychology": {
            "title": "Đánh giá tâm lý",
            "view_tab": "Xem đánh giá",
            "add_tab": "Thêm đánh giá",
            "instructions": """
            ℹ️ **Hướng dẫn:**
            1. Chọn học sinh để đánh giá
            2. Điền thông tin đánh giá và khuyến nghị
            3. Chọn ngày theo dõi tiếp (nếu cần)
            4. Tùy chọn gửi thông báo email
            """,
            "evaluation_info": "Thông tin đánh giá",
            "select_student": "🎓 Chọn học sinh",
            "follow_up_date": "📅 Ngày theo dõi tiếp",
            "assessment": "📝 Đánh giá",
            "assessment_placeholder": "Nhập đánh giá chi tiết về tình trạng tâm lý của học sinh...",
            "recommendations": "💡 Khuyến nghị",
            "recommendations_placeholder": "Nhập các khuyến nghị và hướng dẫn cụ thể...",
            "add_evaluation": "✅ Thêm đánh giá",
            "no_evaluations_found": "🔍 Không tìm thấy đánh giá tâm lý nào phù hợp với bộ lọc",
            "add_permission_denied": "⚠️ Bạn không có quyền thêm đánh giá tâm lý mới",
            "search_student": "🔍 Tìm kiếm theo tên học sinh",
            "view_evaluations": "Xem đánh giá",
            "add_new_evaluation": "Thêm đánh giá mới"
        },
        "classes": {
            "title": "Thông Tin Lớp Học",
            "add_new_class": "➕ Thêm Lớp Mới",
            "add_class_title": "Thêm Lớp Mới",
            "class_name": "Tên lớp",
            "teacher": "Giáo viên chủ nhiệm",
            "academic_year": "Năm học",
            "notes": "Ghi chú",
            "add_class_button": "Thêm lớp",
            "add_success": "Thêm lớp mới thành công!",
            "add_error": "Không thể thêm lớp mới",
            "no_class_info": "Không có thông tin lớp học.",
            "general_info": "Thông tin chung",
            "student_list": "Danh sách học sinh",
            "academic_history": "Lịch sử học tập",
            "edit_class": "✏️ Chỉnh sửa",
            "edit_class_title": "Chỉnh sửa thông tin lớp",
            "save_changes": "Lưu thay đổi",
            "update_success": "Cập nhật thông tin lớp thành công!",
            "update_error": "Không thể cập nhật thông tin lớp",
            "teacher_info": "👨‍🏫 Giáo viên chủ nhiệm",
            "full_name": "Họ và tên",
            "email": "Email",
            "no_students": "Chưa có học sinh trong lớp",
            "add_student": "➕ Thêm học sinh",
            "add_student_title": "Thêm học sinh vào lớp",
            "select_student": "Chọn học sinh",
            "add_to_class": "Thêm vào lớp",
            "add_student_success": "Thêm học sinh vào lớp thành công!",
            "add_student_error": "Không thể thêm học sinh vào lớp",
            "no_unassigned": "Không có học sinh chưa được phân lớp",
            "student_name": "Họ và tên",
            "academic_status": "Tình trạng học tập",
            "health_status": "Tình trạng sức khỏe",
            "remove_students": "Xóa học sinh khỏi lớp",
            "remove_success": "Đã xóa học sinh khỏi lớp!",
            "remove_error": "Không thể xóa học sinh khỏi lớp",
            "no_permission": "Không có quyền xem thông tin học sinh trong lớp này",
            "search_title": "📚 Lịch sử học tập",
            "search_filters": "🔍 Bộ lọc tìm kiếm",
            "student_name_search": "Tên học sinh",
            "date_filter": "Lọc theo thời gian",
            "date_range": "Khoảng thời gian",
            "no_history": "Không tìm thấy lịch sử lớp học phù hợp"
        }
    },
    "groups": {
        "management": "Quản trị hệ thống",
        "support": "Hỗ trợ & Theo dõi",
        "users": "Quản lý người dùng"
    },
    "students": {
        "title": "Quản Lý Sinh Viên",
        "list_title": "Danh Sách Sinh Viên",
        "add_title": "Thêm Sinh Viên Mới",
        "fields": {
            "full_name": "Họ và tên",
            "birth_date": "Ngày sinh",
            "address": "Địa chỉ",
            "email": "Email",
            "admission_date": "Ngày nhập học",
            "health_status": "Tình trạng sức khỏe",
            "academic_status": "Tình trạng học tập"
        },
        "health_status_options": ["Tốt", "Bình thường", "Cần chú ý"],
        "academic_status_options": ["Xuất sắc", "Tốt", "Trung bình", "Cần cải thiện"]
    },
    "veterans": {
        "title": "Quản Lý Cựu Chiến Binh",
        "list_title": "Danh Sách Cựu Chiến Binh",
        "add_title": "Thêm Cựu Chiến Binh Mới",
        "fields": {
            "full_name": "Họ và tên",
            "birth_date": "Ngày sinh",
            "service_period": "Thời gian phục vụ",
            "health_condition": "Tình trạng sức khỏe",
            "address": "Địa chỉ",
            "contact_info": "Thông tin liên hệ"
        }
    }
}

# English translations
en = {
    "app": {
        "title": "Lang Huu Nghi Data Management System",
        "title_full": "Lang Huu Nghi Data Management System - Hệ thống quản lý dữ liệu Làng Hữu Nghị"
    },
    "navigation": {
        "01_Quản_trị": "Administration",
        "02_Y_te": "Healthcare",
        "03_Quản_lý_hồ_sơ": "Records Management",
        "03_Y_tế": "Healthcare",
        "03_Tam_ly": "Healthcare",
        "04_Lớp_học": "Classes", 
        "05_Tìm_kiếm_và_In": "Search, Print & Documents",
        "06_Quản_lý_Database": "Data Management",
        "06_Quản_lý_Hệ_thống": "System Management",
        "07_Thống_kê": "Statistics & Analytics",
        "08_Thong_ke": "Statistics & Analytics",
        "Trang_chủ": "Home Page",
        "main": "Home Page"
    },
    "database_management": {
        "title": "Database Management",
        "view_tables": "View and Edit Tables",
        "export": "Export Data",
        "import": "Import Data",
        "select_table": "Select table",
        "table_info": "Table Information",
        "rows": "Rows",
        "columns": "Columns",
        "edit_data": "Edit Data",
        "rows_per_page": "Rows per page",
        "page_number": "Page",
        "save_changes": "Save Changes",
        "saved_successfully": "Changes saved successfully!",
        "save_error": "Error saving changes",
        "no_data": "No data in this table",
        "export_data": "Export Data",
        "select_table_export": "Select table to export",
        "preview": "Preview",
        "first_rows": "first rows",
        "export_csv": "Export to CSV",
        "export_excel": "Export to Excel",
        "import_data": "Import Data",
        "select_table_import": "Select table to import data",
        "upload_file": "Upload file (CSV or Excel)",
        "preview_import": "Preview import data",
        "import_options": "Import options",
        "append": "Append to current table",
        "replace": "Replace current table (Delete old data)",
        "import_button": "Import Data",
        "imported_successfully": "Data imported successfully! Rows imported",
        "import_error": "Error importing data",
        "file_read_error": "Error reading file",
        "no_matching_columns": "No columns in file match columns in table",
        "tables": {
            "users": "Users",
            "classes": "Classes",
            "families": "Families",
            "veterans": "Veterans",
            "periodic_assessments": "Periodic Assessments",
            "supports": "Supports",
            "medical_records": "Medical Records",
            "psychological_evaluations": "Psychological Evaluations",
            "students": "Students",
            "student_class_history": "Student Class History"
        }
    },
    "common": {
        "login": "Login",
        "logout": "Logout", 
        "username": "Username",
        "password": "Password",
        "welcome": "Welcome",
        "role": "Role",
        "submit": "Submit",
        "cancel": "Cancel",
        "save": "Save",
        "add": "Add",
        "edit": "Edit",
        "delete": "Delete",
        "success": "Success", 
        "error": "Error",
        "select_language": "Select Language",
        "home": "Home",
        "login_required": "Please login to use this feature",
        "no_permission": "You don't have permission to use this feature",
        "not_updated": "Not updated",
        "not_evaluated": "Not evaluated",
        "theme": "Theme",
        "choose_theme": "Choose Theme",
        "search": "Search",
        "back": "Back",
        "next": "Next",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "dob": "Date of Birth",
        "phone": "Phone Number",
        "email": "Email",
        "address": "Address",
        "status": "Status",
        "details": "Details",
        "profile": "Profile",
        "date": "Date",
        "class": "Class",
        "assessment": "Assessment"
    },
    "admin": {
        "title": "Administration Dashboard",
        "user_management": "User Management",
        "interface_customization": "Interface Customization",
        "reports": "Reports",
        "system_statistics": "System Statistics",
        "add_user": "Add New User",
        "username": "Username",
        "password": "Password",
        "role": "Role",
        "full_name": "Full Name",
        "select_student": "Select student",
        "add_user_button": "Add user",
        "add_success": "User added successfully!",
        "username_exists": "Username already exists",
        "customize_sidebar": "Customize Sidebar Menu",
        "drag_drop": "Drag and drop to rearrange pages:",
        "show": "Show",
        "save_customization": "Save Customization",
        "save_success": "Customization saved successfully!",
        "save_error": "Unable to save customization",
        "create_report": "Create Report",
        "report_type": "Report type",
        "generate_pdf": "Generate PDF report",
        "download_report": "Download report",
        "system_stats": "System Statistics",
        "total_students": "Total students",
        "total_veterans": "Total veterans"
    },
    "login": {
        "title": "Login",
        "success": "Login successful!",
        "error": "Invalid username or password"
    },
    "dashboard": {
        "admin": {
            "title": "Admin Dashboard",
            "welcome": "Welcome to the admin dashboard. Use the sidebar to navigate to different sections."
        },
        "doctor": {
            "title": "Medical Dashboard",
            "welcome": "Access medical records and patient information through the sidebar menu."
        },
        "teacher": {
            "title": "Teacher Dashboard",
            "welcome": "View and manage student information using the sidebar menu."
        },
        "counselor": {
            "title": "Counselor Dashboard",
            "welcome": "Access psychological evaluations and student support information."
        }
    },
    "pages": {
        "main": {
            "title": "Lang Huu Nghi Management System",
            "welcome": "Welcome to the Lang Huu Nghi Management System"
        },
        "admin": {
            "title": "Administration Dashboard",
            "user_management": "User Management",
            "interface_customization": "Interface Customization",
            "reports": "Reports",
            "system_statistics": "System Statistics"
        },
        "psychology": {
            "title": "Psychological Assessment",
            "view_tab": "View Assessments",
            "add_tab": "Add Assessment",
            "instructions": "Instructions",
            "evaluation_info": "Evaluation Information",
            "select_student": "🎓 Select Student",
            "follow_up_date": "📅 Follow-up Date",
            "assessment": "📝 Assessment",
            "assessment_placeholder": "Enter detailed assessment of the student's psychological state...",
            "recommendations": "💡 Recommendations",
            "recommendations_placeholder": "Enter specific recommendations and guidance...",
            "add_evaluation": "✅ Add Evaluation",
            "no_evaluations_found": "🔍 No psychological evaluations found matching the filters",
            "add_permission_denied": "⚠️ You don't have permission to add new psychological evaluations",
            "search_student": "🔍 Search by student name",
            "view_evaluations": "View Evaluations",
            "add_new_evaluation": "Add New Evaluation"
        },
        "healthcare": {
            "title": "Medical Records",
            "view_records": "View Records",
            "add_record": "Add New Record",
            "patient_type": "Patient Type",
            "diagnosis": "Diagnosis",
            "treatment": "Treatment",
            "view_tab": "📋 View Records",
            "add_tab": "➕ Add Record",
            "filters": "Filters",
            "all": "All",
            "student": "Student",
            "veteran": "Veteran",
            "search_name": "🔍 Search by name",
            "date_range": "📅 Date range",
            "record": "🏥 Record",
            "date": "🗓️ Examination Date",
            "doctor": "👨‍⚕️ Doctor",
            "patient_type_label": "👤 Patient Type",
            "notes": "📝 Notes",
            "email_section": "---",
            "notification_pending": "⏳ Notification not sent",
            "notification_sent": "✉️ Notification sent",
            "send_notification": "📤 Send notification",
            "notification_success": "Notification sent successfully!",
            "notification_error": "Could not send notification",
            "no_email": "❌ No patient email",
            "no_records": "🔍 No medical records found matching the filters",
            "load_error": "❌ Error loading data",
            "instructions": """
            ℹ️ **Instructions:**
            1. Select patient type (Student/Veteran)
            2. Select patient from the list
            3. Fill in diagnosis and treatment information
            4. Add notes if needed
            5. Optionally send email notification
            """,
            "exam_info": "Examination Information",
            "select_patient": "👤 Select patient",
            "send_email": "📧 Send email notification",
            "diagnosis_placeholder": "Enter detailed diagnosis results...",
            "treatment_placeholder": "Enter treatment methods and prescriptions...",
            "notes_placeholder": "Enter additional notes if needed...",
            "add_record_button": "✅ Add Record",
            "add_success": "✨ Medical record added successfully!",
            "add_error": "❌ Error adding medical record"
        },
        "records": {
            "title": "Records Management",
            "student_list": "Student List",
            "veteran_list": "Veteran List",
            "add_new": "Add New Record",
            "edit": "Edit Record",
            "profile_image": "Profile Image"
        },
        "classes": {
            "title": "Class Management",
            "general_info": "General Information",
            "student_list": "Student List",
            "academic_history": "Academic History",
            "teacher": "Class Teacher"
        },
        "search": {
            "title": "Search & Print",
            "advanced_search": "Advanced Search",
            "print_profile": "Print Profile",
            "export_data": "Export Data",
            "filters": "Search Filters"
        },
        "system": {
            "title": "System Management",
            "import_data": "Import Data from Excel",
            "backup_restore": "Backup & Restore",
            "database_management": "Database Management",
            "cleanup": "Data Cleanup"
        },
        "statistics": {
            "title": "Statistics & Analytics",
            "health_stats": "Health Statistics",
            "academic_stats": "Academic Statistics",
            "medical_records": "Medical Records Analysis",
            "psychological_eval": "Psychological Evaluation Analysis",
            "filters": "Filters",
            "date_range": "Date Range",
            "overview": "Overview Statistics",
            "total_students": "Total Students",
            "total_veterans": "Total Veterans",
            "medical_record_count": "Medical Records",
            "psychological_eval_count": "Psychological Evaluations",
            "chart_customization": "📊 Chart Customization",
            "data_type": "Select Data Type",
            "chart_type": "Chart Type"
        }
    },
    "groups": {
        "management": "System Management",
        "support": "Support & Monitoring",
        "users": "User Management"
    },
    "students": {
        "title": "Student Management",
        "list_title": "Student List",
        "add_title": "Add New Student",
        "search": "Search Students",
        "fields": {
            "full_name": "Full Name",
            "birth_date": "Date of Birth",
            "gender": "Gender",
            "address": "Address",
            "email": "Email",
            "phone": "Phone Number",
            "admission_date": "Admission Date",
            "health_status": "Health Status",
            "academic_status": "Academic Status",
            "psychological_status": "Psychological Status",
            "class": "Class"
        },
        "health_status_options": ["Good", "Normal", "Needs Attention"],
        "academic_status_options": ["Excellent", "Good", "Average", "Needs Improvement"],
        "psychological_status_options": ["Stable", "Good", "Needs Monitoring"]
    },
    "veterans": {
        "title": "Veteran Management",
        "list_title": "Veteran List", 
        "add_title": "Add New Veteran",
        "fields": {
            "full_name": "Full Name",
            "birth_date": "Birth Date",
            "service_period": "Service Period",
            "health_condition": "Health Condition",
            "address": "Address",
            "contact_info": "Contact Information"
        }
    },
    "classes": {
        "title": "Class Management",
        "general_info": "General Information",
        "class_name": "Class Name",
        "school_year": "School Year",
        "teacher_info": "Teacher Information",
        "student_list": "Student List",
        "academic_history": "Academic History",
        "add_class": "Add New Class",
        "edit_class": "Edit Class",
        "save_changes": "Save Changes",
        "update_success": "Class information updated successfully!",
        "update_error": "Unable to update class information",
        "add_success": "New class added successfully!",
        "add_error": "Unable to add new class",
        "no_classes": "No classes found",
        "no_students": "No students in this class yet",
        "add_student": "Add Student",
        "remove_student": "Remove Student",
        "student_name": "Student Name",
        "academic_status": "Academic Status",
        "health_status": "Health Status"
    },
    "family": {
        "restricted_access": "You only have access to information for your assigned student.",
        "child_not_found": "Unable to find your child's information in the system.",
        "view_info": "View Information",
        "statistics": "General Statistics",
        "child_name": "Child's Name",
        "personal_info": "Personal Information",
        "academic_info": "Academic Information",
        "health_info": "Health Information"
    },
    "healthcare": {
        "title": "Medical Records Management",
        "view_records": "📋 View Records",
        "add_record": "➕ Add Record",
        "filters": "Filters",
        "patient_type": "🏥 Patient Type",
        "all": "All",
        "student": "Student",
        "veteran": "Veteran",
        "search_name": "🔍 Search by name",
        "date_range": "📅 Date Range",
        "no_records": "No medical records found",
        "patient_name": "Patient Name",
        "diagnosis": "Diagnosis",
        "treatment": "Treatment",
        "doctor": "Doctor",
        "date": "Date",
        "add_medical_record": "Add Medical Record",
        "select_patient": "Select Patient",
        "diagnosis_placeholder": "Enter detailed diagnosis results...",
        "treatment_placeholder": "Enter treatment methods and prescriptions...",
        "notes_placeholder": "Enter additional notes if needed...",
        "add_record_button": "✅ Add Record",
        "add_success": "✨ Medical record added successfully!",
        "add_error": "❌ Error adding medical record"
    }
}

class Translator:
    def __init__(self):
        self.translations = {
            'vi': vi
        }
        self.current_language = 'vi'  # Vietnamese only

    def set_language(self, language: str):
        if language in self.translations:
            self.current_language = language

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
    return translator.current_language

# Helper function to set language
def set_language(language: str):
    translator.set_language(language)

# Helper function to get text
def get_text(key_path: str, default: str = "") -> str:
    if default is None:
        default = ""
    return translator.get_text(key_path, default)