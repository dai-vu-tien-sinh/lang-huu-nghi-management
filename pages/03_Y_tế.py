import streamlit as st
from auth import init_auth, check_auth, check_role, check_page_access
from database import Database
from utils import show_success, show_error, apply_theme
from datetime import datetime
from translations import get_text

def render():
    # Initialize authentication first
    init_auth()
    
    # Apply theme from session state
    # apply_theme()  # Disabled - using Streamlit defaults

    # Set current page for role checking
    st.session_state.current_page = "03_Y_tế"

    check_auth()
    
    # Check if user has access to this page dynamically
    if not check_page_access('03_Y_tế'):
        st.error("Bạn không có quyền truy cập trang này.")
        st.stop()
        return

    st.title(get_text("pages.healthcare.title", "Quản Lý Hồ Sơ Y Tế"))

    db = Database()

    tab1, tab2 = st.tabs([
        get_text("pages.healthcare.view_records", "📋 Xem Hồ Sơ"), 
        get_text("pages.healthcare.add_record", "➕ Thêm Hồ Sơ")
    ])

    with tab1:
        # Add filters
        st.subheader(get_text("healthcare.filters", "Bộ lọc"))
        col1, col2, col3 = st.columns(3)

        with col1:
            patient_type = st.selectbox(
                get_text("healthcare.patient_type", "🏥 Loại bệnh nhân"),
                [
                    get_text("healthcare.all", "Tất cả"), 
                    get_text("healthcare.student", "Sinh viên"), 
                    get_text("healthcare.veteran", "Cựu chiến binh")
                ],
                key="view_filter_patient_type"
            )
        with col2:
            patient_filter = st.text_input(get_text("healthcare.search_name", "🔍 Tìm theo tên"), key="view_patient_filter")
        with col3:
            # Set default date range to include records from last 30 days
            from datetime import timedelta
            default_start = datetime.now().date() - timedelta(days=30)
            default_end = datetime.now().date()
            date_range = st.date_input(
                get_text("healthcare.date_range", "📅 Khoảng thời gian"),
                value=(default_start, default_end),
                key="view_date_range"
            )

        try:
            # Build query based on filters with proper patient name resolution
            query = """
                SELECT mr.*, 
                    u.full_name as doctor_name,
                    CASE 
                        WHEN mr.patient_type = 'student' THEN s.full_name
                        WHEN mr.patient_type = 'veteran' THEN COALESCE(v.full_name, 'Cựu chiến binh ' || mr.patient_id)
                        ELSE 'Bệnh nhân ' || mr.patient_id
                    END as patient_name,
                    CASE 
                        WHEN mr.patient_type = 'student' THEN s.email
                        WHEN mr.patient_type = 'veteran' THEN v.email
                        ELSE 'unknown@example.com'
                    END as patient_email,
                    mr.patient_id as patient_id_actual
                FROM medical_records mr
                LEFT JOIN users u ON mr.doctor_id = u.id
                LEFT JOIN students s ON mr.patient_id = s.id AND mr.patient_type = 'student'
                LEFT JOIN veterans v ON mr.patient_id = v.id AND mr.patient_type = 'veteran'
                WHERE 1=1
            """
            params = []

            # For family users, only show their student's medical records
            if st.session_state.user.role == 'family':
                query += " AND mr.patient_type = ? AND s.id = ?"
                params.extend(['student', st.session_state.user.family_student_id])

            if patient_type != "Tất cả":
                query += " AND mr.patient_type = ?"
                params.append("student" if patient_type == "Sinh viên" else "veteran")

            if patient_filter:
                query += " AND (s.full_name LIKE ? OR v.full_name LIKE ?)"
                params.extend([f"%{patient_filter}%", f"%{patient_filter}%"])

            if len(date_range) == 2:
                query += " AND DATE(mr.date) BETWEEN ? AND ?"
                params.extend([date_range[0], date_range[1]])

            query += " ORDER BY mr.date DESC"

            medical_records = db.conn.execute(query, params).fetchall()

            if medical_records:
                # Group medical records by patient
                records_by_patient = {}
                for record in medical_records:
                    # From debug output: After mr.* (12 fields), we have doctor_name(12), patient_name(13), patient_email(14), patient_id_actual(15)
                    patient_name = record[13]  # patient_name  
                    patient_id = record[15]    # patient_id_actual
                    patient_type = record[2]   # patient_type
                    
                    if patient_id not in records_by_patient:
                        records_by_patient[patient_id] = {
                            'name': patient_name,
                            'type': patient_type,
                            'records': []
                        }
                    
                    records_by_patient[patient_id]['records'].append(record)
                
                # Display medical records by patient
                for patient_id, data in records_by_patient.items():
                    patient_name = data['name']
                    patient_type = data['type']
                    patient_records = data['records']
                    
                    type_icon = "🎓" if patient_type == "student" else "🎖️"
                    st.write(f"### {type_icon} {patient_name}")
                    
                    for record in patient_records:
                        # Correct field positions from debug output:
                        # ['int:id', 'int:patient_id', 'str:patient_type', 'str:diagnosis', 'str:treatment', 'int:doctor_id', 'str:date', ...]
                        date_field = record[6]  # The date field is actually at position 6
                        
                        try:
                            # Handle different date formats
                            if isinstance(date_field, str):
                                # Try to parse as full datetime string first (YYYY-MM-DD HH:MM:SS)
                                try:
                                    parsed_date = datetime.strptime(date_field, '%Y-%m-%d %H:%M:%S.%f')
                                    exam_date = parsed_date.strftime('%d/%m/%Y')
                                except ValueError:
                                    try:
                                        parsed_date = datetime.strptime(date_field, '%Y-%m-%d %H:%M:%S')
                                        exam_date = parsed_date.strftime('%d/%m/%Y')
                                    except ValueError:
                                        # Try to parse as YYYY-MM-DD format
                                        try:
                                            parsed_date = datetime.strptime(date_field, '%Y-%m-%d')
                                            exam_date = parsed_date.strftime('%d/%m/%Y')
                                        except ValueError:
                                            # Try to parse as datetime string format
                                            try:
                                                parsed_date = datetime.strptime(date_field.split()[0], '%Y-%m-%d')
                                                exam_date = parsed_date.strftime('%d/%m/%Y')
                                            except (ValueError, IndexError):
                                                exam_date = str(date_field)
                            elif hasattr(date_field, 'strftime'):
                                # Handle date/datetime objects
                                exam_date = date_field.strftime('%d/%m/%Y')
                            else:
                                # Handle numeric or other types
                                exam_date = str(date_field)
                        except (ValueError, AttributeError):
                            # Fallback for invalid dates
                            exam_date = str(date_field) if date_field else "Không xác định"
                        
                        with st.expander(f"🏥 Khám ngày: {exam_date}", expanded=False):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown(f"**🗓️ Ngày khám:** {exam_date}")
                                st.markdown(f"**👨‍⚕️ Bác sĩ:** {record[12]}")  # doctor_name
                                st.markdown(f"**🔍 Chẩn đoán:** {record[3]}")  # diagnosis

                            with col2:
                                st.markdown("**💊 Điều trị:**")
                                st.info(record[4])  # treatment
                                if record[7]:  # notes
                                    st.markdown("**📝 Ghi chú:**")
                                    st.info(record[7])

                            # Email notification section (only show for non-family users)
                            if st.session_state.user.role != 'family':
                                st.markdown("---")
                                patient_email = record[14]  # patient_email
                                if patient_email:
                                    col3, col4 = st.columns([3, 1])
                                    with col3:
                                        st.info("📧 Có thể gửi thông báo qua email")
                                    with col4:
                                        if st.button("📤 Gửi thông báo", key=f"notify_medical_{record[0]}"):
                                            if db.send_medical_record_notification(record[0]):
                                                show_success("Đã gửi thông báo thành công!")
                                                st.rerun()
                                            else:
                                                show_error("Không thể gửi thông báo")
                                else:
                                    st.error("❌ Không có email bệnh nhân")
            else:
                st.info(get_text("pages.healthcare.no_records_found", "🔍 Không tìm thấy hồ sơ y tế phù hợp với bộ lọc"))

        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu: {str(e)}")
            print(f"Database error: {str(e)}")

    # Only show add medical record tab for doctors, nurses and admin
    if st.session_state.user.role in ['doctor', 'nurse', 'admin']:
        with tab2:
            st.info(get_text("pages.healthcare.instructions", """
            ℹ️ **Hướng dẫn:**
            1. Chọn bệnh nhân (sinh viên hoặc cựu chiến binh)
            2. Điền thông tin chẩn đoán và điều trị
            3. Thêm ghi chú (nếu cần)
            4. Tùy chọn gửi thông báo email
            """))

            with st.form("add_medical_record", clear_on_submit=True):
                st.subheader(get_text("pages.healthcare.record_info", "Thông tin khám bệnh"))

                # Patient type selection
                col1, col2 = st.columns(2)
                with col1:
                    patient_type = st.selectbox(
                        get_text("healthcare.patient_type", "🏥 Loại bệnh nhân"),
                        ["student", "veteran"],
                        format_func=lambda x: "Sinh viên" if x == "student" else "Cựu chiến binh",
                        key="add_patient_type"
                    )
                
                # Get appropriate patient list based on type
                if patient_type == "student":
                    patients = db.get_students_for_selection()
                    patient_options = [f"{name} (ID: {id})" for id, name in patients]
                    selection_label = "🎓 Chọn sinh viên"
                else:
                    veterans = db.get_veterans_for_selection()
                    patient_options = [f"{name} (ID: {id})" for id, name in veterans]
                    selection_label = "🎖️ Chọn cựu chiến binh"

                with col2:
                    if patient_options:
                        selected_patient = st.selectbox(
                            selection_label,
                            options=patient_options,
                            format_func=lambda x: str(x).split(" (ID: ")[0] if " (ID: " in str(x) else str(x)
                        )
                        # Extract patient ID from selection
                        patient_id = int(str(selected_patient).split("ID: ")[1].rstrip(")"))
                    else:
                        st.error(f"Không có {'sinh viên' if patient_type == 'student' else 'cựu chiến binh'} nào trong hệ thống")
                        patient_id = None

                col3, col4 = st.columns(2)
                with col3:
                    exam_date = st.date_input("📅 Ngày khám", value=datetime.now().date())
                with col4:
                    send_notification = st.checkbox("📧 Gửi thông báo email", value=True)

                diagnosis = st.text_area("🔍 Chẩn đoán", height=100,
                    placeholder="Nhập chẩn đoán chi tiết...")

                treatment = st.text_area("💊 Điều trị", height=100,
                    placeholder="Nhập phương pháp điều trị và thuốc...")

                notes = st.text_area("📝 Ghi chú", height=80,
                    placeholder="Ghi chú bổ sung (không bắt buộc)...")

                if st.form_submit_button("✅ Thêm hồ sơ y tế") and patient_id:
                    try:
                        record_data = {
                            "patient_id": patient_id,
                            "patient_type": patient_type,
                            "doctor_id": st.session_state.user.id,
                            "diagnosis": diagnosis,
                            "treatment": treatment,
                            "notes": notes
                        }
                        record_id = db.add_medical_record(record_data)

                        if record_id:
                            show_success("✨ Thêm hồ sơ y tế thành công!")
                            if send_notification:
                                if db.send_medical_record_notification(record_id):
                                    show_success("📤 Đã gửi thông báo thành công!")
                                else:
                                    show_error("❌ Không thể gửi thông báo")
                            st.rerun()
                        else:
                            show_error("❌ Không thể thêm hồ sơ y tế")
                    except Exception as e:
                        show_error(f"❌ Lỗi khi thêm hồ sơ: {str(e)}")
    else:
        with tab2:
            st.warning("⚠️ Bạn không có quyền thêm hồ sơ y tế mới")

if __name__ == "__main__":
    render()