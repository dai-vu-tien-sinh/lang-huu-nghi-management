import streamlit as st
import pandas as pd
from database import Database
from auth import init_auth, check_auth, check_role, can_manage_data, check_page_access
from utils import show_success, show_error, apply_theme
from datetime import datetime, timedelta
import os
import sqlite3
import io
import re
import time
from translations import get_text
import atexit

# Initialize backup system
try:
    from gdrive_backup import GoogleDriveBackup
    BACKUP_AVAILABLE = True
    
except ImportError as e:
    BACKUP_AVAILABLE = False

def parse_date(date_str):
    """Try multiple date formats and return standardized date string"""
    # Handle None, nan, or empty strings
    if date_str is None:
        return None
        
    # Convert to string for consistent handling
    date_str_lower = str(date_str).lower().strip()
    
    # More comprehensive check for invalid date values
    if (pd.isna(date_str) or 
        date_str_lower == "" or 
        date_str_lower in ['nan', 'none', 'null', 'na', 'n/a', 'không rõ', 'x', '?', '-', '--']):
        return None
        
    # Handle NaT value from pandas
    if hasattr(date_str, 'dtype') and pd.isna(date_str):
        return None
        
    # Special case for Excel "nan" representation
    if date_str_lower == "nan":
        return None

    # Already a datetime object
    if isinstance(date_str, datetime):
        return date_str.strftime('%Y-%m-%d')
    
    # Try to parse various date formats
    date_formats = [
        '%d/%m/%Y',     # 25/12/2023
        '%m/%d/%Y',     # 12/25/2023  
        '%Y-%m-%d',     # 2023-12-25
        '%d-%m-%Y',     # 25-12-2023
        '%m-%d-%Y',     # 12-25-2023
        '%d/%m/%y',     # 25/12/23
        '%m/%d/%y',     # 12/25/23
        '%y-%m-%d',     # 23-12-25
        '%d-%m-%y',     # 25-12-23
        '%m-%d-%y',     # 12-25-23
        '%d.%m.%Y',     # 25.12.2023
        '%m.%d.%Y',     # 12.25.2023
        '%d %m %Y',     # 25 12 2023
        '%m %d %Y',     # 12 25 2023
        '%d %B %Y',     # 25 December 2023
        '%B %d, %Y',    # December 25, 2023
        '%d %b %Y',     # 25 Dec 2023
        '%b %d, %Y',    # Dec 25, 2023
    ]
    
    for fmt in date_formats:
        try:
            # Parse the date
            parsed_date = datetime.strptime(str(date_str).strip(), fmt)
            
            # Basic validation - reject obviously wrong dates
            current_year = datetime.now().year
            if parsed_date.year < 1900 or parsed_date.year > current_year + 10:
                continue
                
            # Return standardized format
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format worked, try to handle numbers (timestamps)
    try:
        # Check if it might be a timestamp or Excel serial number
        num_date = float(date_str)
        
        # Excel date serial number (days since 1900-01-01)
        if 1 <= num_date <= 100000:  # Reasonable range for Excel dates
            # Excel has a bug where it thinks 1900 is a leap year
            if num_date > 59:
                num_date -= 1
            excel_epoch = datetime(1900, 1, 1)
            parsed_date = excel_epoch + timedelta(days=num_date - 1)
            return parsed_date.strftime('%Y-%m-%d')
            
        # Unix timestamp (seconds since 1970-01-01)
        elif 0 <= num_date <= 2147483647:  # Valid Unix timestamp range
            parsed_date = datetime.fromtimestamp(num_date)
            return parsed_date.strftime('%Y-%m-%d')
            
    except (ValueError, OverflowError):
        pass
    
    # If all parsing attempts failed, raise an informative error
    raise ValueError(f"Cannot parse date '{date_str}'. Supported formats: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, etc.")

def database_management_section():
    """Backup and restore management section with local options only"""
    
    # Local backup section
    st.subheader("💾 Sao lưu cục bộ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Tạo bản sao lưu cục bộ", use_container_width=True):
            with st.spinner("Đang tạo bản sao lưu..."):
                try:
                    from local_backup import LocalBackup
                    backup_service = LocalBackup()
                    
                    # Create backup
                    backup_path = backup_service.create_database_backup()
                    
                    if backup_path:
                        st.success("✅ Sao lưu cục bộ thành công!")
                        st.info(f"📂 Vị trí: {backup_path}")
                        
                        # Show download option
                        with open(backup_path, 'rb') as f:
                            backup_data = f.read()
                            st.download_button(
                                label="⬇️ Tải xuống backup",
                                data=backup_data,
                                file_name=os.path.basename(backup_path),
                                mime="application/zip"
                            )
                    else:
                        st.error("❌ Sao lưu thất bại!")
                        
                except Exception as e:
                    st.error(f"❌ Lỗi sao lưu: {str(e)}")
    
    with col2:
        st.write("**📋 Thông tin sao lưu:**")
        try:
            from local_backup import LocalBackup
            backup_service = LocalBackup()
            backups = backup_service.get_backup_info()
            
            if backups:
                st.write(f"🗂️ Có {len(backups)} bản sao lưu")
                for i, backup in enumerate(backups[:3]):  # Show first 3 backups (most recent)
                    col_date, col_restore = st.columns([3, 1])
                    
                    with col_date:
                        st.write(f"• {backup['created']} ({backup['size']})")
                    
                    with col_restore:
                        if st.button("🔄", key=f"restore_{i}", help="Khôi phục backup này"):
                            # Store backup info in session state for confirmation
                            st.session_state.restore_backup_path = backup['path']
                            st.session_state.restore_backup_name = backup['created']
                            st.session_state.show_restore_confirm = True
                            st.rerun()
            else:
                st.write("📭 Chưa có bản sao lưu nào")
                
        except Exception as e:
            st.write("⚠️ Không thể kiểm tra thông tin backup")
    
    # Handle restore confirmation dialog
    if st.session_state.get('show_restore_confirm', False):
        st.subheader("⚠️ Xác nhận khôi phục")
        st.warning(f"""
        **Bạn có chắc chắn muốn khôi phục dữ liệu từ backup:**
        📅 {st.session_state.get('restore_backup_name', 'Không xác định')}
        
        ⚠️ **Lưu ý quan trọng:**
        - Dữ liệu hiện tại sẽ được sao lưu tự động trước khi khôi phục
        - Bạn có thể hoàn tác thao tác này sau khi khôi phục
        - Tất cả thay đổi sau thời điểm backup sẽ bị mất
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Xác nhận khôi phục", type="primary", use_container_width=True):
                with st.spinner("Đang khôi phục dữ liệu..."):
                    try:
                        from local_backup import LocalBackup
                        backup_service = LocalBackup()
                        
                        # Create pre-restore backup
                        pre_restore_backup = backup_service.create_pre_restore_backup()
                        if pre_restore_backup:
                            st.session_state.last_pre_restore_backup = pre_restore_backup
                        
                        # Restore from selected backup
                        success = backup_service.restore_backup(st.session_state.restore_backup_path)
                        
                        if success:
                            st.success("✅ Khôi phục thành công!")
                            st.success("🔄 Dữ liệu đã được khôi phục. Trang sẽ tự động tải lại...")
                            
                            # Store restore info for revert option
                            st.session_state.restore_completed = True
                            st.session_state.restored_from = st.session_state.restore_backup_name
                            
                            # Clear confirmation dialog
                            st.session_state.show_restore_confirm = False
                            del st.session_state.restore_backup_path
                            del st.session_state.restore_backup_name
                            
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Khôi phục thất bại!")
                            
                    except Exception as e:
                        st.error(f"❌ Lỗi khôi phục: {str(e)}")
        
        with col2:
            if st.button("❌ Hủy bỏ", use_container_width=True):
                st.session_state.show_restore_confirm = False
                if 'restore_backup_path' in st.session_state:
                    del st.session_state.restore_backup_path
                if 'restore_backup_name' in st.session_state:
                    del st.session_state.restore_backup_name
                st.rerun()
    
    # Show revert option if a restore was just completed
    if st.session_state.get('restore_completed', False):
        st.subheader("↩️ Hoàn tác khôi phục")
        st.info(f"""
        **Khôi phục gần nhất:** {st.session_state.get('restored_from', 'Không xác định')}
        
        Bạn có thể hoàn tác việc khôi phục này và quay lại dữ liệu trước đó.
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("↩️ Hoàn tác khôi phục", type="secondary", use_container_width=True):
                if st.session_state.get('last_pre_restore_backup'):
                    with st.spinner("Đang hoàn tác khôi phục..."):
                        try:
                            from local_backup import LocalBackup
                            backup_service = LocalBackup()
                            
                            success = backup_service.restore_backup(st.session_state.last_pre_restore_backup)
                            
                            if success:
                                st.success("✅ Đã hoàn tác khôi phục thành công!")
                                st.success("🔄 Dữ liệu đã được khôi phục về trạng thái trước đó")
                                
                                # Clear restore session state
                                st.session_state.restore_completed = False
                                if 'restored_from' in st.session_state:
                                    del st.session_state.restored_from
                                if 'last_pre_restore_backup' in st.session_state:
                                    del st.session_state.last_pre_restore_backup
                                
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Hoàn tác thất bại!")
                                
                        except Exception as e:
                            st.error(f"❌ Lỗi hoàn tác: {str(e)}")
                else:
                    st.error("❌ Không tìm thấy backup để hoàn tác")
        
        with col2:
            if st.button("✓ Giữ nguyên", use_container_width=True):
                st.session_state.restore_completed = False
                if 'restored_from' in st.session_state:
                    del st.session_state.restored_from
                if 'last_pre_restore_backup' in st.session_state:
                    del st.session_state.last_pre_restore_backup
                st.rerun()
    
    # Restore Section - File Upload
    if not st.session_state.get('show_restore_confirm', False):
        st.subheader("📤 Khôi phục từ file")
        
        # Upload and restore backup
        uploaded_file = st.file_uploader(
            "Chọn file backup để khôi phục",
            type=['zip', 'db'],
            help="Chọn file backup (.zip hoặc .db) để khôi phục dữ liệu"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📁 File đã chọn: {uploaded_file.name}")
                st.info(f"📊 Kích thước: {uploaded_file.size / 1024 / 1024:.2f} MB")
            
            with col2:
                if st.button("🔄 Khôi phục từ file", type="primary"):
                    with st.spinner("Đang khôi phục dữ liệu..."):
                        try:
                            # Save uploaded file temporarily
                            temp_path = f"temp_restore_{uploaded_file.name}"
                            with open(temp_path, 'wb') as f:
                                f.write(uploaded_file.getvalue())
                            
                            # Create pre-restore backup
                            from local_backup import LocalBackup
                            backup_service = LocalBackup()
                            pre_restore_backup = backup_service.create_pre_restore_backup()
                            if pre_restore_backup:
                                st.session_state.last_pre_restore_backup = pre_restore_backup
                            
                            # Restore from backup
                            success = backup_service.restore_backup(temp_path)
                            
                            # Clean up temp file
                            os.remove(temp_path)
                            
                            if success:
                                st.success("✅ Khôi phục thành công!")
                                st.success("🔄 Vui lòng tải lại trang để thấy dữ liệu mới")
                                
                                # Store restore info for revert option
                                st.session_state.restore_completed = True
                                st.session_state.restored_from = uploaded_file.name
                                
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Khôi phục thất bại!")
                                
                        except Exception as e:
                            st.error(f"❌ Lỗi khôi phục: {str(e)}")
                            # Clean up temp file if it exists
                            if 'temp_path' in locals() and os.path.exists(temp_path):
                                os.remove(temp_path)
    
    # Information section
    st.subheader("ℹ️ Thông tin hệ thống sao lưu")
    st.info("""
    **Hệ thống sao lưu cục bộ:**
    • Tự động sao lưu hàng ngày lúc 2:00 AM
    • Tạo file backup nén (.zip) với metadata
    • Tự động dọn dẹp các backup cũ (giữ tối đa 10 bản)
    • Hỗ trợ khôi phục từ file backup
    • Backup bao gồm toàn bộ dữ liệu hệ thống
    """)

def user_management_section():
    """User management interface for admin users with password protection"""
    st.subheader("👥 Quản lý người dùng")
    
    # Only main admin can access user management
    if st.session_state.user.username != 'admin':
        st.warning("🚫 Chỉ tài khoản admin chính mới có thể quản lý người dùng.")
        return
    
    # Password protection for user management
    if not st.session_state.get('user_management_unlocked', False):
        st.warning("⚠️ Đây là khu vực nhạy cảm yêu cầu xác thực bổ sung")
        st.info("🔐 Quản lý người dùng có thể thay đổi quyền truy cập và xóa tài khoản. Vui lòng nhập mật khẩu để tiếp tục.")
        
        with st.form("user_management_auth"):
            admin_password = st.text_input(
                "Nhập mật khẩu admin để truy cập quản lý người dùng:",
                type="password",
                help="Nhập mật khẩu hiện tại của tài khoản admin"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                verify_submitted = st.form_submit_button("🔓 Xác thực", type="primary")
            with col2:
                cancel_submitted = st.form_submit_button("❌ Hủy")
            
            if verify_submitted:
                if admin_password:
                    # Verify admin password
                    import hashlib
                    password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
                    
                    db = Database()
                    admin_user = db.get_user_by_username('admin')
                    
                    if admin_user and admin_user.password_hash == password_hash:
                        st.session_state.user_management_unlocked = True
                        st.session_state.user_management_unlock_time = time.time()
                        st.success("✅ Xác thực thành công! Đang mở khóa quản lý người dùng...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Mật khẩu không đúng! Vui lòng thử lại.")
                        time.sleep(2)
                else:
                    st.error("❌ Vui lòng nhập mật khẩu!")
            
            if cancel_submitted:
                st.info("🔒 Đã hủy truy cập quản lý người dùng")
                return
        
        return
    
    # Check if unlock has expired (15 minutes timeout)
    unlock_time = st.session_state.get('user_management_unlock_time', 0)
    if time.time() - unlock_time > 900:  # 15 minutes = 900 seconds
        st.session_state.user_management_unlocked = False
        st.warning("⏰ Phiên xác thực đã hết hạn. Vui lòng xác thực lại.")
        st.rerun()
    
    # Show unlock status and remaining time
    remaining_time = 900 - (time.time() - unlock_time)
    minutes_left = int(remaining_time // 60)
    st.success(f"🔓 Quản lý người dùng đã được mở khóa. Còn lại: {minutes_left} phút")
    
    # Add manual lock button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔒 Khóa lại", help="Khóa lại quản lý người dùng"):
            st.session_state.user_management_unlocked = False
            if 'user_management_unlock_time' in st.session_state:
                del st.session_state.user_management_unlock_time
            st.info("🔒 Đã khóa quản lý người dùng")
            st.rerun()
    
    with col2:
        if st.button("⏰ Gia hạn", help="Gia hạn thời gian truy cập"):
            st.session_state.user_management_unlock_time = time.time()
            st.success("✅ Đã gia hạn thêm 15 phút")
            st.rerun()
    
    db = Database()
    
    # Create tabs for user management
    user_tabs = st.tabs(["📋 Danh sách người dùng", "➕ Thêm người dùng", "🔧 Chỉnh sửa người dùng", "🔑 Xem mật khẩu"])
    
    with user_tabs[0]:
        st.write("**📋 Danh sách tất cả người dùng:**")
        
        # Get all users
        try:
            users = db.get_all_users()
            
            if users:
                # Create DataFrame for display
                user_data = []
                for user in users:
                    user_data.append({
                        'ID': user.id,
                        'Tên đăng nhập': user.username,
                        'Họ tên': user.full_name,
                        'Vai trò': user.role,
                        'Email': user.email or 'Chưa có',
                        'Ngày tạo': user.created_at.strftime('%d/%m/%Y') if hasattr(user.created_at, 'strftime') and user.created_at else 'Không xác định'
                    })
                
                df = pd.DataFrame(user_data)
                st.dataframe(df, use_container_width=True)
                
                st.info(f"📊 Tổng số người dùng: {len(users)}")
                
            else:
                st.info("📭 Chưa có người dùng nào trong hệ thống.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi tải danh sách người dùng: {str(e)}")
    
    with user_tabs[1]:
        st.write("**➕ Thêm người dùng mới:**")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Tên đăng nhập *", key="new_username")
                new_fullname = st.text_input("Họ tên đầy đủ *", key="new_fullname")
                new_email = st.text_input("Email", key="new_email")
            
            with col2:
                new_password = st.text_input("Mật khẩu *", type="password", key="new_password")
                new_role = st.selectbox("Vai trò *", 
                                      ['teacher', 'doctor', 'administrative', 'family'],
                                      key="new_role")
                
                # Family-specific field
                if new_role == 'family':
                    students = db.get_all_students()
                    student_options = {f"{s.full_name} (ID: {s.id})": s.id for s in students}
                    if student_options:
                        selected_student = st.selectbox("Học sinh liên quan", 
                                                       options=list(student_options.keys()),
                                                       key="family_student")
                        family_student_id = student_options[selected_student]
                    else:
                        st.warning("⚠️ Chưa có học sinh nào trong hệ thống.")
                        family_student_id = None
                else:
                    family_student_id = None
            
            submitted = st.form_submit_button("✅ Thêm người dùng", type="primary")
            
            if submitted:
                if not all([new_username, new_fullname, new_password]):
                    st.error("❌ Vui lòng điền đầy đủ các trường bắt buộc (*)")
                else:
                    try:
                        success = db.create_user(
                            username=new_username,
                            password=new_password,
                            role=new_role,
                            full_name=new_fullname,
                            email=new_email if new_email else None,
                            family_student_id=family_student_id
                        )
                        
                        if success:
                            st.success(f"✅ Đã thêm người dùng '{new_username}' thành công!")
                            st.rerun()
                        else:
                            st.error("❌ Thêm người dùng thất bại. Tên đăng nhập có thể đã tồn tại.")
                            
                    except Exception as e:
                        st.error(f"❌ Lỗi khi thêm người dùng: {str(e)}")
    
    with user_tabs[2]:
        st.write("**🔧 Chỉnh sửa thông tin người dùng:**")
        
        try:
            users = db.get_all_users()
            
            if users:
                # Select user to edit
                user_options = {f"{u.full_name} ({u.username})": u.id for u in users}
                selected_user_display = st.selectbox("Chọn người dùng cần chỉnh sửa:", 
                                                   options=list(user_options.keys()))
                
                if selected_user_display:
                    user_id = user_options[selected_user_display]
                    user = db.get_user_by_id(user_id)
                    
                    if user:
                        with st.form("edit_user_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                edit_username = st.text_input("Tên đăng nhập", value=user.username, disabled=True)
                                edit_fullname = st.text_input("Họ tên", value=user.full_name)
                                edit_email = st.text_input("Email", value=user.email or "")
                            
                            with col2:
                                new_password_edit = st.text_input("Mật khẩu mới (để trống nếu không đổi)", 
                                                                type="password")
                                edit_role = st.selectbox("Vai trò", 
                                                        ['admin', 'teacher', 'doctor', 'administrative', 'family'],
                                                        index=['admin', 'teacher', 'doctor', 'administrative', 'family'].index(user.role))
                            
                            col_update, col_delete = st.columns(2)
                            
                            with col_update:
                                update_submitted = st.form_submit_button("💾 Cập nhật", type="primary")
                            
                            with col_delete:
                                if user.username != 'admin':  # Prevent deleting main admin
                                    delete_submitted = st.form_submit_button("🗑️ Xóa người dùng", 
                                                                           type="secondary")
                                else:
                                    st.info("⚠️ Không thể xóa tài khoản admin chính")
                                    delete_submitted = False
                            
                            if update_submitted:
                                try:
                                    success = db.update_user(
                                        user_id=user_id,
                                        full_name=edit_fullname,
                                        email=edit_email if edit_email else None,
                                        role=edit_role,
                                        new_password=new_password_edit if new_password_edit else None
                                    )
                                    
                                    if success:
                                        st.success("✅ Cập nhật thông tin người dùng thành công!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Cập nhật thất bại!")
                                        
                                except Exception as e:
                                    st.error(f"❌ Lỗi khi cập nhật: {str(e)}")
                            
                            if delete_submitted:
                                try:
                                    success = db.delete_user(user_id)
                                    
                                    if success:
                                        st.success("✅ Đã xóa người dùng thành công!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Xóa người dùng thất bại!")
                                        
                                except Exception as e:
                                    st.error(f"❌ Lỗi khi xóa: {str(e)}")
            
            else:
                st.info("📭 Chưa có người dùng nào để chỉnh sửa.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi tải danh sách người dùng: {str(e)}")
    
    with user_tabs[3]:
        st.write("**🔑 Xem mật khẩu người dùng:**")
        st.warning("⚠️ Chức năng này chỉ dành cho việc khôi phục tài khoản. Vui lòng sử dụng cẩn thận!")
        
        try:
            # Get user passwords (this uses the existing method)
            user_passwords = db.get_user_passwords()
            
            if user_passwords:
                st.write("**📊 Danh sách mật khẩu người dùng:**")
                
                # Create password table
                password_data = []
                for user_id, user_info in user_passwords.items():
                    password_data.append({
                        'ID': user_id,
                        'Tên đăng nhập': user_info['username'],
                        'Họ tên': user_info['full_name'],
                        'Vai trò': user_info['role'],
                        'Mật khẩu': user_info['password']
                    })
                
                # Display password table with special formatting
                df_passwords = pd.DataFrame(password_data)
                
                # Use data editor to allow copying
                st.data_editor(
                    df_passwords,
                    use_container_width=True,
                    disabled=True,
                    hide_index=True
                )
                
                st.info(f"📊 Tổng số tài khoản: {len(user_passwords)}")
                
                # Security notice
                st.error("""
                🔒 **Lưu ý bảo mật:**
                • Không chia sẻ thông tin mật khẩu với người khác
                • Chỉ sử dụng khi cần khôi phục tài khoản
                • Khuyến nghị người dùng đổi mật khẩu sau khi khôi phục
                • Mật khẩu được mã hóa trong cơ sở dữ liệu
                """)
                
                # Export passwords option
                if st.button("📄 Xuất danh sách mật khẩu", help="Xuất ra file để sao lưu"):
                    # Create export data
                    export_data = "ID,Tên đăng nhập,Họ tên,Vai trò,Mật khẩu\n"
                    for user_id, user_info in user_passwords.items():
                        export_data += f"{user_id},{user_info['username']},{user_info['full_name']},{user_info['role']},{user_info['password']}\n"
                    
                    st.download_button(
                        label="⬇️ Tải file CSV",
                        data=export_data,
                        file_name=f"user_passwords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Tải xuống danh sách mật khẩu dưới dạng CSV"
                    )
                
            else:
                st.info("📭 Không thể lấy thông tin mật khẩu.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy thông tin mật khẩu: {str(e)}")
            
        # Password reset functionality
        st.subheader("🔄 Đặt lại mật khẩu")
        
        with st.form("reset_password_form"):
            try:
                users = db.get_all_users()
                if users:
                    user_options = {f"{u.full_name} ({u.username})": u.id for u in users}
                    selected_user_reset = st.selectbox(
                        "Chọn người dùng cần đặt lại mật khẩu:",
                        options=list(user_options.keys())
                    )
                    
                    new_password_reset = st.text_input(
                        "Mật khẩu mới:",
                        type="password",
                        help="Nhập mật khẩu mới cho người dùng"
                    )
                    
                    confirm_password = st.text_input(
                        "Xác nhận mật khẩu:",
                        type="password",
                        help="Nhập lại mật khẩu để xác nhận"
                    )
                    
                    reset_submitted = st.form_submit_button("🔄 Đặt lại mật khẩu", type="primary")
                    
                    if reset_submitted:
                        if not new_password_reset:
                            st.error("❌ Vui lòng nhập mật khẩu mới!")
                        elif new_password_reset != confirm_password:
                            st.error("❌ Mật khẩu xác nhận không khớp!")
                        elif len(new_password_reset) < 6:
                            st.error("❌ Mật khẩu phải có ít nhất 6 ký tự!")
                        else:
                            user_id = user_options[selected_user_reset]
                            success = db.update_user(user_id=user_id, new_password=new_password_reset)
                            
                            if success:
                                st.success(f"✅ Đã đặt lại mật khẩu cho '{selected_user_reset}' thành công!")
                                st.info("💡 Vui lòng thông báo mật khẩu mới cho người dùng và yêu cầu họ đổi mật khẩu.")
                            else:
                                st.error("❌ Đặt lại mật khẩu thất bại!")
                
            except Exception as e:
                st.error(f"❌ Lỗi khi đặt lại mật khẩu: {str(e)}")

def spreadsheet_management_section():
    """Spreadsheet-style data management interface"""
    st.subheader("📊 Quản lý dữ liệu Spreadsheet")
    
    db = Database()
    
    # Create tabs for different data types
    data_tabs = st.tabs(["👥 Người dùng", "🎓 Học sinh", "🏛️ Cựu chiến binh", "🏥 Hồ sơ y tế"])
    
    with data_tabs[0]:
        st.write("**👥 Quản lý dữ liệu người dùng:**")
        
        try:
            users = db.get_all_users()
            
            if users:
                # Create editable dataframe
                user_data = []
                for user in users:
                    user_data.append({
                        'ID': user.id,
                        'Tên đăng nhập': user.username,
                        'Họ tên': user.full_name,
                        'Vai trò': user.role,
                        'Email': user.email or '',
                        'Chế độ tối': user.dark_mode if hasattr(user, 'dark_mode') else False
                    })
                
                df = pd.DataFrame(user_data)
                edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
                
                if st.button("💾 Lưu thay đổi người dùng", type="primary"):
                    st.info("💡 Chức năng lưu trực tiếp từ bảng đang được phát triển. Vui lòng sử dụng tab 'Chỉnh sửa người dùng'.")
            else:
                st.info("📭 Chưa có dữ liệu người dùng.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu người dùng: {str(e)}")
    
    with data_tabs[1]:
        st.write("**🎓 Quản lý dữ liệu học sinh:**")
        
        try:
            students = db.get_all_students()
            
            if students:
                student_data = []
                for student in students:
                    student_data.append({
                        'ID': student.id,
                        'Họ tên': student.full_name,
                        'Ngày sinh': student.birth_date,
                        'Địa chỉ': student.address,
                        'Email': student.email or '',
                        'Giới tính': getattr(student, 'gender', ''),
                        'Điện thoại': getattr(student, 'phone', ''),
                        'Lớp ID': student.class_id or ''
                    })
                
                df = pd.DataFrame(student_data)
                st.data_editor(df, use_container_width=True, disabled=True)
                
                st.info("💡 Để chỉnh sửa thông tin học sinh, vui lòng sử dụng trang 'Quản lý hồ sơ'.")
            else:
                st.info("📭 Chưa có dữ liệu học sinh.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu học sinh: {str(e)}")
    
    with data_tabs[2]:
        st.write("**🏛️ Quản lý dữ liệu cựu chiến binh:**")
        
        try:
            veterans = db.get_all_veterans()
            
            if veterans:
                veteran_data = []
                for veteran in veterans:
                    veteran_data.append({
                        'ID': veteran.id,
                        'Họ tên': veteran.full_name,
                        'Ngày sinh': veteran.birth_date,
                        'Địa chỉ': veteran.address,
                        'Email': veteran.email or '',
                        'Đơn vị phục vụ': getattr(veteran, 'unit_served', ''),
                        'Cấp bậc': getattr(veteran, 'rank', '')
                    })
                
                df = pd.DataFrame(veteran_data)
                st.data_editor(df, use_container_width=True, disabled=True)
                
                st.info("💡 Để chỉnh sửa thông tin cựu chiến binh, vui lòng sử dụng trang 'Quản lý hồ sơ'.")
            else:
                st.info("📭 Chưa có dữ liệu cựu chiến binh.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu cựu chiến binh: {str(e)}")
    
    with data_tabs[3]:
        st.write("**🏥 Quản lý hồ sơ y tế:**")
        
        try:
            medical_records = db.get_all_medical_records()
            
            if medical_records:
                medical_data = []
                for record in medical_records:
                    medical_data.append({
                        'ID': record.id,
                        'Bệnh nhân ID': record.student_id,
                        'Ngày khám': record.examination_date,
                        'Chẩn đoán': record.diagnosis,
                        'Điều trị': record.treatment,
                        'Bác sĩ ID': record.doctor_id
                    })
                
                df = pd.DataFrame(medical_data)
                st.data_editor(df, use_container_width=True, disabled=True)
                
                st.info("💡 Để chỉnh sửa hồ sơ y tế, vui lòng sử dụng trang 'Y tế'.")
            else:
                st.info("📭 Chưa có hồ sơ y tế.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi tải hồ sơ y tế: {str(e)}")

def excel_import_section():
    """Excel data import functionality"""
    st.subheader("📥 Nhập dữ liệu từ Excel")
    
    db = Database()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Chọn file Excel để nhập dữ liệu",
        type=['xlsx', 'xls'],
        help="Hỗ trợ định dạng .xlsx và .xls"
    )
    
    if uploaded_file:
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Đã tải file Excel thành công! Tìm thấy {len(df)} dòng dữ liệu.")
            
            # Show preview
            st.subheader("👀 Xem trước dữ liệu")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Data type selection
            st.subheader("📋 Chọn loại dữ liệu")
            data_type = st.selectbox(
                "Dữ liệu trong file Excel này là:",
                ["Học sinh", "Cựu chiến binh", "Người dùng", "Hồ sơ y tế"]
            )
            
            # Column mapping
            st.subheader("🔗 Ánh xạ cột dữ liệu")
            
            excel_columns = list(df.columns)
            
            if data_type == "Học sinh":
                st.write("**Ánh xạ cột cho dữ liệu học sinh:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    name_col = st.selectbox("Cột 'Họ tên':", excel_columns, key="name_col")
                    birth_col = st.selectbox("Cột 'Ngày sinh':", excel_columns, key="birth_col")
                    address_col = st.selectbox("Cột 'Địa chỉ':", excel_columns, key="address_col")
                
                with col2:
                    email_col = st.selectbox("Cột 'Email':", [""] + excel_columns, key="email_col")
                    gender_col = st.selectbox("Cột 'Giới tính':", [""] + excel_columns, key="gender_col")
                    phone_col = st.selectbox("Cột 'Điện thoại':", [""] + excel_columns, key="phone_col")
                
                if st.button("📥 Nhập dữ liệu học sinh", type="primary"):
                    with st.spinner("Đang nhập dữ liệu..."):
                        try:
                            success_count = 0
                            error_count = 0
                            
                            for _, row in df.iterrows():
                                try:
                                    # Prepare student data
                                    student_data = {
                                        'full_name': str(row[name_col]) if pd.notna(row[name_col]) else '',
                                        'birth_date': str(row[birth_col]) if pd.notna(row[birth_col]) else '',
                                        'address': str(row[address_col]) if pd.notna(row[address_col]) else '',
                                        'email': str(row[email_col]) if email_col and pd.notna(row[email_col]) else None,
                                        'gender': str(row[gender_col]) if gender_col and pd.notna(row[gender_col]) else None,
                                        'phone': str(row[phone_col]) if phone_col and pd.notna(row[phone_col]) else None
                                    }
                                    
                                    # Create student
                                    if db.create_student(**student_data):
                                        success_count += 1
                                    else:
                                        error_count += 1
                                        
                                except Exception as e:
                                    error_count += 1
                                    print(f"Error importing row: {e}")
                            
                            st.success(f"✅ Nhập dữ liệu hoàn thành!")
                            st.info(f"📊 Thành công: {success_count} | Lỗi: {error_count}")
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi khi nhập dữ liệu: {str(e)}")
            
            elif data_type == "Người dùng":
                st.write("**Ánh xạ cột cho dữ liệu người dùng:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    username_col = st.selectbox("Cột 'Tên đăng nhập':", excel_columns, key="username_col")
                    fullname_col = st.selectbox("Cột 'Họ tên':", excel_columns, key="fullname_col")
                    role_col = st.selectbox("Cột 'Vai trò':", excel_columns, key="role_col")
                
                with col2:
                    password_col = st.selectbox("Cột 'Mật khẩu':", excel_columns, key="password_col")
                    email_col_user = st.selectbox("Cột 'Email':", [""] + excel_columns, key="email_col_user")
                
                if st.button("📥 Nhập dữ liệu người dùng", type="primary"):
                    st.warning("⚠️ Chức năng nhập người dùng từ Excel cần được triển khai cẩn thận để đảm bảo bảo mật.")
            
            else:
                st.info(f"💡 Chức năng nhập '{data_type}' đang được phát triển.")
                
        except Exception as e:
            st.error(f"❌ Lỗi khi đọc file Excel: {str(e)}")
    
    # Import instructions
    st.subheader("📖 Hướng dẫn nhập dữ liệu")
    st.info("""
    **📋 Định dạng file Excel:**
    • File phải có định dạng .xlsx hoặc .xls
    • Dòng đầu tiên chứa tên cột
    • Không có dòng trống giữa dữ liệu
    
    **🎓 Dữ liệu học sinh:**
    • Cột bắt buộc: Họ tên, Ngày sinh, Địa chỉ
    • Cột tùy chọn: Email, Giới tính, Điện thoại
    
    **👥 Dữ liệu người dùng:**
    • Cột bắt buộc: Tên đăng nhập, Họ tên, Vai trò, Mật khẩu
    • Vai trò hợp lệ: admin, teacher, doctor, administrative, family
    """)

# ... (other function definitions would go here)

def render():
    """Main render function"""
    init_auth()
    
    # Apply theme from session state
    # apply_theme()  # Disabled - using Streamlit defaults

    # Set current page for role checking
    st.session_state.current_page = "01_Quản_lý_Hệ_thống"

    check_auth()
    
    # Restrict page to administrators only
    user_role = getattr(st.session_state, 'user_role', None)
    if user_role not in ['admin', 'administrative']:
        st.error("🚫 Chỉ có quản trị viên mới có thể truy cập trang này.")
        st.info("Trang này chứa các chức năng quản lý hệ thống nhạy cảm và chỉ dành cho người quản trị.")
        st.stop()
    
    # Check if user has access to this page dynamically  
    if not check_page_access('01_Quản_lý_Hệ_thống'):
        st.error("Bạn không có quyền truy cập trang này.")
        st.stop()
        return

    st.title("⚙️ Hệ thống quản lý dữ liệu Làng Hữu Nghị")

    # Create tabs for different management sections - reordered per user request
    tabs = st.tabs([
        "👥 Quản lý người dùng",
        "📊 Quản lý dữ liệu Spreadsheet",
        f"📥 {get_text('pages.system.import_data', 'Nhập Dữ Liệu từ Excel')}", 
        f"💾 {get_text('pages.system.backup_restore', 'Sao lưu & Khôi phục')}"
    ])

    with tabs[0]:
        # User management section with enhanced security
        user_management_section()

    with tabs[1]:
        # Spreadsheet data management
        spreadsheet_management_section()

    with tabs[2]:
        # Excel data import
        excel_import_section()

    with tabs[3]:
        # Backup and restore
        database_management_section()
        
    st.info("""
    ### 🔄 Phân chia chức năng
    - **Nhập dữ liệu từ Excel** (Trang hiện tại): Nhập dữ liệu học sinh từ file Excel với xử lý đặc biệt (chuyển đổi định dạng ngày tháng, làm sạch dữ liệu...)
    - **Quản lý Dữ liệu** (Trang quản lý Database): Xem, chỉnh sửa và xuất/nhập dữ liệu trực tiếp với từng bảng
    - **Sao lưu & Khôi phục** (Trang hiện tại): Tạo và khôi phục các bản sao lưu của toàn bộ cơ sở dữ liệu
    """)

if __name__ == "__main__":
    render()