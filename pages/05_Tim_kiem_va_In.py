import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
from auth import check_auth, is_search_allowed, is_print_allowed, can_manage_data, get_role_based_search_types
from database import Database
from utils import show_success, show_error, apply_theme, format_date
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from translations import get_text
import os

def export_to_excel(db, person_type, person_id):
    """Export person data to Excel with formatting"""
    # Create Excel writer
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    # Get basic info - chỉ lấy các trường cụ thể để tránh lỗi không khớp số cột
    if person_type == "student":
        query = """
            SELECT s.id, s.full_name, s.birth_date, s.address, s.email, 
                   s.admission_date, s.health_status, s.academic_status, 
                   s.psychological_status, s.gender, s.phone, 
                   c.name as class_name, c.academic_year
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            WHERE s.id = ?
        """
    else:
        query = """
            SELECT id, full_name, birth_date, address, email, 
                   service_period, health_condition, contact_info
            FROM veterans 
            WHERE id = ?
        """

    person = db.conn.execute(query, (person_id,)).fetchone()

    if person:
        # Basic Info Sheet
        basic_info = {
            'Thông tin': ['Họ và tên', 'Ngày sinh', 'Địa chỉ', 'Email'],
            'Giá trị': [
                person[1],  # full_name
                person[2] or 'Chưa cập nhật',  # birth_date
                person[3] or 'Chưa cập nhật',  # address
                person[4] or 'Chưa cập nhật'   # email
            ]
        }

        if person_type == "student":
            # Cập nhật chỉ số dựa trên thứ tự trường trong câu truy vấn SQL
            # SELECT s.id, s.full_name, s.birth_date, s.address, s.email, 
            #        s.admission_date, s.health_status, s.academic_status, 
            #        s.psychological_status, s.gender, s.phone, 
            #        c.name as class_name, c.academic_year
            basic_info['Thông tin'].extend([
                'Lớp',
                'Năm học',
                'Ngày nhập học',
                'Tình trạng sức khỏe',
                'Tình trạng học tập',
                'Tình trạng tâm lý'
            ])
            basic_info['Giá trị'].extend([
                person[11] or 'Chưa phân lớp',  # class_name
                person[12] or 'Chưa cập nhật',  # academic_year
                person[5] or 'Chưa cập nhật',   # admission_date
                person[6] or 'Chưa cập nhật',   # health_status
                person[7] or 'Chưa đánh giá',   # academic_status
                person[8] or 'Chưa đánh giá'    # psychological_status
            ])
        else:
            # Cập nhật chỉ số dựa trên thứ tự trường trong câu truy vấn SQL
            # SELECT id, full_name, birth_date, address, email, 
            #        service_period, health_condition, contact_info
            basic_info['Thông tin'].extend([
                'Thời gian phục vụ',
                'Tình trạng sức khỏe',
                'Liên hệ'
            ])
            basic_info['Giá trị'].extend([
                person[5] or 'Chưa cập nhật',  # service_period
                person[6] or 'Chưa cập nhật',  # health_condition
                person[7] or 'Chưa cập nhật'   # contact_info
            ])

        df_basic = pd.DataFrame(basic_info)
        df_basic.to_excel(writer, sheet_name='Thông tin cơ bản', index=False)

        # Medical Records Sheet
        records = db.conn.execute("""
            SELECT mr.id, mr.patient_id, mr.patient_type, mr.diagnosis, mr.treatment,
                   mr.doctor_id, mr.date, mr.notes, mr.notification_sent,
                   u.full_name as doctor_name
            FROM medical_records mr
            JOIN users u ON mr.doctor_id = u.id
            WHERE mr.patient_id = ? AND mr.patient_type = ?
            ORDER BY mr.date DESC
        """, (person_id, person_type)).fetchall()

        if records:
            medical_data = []
            for record in records:
                medical_data.append({
                    'Ngày khám': record[6],
                    'Bác sĩ': record[-1],
                    'Chẩn đoán': record[3],
                    'Điều trị': record[4],
                    'Ghi chú': record[7] or ''
                })
            df_medical = pd.DataFrame(medical_data)
            df_medical.to_excel(writer, sheet_name='Hồ sơ y tế', index=False)

        # Psychological Evaluations Sheet (only for students)
        if person_type == "student":
            evals = db.conn.execute("""
                SELECT pe.id, pe.student_id, pe.evaluation_date, pe.evaluator_id, 
                       pe.assessment, pe.recommendations, pe.follow_up_date, pe.notification_sent,
                       u.full_name as evaluator_name
                FROM psychological_evaluations pe
                JOIN users u ON pe.evaluator_id = u.id
                WHERE pe.student_id = ?
                ORDER BY pe.evaluation_date DESC
            """, (person_id,)).fetchall()

            if evals:
                psych_data = []
                for eval in evals:
                    psych_data.append({
                        'Ngày đánh giá': eval[2],
                        'Người đánh giá': eval[-1],
                        'Đánh giá': eval[4],
                        'Khuyến nghị': eval[5],
                        'Ngày theo dõi tiếp': eval[6] or ''
                    })
                df_psych = pd.DataFrame(psych_data)
                df_psych.to_excel(writer, sheet_name='Đánh giá tâm lý', index=False)

        # Auto-adjust columns width
        for worksheet in writer.sheets.values():
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

        # Save the file
        writer.close()
        return output.getvalue()
    return None

def search_section():
    """Phần tìm kiếm toàn bộ dữ liệu"""
    st.subheader(f"🔍 {get_text('pages.search.detailed_search', 'Tìm kiếm chi tiết')}")
    
    # Kiểm tra quyền sử dụng tìm kiếm
    if not is_search_allowed():
        st.error("Bạn không có quyền sử dụng chức năng tìm kiếm")
        return
    
    db = Database()
    
    # Chọn loại tìm kiếm dựa theo vai trò người dùng
    all_search_types = {
        "students": "Học sinh",
        "veterans": "Cựu chiến binh",
        "medical_records": "Hồ sơ y tế", 
        "psychological_evaluations": "Đánh giá tâm lý"
    }
    
    # Lấy danh sách loại tìm kiếm được phép theo vai trò
    allowed_search_types_keys = get_role_based_search_types()
    
    # Chỉ hiển thị các loại tìm kiếm được phép
    search_types = [all_search_types[key] for key in allowed_search_types_keys]
    
    if not search_types:
        st.error("Bạn không có quyền tìm kiếm bất kỳ loại dữ liệu nào")
        return
        
    search_type = st.selectbox("🔍 Chọn loại tìm kiếm", search_types, key="search_type")

    # Tạo form tìm kiếm
    with st.form("search_form"):
        # Tìm kiếm chung
        name_query = st.text_input("Tên", key="search_name")
        
        # Các trường tìm kiếm bổ sung tùy theo loại
        advanced_fields = st.expander("📋 Tìm kiếm nâng cao")
        
        # Trường dữ liệu tùy theo loại tìm kiếm
        with advanced_fields:
            if search_type == "Học sinh":
                st.markdown("#### Thông tin cơ bản")
                
                col1, col2 = st.columns(2)
                with col1:
                    address = st.text_input("Địa chỉ", key="search_address")
                    email = st.text_input("Email", key="search_email")
                    phone = st.text_input("Số điện thoại", key="search_phone")
                    
                with col2:
                    gender = st.selectbox(
                        "Giới tính",
                        ["Tất cả", "Nam", "Nữ", "Khác"],
                        key="search_gender"
                    )
                    year = st.text_input("Năm", key="search_year")
                    parent_name = st.text_input("Phụ huynh", key="search_parent")
                
                st.markdown("#### Thông tin học tập")
                class_options = [(None, "Tất cả lớp")] + [(c.id, c.name) for c in db.get_classes()]
                selected_class = st.selectbox(
                    "Lớp",
                    options=range(len(class_options)),
                    format_func=lambda i: class_options[i][1],
                    key="search_class"
                )
                class_id = class_options[selected_class][0] if selected_class > 0 else None
                
                col1, col2 = st.columns(2)
                with col1:
                    use_admission_date = st.checkbox("Lọc theo ngày nhập học", key="use_admission_date")
                    if use_admission_date:
                        admission_date_range = st.date_input(
                            "Phạm vi ngày nhập học",
                            value=[datetime.now().replace(day=1), datetime.now()],
                            key="admission_date_range"
                        )
                
                with col2:
                    use_birth_date = st.checkbox("Lọc theo ngày sinh", key="use_birth_date")
                    if use_birth_date:
                        birth_date_range = st.date_input(
                            "Phạm vi ngày sinh",
                            value=[datetime.now().replace(year=datetime.now().year-18, day=1), datetime.now()],
                            key="birth_date_range"
                        )
                
                st.markdown("#### Tình trạng")
                col1, col2, col3 = st.columns(3)
                with col1:
                    health_status = st.selectbox(
                        "Tình trạng sức khỏe",
                        ["Tất cả", "Tốt", "Bình thường", "Ổn định", "Cần chú ý"],
                        key="search_health"
                    )
                with col2:
                    academic_status = st.selectbox(
                        "Tình trạng học tập",
                        ["Tất cả", "Xuất sắc", "Tốt", "Trung bình", "Cần cải thiện", "Chưa đánh giá"],
                        key="search_academic"
                    )
                with col3:
                    psychological_status = st.selectbox(
                        "Tình trạng tâm lý",
                        ["Tất cả", "Ổn định", "Cần theo dõi", "Cần hỗ trợ", "Tốt", "Chưa đánh giá"],
                        key="search_psych"
                    )
                
            elif search_type == "Cựu chiến binh":
                st.markdown("#### Thông tin cơ bản")
                col1, col2 = st.columns(2)
                with col1:
                    address = st.text_input("Địa chỉ", key="search_vet_address")
                    email = st.text_input("Email", key="search_vet_email")
                with col2:
                    contact_info = st.text_input("Thông tin liên hệ", key="search_vet_contact")
                    service_period = st.text_input("Thời gian phục vụ", key="search_service")
                
                st.markdown("#### Tình trạng sức khỏe")
                health_condition = st.text_input("Tình trạng sức khỏe", key="search_vet_health")
                
                use_birth_date = st.checkbox("Lọc theo ngày sinh", key="use_vet_birth_date")
                if use_birth_date:
                    birth_date_range = st.date_input(
                        "Phạm vi ngày sinh",
                        value=[datetime.now().replace(year=datetime.now().year-65), datetime.now()],
                        key="vet_birth_date_range"
                    )
                
            else:  # Y tế và Tâm lý
                st.markdown("#### Thời gian")
                use_date_filter = st.checkbox("Lọc theo thời gian", key="use_date_filter")
                if use_date_filter:
                    date_range = st.date_input(
                        "Phạm vi thời gian",
                        value=[datetime.now().replace(day=1), datetime.now()],
                        key="date_range"
                    )
                
                if search_type == "Hồ sơ y tế":
                    # Danh sách bác sĩ
                    doctor_options = [(None, "Tất cả bác sĩ")]
                    doctors = db.conn.execute("""
                        SELECT id, full_name FROM users 
                        WHERE role = 'doctor' OR role = 'nurse' OR role = 'admin'
                        ORDER BY full_name
                    """).fetchall()
                    doctor_options += [(d[0], d[1]) for d in doctors]
                    
                    selected_doctor = st.selectbox(
                        "Bác sĩ",
                        options=range(len(doctor_options)),
                        format_func=lambda i: doctor_options[i][1],
                        key="search_doctor"
                    )
                    doctor_id = doctor_options[selected_doctor][0] if selected_doctor > 0 else None
                    
                    diagnosis = st.text_input("Chẩn đoán", key="search_diagnosis")
                    treatment = st.text_input("Điều trị", key="search_treatment")
                
                elif search_type == "Đánh giá tâm lý":
                    # Danh sách chuyên viên tâm lý
                    counselor_options = [(None, "Tất cả chuyên viên")]
                    counselors = db.conn.execute("""
                        SELECT id, full_name FROM users 
                        WHERE role = 'counselor' OR role = 'admin'
                        ORDER BY full_name
                    """).fetchall()
                    counselor_options += [(c[0], c[1]) for c in counselors]
                    
                    selected_counselor = st.selectbox(
                        "Chuyên viên",
                        options=range(len(counselor_options)),
                        format_func=lambda i: counselor_options[i][1],
                        key="search_counselor"
                    )
                    counselor_id = counselor_options[selected_counselor][0] if selected_counselor > 0 else None
                    
                    assessment = st.text_input("Đánh giá", key="search_assessment")
                    recommendations = st.text_input("Khuyến nghị", key="search_recommendations")
        
        # Nút tìm kiếm
        search_button = st.form_submit_button("🔍 Tìm kiếm")
        
        if search_button:
            # Tạo query tìm kiếm
            query = {"name": name_query}
            
            # Thêm các trường tìm kiếm nâng cao
            if search_type == "Học sinh":
                if address:
                    query["address"] = address
                if email:
                    query["email"] = email
                if phone:
                    query["phone"] = phone
                if gender != "Tất cả":
                    query["gender"] = gender
                if year:
                    query["year"] = year
                if parent_name:
                    query["parent_name"] = parent_name
                if class_id is not None:
                    query["class_id"] = class_id
                if health_status != "Tất cả":
                    query["health_status"] = health_status
                if academic_status != "Tất cả":
                    query["academic_status"] = academic_status
                if psychological_status != "Tất cả":
                    query["psychological_status"] = psychological_status
                
                # Thêm lọc theo ngày nhập học
                if 'use_admission_date' in locals() and use_admission_date and 'admission_date_range' in locals() and len(admission_date_range) > 1:
                    query["from_date"] = admission_date_range[0].strftime("%Y-%m-%d")
                    query["to_date"] = admission_date_range[1].strftime("%Y-%m-%d")
                
                # Thêm lọc theo ngày sinh
                if 'use_birth_date' in locals() and use_birth_date and 'birth_date_range' in locals() and len(birth_date_range) > 1:
                    query["birth_date_from"] = birth_date_range[0].strftime("%Y-%m-%d")
                    query["birth_date_to"] = birth_date_range[1].strftime("%Y-%m-%d")
                
                # In log debug
                st.write(f"Query: {query}")
                
                # Thực hiện tìm kiếm và lưu vào session state
                st.session_state.search_results_students = db.search_students(query)
                st.session_state.current_search_type = "Học sinh"
                
            elif search_type == "Cựu chiến binh":
                if address:
                    query["address"] = address
                if email:
                    query["email"] = email
                if contact_info:
                    query["contact_info"] = contact_info
                if service_period:
                    query["service_period"] = service_period
                if health_condition:
                    query["health_condition"] = health_condition
                
                # Thêm lọc theo ngày sinh
                if 'use_birth_date' in locals() and use_birth_date and 'birth_date_range' in locals() and len(birth_date_range) > 1:
                    query["birth_date_from"] = birth_date_range[0].strftime("%Y-%m-%d")
                    query["birth_date_to"] = birth_date_range[1].strftime("%Y-%m-%d")
                
                # In log debug
                st.write(f"Veteran Query: {query}")
                
                # Thực hiện tìm kiếm
                st.session_state.search_results_veterans = db.search_veterans(query)
                st.session_state.current_search_type = "Cựu chiến binh"
                
            elif search_type == "Hồ sơ y tế":
                if doctor_id is not None:
                    query["doctor_id"] = doctor_id
                if diagnosis:
                    query["diagnosis"] = diagnosis
                if treatment:
                    query["treatment"] = treatment
                
                # Thêm lọc theo thời gian
                if use_date_filter and 'date_range' in locals() and len(date_range) > 1:
                    query["from_date"] = date_range[0].strftime("%Y-%m-%d")
                    query["to_date"] = date_range[1].strftime("%Y-%m-%d")
                
                # Thực hiện tìm kiếm
                st.session_state.search_results_medical = db.search_medical_records(query)
                st.session_state.current_search_type = "Hồ sơ y tế"
                
            elif search_type == "Đánh giá tâm lý":
                if counselor_id is not None:
                    query["evaluator_id"] = counselor_id
                if assessment:
                    query["assessment"] = assessment
                if recommendations:
                    query["recommendations"] = recommendations
                
                # Thêm lọc theo thời gian
                if use_date_filter and 'date_range' in locals() and len(date_range) > 1:
                    query["from_date"] = date_range[0].strftime("%Y-%m-%d")
                    query["to_date"] = date_range[1].strftime("%Y-%m-%d")
                
                # Thực hiện tìm kiếm
                st.session_state.search_results_psych = db.search_psychological_evaluations(query)
                st.session_state.current_search_type = "Đánh giá tâm lý"
    
    # Hiển thị kết quả tìm kiếm (ngoài form)
    if 'current_search_type' in st.session_state:
        search_type = st.session_state.current_search_type
        
        if search_type == "Học sinh" and 'search_results_students' in st.session_state:
            students = st.session_state.search_results_students
            
            st.subheader(f"🔎 Kết quả: {len(students)} học sinh")
            
            # Nếu có kết quả, hiển thị các nút xuất danh sách
            if students:
                # Button để xuất danh sách học sinh kết quả (ngoài form)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📄 Xuất danh sách Excel", key="export_students_excel"):
                        export_student_list(students, 'excel')
                with col2:
                    if st.button("📄 Xuất danh sách CSV", key="export_students_csv"):
                        export_student_list(students, 'csv')
                with col3:
                    if st.button("📄 Xuất danh sách PDF", key="export_students_pdf"):
                        export_student_list(students, 'pdf')
                
                st.markdown("---")
                
                # Hiển thị danh sách học sinh
                for student in students:
                    with st.expander(f"👨‍🎓 {student.full_name}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**🎂 Ngày sinh:** {student.birth_date or 'Chưa cập nhật'}")
                            st.markdown(f"**📧 Email:** {student.email or 'Chưa cập nhật'}")
                            st.markdown(f"**📍 Địa chỉ:** {student.address or 'Chưa cập nhật'}")
                        with col2:
                            if student.admission_date:
                                st.markdown(f"**📅 Ngày nhập học:** {student.admission_date}")
                            else:
                                st.markdown(f"**📅 Ngày nhập học:** Chưa cập nhật")
                            st.markdown(f"**🏥 Tình trạng sức khỏe:** {student.health_status or 'Chưa cập nhật'}")
                            st.markdown(f"**📚 Tình trạng học tập:** {student.academic_status or 'Chưa cập nhật'}")
                            if hasattr(student, 'psychological_status'):
                                st.markdown(f"**🧠 Tình trạng tâm lý:** {student.psychological_status or 'Chưa đánh giá'}")
                            else:
                                st.markdown(f"**🧠 Tình trạng tâm lý:** Chưa đánh giá")
            else:
                st.info("Không tìm thấy kết quả nào phù hợp")
                
        elif search_type == "Cựu chiến binh" and 'search_results_veterans' in st.session_state:
            veterans = st.session_state.search_results_veterans
            
            st.subheader(f"🔎 Kết quả: {len(veterans)} cựu chiến binh")
            if veterans:
                # Hiển thị danh sách cựu chiến binh
                for veteran in veterans:
                    with st.expander(f"🎖️ {veteran.full_name}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**🎂 Ngày sinh:** {veteran.birth_date or 'Chưa cập nhật'}")
                            st.markdown(f"**🏅 Thời gian phục vụ:** {veteran.service_period or 'Chưa cập nhật'}")
                            st.markdown(f"**📍 Địa chỉ:** {veteran.address or 'Chưa cập nhật'}")
                        with col2:
                            st.markdown(f"**📧 Email:** {veteran.email or 'Chưa cập nhật'}")
                            st.markdown(f"**📞 Liên hệ:** {veteran.contact_info or 'Chưa cập nhật'}")
                            st.markdown(f"**🏥 Tình trạng sức khỏe:** {veteran.health_condition or 'Chưa cập nhật'}")
            else:
                st.info("Không tìm thấy kết quả nào phù hợp")
                
        elif search_type == "Hồ sơ y tế" and 'search_results_medical' in st.session_state:
            records = st.session_state.search_results_medical
            
            st.subheader(f"🔎 Kết quả: {len(records)} hồ sơ y tế")
            if records:
                for record in records:
                    patient_type = "Học sinh" if record['patient_type'] == "student" else "Cựu chiến binh"
                    with st.expander(f"🏥 {record['patient_name']} - {patient_type} - {record['date']}", expanded=False):
                        st.markdown(f"**👨‍⚕️ Bác sĩ:** {record['doctor_name']}")
                        st.markdown(f"**📅 Ngày khám:** {record['date']}")
                        st.markdown("**📋 Chẩn đoán:**")
                        st.info(record['diagnosis'])
                        st.markdown("**💊 Điều trị:**")
                        st.info(record['treatment'])
                        if record['notes']:
                            st.markdown("**📝 Ghi chú:**")
                            st.info(record['notes'])
            else:
                st.info("Không tìm thấy kết quả nào phù hợp")
                
        elif search_type == "Đánh giá tâm lý" and 'search_results_psych' in st.session_state:
            evals = st.session_state.search_results_psych
            
            st.subheader(f"🔎 Kết quả: {len(evals)} đánh giá tâm lý")
            if evals:
                for eval in evals:
                    with st.expander(f"🧠 {eval['student_name']} - {eval['evaluation_date']}", expanded=False):
                        st.markdown(f"**👨‍⚕️ Chuyên viên:** {eval['evaluator_name']}")
                        st.markdown(f"**📅 Ngày đánh giá:** {eval['evaluation_date']}")
                        st.markdown("**📋 Đánh giá:**")
                        st.info(eval['assessment'])
                        st.markdown("**💡 Khuyến nghị:**")
                        st.info(eval['recommendations'])
                        if eval['follow_up_date']:
                            st.markdown(f"**📅 Ngày theo dõi tiếp:** {eval['follow_up_date']}")
            else:
                st.info("Không tìm thấy kết quả nào phù hợp")

def save_changes_to_db(conn, table_name, original_df, edited_df, start_idx):
    """Lưu thay đổi vào database"""
    cursor = conn.cursor()
    
    # Lấy thông tin các cột của bảng
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    primary_key = next((col[1] for col in columns_info if col[5] == 1), None)  # Lấy tên cột là khóa chính
    
    if not primary_key:
        # Nếu không có khóa chính, dùng rowid
        primary_key = "rowid"
    
    # Duyệt qua từng hàng để kiểm tra sự thay đổi
    for i in range(len(edited_df)):
        original_row = original_df.iloc[i]
        edited_row = edited_df.iloc[i]
        
        # So sánh từng hàng để phát hiện thay đổi
        if not original_row.equals(edited_row):
            # Tạo chuỗi cập nhật SET column=value
            updates = []
            params = []
            
            for col in edited_df.columns:
                if original_row[col] != edited_row[col]:
                    updates.append(f"{col} = ?")
                    params.append(edited_row[col])
            
            if updates:
                # Lấy giá trị của khóa chính
                if primary_key in original_row:
                    pk_value = original_row[primary_key]
                else:
                    # Nếu không tìm thấy khóa chính trong DataFrame, dùng rowid
                    pk_value = start_idx + i + 1
                
                # Tạo và thực thi truy vấn UPDATE
                query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE {primary_key} = ?"
                params.append(pk_value)
                cursor.execute(query, params)
    
    # Commit các thay đổi
    conn.commit()

def export_student_list(students, format_type='excel'):
    """Xuất danh sách học sinh dựa theo kết quả tìm kiếm"""
    if not students:
        st.warning("Không có học sinh nào để xuất")
        return
    
    # Không cần debug code nữa, đã hiểu rõ cấu trúc của Student object
    
    db = Database()
    
    # Danh sách các trường bắt buộc để xuất - lưu ý phải giữ số lượng cột này khớp với student_data
    export_fields = [
        "ID", "Họ và tên", "Ngày sinh", "Giới tính", "Địa chỉ", 
        "Email", "Số điện thoại", "Lớp", "Ngày nhập học", 
        "Tình trạng sức khỏe", "Tình trạng học tập", "Tình trạng tâm lý"
    ]
    
    # Chuẩn bị dữ liệu cho export
    data = []
    for student in students:
        # Lấy thông tin lớp học nếu có
        class_name = "Chưa phân lớp"
        if student.class_id:
            class_info = db.get_class(student.class_id)
            if class_info:
                class_name = class_info.name
        
        # Tạo dictionary cho mỗi học sinh - QUAN TRỌNG: chỉ lấy các trường có trong export_fields
        student_data = {}
        student_data["ID"] = student.id
        student_data["Họ và tên"] = student.full_name
        student_data["Ngày sinh"] = format_date(student.birth_date) if student.birth_date else "Chưa cập nhật"
        student_data["Giới tính"] = student.gender or "Chưa cập nhật"
        student_data["Địa chỉ"] = student.address or "Chưa cập nhật"
        student_data["Email"] = student.email or "Chưa cập nhật"
        student_data["Số điện thoại"] = student.phone or "Chưa cập nhật"
        student_data["Lớp"] = class_name
        student_data["Ngày nhập học"] = format_date(student.admission_date) if student.admission_date else "Chưa cập nhật"
        student_data["Tình trạng sức khỏe"] = student.health_status or "Chưa đánh giá"
        student_data["Tình trạng học tập"] = student.academic_status or "Chưa đánh giá"
        student_data["Tình trạng tâm lý"] = student.psychological_status or "Chưa đánh giá"
        
        # Đảm bảo không có trường thừa
        data.append({field: student_data[field] for field in export_fields})
    
    # Tạo DataFrame với đúng số cột như đã định nghĩa
    df = pd.DataFrame(data)
    
    # Timestamp cho tên file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Xuất theo định dạng yêu cầu
    if format_type == 'excel':
        # Đảm bảo chỉ lấy các cột ổn định cho Excel
        # Lấy danh sách cột và loại bỏ các thuộc tính không cần thiết
        required_columns = [
            "ID", "Họ và tên", "Ngày sinh", "Giới tính", "Địa chỉ", 
            "Email", "Số điện thoại", "Lớp", "Ngày nhập học", 
            "Tình trạng sức khỏe", "Tình trạng học tập", "Tình trạng tâm lý"
        ]
        
        # Đây là vấn đề chính - tạo DataFrame mới hoàn toàn từ dữ liệu đã xử lý
        # thay vì dùng DataFrame hiện tại và các cột của nó
        excel_data = []
        for student_data in data:
            row = {}
            for col in required_columns:
                row[col] = student_data.get(col, "")
            excel_data.append(row)
                
        # Tạo DataFrame mới với đúng cấu trúc
        excel_df = pd.DataFrame(excel_data, columns=required_columns)
                
        # Xuất ra Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            excel_df.to_excel(writer, index=False, sheet_name="Danh sách học sinh")
            
            # Định dạng sheet để dễ đọc
            worksheet = writer.sheets["Danh sách học sinh"]
            for idx, col in enumerate(excel_df.columns, 1):
                # Đặt độ rộng cột dựa vào nội dung
                max_length = max(excel_df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[chr(64 + idx)].width = max_length + 5
        
        # Chuẩn bị dữ liệu để tải xuống
        excel_data = output.getvalue()
        
        # Tên file
        filename = f"Danh_sach_hoc_sinh_{timestamp}.xlsx"
        
        # Download button
        st.download_button(
            label="📥 Tải xuống danh sách (Excel)",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_student_list_excel"
        )
        show_success("Đã tạo file Excel thành công! Nhấn nút tải xuống để lưu file.")
        
    elif format_type == 'csv':
        # Đảm bảo chỉ lấy các cột ổn định cho CSV
        # Lấy danh sách cột và loại bỏ các thuộc tính không cần thiết
        required_columns = [
            "ID", "Họ và tên", "Ngày sinh", "Giới tính", "Địa chỉ", 
            "Email", "Số điện thoại", "Lớp", "Ngày nhập học", 
            "Tình trạng sức khỏe", "Tình trạng học tập", "Tình trạng tâm lý"
        ]
        
        # Tạo DataFrame mới hoàn toàn từ dữ liệu đã xử lý
        csv_data = []
        for student_data in data:
            row = {}
            for col in required_columns:
                row[col] = student_data.get(col, "")
            csv_data.append(row)
                
        # Tạo DataFrame mới với đúng cấu trúc
        csv_df = pd.DataFrame(csv_data, columns=required_columns)
                
        # Xuất ra CSV
        csv = csv_df.to_csv(index=False).encode('utf-8')
        
        # Tên file
        filename = f"Danh_sach_hoc_sinh_{timestamp}.csv"
        
        # Download button
        st.download_button(
            label="📥 Tải xuống danh sách (CSV)",
            data=csv,
            file_name=filename,
            mime="text/csv",
            key="download_student_list_csv"
        )
        show_success("Đã tạo file CSV thành công! Nhấn nút tải xuống để lưu file.")
        
    elif format_type == 'pdf':
        # Tạo PDF với reportlab
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, title="Danh sách học sinh")
        
        # Danh sách các phần tử để thêm vào PDF
        elements = []
        
        # Đăng ký font hỗ trợ tiếng Việt (cần tạo trước)
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
            font_name = 'DejaVuSans'
        except:
            font_name = 'Helvetica'
        
        # Style cho tiêu đề
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontName=font_name+'-Bold',
            fontSize=16,
            alignment=1, # center
            spaceAfter=12
        )
        
        # Thêm tiêu đề
        elements.append(Paragraph("DANH SÁCH HỌC SINH", title_style))
        elements.append(Spacer(1, 12))
        
        # Đảm bảo chỉ lấy các cột ổn định cho bảng
        # Lấy danh sách cột và loại bỏ các thuộc tính không cần thiết
        required_columns = [
            "ID", "Họ và tên", "Ngày sinh", "Giới tính", "Địa chỉ", 
            "Email", "Số điện thoại", "Lớp", "Ngày nhập học", 
            "Tình trạng sức khỏe", "Tình trạng học tập", "Tình trạng tâm lý"
        ]
        
        # Tạo DataFrame mới hoàn toàn từ dữ liệu đã xử lý
        pdf_data = []
        for student_data in data:
            row = {}
            for col in required_columns:
                row[col] = student_data.get(col, "")
            pdf_data.append(row)
                
        # Tạo DataFrame mới với đúng cấu trúc
        pdf_df = pd.DataFrame(pdf_data, columns=required_columns)
        
        # Chuẩn bị dữ liệu cho bảng
        table_data = [pdf_df.columns.tolist()]  # Tiêu đề các cột
        for _, row in pdf_df.iterrows():
            table_data.append(row.tolist())
        
        # Tạo bảng
        table = Table(table_data, repeatRows=1)
        
        # Style cho bảng
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name+'-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(table_style)
        
        # Giới hạn độ rộng của bảng
        table._argW = [1.2*inch] + [1.5*inch] * (len(pdf_df.columns) - 1)
        
        # Thêm bảng vào tài liệu
        elements.append(table)
        
        # Tạo PDF
        doc.build(elements)
        
        # Chuẩn bị dữ liệu để tải xuống
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Tên file
        filename = f"Danh_sach_hoc_sinh_{timestamp}.pdf"
        
        # Download button
        st.download_button(
            label="📥 Tải xuống danh sách (PDF)",
            data=pdf_data,
            file_name=filename,
            mime="application/pdf",
            key="download_student_list_pdf"
        )
        show_success("Đã tạo file PDF thành công! Nhấn nút tải xuống để lưu file.")

def database_section():
    """Phần quản lý database"""
    # Kiểm tra quyền quản lý dữ liệu
    if not can_manage_data():
        st.error(get_text("common.no_permission", "Bạn không có quyền sử dụng chức năng này"))
        return
    
    st.subheader("🗄️ " + get_text("database_management.title", "Quản lý Dữ liệu"))
    
    # Thông tin hướng dẫn
    st.info("""
    ### 📌 Thông tin
    - Trang này cho phép bạn trực tiếp truy cập và quản lý dữ liệu trong cơ sở dữ liệu
    - Bạn có thể xem, chỉnh sửa, xuất và nhập dữ liệu theo từng bảng
    - Để quản lý sao lưu và khôi phục database, vui lòng sử dụng trang **Quản lý Hệ thống**
    """)
    
    # Tạo các tab để phân chia chức năng
    tab1, tab2, tab3 = st.tabs([
        get_text("database_management.view_tables", "Xem và Chỉnh sửa Bảng"),
        get_text("database_management.export", "Xuất dữ liệu"),
        get_text("database_management.import", "Nhập dữ liệu từ File")
    ])
    
    # Kết nối đến database
    conn = sqlite3.connect('lang_huu_nghi.db')
    
    # Tab 1: Xem và chỉnh sửa bảng
    with tab1:
        # Lấy danh sách tất cả các bảng
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Chọn bảng để xem và chỉnh sửa - hiển thị tên đã dịch
        table_options = []
        table_display_names = {}
        
        for table in tables:
            # Lấy tên đã dịch của bảng nếu có, nếu không dùng tên gốc
            display_name = get_text(f"database_management.tables.{table}", table)
            table_options.append(display_name)
            table_display_names[display_name] = table
            
        selected_table_display = st.selectbox(
            get_text("database_management.select_table", "Chọn bảng"),
            table_options,
            key="db_select_table"
        )
        
        # Lấy tên bảng thực tế từ tên hiển thị
        selected_table = table_display_names.get(selected_table_display, selected_table_display)
        
        if selected_table:
            # Đọc dữ liệu từ bảng đã chọn - sử dụng SELECT cụ thể thay vì SELECT *
            # Lấy danh sách các cột trong bảng
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Tạo câu truy vấn SELECT với các cột cụ thể
            columns_str = ", ".join(columns)
            df = pd.read_sql_query(f"SELECT {columns_str} FROM {selected_table}", conn)
            
            # Hiển thị thông tin bảng với tên đã dịch
            st.markdown(f"##### {get_text('database_management.table_info', 'Thông tin bảng')}: {selected_table_display}")
            st.write(f"{get_text('database_management.rows', 'Số hàng')}: {len(df)}, {get_text('database_management.columns', 'Số cột')}: {len(df.columns)}")
            
            # Hiển thị và cho phép chỉnh sửa dữ liệu
            st.markdown(f"##### {get_text('database_management.edit_data', 'Chỉnh sửa dữ liệu')}")
            
            # Giới hạn số hàng hiển thị để tránh quá tải
            rows_per_page = st.number_input(
                get_text("database_management.rows_per_page", "Số hàng mỗi trang"), 
                min_value=5, max_value=100, value=10, step=5,
                key="db_rows_per_page"
            )
            
            total_pages = (len(df) + rows_per_page - 1) // rows_per_page
            page = st.number_input(
                get_text("database_management.page_number", "Trang"),
                min_value=1, max_value=max(1, total_pages), value=1, step=1,
                key="db_page_number"
            )
            
            # Phân trang
            start_idx = (page - 1) * rows_per_page
            end_idx = min(start_idx + rows_per_page, len(df))
            
            # Hiển thị và cho phép chỉnh sửa dữ liệu trên trang hiện tại
            if len(df) > 0:
                try:
                    edited_df = st.data_editor(
                        df.iloc[start_idx:end_idx].reset_index(drop=True), 
                        key=f"editor_{selected_table}_{page}"
                    )
                    
                    if st.button(get_text("database_management.save_changes", "Lưu thay đổi"), key="db_save_changes"):
                        try:
                            # Lưu các thay đổi vào database
                            save_changes_to_db(conn, selected_table, df.iloc[start_idx:end_idx], edited_df, start_idx)
                            show_success(get_text("database_management.saved_successfully", "Đã lưu thay đổi thành công!"))
                        except Exception as e:
                            show_error(f"{get_text('database_management.save_error', 'Lỗi khi lưu thay đổi')}: {str(e)}")
                except Exception as e:
                    st.error(f"Lỗi khi hiển thị dữ liệu: {str(e)}")
            else:
                st.info(get_text("database_management.no_data", "Không có dữ liệu trong bảng này"))
    
    # Tab 2: Xuất dữ liệu
    with tab2:
        st.markdown(f"##### {get_text('database_management.export_data', 'Xuất dữ liệu')}")
        
        # Chọn bảng để xuất - hiển thị tên đã dịch
        export_table_display = st.selectbox(
            get_text("database_management.select_table_export", "Chọn bảng để xuất"),
            table_options,
            key="db_export_table"
        )
        
        # Lấy tên bảng thực tế từ tên hiển thị
        export_table = table_display_names.get(export_table_display, export_table_display)
        
        if export_table:
            # Đọc dữ liệu từ bảng đã chọn - sử dụng SELECT cụ thể thay vì SELECT *
            # Lấy danh sách các cột trong bảng
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({export_table})")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Tạo câu truy vấn SELECT với các cột cụ thể
            columns_str = ", ".join(columns)
            export_df = pd.read_sql_query(f"SELECT {columns_str} FROM {export_table}", conn)
            
            # Xem trước dữ liệu
            preview_rows = min(5, len(export_df))
            st.markdown(f"##### {get_text('database_management.preview', 'Xem trước')} {preview_rows} {get_text('database_management.first_rows', 'hàng đầu tiên')}")
            st.dataframe(export_df.head(preview_rows))
            
            # Nút xuất dữ liệu
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(get_text("database_management.export_csv", "Xuất ra CSV"), key="db_export_csv"):
                    # Xuất dữ liệu ra CSV
                    csv = export_df.to_csv(index=False).encode('utf-8')
                    
                    # Tạo tên file với timestamp
                    now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{export_table}_{now}.csv"
                    
                    # Download button
                    st.download_button(
                        label="📥 Tải xuống CSV",
                        data=csv,
                        file_name=filename,
                        mime="text/csv",
                        key="db_download_csv"
                    )
                    show_success(f"Đã xuất dữ liệu thành công. Nhấn nút tải xuống để lưu file.")
            
            with col2:
                if st.button(get_text("database_management.export_excel", "Xuất ra Excel"), key="db_export_excel"):
                    # Xuất dữ liệu ra Excel
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        export_df.to_excel(writer, index=False, sheet_name=export_table)
                    
                    # Chuẩn bị dữ liệu để tải xuống
                    excel_data = output.getvalue()
                    
                    # Tạo tên file với timestamp
                    now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{export_table}_{now}.xlsx"
                    
                    # Download button
                    st.download_button(
                        label="📥 Tải xuống Excel",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="db_download_excel"
                    )
                    show_success(f"Đã xuất dữ liệu thành công. Nhấn nút tải xuống để lưu file.")
    
    # Tab 3: Nhập dữ liệu từ file
    with tab3:
        st.markdown(f"##### {get_text('database_management.import_data', 'Nhập dữ liệu')}")
        
        # Chọn bảng để nhập dữ liệu - hiển thị tên đã dịch
        import_table_display = st.selectbox(
            get_text("database_management.select_table_import", "Chọn bảng để nhập dữ liệu"),
            table_options,
            key="db_import_table"
        )
        
        # Lấy tên bảng thực tế từ tên hiển thị
        import_table = table_display_names.get(import_table_display, import_table_display)
        
        if import_table:
            # Upload file
            uploaded_file = st.file_uploader(
                get_text("database_management.upload_file", "Tải lên file (CSV hoặc Excel)"),
                type=["csv", "xlsx"],
                key="db_upload_file"
            )
            
            if uploaded_file is not None:
                try:
                    # Đọc dữ liệu từ file
                    if uploaded_file.name.endswith('.csv'):
                        import_df = pd.read_csv(uploaded_file)
                    else:
                        import_df = pd.read_excel(uploaded_file)
                    
                    # Xem trước dữ liệu
                    st.markdown(f"##### {get_text('database_management.preview_import', 'Xem trước dữ liệu nhập')}")
                    st.dataframe(import_df.head())
                    
                    # Lấy cấu trúc bảng hiện tại để so sánh
                    table_structure = pd.read_sql_query(f"PRAGMA table_info({import_table})", conn)
                    table_columns = table_structure['name'].tolist()
                    
                    # Kiểm tra xem có cột nào khớp không
                    matching_columns = [col for col in import_df.columns if col in table_columns]
                    
                    if matching_columns:
                        # Hiển thị cột khớp
                        st.write(f"Các cột khớp: {', '.join(matching_columns)}")
                        
                        # Tùy chọn nhập
                        st.markdown(f"##### {get_text('database_management.import_options', 'Tùy chọn nhập')}")
                        import_mode = st.radio(
                            "Chọn chế độ nhập:",
                            ["append", "replace"],
                            format_func=lambda x: get_text(f"database_management.{x}", x),
                            key="db_import_mode"
                        )
                        
                        if st.button(get_text("database_management.import_button", "Nhập dữ liệu"), key="db_import_data"):
                            try:
                                # Lọc dữ liệu chỉ giữ các cột khớp
                                filtered_df = import_df[matching_columns]
                                
                                # Xử lý dữ liệu trước khi nhập (nếu cần)
                                
                                # Thực hiện nhập dữ liệu
                                if import_mode == "replace":
                                    # Xóa dữ liệu cũ
                                    cursor.execute(f"DELETE FROM {import_table}")
                                
                                # Nhập dữ liệu mới
                                filtered_df.to_sql(import_table, conn, if_exists='append', index=False)
                                conn.commit()
                                
                                show_success(f"{get_text('database_management.imported_successfully', 'Đã nhập dữ liệu thành công!')}: {len(filtered_df)}")
                            except Exception as e:
                                show_error(f"{get_text('database_management.import_error', 'Lỗi khi nhập dữ liệu')}: {str(e)}")
                    else:
                        st.error(get_text("database_management.no_matching_columns", "Không có cột nào trong file khớp với cột trong bảng"))
                
                except Exception as e:
                    st.error(f"{get_text('database_management.file_read_error', 'Lỗi khi đọc file')}: {str(e)}")
    
    # Đóng kết nối database khi hoàn tất
    conn.close()

def print_section():
    """Phần in hồ sơ"""
    st.subheader(f"🖨️ {get_text('pages.search.print_profile', 'In Hồ Sơ')}")
    
    # Kiểm tra quyền in hồ sơ
    if not is_print_allowed():
        st.error("Bạn không có quyền sử dụng chức năng in hồ sơ")
        return
    
    db = Database()
    
    st.info("""
    ℹ️ **Hướng dẫn:**
    1. Chọn loại hồ sơ (Học sinh/Cựu chiến binh)
    2. Chọn người cần in hồ sơ
    3. Xem trước thông tin trước khi in
    """)

    # Xác định loại hồ sơ người dùng có quyền in theo vai trò
    allowed_print_types = []
    allowed_search_types = get_role_based_search_types()
    
    # Xác định quyền in dựa trên quyền tìm kiếm
    if 'students' in allowed_search_types:
        allowed_print_types.append("student")
    if 'veterans' in allowed_search_types:
        allowed_print_types.append("veteran")
    
    # Nếu không có loại hồ sơ nào được phép
    if not allowed_print_types:
        st.error("Bạn không có quyền in bất kỳ loại hồ sơ nào")
        return
        
    # Chọn loại hồ sơ từ danh sách được phép
    profile_type = st.selectbox(
        "🎯 Chọn loại hồ sơ",
        allowed_print_types,
        format_func=lambda x: "Học sinh" if x == "student" else "Cựu chiến binh"
    )

    # Get list of people based on type
    if profile_type == "student":
        people = db.get_students_for_selection()
    else:
        people = db.get_veterans_for_selection()

    person_options = [f"{name} (ID: {id})" for id, name in people]

    # Select person
    selected_person = st.selectbox(
        "👤 Chọn người cần in hồ sơ",
        options=person_options,
        format_func=lambda x: x.split(" (ID: ")[0]
    )

    # Extract ID from selection
    person_id = int(selected_person.split("ID: ")[1].rstrip(")"))

    # Add tabs for different output formats
    tabs = st.tabs(["📄 Xem trước", "📊 Xuất Excel", "📊 Phân tích dữ liệu"])

    with tabs[0]:
        # Get language setting
        from translations import get_current_language
        current_language = get_current_language()
        
        # Translate button text
        button_text = "📄 Tạo hồ sơ" if current_language == 'vi' else "📄 Generate Profile"
        profile_title = "📋 Hồ sơ chi tiết" if current_language == 'vi' else "📋 Detailed Profile"
        
        if st.button(button_text):
            try:
                with st.container():
                    st.markdown("---")
                    st.subheader(profile_title)

                    # Get person details
                    if profile_type == "student":
                        query = """
                            SELECT s.id, s.full_name, s.birth_date, s.address, s.email, 
                                   s.admission_date, s.health_status, s.academic_status, 
                                   s.psychological_status, s.gender, s.phone,
                                   c.name as class_name, c.academic_year
                            FROM students s
                            LEFT JOIN classes c ON s.class_id = c.id
                            WHERE s.id = ?
                        """
                    else:
                        query = """
                            SELECT id, full_name, birth_date, address, email, 
                                   service_period, health_condition, contact_info
                            FROM veterans 
                            WHERE id = ?
                        """

                    person = db.conn.execute(query, (person_id,)).fetchone()

                    if person:
                        # Personal Information
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("##### 👤 Thông tin cá nhân")
                            st.markdown(f"**Họ và tên:** {person[1]}")
                            st.markdown(f"**Ngày sinh:** {person[2] or 'Chưa cập nhật'}")
                            st.markdown(f"**Địa chỉ:** {person[3] or 'Chưa cập nhật'}")
                            st.markdown(f"**Email:** {person[4] or 'Chưa cập nhật'}")

                            if profile_type == "student":
                                st.markdown(f"**Lớp:** {person[-2] or 'Chưa phân lớp'}")
                                st.markdown(f"**Năm học:** {person[-1] or 'Chưa cập nhật'}")
                                st.markdown(f"**Ngày nhập học:** {person[5] or 'Chưa cập nhật'}")
                            else:
                                st.markdown(f"**Thời gian phục vụ:** {person[3] or 'Chưa cập nhật'}")
                                st.markdown(f"**Liên hệ:** {person[7] or 'Chưa cập nhật'}")

                        with col2:
                            st.markdown("##### 🏥 Tình trạng")
                            if profile_type == "student":
                                st.markdown(f"**Sức khỏe:** {person[7] or 'Chưa cập nhật'}")
                                st.markdown(f"**Học tập:** {person[8] or 'Chưa đánh giá'}")
                                st.markdown(f"**Tâm lý:** {person[9] or 'Chưa đánh giá'}")
                            else:
                                st.markdown(f"**Sức khỏe:** {person[4] or 'Chưa cập nhật'}")

                        # Medical Records
                        st.markdown("---")
                        st.markdown("##### 🏥 Lịch sử y tế")
                        records = db.conn.execute("""
                            SELECT mr.id, mr.patient_id, mr.patient_type, mr.diagnosis, mr.treatment,
                                   mr.doctor_id, mr.date, mr.notes, mr.notification_sent,
                                   u.full_name as doctor_name
                            FROM medical_records mr
                            JOIN users u ON mr.doctor_id = u.id
                            WHERE mr.patient_id = ? AND mr.patient_type = ?
                            ORDER BY mr.date DESC
                        """, (person_id, profile_type)).fetchall()

                        if records:
                            for record in records:
                                with st.expander(f"🏥 Khám ngày: {record[6].split()[0]}", expanded=True):
                                    st.markdown(f"**👨‍⚕️ Bác sĩ:** {record[-1]}")
                                    st.markdown("**📋 Chẩn đoán:**")
                                    st.info(record[3])
                                    st.markdown("**💊 Điều trị:**")
                                    st.info(record[4])
                                    if record[7]:  # notes
                                        st.markdown("**📝 Ghi chú:**")
                                        st.info(record[7])
                        else:
                            st.info("Chưa có hồ sơ y tế")

                        # Psychological Evaluations (only for students)
                        if profile_type == "student":
                            st.markdown("---")
                            st.markdown("##### 🧠 Đánh giá tâm lý")
                            evals = db.conn.execute("""
                                SELECT pe.id, pe.student_id, pe.evaluation_date, pe.evaluator_id, 
                                       pe.assessment, pe.recommendations, pe.follow_up_date,
                                       pe.notification_sent, u.full_name as evaluator_name
                                FROM psychological_evaluations pe
                                JOIN users u ON pe.evaluator_id = u.id
                                WHERE pe.student_id = ?
                                ORDER BY pe.evaluation_date DESC
                            """, (person_id,)).fetchall()

                            if evals:
                                for eval in evals:
                                    with st.expander(f"📝 Đánh giá ngày: {eval[2].split()[0]}", expanded=True):
                                        st.markdown(f"**👤 Người đánh giá:** {eval[-1]}")
                                        st.markdown("**📋 Đánh giá:**")
                                        st.info(eval[4])
                                        st.markdown("**💡 Khuyến nghị:**")
                                        st.info(eval[5])
                                        if eval[6]:  # follow_up_date
                                            st.markdown(f"**📅 Ngày theo dõi tiếp:** {eval[6]}")
                            else:
                                st.info("Chưa có đánh giá tâm lý")

                        # Print instructions
                        st.markdown("---")
                        st.markdown("""
                        ℹ️ **Hướng dẫn in:**
                        1. Nhấn Ctrl + P (Windows) hoặc Command + P (Mac)
                        2. Chọn máy in hoặc lưu thành PDF
                        3. Điều chỉnh cài đặt in nếu cần
                        """)
                    else:
                        st.error("❌ Không tìm thấy thông tin")

            except Exception as e:
                st.error(f"❌ Lỗi khi tải dữ liệu: {str(e)}")
                print(f"Database error: {str(e)}")

    with tabs[1]:
        # Get language setting
        from translations import get_current_language
        current_language = get_current_language()
        
        # Translate texts
        if current_language == 'vi':
            excel_info = "📊 Xuất dữ liệu sang file Excel"
            options_title = "##### Tùy chọn xuất Excel"
            medical_option = "🏥 Bao gồm hồ sơ y tế"
            psych_option = "🧠 Bao gồm đánh giá tâm lý"
            submit_button = "📥 Tạo file Excel"
        else:
            excel_info = "📊 Export data to Excel file"
            options_title = "##### Excel Export Options"
            medical_option = "🏥 Include medical records"
            psych_option = "🧠 Include psychological evaluations"
            submit_button = "📥 Generate Excel File"
            
        st.info(excel_info)

        # Excel export options
        with st.form("excel_export_options"):
            st.write(options_title)
            include_medical = st.checkbox(medical_option, value=True)
            if profile_type == "student":
                include_psych = st.checkbox(psych_option, value=True)

            generate_clicked = st.form_submit_button(submit_button)
        
        # Tạo file Excel và nút tải xuống ở ngoài form
        if 'generate_clicked' in locals() and generate_clicked:
            try:
                excel_data = export_to_excel(db, profile_type, person_id)
                if excel_data:
                    # Create download button for Excel file
                    # Get language for label and success message
                    if current_language == 'vi':
                        download_label = "⬇️ Tải file Excel"
                        success_msg = "✅ File Excel đã được tạo thành công!"
                    else:
                        download_label = "⬇️ Download Excel File"
                        success_msg = "✅ Excel file created successfully!"
                    
                    filename = f"ho_so_{person_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    st.download_button(
                        label=download_label,
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success(success_msg)
                else:
                    st.error("❌ Không thể tạo file Excel")
            except Exception as e:
                st.error(f"❌ Lỗi khi tạo file Excel: {str(e)}")

    with tabs[2]:
        # Get language setting
        from translations import get_current_language
        current_language = get_current_language()
        
        # Translate texts based on current language
        if current_language == 'vi':
            tab_title = "📊 Phân tích dữ liệu"
            academic_section = "##### 📚 Tiến độ học tập"
            no_academic_data = "Chưa có dữ liệu đánh giá học tập"
            health_section = "##### 🏥 Theo dõi sức khỏe"
            chart_title = 'Lịch sử khám bệnh theo thời gian'
            chart_series = 'Lịch sử khám'
            chart_x_title = 'Thời gian'
            chart_y_title = 'Số lần khám'
            stats_section = "##### 📊 Thống kê" 
            total_visits = "Tổng số lần khám"
            monitoring_period = "Thời gian theo dõi"
            days_unit = "ngày"
            last_visit = "Lần khám gần nhất"
            days_ago = "ngày trước"
            no_medical_data = "Chưa có dữ liệu khám bệnh"
        else:
            tab_title = "📊 Data Analysis"
            academic_section = "##### 📚 Academic Progress"
            no_academic_data = "No academic evaluation data available"
            health_section = "##### 🏥 Health Monitoring"
            chart_title = 'Medical History Timeline'
            chart_series = 'Medical History'
            chart_x_title = 'Time'
            chart_y_title = 'Number of Visits'
            stats_section = "##### 📊 Statistics"
            total_visits = "Total Visits"
            monitoring_period = "Monitoring Period"
            days_unit = "days"
            last_visit = "Last Visit"
            days_ago = "days ago"
            no_medical_data = "No medical data available"
        
        st.subheader(tab_title)

        if profile_type == "student":
            # Academic Performance Timeline
            st.markdown(academic_section)
            academic_records = db.conn.execute("""
                SELECT evaluation_date, assessment, recommendations
                FROM psychological_evaluations
                WHERE student_id = ?
                ORDER BY evaluation_date
            """, (person_id,)).fetchall()

            if academic_records:
                df_academic = pd.DataFrame(academic_records, 
                    columns=['date', 'assessment', 'recommendations'])
                df_academic['date'] = pd.to_datetime(df_academic['date'])

                st.line_chart(df_academic.set_index('date'))
            else:
                st.info(no_academic_data)

        # Health Status Timeline
        st.markdown(health_section)
        medical_records = db.conn.execute("""
            SELECT date, diagnosis, treatment
            FROM medical_records
            WHERE patient_id = ? AND patient_type = ?
            ORDER BY date
        """, (person_id, profile_type)).fetchall()

        if medical_records:
            df_medical = pd.DataFrame(medical_records,
                columns=['date', 'diagnosis', 'treatment'])
            df_medical['date'] = pd.to_datetime(df_medical['date'])

            # Create a timeline visualization
            medical_fig = go.Figure()
            medical_fig.add_trace(go.Scatter(
                x=df_medical['date'],
                y=list(range(len(df_medical))),
                mode='lines+markers',
                name=chart_series
            ))
            medical_fig.update_layout(
                title=chart_title,
                xaxis_title=chart_x_title,
                yaxis_title=chart_y_title
            )
            st.plotly_chart(medical_fig)

            # Display statistics
            st.markdown(stats_section)
            col1, col2 = st.columns(2)
            with col1:
                st.metric(total_visits, len(medical_records))
                st.metric(monitoring_period, 
                    f"{(df_medical['date'].max() - df_medical['date'].min()).days} {days_unit}")
            with col2:
                recent_visit = df_medical['date'].max()
                days_since_visit = (pd.Timestamp.now() - recent_visit).days
                st.metric(last_visit, 
                    recent_visit.strftime('%d/%m/%Y'),
                    f"{days_since_visit} {days_ago}")
        else:
            st.info(no_medical_data)

def render():
    """Main render function"""
    # Apply theme from session state
    apply_theme()
    
    # Set current page for role checking
    st.session_state.current_page = "05_Tim_kiem_va_In"
    
    check_auth()
    
    st.title(f"🔍 {get_text('pages.search.title', 'Tìm kiếm & In hồ sơ')}")
    
    # Tạo các tab chính
    tabs = st.tabs([
        f"🔍 {get_text('pages.search.search_tab', 'Tìm kiếm')}", 
        f"🖨️ {get_text('pages.search.print_tab', 'In hồ sơ')}",
        f"🗄️ {get_text('database_management.title', 'Quản lý Database')}"
    ])
    
    with tabs[0]:
        search_section()
    
    with tabs[1]:
        print_section()
        
    with tabs[2]:
        database_section()

if __name__ == "__main__":
    render()