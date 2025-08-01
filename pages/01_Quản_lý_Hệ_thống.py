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
                for backup in backups[-3:]:  # Show last 3 backups
                    st.write(f"• {backup['filename']} ({backup['size']})")
            else:
                st.write("📭 Chưa có bản sao lưu nào")
                
        except Exception as e:
            st.write("⚠️ Không thể kiểm tra thông tin backup")
    
    # Restore Section
    st.subheader("🔄 Khôi phục dữ liệu")
    
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
            if st.button("🔄 Khôi phục", type="primary"):
                with st.spinner("Đang khôi phục dữ liệu..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = f"temp_restore_{uploaded_file.name}"
                        with open(temp_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())
                        
                        # Restore from backup
                        from local_backup import LocalBackup
                        backup_service = LocalBackup()
                        
                        success = backup_service.restore_backup(temp_path)
                        
                        # Clean up temp file
                        os.remove(temp_path)
                        
                        if success:
                            st.success("✅ Khôi phục thành công!")
                            st.success("🔄 Vui lòng tải lại trang để thấy dữ liệu mới")
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
    """User management interface for admin users"""
    # ... (keeping the existing user management code)
    pass

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
        # User management section (merged from admin page)
        user_management_section()

    with tabs[1]:
        # Spreadsheet data management
        st.info("Chức năng quản lý dữ liệu spreadsheet")

    with tabs[2]:
        # Excel data import
        st.info("Chức năng nhập dữ liệu từ Excel")

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