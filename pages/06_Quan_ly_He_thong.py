import streamlit as st
import pandas as pd
from database import Database
from auth import check_auth, check_role, can_manage_data
from utils import show_success, show_error, apply_theme
from datetime import datetime, timedelta
import os
import sqlite3
import io
import re
from translations import get_text

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

    # Convert to string and clean up
    date_str = str(date_str).strip()

    # Skip header-like strings or likely addresses
    header_keywords = ['năm sinh', 'ngày sinh', 'họ và tên', 'họ tên', 'stt', 'số thứ tự', 'xóm', 'thôn', 
                     'đường', 'phố', 'phường', 'quận', 'huyện', 'tỉnh', 'tp', 'thành phố', 'hà nội', 'hải phòng']
    if any(keyword in date_str.lower() for keyword in header_keywords):
        return None
    
    # Nếu dữ liệu có dấu phẩy hoặc quá dài, đây có thể là địa chỉ, không phải ngày tháng
    if len(date_str) > 20 or ',' in date_str:
        return None
        
    # Kiểm tra nếu chuỗi có chứa chữ không phải số, dấu gạch ngang, hay dấu chấm (có thể là địa chỉ)
    if re.search(r'[^\d\-\.\/\s]', date_str):
        # Cho phép các chữ tháng trong tiếng Việt hoặc Anh 
        month_keywords = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
                        'january', 'february', 'march', 'april', 'june', 'july', 'august', 'september', 'october', 'november', 'december',
                        'tháng', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười', 'mươi', 'mốt']
        if not any(keyword in date_str.lower() for keyword in month_keywords):
            return None
    
    # Special case for "X" which appears in some cells
    if date_str.upper() == 'X' or date_str == '?':
        return None

    # Handle Excel serial numbers (e.g. 42009)
    try:
        if str(date_str).replace('.0', '').isdigit():
            excel_date = int(float(date_str))
            if excel_date > 1000:  # Excel serial date
                base_date = datetime(1899, 12, 30)
                date_obj = base_date + timedelta(days=excel_date)
                if 1900 <= date_obj.year <= 2100:
                    return date_obj.strftime('%Y-%m-%d')
            elif 1900 <= excel_date <= 2100:  # Year only
                return f"{excel_date}-01-01"
    except:
        pass

    # Try common date formats including Excel's full datetime format
    formats = [
        '%Y-%m-%d %H:%M:%S',  # e.g. "1996-01-15 00:00:00"
        '%Y-%m-%d %H:%M:%S.%f',  # handles milliseconds
        '%m/%d/%Y %H:%M',  # alternative Excel format
        '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y',
        '%Y/%m/%d', '%d.%m.%Y', '%Y.%m.%d',
        '%B %d, %Y',  # "January 15, 1996"
        '%d %B %Y',   # "15 January 1996"
        '%Y-%m-%d.000',  # "1996-01-15.000"
        '%d/%m/%Y.000'  # "15/01/1996.000"
    ]

    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            if 1900 <= date_obj.year <= 2100:
                return date_obj.strftime('%Y-%m-%d')
        except:
            continue
            
    # Try to extract just a year if everything else fails
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', date_str)
    if year_match:
        year = year_match.group(1)
        return f"{year}-01-01"

    # Instead of raising an error, return None to allow processing to continue
    return None

def is_header_row(row):
    """Check if row appears to be a header"""
    if pd.isna(row).all():  # Empty row
        return True

    row_values = [str(val).lower().strip() for val in row]
    header_keywords = ['họ và tên', 'họ tên', 'stt', 'số thứ tự', 'năm sinh', 'ngày sinh', 'mã học sinh', 'địa chỉ', 'giới tính', 'lớp']
    return any(any(keyword in val for keyword in header_keywords) for val in row_values)

def clean_string(text):
    """Clean and standardize text input"""
    if pd.isna(text):
        return ""
    return ' '.join(str(text).strip().split())

def import_data_section():
    """Import data from Excel section"""
    st.subheader("📥 Nhập Dữ Liệu từ Excel")
    
    st.write("""
    ### 📋 Hướng dẫn
    1. File Excel cần có các cột sau:
        - Họ và tên (bắt buộc)
        - Ngày sinh (không bắt buộc)
        - Giới tính (không bắt buộc - có thể dùng 1 cột hoặc 2 cột Nam/Nữ)
        - Địa chỉ (không bắt buộc)
        - Email (không bắt buộc)
        - Số điện thoại (không bắt buộc)
        - Năm (không bắt buộc)
        - Tên bố mẹ/người giám hộ (không bắt buộc)
        - Ngày nhập học (không bắt buộc, mặc định là ngày hôm nay)
        - Tình trạng sức khỏe (không bắt buộc)
        - Tình trạng học tập (không bắt buộc)
    2. Hỗ trợ nhiều định dạng ngày tháng:
        - DD/MM/YYYY (VD: 25/12/2023)
        - YYYY-MM-DD (VD: 2023-12-25)
        - Năm (VD: 2007)
        - Số serial Excel (tự động chuyển đổi)
        - Định dạng đầy đủ (VD: 1996-01-15 00:00:00)
        - Định dạng Excel đầy đủ (VD: 1996-01-15 00:00:00.000)
        - Định dạng văn bản (VD: 15 Tháng 1, 1996)
    3. Hệ thống sẽ tự động:
        - Bỏ qua các dòng trống
        - Bỏ qua các dòng tiêu đề trùng lặp
        - Định dạng lại ngày tháng
        - Cho phép giá trị trống với trường ngày sinh
        - Tự động bỏ qua các chuỗi 'nan', 'X' hoặc '?'
        - Chỉ giữ lại dữ liệu mới nhất nếu trùng tên học sinh
        - Loại bỏ dữ liệu trùng lặp, tự động cập nhật nếu có thông tin mới
    """)

    uploaded_file = st.file_uploader("📎 Chọn file Excel", type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            # Read Excel file
            df = pd.read_excel(
                uploaded_file,
                engine='openpyxl',
                dtype=str  # Read all columns as string
            )

            # Remove empty rows
            df = df.dropna(how='all')

            # Show preview
            st.write("### 📊 Xem trước dữ liệu gốc")
            st.dataframe(df.head(), use_container_width=True)
            st.write(f"📌 Tổng số dòng trong file: {len(df)}")

            st.markdown("---")

            # Column mapping
            st.write("### 🔄 Ánh xạ cột")
            st.info("Chọn cột tương ứng với từng trường thông tin")

            columns = [''] + df.columns.tolist()

            mapping = {
                'full_name': st.selectbox('👤 Họ và tên (*)', options=columns, key='map_name'),
                'birth_date': st.selectbox('📅 Ngày sinh', options=columns, key='map_birth'),
                'gender': st.selectbox('⚧ Giới tính (một cột)', options=columns, key='map_gender'),
                'gender_male': st.selectbox('♂️ Cột Nam', options=columns, key='map_gender_male'),
                'gender_female': st.selectbox('♀️ Cột Nữ', options=columns, key='map_gender_female'),
                'phone': st.selectbox('📞 Số điện thoại', options=columns, key='map_phone'),
                'address': st.selectbox('📍 Địa chỉ', options=columns, key='map_address'),
                'email': st.selectbox('📧 Email', options=columns, key='map_email'),
                'year': st.selectbox('📅 Năm', options=columns, key='map_year'),
                'parent_name': st.selectbox('👪 Họ tên bố mẹ', options=columns, key='map_parent'),
                'health_status': st.selectbox('🏥 Tình trạng sức khỏe', options=columns, key='map_health'),
                'academic_status': st.selectbox('📚 Tình trạng học tập', options=columns, key='map_academic')
            }
            
            with st.expander("🔍 Hướng dẫn trường Giới tính"):
                st.info("""
                Bạn có 2 cách để nhập giới tính:
                1. Sử dụng một cột đã có giới tính (Nam/Nữ/Nam, Nữ,...) - Chọn ở trường "Giới tính (một cột)"
                2. Hoặc sử dụng 2 cột riêng biệt (cột Nam và cột Nữ):
                   - Chọn cột có đánh dấu Nam (thường có giá trị X, đánh dấu, hoặc 1)
                   - Chọn cột có đánh dấu Nữ (thường có giá trị X, đánh dấu, hoặc 1)
                """)
                st.warning("Nếu bạn sử dụng cách 2 (2 cột), hệ thống sẽ ưu tiên sử dụng 2 cột Nam/Nữ.")

            if st.button("✅ Nhập dữ liệu"):
                if not mapping['full_name']:
                    st.error("Vui lòng chọn cột Họ và tên")
                    return

                success_count = 0
                error_count = 0
                error_logs = []
                today = datetime.now().strftime("%Y-%m-%d")

                # Dictionary to store latest data for each name
                name_data = {}
                
                # Tạo dataframe để xem trước dữ liệu đã xử lý
                preview_data = []

                # First pass: collect all valid data and keep only the latest entry for each name
                for idx, row in df.iterrows():
                    full_name = None
                    try:
                        # Skip header rows
                        if is_header_row(row):
                            continue

                        # Get and validate name
                        if mapping['full_name'] not in row:
                            continue  # Skip rows without the mapped name column
                            
                        full_name = clean_string(row[mapping['full_name']])
                        if not full_name:
                            continue  # Skip rows with empty names

                        # Build student data with safe access to mapped columns first (to use later)
                        student_data = {
                            "full_name": full_name,
                            "birth_date": None,
                            "admission_date": today,
                            "health_status": "Bình thường",
                            "academic_status": "Chưa đánh giá",
                            "psychological_status": "Ổn định",
                            "address": ""
                        }
                        
                        # Parse birth date if column is selected
                        birth_date = None
                        if mapping['birth_date'] and mapping['birth_date'] in row:
                            birth_date_raw = str(row[mapping['birth_date']]).strip()
                            
                            # Kiểm tra nhanh trước khi xử lý ngày tháng
                            # Nếu dữ liệu có vẻ như là địa chỉ, lưu vào trường địa chỉ
                            address_keywords = ["xóm", "thôn", "phố", "đường", "quận", "huyện", "tỉnh", "tp", "hà nội", "hải phòng"]
                            
                            # Kiểm tra xem có phải số điện thoại không
                            is_phone = birth_date_raw.isdigit() and len(birth_date_raw) >= 9 and birth_date_raw.startswith('0')
                            
                            if is_phone:
                                # Trường hợp đặc biệt: ngày sinh là số điện thoại
                                if not student_data.get('phone'):
                                    student_data['phone'] = birth_date_raw
                                    error_logs.append(f"Dòng {idx + 2}: {full_name} - Phát hiện số điện thoại trong cột ngày sinh, đã chuyển sang trường số điện thoại")
                                birth_date = None
                            elif any(keyword in birth_date_raw.lower() for keyword in address_keywords):
                                if not mapping['address'] or mapping['address'] not in row or not row.get(mapping['address']):
                                    # Chỉ gán vào address nếu chưa có dữ liệu địa chỉ
                                    student_data['address'] = birth_date_raw
                                error_logs.append(f"Dòng {idx + 2}: {full_name} - Cảnh báo: Dữ liệu ngày sinh ({birth_date_raw}) có vẻ là địa chỉ, đã tự động chuyển sang trường địa chỉ")
                                birth_date = None
                            # Handle missing or invalid birth dates
                            elif not (pd.isna(birth_date_raw) or birth_date_raw.lower() in ['nan', 'none', 'null', '?', 'x', 'n/a', '']):
                                try:
                                    birth_date = parse_date(birth_date_raw)
                                    if not birth_date:
                                        error_logs.append(f"Dòng {idx + 2}: {full_name} - Cảnh báo: Không thể đọc định dạng ngày tháng: {birth_date_raw}")
                                except ValueError as e:
                                    # Just log the error but continue processing this record
                                    error_logs.append(f"Dòng {idx + 2}: {full_name} - Cảnh báo: {str(e)}")
                                    # Don't increment error_count since we're allowing empty birth dates now

                        # Cập nhật dữ liệu student_data sau khi đã xử lý
                        student_data["birth_date"] = birth_date
                        
                        # Biến để theo dõi trạng thái đã xử lý giới tính chưa
                        gender_processed = False
                        
                        # Xử lý 2 cột giới tính (Nam và Nữ) nếu đã được chọn
                        if mapping['gender_male'] and mapping['gender_female'] and \
                           mapping['gender_male'] in row and mapping['gender_female'] in row:
                            male_value = str(row[mapping['gender_male']]).strip()
                            female_value = str(row[mapping['gender_female']]).strip()
                            
                            # Các ký hiệu đánh dấu có thể gặp
                            male_markers = ['x', 'X', '1', 'có', 'yes', 'true', '+', '✓', '✔', 'nam', 'v']
                            female_markers = ['x', 'X', '1', 'có', 'yes', 'true', '+', '✓', '✔', 'nữ', 'v']
                            
                            # Kiểm tra sự tồn tại của các đánh dấu trong cột
                            male_marked = any(marker == male_value.lower() or marker in male_value.lower() for marker in male_markers)
                            female_marked = any(marker == female_value.lower() or marker in female_value.lower() for marker in female_markers)
                            
                            if male_marked and not female_marked:
                                student_data['gender'] = 'Nam'
                                gender_processed = True
                            elif female_marked and not male_marked:
                                student_data['gender'] = 'Nữ'
                                gender_processed = True
                            elif male_marked and female_marked:
                                # Trường hợp cả hai cột đều có đánh dấu - lấy theo quy tắc ưu tiên
                                student_data['gender'] = 'Nam'  # Mặc định chọn Nam nếu cả hai đều được đánh dấu
                                gender_processed = True
                                error_logs.append(f"Cảnh báo - Dòng {idx + 2}: {full_name} - Cả hai cột Nam và Nữ đều được đánh dấu. Mặc định chọn 'Nam'.")
                            # Nếu cả hai cột đều không có đánh dấu, sẽ thử xử lý từ cột giới tính đơn ở bước tiếp theo
                        
                        # Nếu chưa xử lý được giới tính từ 2 cột Nam/Nữ, thử xử lý từ cột giới tính đơn
                        if not gender_processed and mapping['gender'] and mapping['gender'] in row:
                            gender_value = str(row[mapping['gender']]).strip().lower()
                            
                            if gender_value in ['', 'nan', 'none', 'null', 'n/a', '?']:
                                # Giữ giá trị mặc định nếu trống
                                pass
                            elif gender_value in ['nam', 'male', 'm', 'trai', 'boy']:
                                student_data['gender'] = 'Nam'
                            elif gender_value in ['nữ', 'nu', 'female', 'f', 'gái', 'girl']:
                                student_data['gender'] = 'Nữ'
                            elif 'nam' in gender_value or 'male' in gender_value or 'trai' in gender_value or 'boy' in gender_value:
                                student_data['gender'] = 'Nam'
                            elif 'nữ' in gender_value or 'nu' in gender_value or 'female' in gender_value or 'gái' in gender_value or 'girl' in gender_value:
                                student_data['gender'] = 'Nữ'
                            else:
                                student_data['gender'] = 'Khác'
                        
                        # Process other columns
                        for field, column in mapping.items():
                            # Skip fields already processed (birth_date and gender)
                            if field in ['full_name', 'birth_date', 'gender', 'gender_male', 'gender_female']:
                                continue
                                
                            # Process if column is selected and exists in the row
                            if column and column in row:
                                value = clean_string(row[column])
                                if value:  # Only add if not empty
                                    # Special processing for different field types
                                    if field == 'health_status':
                                        # Map to our standardized health status values
                                        value_lower = value.lower()
                                        if any(word in value_lower for word in ['tốt', 'good', 'khỏe', 'excellent']):
                                            student_data['health_status'] = 'Tốt'
                                        elif any(word in value_lower for word in ['bình thường', 'normal', 'average', 'khá']):
                                            student_data['health_status'] = 'Bình thường'
                                        elif any(word in value_lower for word in ['ổn định', 'stable']):
                                            student_data['health_status'] = 'Ổn định'
                                        elif any(word in value_lower for word in ['cần chú ý', 'cần theo dõi', 'chú ý', 'theo dõi', 'attention', 'monitor']):
                                            student_data['health_status'] = 'Cần chú ý'
                                        else:
                                            student_data['health_status'] = 'Bình thường'
                                    elif field == 'academic_status':
                                        # Map to our standardized academic status values
                                        value_lower = value.lower()
                                        if any(word in value_lower for word in ['xuất sắc', 'excellent', 'giỏi']):
                                            student_data['academic_status'] = 'Xuất sắc'
                                        elif any(word in value_lower for word in ['tốt', 'good', 'khá']):
                                            student_data['academic_status'] = 'Tốt'
                                        elif any(word in value_lower for word in ['trung bình', 'average']):
                                            student_data['academic_status'] = 'Trung bình'
                                        elif any(word in value_lower for word in ['cần cải thiện', 'improve', 'yếu', 'kém']):
                                            student_data['academic_status'] = 'Cần cải thiện'
                                        else:
                                            student_data['academic_status'] = 'Chưa đánh giá'
                                    elif field == 'phone' and not value.isdigit():
                                        # Validate phone number - should contain only digits
                                        digits_only = ''.join(c for c in value if c.isdigit())
                                        if len(digits_only) >= 8:
                                            student_data['phone'] = digits_only
                                        else:
                                            error_logs.append(f"Dòng {idx + 2}: {full_name} - Cảnh báo: Số điện thoại không hợp lệ: {value}")
                                    elif field == 'email' and '@' not in value:
                                        # Basic email validation
                                        address_keywords = ["xóm", "thôn", "phố", "đường", "quận", "huyện", "tỉnh", "tp", "hà nội", "hải phòng"]
                                        if any(keyword in value.lower() for keyword in address_keywords):
                                            if not student_data.get('address'):
                                                student_data['address'] = value
                                                error_logs.append(f"Dòng {idx + 2}: {full_name} - Cảnh báo: Dữ liệu email ({value}) có vẻ là địa chỉ, đã tự động chuyển sang trường địa chỉ")
                                        else:
                                            error_logs.append(f"Dòng {idx + 2}: {full_name} - Cảnh báo: Email không hợp lệ: {value}")
                                    else:
                                        # Default processing for all other fields
                                        student_data[field] = value
                                
                        # Add or update data in our name-indexed collection
                        # Always keep the newest entry (based on row index)
                        name_data[full_name] = student_data
                        
                        # Add to preview data
                        preview_data.append(student_data)
                        
                    except Exception as e:
                        error_count += 1
                        error_logs.append(f"Dòng {idx + 2}: Lỗi xử lý - {str(e)}")
                
                # Display preview of processed data
                st.subheader("📊 Dữ liệu đã xử lý")
                preview_df = pd.DataFrame(preview_data)
                st.dataframe(preview_df, use_container_width=True)
                
                # Display error logs if any
                if error_logs:
                    with st.expander(f"⚠️ Cảnh báo và Ghi chú ({len(error_logs)})"):
                        for log in error_logs:
                            st.warning(log)
                
                # Confirm import
                confirm = st.checkbox("✓ Tôi đã kiểm tra dữ liệu và muốn nhập vào hệ thống")
                if confirm:
                    with st.spinner("Đang nhập dữ liệu..."):
                        db = Database()

                        # Second pass: add unique entries to database
                        for full_name, student_data in name_data.items():
                            try:
                                student_id = db.add_student(student_data)
                                if student_id:
                                    success_count += 1
                                else:
                                    error_count += 1
                                    error_logs.append(f"Không thể thêm học sinh: {full_name}")
                            except Exception as e:
                                error_count += 1
                                error_logs.append(f"Lỗi khi thêm học sinh {full_name}: {str(e)}")
                        
                        st.success(f"✅ Đã nhập thành công {success_count} học sinh!")
                        if error_count > 0:
                            st.error(f"❌ Có {error_count} lỗi khi nhập dữ liệu")
                            with st.expander("Xem chi tiết lỗi"):
                                for log in error_logs:
                                    st.error(log)

        except Exception as e:
            st.error(f"❌ Lỗi khi đọc file Excel: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

def database_management_section():
    """Database backup and cleanup section"""
    st.subheader("💾 Sao lưu & Khôi phục cơ sở dữ liệu")
    
    db = Database()
    
    tabs = st.tabs(["💾 Sao lưu & Khôi phục", "🧹 Dọn dẹp dữ liệu"])
    
    with tabs[0]:
        st.info("""
        ℹ️ **Hướng dẫn:**
        1. Sao lưu: Tạo bản sao lưu của cơ sở dữ liệu hiện tại
        2. Khôi phục: Quay lại phiên bản cũ từ bản sao lưu
        3. Tải xuống: Tải file sao lưu về máy tính của bạn
        4. Các bản sao lưu được lưu trong thư mục 'database_backups'
        """)

        # Create backup section
        st.subheader("📥 Tạo Bản Sao Lưu")
        with st.form("backup_form"):
            backup_name = st.text_input(
                "Tên bản sao lưu",
                placeholder="Để trống để dùng tên mặc định (timestamp)",
                help="Tên file sẽ được thêm đuôi .db"
            )
            
            if st.form_submit_button("💾 Tạo bản sao lưu"):
                try:
                    backup_path = db.backup_database(backup_name)
                    show_success(f"✨ Đã tạo bản sao lưu tại: {backup_path}")
                    st.rerun()
                except Exception as e:
                    show_error(f"❌ Lỗi khi tạo bản sao lưu: {str(e)}")

        # List and restore backups section
        st.subheader("📋 Danh Sách Bản Sao Lưu")
        backups = db.get_available_backups()
        
        if backups:
            for backup_file, timestamp, size in backups:
                with st.expander(f"📁 {backup_file} - {timestamp.strftime('%d/%m/%Y %H:%M:%S')}", expanded=False):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.info(f"""
                        **📅 Thời gian tạo:** {timestamp.strftime('%d/%m/%Y %H:%M:%S')}
                        **📦 Kích thước:** {size}
                        **📍 Đường dẫn:** database_backups/{backup_file}
                        """)
                    
                    with col2:
                        # Download button
                        backup_path = os.path.join('database_backups', backup_file)
                        if os.path.exists(backup_path):
                            with open(backup_path, 'rb') as file:
                                download_button = st.download_button(
                                    label="⬇️ Tải xuống",
                                    data=file,
                                    file_name=backup_file,
                                    mime="application/octet-stream",
                                    key=f"download_{backup_file}"
                                )
                    
                    with col3:
                        if st.button("🔄 Khôi phục", key=f"restore_{backup_file}"):
                            if st.session_state.get('confirm_restore') != backup_file:
                                st.session_state.confirm_restore = backup_file
                                st.warning("⚠️ Cảnh báo: Khôi phục sẽ ghi đè lên dữ liệu hiện tại. Bạn có chắc chắn muốn tiếp tục?")
                                st.button("✅ Xác nhận khôi phục", key=f"confirm_{backup_file}")
                            else:
                                try:
                                    backup_path = os.path.join('database_backups', backup_file)
                                    db.restore_database(backup_path)
                                    show_success("✨ Đã khôi phục cơ sở dữ liệu thành công!")
                                    st.session_state.confirm_restore = None
                                    st.rerun()
                                except Exception as e:
                                    show_error(f"❌ Lỗi khi khôi phục: {str(e)}")
        else:
            st.info("💡 Chưa có bản sao lưu nào")
    
    with tabs[1]:
        st.subheader("🧹 Dọn dẹp dữ liệu trùng lặp")
        
        # Thêm code phát hiện và xử lý dữ liệu trùng lặp
        def find_duplicate_students():
            conn = sqlite3.connect('lang_huu_nghi.db')
            cursor = conn.cursor()
            
            # Tìm học sinh có tên trùng lặp
            cursor.execute("""
                SELECT full_name, COUNT(*) as count 
                FROM students 
                GROUP BY full_name 
                HAVING count > 1
                ORDER BY count DESC
            """)
            
            duplicates = cursor.fetchall()
            
            if not duplicates:
                return None, 0
            
            # Tạo danh sách chi tiết
            duplicate_details = []
            for name, count in duplicates:
                cursor.execute("""
                    SELECT id, full_name, birth_date, admission_date, class_id 
                    FROM students 
                    WHERE full_name = ?
                    ORDER BY id
                """, (name,))
                students = cursor.fetchall()
                for student in students:
                    duplicate_details.append({
                        'id': student[0],
                        'full_name': student[1],
                        'birth_date': student[2],
                        'admission_date': student[3],
                        'class_id': student[4]
                    })
            
            conn.close()
            return pd.DataFrame(duplicate_details), len(duplicates)
        
        def clean_duplicate_students():
            conn = sqlite3.connect('lang_huu_nghi.db')
            cursor = conn.cursor()
            
            # Lấy tất cả học sinh có tên trùng nhau
            cursor.execute("""
                SELECT full_name, COUNT(*) as count 
                FROM students 
                GROUP BY full_name 
                HAVING count > 1
                ORDER BY count DESC
            """)
            
            duplicates = cursor.fetchall()
            
            if not duplicates:
                conn.close()
                return 0
            
            # Với mỗi tên trùng lặp, giữ lại bản ghi mới nhất (dựa trên ID cao nhất)
            total_deleted = 0
            for name, count in duplicates:
                # Lấy tất cả ID của học sinh có tên này
                cursor.execute('SELECT id FROM students WHERE full_name = ? ORDER BY id', (name,))
                student_ids = [row[0] for row in cursor.fetchall()]
                
                # Lấy ID cao nhất (mới nhất)
                newest_id = max(student_ids)
                
                # Xóa tất cả bản ghi cũ hơn
                ids_to_delete = [id for id in student_ids if id != newest_id]
                for id_to_delete in ids_to_delete:
                    cursor.execute('DELETE FROM students WHERE id = ?', (id_to_delete,))
                    total_deleted += 1
            
            conn.commit()
            conn.close()
            return total_deleted
        
        st.write("Công cụ này giúp phát hiện và xử lý các bản ghi học sinh trùng lặp trong hệ thống.")
        st.write("Quy tắc: Đối với mỗi tên học sinh trùng lặp, hệ thống sẽ giữ lại bản ghi mới nhất và xóa các bản ghi cũ hơn.")
        
        if st.button("🔍 Tìm kiếm bản ghi trùng lặp"):
            with st.spinner("Đang tìm kiếm..."):
                duplicates_df, duplicate_count = find_duplicate_students()
                
                if duplicate_count == 0:
                    st.success("✅ Không tìm thấy bản ghi trùng lặp. Dữ liệu đã sạch!")
                else:
                    st.warning(f"⚠️ Tìm thấy {duplicate_count} tên học sinh bị trùng lặp!")
                    st.dataframe(duplicates_df)
                    
                    if st.button("🧹 Dọn dẹp tất cả bản ghi trùng lặp"):
                        if st.session_state.get('confirm_cleanup') != True:
                            st.session_state.confirm_cleanup = True
                            st.warning("⚠️ Cảnh báo: Thao tác này sẽ xóa các bản ghi trùng lặp cũ hơn. Bạn có chắc chắn muốn tiếp tục?")
                            st.button("✅ Xác nhận xóa", key="confirm_cleanup_button")
                        else:
                            with st.spinner("Đang dọn dẹp..."):
                                deleted_count = clean_duplicate_students()
                                st.success(f"✅ Đã xóa thành công {deleted_count} bản ghi trùng lặp!")
                                st.session_state.confirm_cleanup = False
                                st.rerun()

def render():
    # Apply theme from session state
    apply_theme()

    # Set current page for role checking
    st.session_state.current_page = "06_Quan_ly_He_thong"

    check_auth()
    check_role(['admin'])  # Only admin can access this page

    # Check if user has permission to manage data
    if not can_manage_data():
        st.error("Bạn không có quyền truy cập trang này")
        st.stop()

    st.title(get_text("pages.system.title", "⚙️ Quản Lý Hệ Thống"))

    # Create tabs for different management sections
    tabs = st.tabs([
        f"📥 {get_text('pages.system.import_data', 'Nhập Dữ Liệu từ Excel')}", 
        f"💾 {get_text('pages.system.backup_restore', 'Sao lưu & Khôi phục')}"
    ])

    with tabs[0]:
        import_data_section()

    with tabs[1]:
        database_management_section()
        
    st.info("""
    ### 🔄 Phân chia chức năng
    - **Nhập dữ liệu từ Excel** (Trang hiện tại): Nhập dữ liệu học sinh từ file Excel với xử lý đặc biệt (chuyển đổi định dạng ngày tháng, làm sạch dữ liệu...)
    - **Quản lý Dữ liệu** (Trang quản lý Database): Xem, chỉnh sửa và xuất/nhập dữ liệu trực tiếp với từng bảng
    - **Sao lưu & Khôi phục** (Trang hiện tại): Tạo và khôi phục các bản sao lưu của toàn bộ cơ sở dữ liệu
    """)

if __name__ == "__main__":
    render()