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

def parse_date_advanced(date_str, format_hint="Auto-detect"):
    """Advanced date parsing with multiple format support and auto-detection"""
    if not date_str or pd.isna(date_str):
        return None
        
    # Convert to string for consistent handling
    date_str_clean = str(date_str).strip()
    
    # Handle empty or invalid values
    if not date_str_clean or date_str_clean.lower() in ['nan', 'none', 'null', 'na', 'n/a', 'không rõ', 'x', '?', '-', '--']:
        return None
    
    # Define date formats to try
    date_formats = []
    
    if format_hint == "Auto-detect":
        # Auto-detect based on common patterns
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y',
            '%d/%m/%y', '%d-%m-%y', '%Y/%m/%d', '%m-%d-%Y',
            '%d.%m.%Y', '%d.%m.%y', '%Y.%m.%d',
            '%d %m %Y', '%d %m %y', '%Y %m %d'
        ]
    else:
        # Use specific format hint
        format_map = {
            "dd/mm/yyyy": ['%d/%m/%Y'],
            "dd-mm-yyyy": ['%d-%m-%Y'],
            "yyyy-mm-dd": ['%Y-%m-%d'],
            "mm/dd/yyyy": ['%m/%d/%Y'],
            "dd/mm/yy": ['%d/%m/%y'],
            "dd-mm-yy": ['%d-%m-%y'],
            "yyyy/mm/dd": ['%Y/%m/%d']
        }
        date_formats = format_map.get(format_hint, ['%d/%m/%Y'])
    
    # Try parsing with pandas first (handles Excel dates)
    try:
        parsed_date = pd.to_datetime(date_str_clean, dayfirst=True)
        return parsed_date.strftime('%Y-%m-%d')
    except:
        pass
    
    # Try parsing with specified formats
    from datetime import datetime
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str_clean, fmt)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # Try parsing numeric Excel serial dates
    try:
        if date_str_clean.replace('.', '').isdigit():
            excel_date = float(date_str_clean)
            if 1 <= excel_date <= 100000:  # Reasonable range for Excel dates
                from datetime import datetime, timedelta
                # Excel epoch starts from 1900-01-01, but with 1900 leap year bug
                excel_epoch = datetime(1899, 12, 30)
                parsed_date = excel_epoch + timedelta(days=excel_date)
                return parsed_date.strftime('%Y-%m-%d')
    except:
        pass
    
    return None

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
    user_tabs = st.tabs(["🔑 Xem mật khẩu", "➕ Thêm người dùng", "🔧 Chỉnh sửa người dùng"])
    
    with user_tabs[0]:
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
    """Excel data import functionality with advanced edge case handling"""
    st.subheader("📥 Nhập dữ liệu từ Excel - Nâng cao")
    
    db = Database()
    
    # Advanced settings section
    with st.expander("⚙️ Cài đặt nâng cao", expanded=False):
        st.write("**📅 Định dạng ngày tháng:**")
        col1, col2 = st.columns(2)
        with col1:
            date_formats = [
                "dd/mm/yyyy", "dd-mm-yyyy", "yyyy-mm-dd", "mm/dd/yyyy", 
                "dd/mm/yy", "dd-mm-yy", "yyyy/mm/dd", "Auto-detect"
            ]
            selected_date_format = st.selectbox(
                "Định dạng ngày tháng trong Excel:",
                date_formats,
                index=len(date_formats)-1,
                help="Chọn định dạng ngày tháng hoặc để Auto-detect tự nhận diện"
            )
        
        with col2:
            # Duplicate handling options
            duplicate_options = [
                "Skip duplicates", "Update existing", "Create new", "Ask for each"
            ]
            duplicate_handling = st.selectbox(
                "Xử lý bản ghi trùng lặp:",
                duplicate_options,
                help="Cách xử lý khi phát hiện dữ liệu trùng lặp"
            )
        
        st.write("**🔧 Tùy chọn xử lý dữ liệu:**")
        col3, col4 = st.columns(2)
        with col3:
            clean_data = st.checkbox("Tự động làm sạch dữ liệu", value=True, help="Loại bỏ khoảng trắng thừa, định dạng lại text")
            validate_email = st.checkbox("Kiểm tra định dạng email", value=True, help="Xác thực địa chỉ email hợp lệ")
        
        with col4:
            validate_phone = st.checkbox("Kiểm tra số điện thoại", value=True, help="Xác thực định dạng số điện thoại Việt Nam")
            ignore_empty_rows = st.checkbox("Bỏ qua dòng trống", value=True, help="Không xử lý các dòng không có dữ liệu quan trọng")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Chọn file Excel để nhập dữ liệu",
        type=['xlsx', 'xls'],
        help="Hỗ trợ định dạng .xlsx và .xls. File tối đa 200MB"
    )
    
    if uploaded_file:
        try:
            # Enhanced file reading with error handling
            with st.spinner("Đang đọc file Excel..."):
                try:
                    # Try reading with different encodings and engines
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                except Exception as e1:
                    try:
                        df = pd.read_excel(uploaded_file, engine='xlrd')
                    except Exception as e2:
                        st.error(f"❌ Không thể đọc file Excel. Lỗi: {str(e1)}")
                        st.error(f"Thử lại với engine khác: {str(e2)}")
                        return
            
            # Data validation and cleaning
            original_rows = len(df)
            
            # Remove completely empty rows if option is selected
            if ignore_empty_rows:
                df = df.dropna(how='all')
                removed_empty = original_rows - len(df)
                if removed_empty > 0:
                    st.info(f"🧹 Đã loại bỏ {removed_empty} dòng trống")
            
            # Basic data info
            st.success(f"✅ Đã tải file Excel thành công!")
            
            # Show data statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Tổng dòng", len(df))
            with col2:
                st.metric("📋 Tổng cột", len(df.columns))
            with col3:
                st.metric("📝 Dòng có dữ liệu", df.count().max())
            with col4:
                st.metric("🚫 Dòng thiếu dữ liệu", len(df) - df.count().max())
            
            # Show data quality assessment
            st.subheader("🔍 Đánh giá chất lượng dữ liệu")
            quality_tab1, quality_tab2, quality_tab3 = st.tabs(["📊 Tổng quan", "⚠️ Vấn đề phát hiện", "👀 Xem trước"])
            
            with quality_tab1:
                # Data type analysis
                st.write("**📈 Phân tích kiểu dữ liệu:**")
                dtype_info = []
                for col in df.columns:
                    null_count = df[col].isnull().sum()
                    null_percent = (null_count / len(df)) * 100
                    dtype_info.append({
                        'Cột': col,
                        'Kiểu dữ liệu': str(df[col].dtype),
                        'Giá trị null': null_count,
                        '% Thiếu': f"{null_percent:.1f}%"
                    })
                
                st.dataframe(pd.DataFrame(dtype_info), use_container_width=True)
            
            with quality_tab2:
                # Identify potential issues
                issues = []
                
                for col in df.columns:
                    col_data = df[col].dropna()
                    if len(col_data) == 0:
                        continue
                    
                    # Check for potential date columns
                    if any(keyword in col.lower() for keyword in ['date', 'ngày', 'sinh', 'tạo', 'cập nhật']):
                        try:
                            pd.to_datetime(col_data.iloc[0])
                            issues.append(f"✅ Cột '{col}' có thể là ngày tháng")
                        except:
                            issues.append(f"⚠️ Cột '{col}' có thể là ngày tháng nhưng định dạng không chuẩn")
                    
                    # Check for potential email columns
                    if any(keyword in col.lower() for keyword in ['email', 'mail', 'e-mail']):
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        valid_emails = col_data.astype(str).str.match(email_pattern).sum()
                        if valid_emails < len(col_data) * 0.8:
                            issues.append(f"⚠️ Cột '{col}' có {len(col_data) - valid_emails} email không hợp lệ")
                        else:
                            issues.append(f"✅ Cột '{col}' có định dạng email hợp lệ")
                    
                    # Check for duplicate values
                    duplicates = col_data.duplicated().sum()
                    if duplicates > 0:
                        issues.append(f"🔄 Cột '{col}' có {duplicates} giá trị trùng lặp")
                
                if issues:
                    for issue in issues:
                        if issue.startswith("✅"):
                            st.success(issue)
                        elif issue.startswith("⚠️"):
                            st.warning(issue)
                        elif issue.startswith("🔄"):
                            st.info(issue)
                else:
                    st.success("✅ Không phát hiện vấn đề nào trong dữ liệu")
            
            with quality_tab3:
                # Show preview with enhanced formatting
                st.write("**👀 Xem trước dữ liệu (10 dòng đầu):**")
                preview_df = df.head(10).copy()
                
                # Apply basic cleaning for preview if enabled
                if clean_data:
                    for col in preview_df.columns:
                        if preview_df[col].dtype == 'object':
                            preview_df[col] = preview_df[col].astype(str).str.strip()
                
                st.dataframe(preview_df, use_container_width=True)
            
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
                    with st.spinner("Đang xử lý và nhập dữ liệu..."):
                        try:
                            success_count = 0
                            error_count = 0
                            duplicate_count = 0
                            updated_count = 0
                            error_details = []
                            
                            # Progress tracking
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            total_rows = len(df)
                            
                            for idx, row in df.iterrows():
                                # Update progress
                                progress = (idx + 1) / total_rows
                                progress_bar.progress(progress)
                                status_text.text(f"Đang xử lý dòng {idx + 1}/{total_rows}")
                                
                                try:
                                    # Clean and validate data
                                    raw_name = row[name_col] if pd.notna(row[name_col]) else ''
                                    raw_birth = row[birth_col] if pd.notna(row[birth_col]) else ''
                                    raw_address = row[address_col] if pd.notna(row[address_col]) else ''
                                    raw_email = row[email_col] if email_col and pd.notna(row[email_col]) else None
                                    raw_gender = row[gender_col] if gender_col and pd.notna(row[gender_col]) else None
                                    raw_phone = row[phone_col] if phone_col and pd.notna(row[phone_col]) else None
                                    
                                    # Skip empty rows if option enabled
                                    if ignore_empty_rows and not any([raw_name, raw_birth, raw_address]):
                                        continue
                                    
                                    # Clean data if enabled
                                    if clean_data:
                                        raw_name = str(raw_name).strip() if raw_name else ''
                                        raw_address = str(raw_address).strip() if raw_address else ''
                                        if raw_email:
                                            raw_email = str(raw_email).strip().lower()
                                        if raw_phone:
                                            # Clean phone number (remove spaces, dashes, etc.)
                                            raw_phone = ''.join(filter(str.isdigit, str(raw_phone)))
                                    
                                    # Validate email format
                                    if validate_email and raw_email:
                                        import re
                                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                                        if not re.match(email_pattern, raw_email):
                                            error_details.append(f"Dòng {idx + 1}: Email không hợp lệ '{raw_email}'")
                                            raw_email = None
                                    
                                    # Validate phone number format
                                    if validate_phone and raw_phone:
                                        # Vietnamese phone number validation
                                        if not (raw_phone.startswith('0') and len(raw_phone) in [10, 11]):
                                            error_details.append(f"Dòng {idx + 1}: SĐT không hợp lệ '{raw_phone}'")
                                            raw_phone = None
                                    
                                    # Parse date with multiple formats
                                    processed_birth_date = None
                                    if raw_birth:
                                        processed_birth_date = parse_date_advanced(raw_birth, selected_date_format)
                                        if not processed_birth_date:
                                            error_details.append(f"Dòng {idx + 1}: Ngày sinh không hợp lệ '{raw_birth}'")
                                    
                                    # Check for duplicates
                                    existing_student = None
                                    if raw_name and processed_birth_date:
                                        # Check for existing student with same name and birth date
                                        try:
                                            students = db.get_all_students()
                                            for student in students:
                                                if (student.full_name.lower() == raw_name.lower() and 
                                                    student.birth_date == processed_birth_date):
                                                    existing_student = student
                                                    break
                                        except:
                                            pass
                                    
                                    # Prepare student data
                                    student_data = {
                                        'full_name': raw_name,
                                        'birth_date': processed_birth_date,
                                        'address': raw_address,
                                        'email': raw_email,
                                        'gender': raw_gender,
                                        'phone': raw_phone
                                    }
                                    
                                    # Handle duplicates based on user preference
                                    if existing_student:
                                        if duplicate_handling == "Skip duplicates":
                                            duplicate_count += 1
                                            continue
                                        elif duplicate_handling == "Update existing":
                                            # Update existing student
                                            if db.update_student(existing_student.id, **student_data):
                                                updated_count += 1
                                            else:
                                                error_count += 1
                                                error_details.append(f"Dòng {idx + 1}: Không thể cập nhật học sinh '{raw_name}'")
                                            continue
                                        elif duplicate_handling == "Ask for each":
                                            # This would require UI interaction - for now, skip
                                            duplicate_count += 1
                                            continue
                                        # "Create new" - proceed with creation
                                    
                                    # Validate required fields
                                    if not raw_name:
                                        error_count += 1
                                        error_details.append(f"Dòng {idx + 1}: Thiếu họ tên")
                                        continue
                                    
                                    # Create student
                                    if db.create_student(**student_data):
                                        success_count += 1
                                    else:
                                        error_count += 1
                                        error_details.append(f"Dòng {idx + 1}: Không thể tạo học sinh '{raw_name}'")
                                        
                                except Exception as e:
                                    error_count += 1
                                    error_details.append(f"Dòng {idx + 1}: Lỗi xử lý - {str(e)}")
                            
                            # Complete progress
                            progress_bar.progress(1.0)
                            status_text.text("Hoàn thành!")
                            
                            # Show results
                            st.success(f"✅ Nhập dữ liệu hoàn thành!")
                            
                            # Results summary
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("✅ Thành công", success_count)
                            with col2:
                                st.metric("🔄 Cập nhật", updated_count)
                            with col3:
                                st.metric("⏭️ Bỏ qua", duplicate_count)
                            with col4:
                                st.metric("❌ Lỗi", error_count)
                            
                            # Show error details if any
                            if error_details:
                                with st.expander(f"⚠️ Chi tiết lỗi ({len(error_details)} mục)", expanded=False):
                                    for error in error_details[:50]:  # Limit to first 50 errors
                                        st.error(error)
                                    if len(error_details) > 50:
                                        st.warning(f"... và {len(error_details) - 50} lỗi khác")
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi nghiêm trọng khi nhập dữ liệu: {str(e)}")
                            st.exception(e)
            
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
    
    # Enhanced import instructions
    st.subheader("📖 Hướng dẫn nhập dữ liệu nâng cao")
    
    instruction_tabs = st.tabs(["📋 Định dạng file", "🎓 Dữ liệu học sinh", "👥 Dữ liệu người dùng", "⚙️ Tính năng nâng cao"])
    
    with instruction_tabs[0]:
        st.info("""
        **📋 Định dạng file Excel được hỗ trợ:**
        • File phải có định dạng .xlsx hoặc .xls
        • Dòng đầu tiên chứa tên cột (header)
        • Tối đa 200MB, không giới hạn số dòng
        • Hỗ trợ nhiều engine đọc file (openpyxl, xlrd)
        • Tự động phát hiện và xử lý encoding
        """)
    
    with instruction_tabs[1]:
        st.info("""
        **🎓 Dữ liệu học sinh:**
        • **Cột bắt buộc:** Họ tên, Ngày sinh, Địa chỉ
        • **Cột tùy chọn:** Email, Giới tính, Điện thoại
        • **Định dạng ngày:** dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, hoặc Auto-detect
        • **Email:** Tự động validate định dạng email@domain.com
        • **SĐT:** Validate số điện thoại Việt Nam (10-11 số, bắt đầu bằng 0)
        """)
    
    with instruction_tabs[2]:
        st.warning("""
        **👥 Dữ liệu người dùng:**
        • **Cột bắt buộc:** Tên đăng nhập, Họ tên, Vai trò, Mật khẩu
        • **Vai trò hợp lệ:** admin, teacher, doctor, administrative, family
        • **Bảo mật:** Chức năng này cần được triển khai cẩn thận
        • **Khuyến nghị:** Chỉ admin có thể nhập dữ liệu người dùng
        """)
    
    with instruction_tabs[3]:
        st.success("""
        **⚙️ Tính năng nâng cao:**
        • **Xử lý trùng lặp:** Skip, Update, Create new, Ask for each
        • **Làm sạch dữ liệu:** Tự động loại bỏ khoảng trắng, định dạng text
        • **Validation:** Email, số điện thoại, ngày tháng
        • **Progress tracking:** Theo dõi tiến trình import real-time
        • **Error reporting:** Chi tiết lỗi với số dòng cụ thể
        • **Data quality:** Phân tích chất lượng dữ liệu trước khi import
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