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
            
            # Enhanced smart house detection for multiple houses in one file
            house_info = None
            all_houses = []
            house_mapping = {}  # Will store row -> house mapping
            import re
            
            # Define common house patterns for your organization
            house_patterns = [
                r'NHÀ\s+([T][2-9])',  # T2, T3, T4, T5, T6, etc.
                r'NHÀ\s+([A-Z]\d+)',  # A1, B2, etc.
                r'NHÀ\s+([A-Z]+\d*)',  # General pattern
                r'([T][2-9])\s*$',  # Just T2, T3 at end of text
                r'([T][2-9])\s',      # T2, T3 with space after
            ]
            
            # Step 1: Check column names for house info
            house_columns = {}  # column_name -> house_name
            for col_name in df.columns:
                if isinstance(col_name, str) and 'NHÀ' in col_name.upper():
                    for pattern in house_patterns:
                        house_match = re.search(pattern, col_name, re.IGNORECASE)
                        if house_match:
                            found_house = house_match.group(1).upper()
                            house_columns[col_name] = found_house
                            if found_house not in all_houses:
                                all_houses.append(found_house)
                            if not house_info:  # Use first match as primary
                                house_info = found_house
            
            # Step 2: Scan the entire file for house information patterns
            for i, row in df.iterrows():
                current_house = None
                
                # Check if any cell in this row contains house info
                for j, cell_value in enumerate(row):
                    cell_str = str(cell_value).upper().strip()
                    if 'NHÀ' in cell_str:
                        for pattern in house_patterns:
                            house_match = re.search(pattern, cell_str, re.IGNORECASE)
                            if house_match:
                                found_house = house_match.group(1).upper()
                                current_house = found_house
                                if found_house not in all_houses:
                                    all_houses.append(found_house)
                                if not house_info:
                                    house_info = found_house
                                break
                        if current_house:
                            break
                
                # Store house mapping for this row
                if current_house:
                    house_mapping[i] = current_house
                    
            # Step 3: Smart house propagation - assign houses to nearby rows
            if house_mapping:
                # Sort house mappings by row index
                sorted_house_rows = sorted(house_mapping.items())
                
                # Assign houses to students based on proximity
                for i, row in df.iterrows():
                    if i not in house_mapping:
                        # Find the nearest house assignment
                        nearest_house = None
                        min_distance = float('inf')
                        
                        for house_row, house_name in sorted_house_rows:
                            distance = abs(i - house_row)
                            if distance < min_distance:
                                min_distance = distance
                                nearest_house = house_name
                        
                        if nearest_house and min_distance <= 50:  # Within 50 rows
                            house_mapping[i] = nearest_house

            # Show preview
            st.write("### 📊 Xem trước dữ liệu gốc")
            st.dataframe(df.head(), use_container_width=True)
            st.write(f"📌 Tổng số dòng trong file: {len(df)}")
            
            # Show intelligent house detection results
            if all_houses:
                if len(all_houses) == 1:
                    st.success(f"🏘️ Phát hiện thông tin nhà: **{all_houses[0]}**")
                    st.info("Thông tin nhà này sẽ được tự động gán cho tất cả học sinh trong file")
                else:
                    st.success(f"🏘️ Phát hiện nhiều nhà: **{', '.join(all_houses)}**")
                    st.info(f"🤖 **Phân bổ thông minh:** Hệ thống sẽ tự động gán từng học sinh vào đúng nhà của họ")
                    
                    # Show house distribution
                    house_counts = {}
                    for house in house_mapping.values():
                        house_counts[house] = house_counts.get(house, 0) + 1
                    
                    if house_counts:
                        st.write("📊 **Phân bổ dự kiến:**")
                        for house, count in house_counts.items():
                            st.write(f"  - Nhà {house}: {count} học sinh")
            else:
                st.warning("⚠️ Không phát hiện thông tin nhà trong file")
                st.info("💡 **Gợi ý:** Hệ thống hỗ trợ tự động phát hiện các nhà như: T2, T3, T4, T5, T6, A1, B2...")

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

            }
            
            # Smart house assignment options
            st.write("### 🏘️ Cấu hình nhà")
            
            if len(all_houses) > 1:
                # Multiple houses detected - offer smart assignment
                assignment_mode = st.radio(
                    "Chọn cách gán nhà:",
                    ["🤖 Tự động gán theo phát hiện (khuyến nghị)", "🏠 Gán một nhà cho tất cả"],
                    key='assignment_mode'
                )
                
                if assignment_mode.startswith("🤖"):
                    # Smart assignment mode
                    st.success("✨ **Chế độ thông minh đã bật:** Mỗi học sinh sẽ được gán vào đúng nhà của họ")
                    use_smart_assignment = True
                    manual_house = None
                    
                    with st.expander("🔍 Chi tiết phân bổ thông minh"):
                        st.write("**Cách hoạt động:**")
                        st.write("1. Hệ thống quét toàn bộ file tìm các dòng chứa thông tin nhà (VD: 'NHÀ T2', 'NHÀ T3')")
                        st.write("2. Gán các học sinh ở gần dòng đó vào nhà tương ứng")
                        st.write("3. Nếu không tìm thấy nhà cho học sinh nào, sẽ gán vào nhà đầu tiên được phát hiện")
                        
                        st.write(f"**Các nhà được phát hiện:** {', '.join(all_houses)}")
                        if house_mapping:
                            sample_assignments = list(house_mapping.items())[:5]
                            st.write("**Mẫu phân bổ (5 dòng đầu):**")
                            for row_idx, house in sample_assignments:
                                st.write(f"  - Dòng {row_idx + 1}: Nhà {house}")
                else:
                    # Manual single house assignment
                    use_smart_assignment = False
                    house_options = [""] + all_houses + ["Khác..."]
                    selected_house = st.selectbox(
                        "Chọn nhà cho tất cả học sinh:", 
                        options=house_options,
                        key='single_house_selection'
                    )
                    
                    if selected_house == "Khác...":
                        manual_house = st.text_input(
                            "Nhập tên nhà tùy chỉnh", 
                            placeholder="Ví dụ: T7, D2, E1...",
                            key='custom_house_input'
                        )
                    else:
                        manual_house = selected_house
                        
                    if manual_house:
                        st.info(f"✅ Tất cả học sinh sẽ được gán nhà: **{manual_house}**")
            else:
                # Single or no house detected - use traditional method
                use_smart_assignment = False
                house_options = ["T2", "T3", "T4", "T5", "T6", "A1", "B1", "C1", "Khác..."]
                
                if house_info:
                    if house_info in house_options:
                        default_index = house_options.index(house_info)
                    else:
                        house_options.insert(-1, house_info)
                        default_index = len(house_options) - 2
                    
                    selected_house = st.selectbox(
                        "Chọn nhà (tự động phát hiện)", 
                        options=house_options,
                        index=default_index,
                        key='house_selection'
                    )
                else:
                    selected_house = st.selectbox(
                        "Chọn nhà", 
                        options=house_options,
                        index=0,
                        key='house_selection'
                    )
                
                if selected_house == "Khác...":
                    manual_house = st.text_input(
                        "Nhập tên nhà tùy chỉnh", 
                        placeholder="Ví dụ: T7, D2, E1...",
                        key='custom_house_input'
                    )
                else:
                    manual_house = selected_house
                
                if manual_house and manual_house != "Khác...":
                    st.info(f"✅ Tất cả học sinh sẽ được gán nhà: **{manual_house}**")
            
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

                        # Smart house assignment - determine house for this specific student
                        assigned_house = ""
                        if 'use_smart_assignment' in locals() and use_smart_assignment and house_mapping:
                            # Use smart assignment - get house for this specific row
                            assigned_house = house_mapping.get(idx, all_houses[0] if all_houses else "")
                        else:
                            # Use manual assignment for all students
                            assigned_house = manual_house if manual_house else ""
                        
                        # Build student data with safe access to mapped columns first (to use later)
                        student_data = {
                            "full_name": full_name,
                            "birth_date": None,
                            "admission_date": today,

                            "address": "",
                            "nha_chu_t_info": assigned_house
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
                                    if field == 'phone' and not value.isdigit():
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
                        
                        # Show smart assignment summary
                        if 'use_smart_assignment' in locals() and use_smart_assignment and house_mapping:
                            house_summary = {}
                            for student_data in name_data.values():
                                house = student_data.get('nha_chu_t_info', 'Không xác định')
                                house_summary[house] = house_summary.get(house, 0) + 1
                            
                            st.success(f"✅ Đã nhập thành công {success_count} học sinh với phân bổ thông minh!")
                            st.info("🏘️ **Phân bổ nhà thực tế:**")
                            for house, count in house_summary.items():
                                st.write(f"  - Nhà {house}: {count} học sinh")
                        else:
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

def check_google_auth_status():
    """Check if Google Drive authentication is properly configured - safe for cloud deployment"""
    try:
        # Check for Service Account first (recommended approach)
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        
        if service_account_json:
            try:
                import json
                json.loads(service_account_json)
                return {'authenticated': True, 'status': 'Service Account Ready', 'method': 'service_account'}
            except:
                return {'authenticated': False, 'status': 'Service Account JSON Invalid', 'method': 'service_account'}
        
        # Check for OAuth credentials (legacy method)
        google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if google_client_id and google_client_secret:
            # Check if OAuth token exists
            try:
                from gdrive_cloud_auth import CloudGoogleAuth
                cloud_auth = CloudGoogleAuth()
                
                if cloud_auth.has_credentials() and cloud_auth.is_authenticated():
                    return {'authenticated': True, 'status': 'OAuth Authenticated', 'method': 'oauth'}
                else:
                    return {'authenticated': False, 'status': 'OAuth Required', 'method': 'oauth'}
            except:
                return {'authenticated': False, 'status': 'OAuth Required', 'method': 'oauth'}
        
        # Check for local file-based auth (development)
        if not os.path.exists('credentials.json'):
            return {'authenticated': False, 'error': 'Google Drive backup not configured', 'method': 'file'}
        
        if not os.path.exists('token.json'):
            return {'authenticated': False, 'error': 'Not authenticated yet', 'method': 'file'}
        
        # Try to load and verify token
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive.file'])
        
        if creds and creds.valid:
            return {'authenticated': True, 'status': 'Active', 'method': 'file'}
        elif creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                return {'authenticated': True, 'status': 'Refreshed', 'method': 'file'}
            except Exception as e:
                return {'authenticated': False, 'error': f'Token refresh failed: {e}', 'method': 'file'}
        else:
            return {'authenticated': False, 'error': 'Invalid token', 'method': 'file'}
            
    except ImportError:
        return {'authenticated': False, 'error': 'Google libraries not available', 'method': 'none'}
    except Exception as e:
        return {'authenticated': False, 'error': f'Authentication check failed: {e}', 'method': 'unknown'}

def database_management_section():
    """Google Drive backup management section - cloud deployment safe"""
    st.subheader("💾 Sao lưu Google Drive (Supabase)")
    
    # Check authentication status safely
    auth_status = check_google_auth_status()
    
    if not auth_status['authenticated']:
        if auth_status.get('method') == 'service_account':
            st.warning("🔧 Service Account JSON không hợp lệ")
            st.error("GOOGLE_SERVICE_ACCOUNT_JSON trong Streamlit Secrets có vấn đề")
            
            st.info("""
            **Kiểm tra GOOGLE_SERVICE_ACCOUNT_JSON:**
            1. Đảm bảo toàn bộ nội dung JSON được copy chính xác
            2. JSON phải bắt đầu bằng { và kết thúc bằng }
            3. Không có dấu ngoặc kép thừa hoặc ký tự lạ
            4. Download lại JSON file từ Google Cloud Console nếu cần
            
            **Format đúng:**
            ```
            {
              "type": "service_account",
              "project_id": "your-project",
              "private_key_id": "...",
              "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
              "client_email": "...@....iam.gserviceaccount.com",
              ...
            }
            ```
            """)
            
            # Add JSON validator
            if st.button("🔍 Test JSON Format"):
                service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
                if service_account_json:
                    try:
                        import json
                        parsed = json.loads(service_account_json)
                        required_fields = ['type', 'project_id', 'private_key', 'client_email']
                        missing = [f for f in required_fields if f not in parsed]
                        
                        if missing:
                            st.error(f"❌ Thiếu các field: {', '.join(missing)}")
                        else:
                            st.success("✅ JSON format hợp lệ!")
                            st.info(f"Project: {parsed.get('project_id')}")
                            st.info(f"Email: {parsed.get('client_email')}")
                    except json.JSONDecodeError as e:
                        st.error(f"❌ JSON không hợp lệ: {str(e)}")
                        st.error("Vui lòng kiểm tra và sửa format JSON")
                else:
                    st.error("❌ Không tìm thấy GOOGLE_SERVICE_ACCOUNT_JSON")
            
        elif auth_status.get('method') == 'oauth':
            st.warning("🔧 Cần xác thực Google Drive")
            st.info("""
            **Google Drive OAuth Credentials đã có, cần xác thực:**
            1. ✅ Client ID và Secret đã có trong environment variables
            2. ⏳ Cần thực hiện xác thực OAuth một lần
            3. ✅ Sau đó sao lưu sẽ hoạt động tự động
            
            ⚠️ **Lưu ý:** OAuth có thể gặp lỗi redirect URI. Khuyến nghị dùng Service Account.
            """)
            
            # Show authentication interface for cloud deployment
            show_cloud_auth_interface()
            
        else:
            st.info("ℹ️ Sao lưu Google Drive chưa được cấu hình")
            
            # Show both options
            method = st.radio(
                "Chọn phương thức xác thực:",
                ["Service Account (Khuyến nghị)", "OAuth 2.0 (Phức tạp)"],
                help="Service Account đơn giản hơn và ổn định hơn cho production"
            )
            
            if "Service Account" in method:
                st.info("""
                **🎯 KHUYẾN NGHỊ: Sử dụng Service Account**
                
                **Ưu điểm:**
                ✅ Không cần OAuth flow phức tạp
                ✅ Không có vấn đề redirect URI  
                ✅ Hoạt động ngay lập tức
                ✅ Phù hợp với Streamlit Cloud
                
                **Các bước setup:**
                1. Tạo Service Account trong Google Cloud Console
                2. Download JSON key file
                3. Thêm toàn bộ nội dung JSON vào GOOGLE_SERVICE_ACCOUNT_JSON trong Streamlit Secrets
                4. Chia sẻ Google Drive folder với email service account
                
                📋 **Xem hướng dẫn chi tiết:** SERVICE_ACCOUNT_SETUP.md
                📋 **Khắc phục JSON Invalid:** STREAMLIT_SECRETS_GUIDE.md
                """)
            else:
                st.info("""
                **⚠️ OAuth 2.0 (Có thể gặp vấn đề)**
                
                **Vấn đề thường gặp:**
                ❌ Redirect URI mismatch
                ❌ App verification required
                ❌ Test users required
                ❌ Token expiration
                
                **Nếu vẫn muốn dùng OAuth:**
                1. Tạo OAuth 2.0 credentials trong Google Cloud Console
                2. Set redirect URI chính xác: https://your-app.streamlit.app
                3. Thêm GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET vào Streamlit Secrets
                4. Thêm email vào Test users
                5. Hoàn thành OAuth flow
                
                📋 **Khắc phục sự cố:** GOOGLE_OAUTH_REDIRECT_FIX.md
                """)
                
    else:
        st.success(f"✅ Google Drive đã kết nối: {auth_status['status']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Sao lưu ngay", help="Tạo bản sao lưu database ngay lập tức"):
                with st.spinner("Đang tạo bản sao lưu..."):
                    try:
                        # Use appropriate backup method based on authentication
                        if auth_status.get('method') == 'service_account':
                            from gdrive_service_account import GoogleDriveServiceAccount
                            backup_system = GoogleDriveServiceAccount()
                        else:
                            backup_system = GoogleDriveBackup()
                        
                        if backup_system.create_backup():
                            st.success("✅ Sao lưu thành công lên Google Drive!")
                            st.rerun()
                        else:
                            st.error("❌ Sao lưu thất bại")
                    except Exception as e:
                        st.error(f"❌ Lỗi sao lưu: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
        
        with col2:
            if st.button("📋 Xem lịch sử sao lưu"):
                with st.spinner("Đang tải danh sách sao lưu..."):
                    try:
                        # Use appropriate backup method based on authentication
                        if auth_status.get('method') == 'service_account':
                            from gdrive_service_account import GoogleDriveServiceAccount
                            backup_system = GoogleDriveServiceAccount()
                        else:
                            backup_system = GoogleDriveBackup()
                            
                        backups = backup_system.list_backups()
                        
                        if backups:
                            st.write("**📁 Danh sách backup trên Google Drive:**")
                            for backup in backups:
                                created_time = backup.get('createdTime', 'Unknown')
                                if 'T' in created_time:
                                    # Parse ISO format
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                                    created_time = dt.strftime("%d/%m/%Y %H:%M:%S")
                                
                                size_mb = int(backup.get('size', 0)) / (1024 * 1024)
                                st.write(f"• **{backup['name']}** - {created_time} ({size_mb:.1f} MB)")
                        else:
                            st.info("Chưa có backup nào trên Google Drive")
                    except Exception as e:
                        st.error(f"❌ Lỗi tải danh sách: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
        return
    
    # Show backup system status 
    st.success(f"✅ Google Drive kết nối thành công ({auth_status['status']})")
    
    # Show backup management interface
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Sao lưu ngay", help="Tạo bản sao lưu database ngay lập tức"):
            try:
                if BACKUP_AVAILABLE:
                    backup = GoogleDriveBackup()
                    with st.spinner("Đang tạo bản sao lưu..."):
                        result = backup.create_backup()
                        if result:
                            st.success("✅ Sao lưu thành công lên Google Drive!")
                        else:
                            st.error("❌ Sao lưu thất bại")
                else:
                    st.error("❌ Hệ thống sao lưu không khả dụng")
            except Exception as e:
                st.error(f"❌ Lỗi sao lưu: {str(e)}")
    
    with col2:
        if st.button("📋 Xem lịch sử sao lưu", help="Xem các bản sao lưu trước đó"):
            try:
                if BACKUP_AVAILABLE:
                    backup = GoogleDriveBackup()
                    backups = backup.list_backups()
                    if backups:
                        st.info(f"📦 Có {len(backups)} bản sao lưu trên Google Drive")
                        for backup_file in backups[:5]:  # Show latest 5
                            st.write(f"- {backup_file.get('name', 'Unknown')} ({backup_file.get('createdTime', 'Unknown time')})")
                    else:
                        st.info("📭 Chưa có bản sao lưu nào")
                else:
                    st.error("❌ Hệ thống sao lưu không khả dụng")
            except Exception as e:
                st.error(f"❌ Không thể tải lịch sử: {str(e)}")

def show_cloud_auth_interface():
    """Show Google Drive authentication interface for cloud deployment"""
    from gdrive_cloud_auth import CloudGoogleAuth
    
    cloud_auth = CloudGoogleAuth()
    
    st.markdown("### 🔐 Xác thực Google Drive")
    
    # Check if already authenticated
    if cloud_auth.is_authenticated():
        st.success("✅ Đã xác thực Google Drive thành công!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Làm mới xác thực"):
                cloud_auth.clear_credentials()
                st.rerun()
        
        with col2:
            if st.button("❌ Huỷ xác thực"):
                cloud_auth.clear_credentials()
                st.success("Đã huỷ xác thực Google Drive")
                st.rerun()
        
        return True
    
    # Show authentication steps
    st.info("""
    **Các bước xác thực:**
    1. Nhấn "Lấy URL xác thực" bên dưới
    2. Sao chép URL và mở trong tab mới
    3. Đăng nhập Google và cho phép quyền truy cập
    4. Sao chép mã xác thực từ URL hoặc trang phản hồi
    5. Dán mã xác thực vào ô bên dưới
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔗 Lấy URL xác thực"):
            auth_url = cloud_auth.get_authorization_url()
            if auth_url:
                st.success("✅ URL xác thực đã được tạo!")
                st.code(auth_url, language="text")
                st.info("Sao chép URL trên và mở trong tab mới để xác thực")
            else:
                st.error("❌ Không thể tạo URL xác thực. Kiểm tra GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET")
    
    with col2:
        auth_code = st.text_input(
            "Mã xác thực",
            placeholder="Dán mã xác thực từ Google tại đây",
            help="Sau khi xác thực với Google, sao chép mã từ URL hoặc trang kết quả"
        )
        
        if st.button("✅ Xác thực") and auth_code:
            with st.spinner("Đang xác thực..."):
                credentials = cloud_auth.exchange_code_for_token(auth_code.strip())
                
                if credentials:
                    success = cloud_auth.store_credentials(credentials)
                    if success:
                        st.success("🎉 Xác thực Google Drive thành công!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Lỗi lưu thông tin xác thực")
                else:
                    st.error("❌ Mã xác thực không hợp lệ hoặc đã hết hạn")
    
    return False
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 Sao lưu thủ công")
        if st.button("📤 Sao lưu ngay", help="Thực hiện sao lưu dữ liệu ngay lập tức"):
            with st.spinner("Đang sao lưu dữ liệu lên Google Drive..."):
                if BACKUP_AVAILABLE:
                    try:
                        from gdrive_backup import GoogleDriveBackup
                        backup = GoogleDriveBackup()
                        
                        # Perform backup
                        if backup.perform_backup():
                            st.success("✅ Sao lưu thành công!")
                            st.info("Dữ liệu đã được lưu vào thư mục 'Lang Huu Nghi Database Backups' trên Google Drive của bạn.")
                            
                            # Update last backup timestamp
                            try:
                                import json
                                with open('last_backup.json', 'w') as f:
                                    json.dump({
                                        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                                        'status': 'success'
                                    }, f)
                            except:
                                pass
                                
                        else:
                            st.error("❌ Sao lưu thất bại.")
                            st.info("🔧 Kiểm tra kết nối Google Drive và thử lại.")
                    except Exception as e:
                        st.error(f"❌ Lỗi sao lưu: {str(e)}")
                        st.info("🔧 Hãy đảm bảo hệ thống đã được khởi tạo trước khi sao lưu.")
                else:
                    st.error("❌ Hệ thống backup không khả dụng.")
    
    with col2:
        st.markdown("### 📅 Sao lưu tự động")
        st.info("**Lịch trình**: Mỗi Chủ nhật lúc 2:00 AM")
        st.info("**Số bản sao lưu**: Tối đa 10 bản (tự động xóa bản cũ)")
        
        # Check authentication status more accurately
        auth_status = check_google_auth_status()
        
        if auth_status['authenticated']:
            st.success("✅ Google Drive đã được xác thực")
            if st.button("🔄 Kiểm tra kết nối"):
                with st.spinner("Đang kiểm tra..."):
                    if BACKUP_AVAILABLE:
                        try:
                            from gdrive_backup import GoogleDriveBackup
                            backup = GoogleDriveBackup()
                            if backup.authenticate() and backup.create_backup_folder():
                                st.success("✅ Kết nối Google Drive hoạt động tốt!")
                            else:
                                st.error("❌ Có vấn đề với kết nối Google Drive")
                        except Exception as e:
                            st.error(f"❌ Lỗi: {e}")
        else:
            error_msg = auth_status.get('error', 'Unknown error')
            st.warning(f"⚠️ Google Drive not authenticated: {error_msg}")
            
            # Simple authentication form (no button to prevent refresh)
            st.error("Google Verification Required")
            st.markdown("**Fix:** Add your email as test user in [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent)")
            st.markdown("Test users → + ADD USERS → langtrehuunghivietnam@gmail.com → Save")
            
            st.markdown("---")
            
            # Get credentials
            try:
                import json
                with open('credentials.json', 'r') as f:
                    creds = json.load(f)
                client_id = creds['web']['client_id']
                client_secret = creds['web']['client_secret']
            except:
                # Use environment variables or placeholder values
                import os
                client_id = os.getenv('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
                client_secret = os.getenv('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET')
            
            st.markdown("**OAuth Playground:** https://developers.google.com/oauthplayground/")
            st.code(f"Client ID: {client_id}")
            st.code(f"Client Secret: {client_secret}")
            
            # Simple token form with unique keys
            st.markdown("**Paste tokens here:**")
            
            access_token = st.text_area("Access Token", key="oauth_access_token", height=80, placeholder="ya29.a0...")
            refresh_token = st.text_area("Refresh Token", key="oauth_refresh_token", height=80, placeholder="1//...")
            
            if st.button("Create token.json", key="create_token_btn"):
                if access_token.strip() and refresh_token.strip():
                    try:
                        token_data = {
                            "token": access_token.strip(),
                            "refresh_token": refresh_token.strip(), 
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "scopes": ["https://www.googleapis.com/auth/drive.file"]
                        }
                        
                        import json
                        with open('token.json', 'w') as f:
                            json.dump(token_data, f, indent=2)
                        
                        st.success("Token created! Google Drive backup ready.")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter both tokens")
    
    # Show backup history if available
    st.markdown("---")
    st.markdown("### 📋 Lịch sử sao lưu")
    
    if BACKUP_AVAILABLE:
        try:
            # Read last backup metadata
            if os.path.exists('last_backup.json'):
                import json
                with open('last_backup.json', 'r') as f:
                    backup_info = json.loads(f.read())
                
                st.success(f"**Lần sao lưu cuối**: {backup_info.get('timestamp', 'Không rõ')}")
                st.info(f"**Thư mục Google Drive**: Lang Huu Nghi Database Backups")
            else:
                st.warning("Chưa có lịch sử sao lưu")
        except Exception as e:
            st.error(f"Lỗi khi đọc thông tin sao lưu: {e}")
    
    # Backup settings
    st.markdown("---")
    st.markdown("### ⚙️ Cài đặt")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Thư mục đích**: Lang Huu Nghi Database Backups")
        st.info("**Định dạng file**: SQL dump và metadata JSON")
    
    with col2:
        st.info("**Bảo mật**: OAuth 2.0 authentication")
        st.info("**Dữ liệu**: PostgreSQL database (Supabase)")


def safe_spreadsheet_management_section():
    """Safe spreadsheet-style database management section"""
    st.subheader("📊 Quản lý dữ liệu người dùng (Dạng Spreadsheet)")
    
    st.info("""
    ℹ️ **Giao diện quản lý an toàn**: Xem và chỉnh sửa dữ liệu người dùng một cách trực quan và an toàn.
    Giao diện này được thiết kế đặc biệt cho quản trị viên với các biện pháp bảo vệ dữ liệu.
    """)
    
    db = Database()
    
    # Create sub-tabs for different user data types
    db_tabs = st.tabs([
        "🎓 Quản lý học sinh", 
        "🎖️ Quản lý cựu chiến binh",
        "🏥 Hồ sơ y tế"
    ])
    
    with db_tabs[0]:
        manage_students_spreadsheet(db)
        
    with db_tabs[1]:
        manage_veterans_spreadsheet(db)
        
    with db_tabs[2]:
        manage_medical_records_spreadsheet(db)

def view_database_data(db):
    """View database tables and data"""
    st.subheader("📊 Xem dữ liệu bảng")
    
    # List of available tables
    tables = [
        ("students", "Học sinh"),
        ("veterans", "Cựu chiến binh"), 
        ("users", "Người dùng"),
        ("classes", "Lớp học"),
        ("medical_records", "Hồ sơ y tế"),
        ("psychological_evaluations", "Đánh giá tâm lý"),
        ("documents", "Tài liệu")
    ]
    
    selected_table = st.selectbox(
        "Chọn bảng để xem:",
        options=[table[0] for table in tables],
        format_func=lambda x: next(table[1] for table in tables if table[0] == x)
    )
    
    if selected_table:
        try:
            # Get table data
            query = f"SELECT * FROM {selected_table} LIMIT 100"
            data = db.conn.execute(query).fetchall()
            
            if data:
                # Get column names
                cursor = db.conn.execute(f"PRAGMA table_info({selected_table})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Create dataframe
                import pandas as pd
                df = pd.DataFrame(data, columns=columns)
                
                st.write(f"**Tổng số bản ghi**: {len(data)} (hiển thị tối đa 100)")
                st.dataframe(df, use_container_width=True)
                
                # Export option
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Tải xuống {selected_table}.csv",
                    data=csv,
                    file_name=f"{selected_table}.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"Bảng {selected_table} không có dữ liệu")
                
        except Exception as e:
            st.error(f"Lỗi khi truy xuất dữ liệu: {str(e)}")

def edit_database_data(db):
    """Edit database records"""
    st.subheader("✏️ Chỉnh sửa dữ liệu")
    
    st.info("Chọn bảng và ID để chỉnh sửa bản ghi cụ thể")
    
    # Simple edit interface
    tables = ["students", "veterans", "users", "classes"]
    selected_table = st.selectbox("Chọn bảng:", tables)
    
    if selected_table:
        record_id = st.number_input("Nhập ID bản ghi:", min_value=1, step=1)
        
        if st.button("🔍 Tải dữ liệu"):
            try:
                query = f"SELECT * FROM {selected_table} WHERE id = ?"
                record = db.conn.execute(query, (record_id,)).fetchone()
                
                if record:
                    # Get column info
                    cursor = db.conn.execute(f"PRAGMA table_info({selected_table})")
                    columns = [(row[1], row[2]) for row in cursor.fetchall()]
                    
                    st.success(f"Tìm thấy bản ghi ID {record_id}")
                    
                    # Create edit form
                    with st.form("edit_record"):
                        st.write("**Chỉnh sửa các trường:**")
                        
                        new_values = {}
                        for i, (col_name, col_type) in enumerate(columns):
                            if col_name != 'id':  # Don't edit ID
                                current_value = record[i] if i < len(record) else ""
                                new_values[col_name] = st.text_input(
                                    f"{col_name} ({col_type}):", 
                                    value=str(current_value) if current_value is not None else ""
                                )
                        
                        if st.form_submit_button("💾 Cập nhật"):
                            try:
                                # Build update query
                                set_clause = ", ".join([f"{col} = ?" for col in new_values.keys()])
                                update_query = f"UPDATE {selected_table} SET {set_clause} WHERE id = ?"
                                
                                values = list(new_values.values()) + [record_id]
                                db.conn.execute(update_query, values)
                                db.conn.commit()
                                
                                st.success(f"✅ Đã cập nhật bản ghi ID {record_id}")
                                
                            except Exception as e:
                                st.error(f"Lỗi khi cập nhật: {str(e)}")
                else:
                    st.error(f"Không tìm thấy bản ghi với ID {record_id}")
                    
            except Exception as e:
                st.error(f"Lỗi khi tải dữ liệu: {str(e)}")

def delete_database_data(db):
    """Delete database records"""
    st.subheader("🗑️ Xóa dữ liệu")
    
    st.error("""
    ⚠️ **NGUY HIỂM**: Xóa dữ liệu là thao tác không thể hoàn tác!
    Hãy chắc chắn bạn đã sao lưu dữ liệu trước khi thực hiện.
    """)
    
    tables = ["students", "veterans", "users", "classes", "medical_records", "psychological_evaluations"]
    selected_table = st.selectbox("Chọn bảng:", tables)
    
    if selected_table:
        record_id = st.number_input("Nhập ID bản ghi cần xóa:", min_value=1, step=1)
        
        # Double confirmation
        confirm1 = st.checkbox(f"Tôi hiểu rằng việc xóa bản ghi ID {record_id} từ bảng {selected_table} không thể hoàn tác")
        confirm2 = st.checkbox("Tôi đã sao lưu dữ liệu quan trọng")
        
        if confirm1 and confirm2:
            if st.button("🗑️ XÓA VĨNH VIỄN", type="primary"):
                try:
                    # Check if record exists first
                    check_query = f"SELECT * FROM {selected_table} WHERE id = ?"
                    record = db.conn.execute(check_query, (record_id,)).fetchone()
                    
                    if record:
                        # Delete the record
                        delete_query = f"DELETE FROM {selected_table} WHERE id = ?"
                        db.conn.execute(delete_query, (record_id,))
                        db.conn.commit()
                        
                        st.success(f"✅ Đã xóa bản ghi ID {record_id} từ bảng {selected_table}")
                    else:
                        st.error(f"Không tìm thấy bản ghi với ID {record_id}")
                        
                except Exception as e:
                    st.error(f"Lỗi khi xóa: {str(e)}")



def manage_students_spreadsheet(db):
    """Manage students in spreadsheet format with ID display"""
    st.subheader("🎓 Quản lý học sinh")
    
    try:
        # Get students data
        query = """
            SELECT s.id, s.full_name, s.birth_date, s.gender, s.address, s.email, 
                   s.admission_date,
                   c.name as class_name
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            ORDER BY s.id
        """
        results = db.conn.execute(query).fetchall()
        
        if results:
            # Create DataFrame with ID prominently displayed
            df = pd.DataFrame(results, columns=[
                'ID', 'Họ và tên', 'Ngày sinh', 'Giới tính', 'Địa chỉ', 'Email', 
                'Ngày nhập học', 'Lớp'
            ])
            
            st.write(f"**Tổng số học sinh**: {len(results)}")
            
            # Display with edit capabilities
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "ID": st.column_config.NumberColumn("ID Bệnh nhân", disabled=True, width="small"),
                    "Họ và tên": st.column_config.TextColumn("Họ và tên", required=True),
                    "Giới tính": st.column_config.SelectboxColumn(
                        "Giới tính",
                        options=["Nam", "Nữ"],
                        required=False
                    ),

                },
                key="students_editor"
            )
            
            # Save changes button
            if st.button("💾 Lưu thay đổi", key="save_students"):
                save_students_changes(db, edited_df)
                
        else:
            st.info("Không có dữ liệu học sinh")
            
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu học sinh: {str(e)}")

def manage_veterans_spreadsheet(db):
    """Manage veterans in spreadsheet format with ID display"""
    st.subheader("🎖️ Quản lý cựu chiến binh")
    
    try:
        # Use direct query with error handling
        query = """
            SELECT id, full_name, birth_date, gender, address, email, 
                   health_condition, admission_date
            FROM veterans
            ORDER BY id
        """
        
        try:
            results = db.conn.execute(query).fetchall()
        except Exception as e:
            st.error(f"Lỗi truy vấn database: {str(e)}")
            # Try simpler query without gender
            query_simple = """
                SELECT id, full_name, birth_date, address, email, 
                       health_condition, admission_date
                FROM veterans
                ORDER BY id
            """
            results = db.conn.execute(query_simple).fetchall()
            # Adjust column names accordingly
            use_gender = False
        else:
            use_gender = True
        
        if results:
            # Create DataFrame with proper columns based on query
            if 'use_gender' in locals() and use_gender:
                column_names = [
                    'ID', 'Họ và tên', 'Ngày sinh', 'Giới tính', 'Địa chỉ', 'Email', 
                    'Sức khỏe', 'Ngày nhập làng'
                ]
            else:
                column_names = [
                    'ID', 'Họ và tên', 'Ngày sinh', 'Địa chỉ', 'Email', 
                    'Sức khỏe', 'Ngày nhập làng'
                ]
            
            df = pd.DataFrame(results, columns=column_names)
            
            st.write(f"**Tổng số cựu chiến binh**: {len(results)}")
            
            # Display with edit capabilities
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "ID": st.column_config.NumberColumn("ID Bệnh nhân", disabled=True, width="small"),
                    "Họ và tên": st.column_config.TextColumn("Họ và tên", required=True),
                    "Giới tính": st.column_config.SelectboxColumn(
                        "Giới tính",
                        options=["Nam", "Nữ"],
                        required=False
                    ),
                    "Tình trạng sức khỏe": st.column_config.SelectboxColumn(
                        "Tình trạng sức khỏe",
                        options=["Tốt", "Bình thường", "Cần chú ý"],
                        required=False
                    )
                },
                key="veterans_editor"
            )
            
            # Save changes button
            if st.button("💾 Lưu thay đổi", key="save_veterans"):
                save_veterans_changes(db, edited_df)
                
        else:
            st.info("Không có dữ liệu cựu chiến binh")
            
            # Option to recreate table and add sample data
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔧 Tái tạo bảng cựu chiến binh", key="recreate_veterans_table"):
                    try:
                        # Recreate veterans table with proper structure
                        db.conn.execute("DROP TABLE IF EXISTS veterans CASCADE")
                        create_query = """
                            CREATE TABLE veterans (
                                id SERIAL PRIMARY KEY,
                                full_name TEXT NOT NULL,
                                birth_date TEXT,
                                gender TEXT,
                                address TEXT,
                                email TEXT,
                                admission_date TEXT,

                                profile_image TEXT,
                                initial_characteristics TEXT
                            )
                        """
                        db.conn.execute(create_query)
                        db.conn.commit()
                        st.success("✅ Đã tái tạo bảng cựu chiến binh!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi tái tạo bảng: {str(e)}")
            
            with col2:
                if st.button("➕ Thêm dữ liệu mẫu", key="add_sample_veteran"):
                    try:
                        # Add sample veterans
                        sample_query = """
                            INSERT INTO veterans (full_name, birth_date, gender, address, email, initial_characteristics, admission_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        db.conn.execute(sample_query, (
                            "Nguyễn Văn Thành", "1965-03-15", "Nam", "Hà Nội", "thanh@email.com", 
                            "Tình trạng sức khỏe bình thường khi vào làng", "2024-01-15"
                        ))
                        db.conn.execute(sample_query, (
                            "Trần Văn Hùng", "1970-08-20", "Nam", "TP.HCM", "hung@email.com", 
                            "Tình trạng sức khỏe tốt khi vào làng", "2024-02-10"
                        ))
                        db.conn.commit()
                        st.success("✅ Đã thêm dữ liệu mẫu cựu chiến binh!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi thêm dữ liệu mẫu: {str(e)}")
            
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu cựu chiến binh: {str(e)}")

def manage_medical_records_spreadsheet(db):
    """Manage medical records in spreadsheet format with patient ID display"""
    st.subheader("🏥 Hồ sơ y tế")
    
    try:
        # Get medical records with patient names and doctor names
        query = """
            SELECT mr.id, mr.patient_id, 
                   CASE 
                       WHEN mr.patient_type = 'student' THEN s.full_name
                       WHEN mr.patient_type = 'veteran' THEN v.full_name
                       ELSE 'Bệnh nhân ' || mr.patient_id
                   END as patient_name,
                   mr.patient_type as patient_type,
                   mr.date, mr.diagnosis, mr.treatment, mr.notes,
                   u.full_name as doctor_name
            FROM medical_records mr
            JOIN users u ON mr.doctor_id = u.id
            LEFT JOIN students s ON mr.patient_id = s.id AND mr.patient_type = 'student'
            LEFT JOIN veterans v ON mr.patient_id = v.id AND mr.patient_type = 'veteran'
            ORDER BY mr.date DESC
        """
        results = db.conn.execute(query).fetchall()
        
        if results:
            # Create DataFrame with patient ID prominently displayed
            df = pd.DataFrame(results, columns=[
                'ID Hồ sơ', 'ID Bệnh nhân', 'Tên bệnh nhân', 'Loại bệnh nhân', 
                'Ngày khám', 'Chẩn đoán', 'Điều trị', 'Ghi chú', 'Bác sĩ'
            ])
            
            st.write(f"**Tổng số hồ sơ y tế**: {len(results)}")
            
            # Display with edit capabilities (read-only for safety)
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "ID Hồ sơ": st.column_config.NumberColumn("ID Hồ sơ", width="small"),
                    "ID Bệnh nhân": st.column_config.NumberColumn("ID Bệnh nhân", width="small"),
                    "Tên bệnh nhân": st.column_config.TextColumn("Tên bệnh nhân", width="medium"),
                    "Loại bệnh nhân": st.column_config.TextColumn("Loại", width="small"),
                    "Ngày khám": st.column_config.DatetimeColumn("Ngày khám", format="DD/MM/YYYY")
                }
            )
            
            # Export functionality
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Xuất hồ sơ y tế CSV",
                data=csv,
                file_name=f"ho_so_y_te_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
                
        else:
            st.info("Không có dữ liệu hồ sơ y tế")
            
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu hồ sơ y tế: {str(e)}")



def save_students_changes(db, edited_df):
    """Save changes to students table"""
    try:
        for index, row in edited_df.iterrows():
            student_id = row['ID']
            
            # Update student record using PostgreSQL syntax
            update_query = """
                UPDATE students 
                SET full_name = %s, birth_date = %s, gender = %s, address = %s, email = %s,
                    health_on_admission = %s, admission_date = %s
                WHERE id = %s
            """
            db.conn.execute(update_query, (
                row['Họ và tên'], row['Ngày sinh'], row['Giới tính'], row['Địa chỉ'], 
                row['Email'], row.get('Sức khỏe khi nhập học', ''), 
                row['Ngày nhập học'], student_id
            ))
        
        db.conn.commit()
        st.success("✅ Đã lưu thay đổi học sinh thành công!")
        
    except Exception as e:
        st.error(f"Lỗi khi lưu thay đổi: {str(e)}")

def save_veterans_changes(db, edited_df):
    """Save changes to veterans table"""
    try:
        for index, row in edited_df.iterrows():
            veteran_id = row['ID']
            
            # Update veteran record using PostgreSQL syntax
            update_query = """
                UPDATE veterans 
                SET full_name = %s, birth_date = %s, gender = %s, address = %s, email = %s,
                    initial_characteristics = %s, admission_date = %s
                WHERE id = %s
            """
            db.conn.execute(update_query, (
                row['Họ và tên'], row['Ngày sinh'], row['Giới tính'], row['Địa chỉ'], 
                row['Email'], row.get('Đặc điểm ban đầu', ''), row['Ngày nhập làng'], veteran_id
            ))
        
        db.conn.commit()
        st.success("✅ Đã lưu thay đổi cựu chiến binh thành công!")
        
    except Exception as e:
        st.error(f"Lỗi khi lưu thay đổi: {str(e)}")

def user_management_section():
    """User management section merged from admin page"""
    st.subheader("👥 Quản Lý Người Dùng")
    
    # Check if current user is main admin (not administrative or other admin accounts) to access user management
    current_user = st.session_state.get('user')
    if not (current_user and current_user.role == 'admin' and current_user.username == 'admin'):
        st.warning("⚠️ Chỉ có tài khoản admin chính mới có quyền truy cập quản lý người dùng")
        st.info("Các tài khoản 'administrative' và 'admin tổng' không được phép quản lý người dùng")
        return
    
    db = Database()
    
    with st.form("add_user"):
        st.write("### Thêm Người Dùng Mới")
        
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        role = st.selectbox("Vai trò", [
            "admin", "doctor", "teacher", "administrative", "family"
        ])
        full_name = st.text_input("Họ và tên")

        # Show student selection for family role
        if role == "family":
            students = db.get_students()
            student_options = [f"{s.id} - {s.full_name}" for s in students]
            student_selection = st.selectbox(
                "Chọn học sinh",
                [""] + student_options,
                format_func=lambda x: x.split(" - ")[1] if x else "Chọn học sinh"
            )
            student_id = int(student_selection.split(" - ")[0]) if student_selection else None
        else:
            student_id = None

        if st.form_submit_button("Thêm người dùng", type="primary"):
            if db.add_user(username, password, role, full_name, family_student_id=student_id):
                st.success("Thêm người dùng thành công!")
                st.rerun()
            else:
                st.error("Tên đăng nhập đã tồn tại")
    
    # Display existing users
    st.write("### Danh sách người dùng hiện tại")
    users = db.get_all_users()
    if users:
        # Check if current user is admin to show passwords
        current_user = st.session_state.get('user')
        is_admin_user = current_user and current_user.role == 'admin'
        
        # Password viewing toggle for admin users
        show_passwords = False
        if is_admin_user:
            show_passwords = st.checkbox("👁️ Hiển thị mật khẩu người dùng (Chỉ dành cho Admin)", 
                                       help="Tính năng nhạy cảm - chỉ dành cho quản trị viên cấp cao")
        
        users_data = []
        user_passwords = db.get_user_passwords() if show_passwords else {}
        
        for user in users:
            user_data = {
                "ID": user.id,
                "Tên đăng nhập": user.username,
                "Họ và tên": user.full_name,
                "Vai trò": user.role,
                "Email": user.email or "Chưa có",
                "Ngày tạo": user.created_at or "Không rõ"
            }
            
            # Add password column for admin users
            if show_passwords and user.id in user_passwords:
                user_data["Mật khẩu"] = user_passwords[user.id]['password']
            
            users_data.append(user_data)
        
        df = pd.DataFrame(users_data)
        st.dataframe(df, use_container_width=True)
        
        # Security warning for password viewing
        if show_passwords:
            st.warning("🔒 **Cảnh báo bảo mật**: Mật khẩu đang được hiển thị. Đảm bảo không có người khác nhìn thấy màn hình của bạn.")
        
        # Delete user functionality
        st.write("### Xóa người dùng")
        user_to_delete = st.selectbox(
            "Chọn người dùng cần xóa:",
            options=[f"{u.id} - {u.username} ({u.full_name})" for u in users],
            key="delete_user_select"
        )
        
        if st.button("🗑️ Xóa người dùng", type="secondary"):
            if user_to_delete:
                user_id = int(user_to_delete.split(" - ")[0])
                if user_id != 1:  # Don't allow deleting admin user
                    if db.delete_user(user_id):
                        st.success("Đã xóa người dùng thành công!")
                        st.rerun()
                    else:
                        st.error("Không thể xóa người dùng!")
                else:
                    st.error("Không thể xóa tài khoản admin chính!")
    else:
        st.info("Chưa có người dùng nào trong hệ thống")

def render():
    # Initialize authentication first
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
        safe_spreadsheet_management_section()

    with tabs[2]:
        # Excel data import
        import_data_section()

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