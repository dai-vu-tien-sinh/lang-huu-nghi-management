import streamlit as st
from auth import check_auth, check_role
from database import Database
from utils import show_success, show_error, apply_theme
from datetime import datetime
from translations import get_text

def render():
    # Apply theme from session state
    apply_theme()

    # Set current page for role checking
    st.session_state.current_page = "02_Y_te"

    check_auth()
    # Add nurse to allowed roles
    check_role(['doctor', 'family', 'nurse'])

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
                key="filter_patient_type"
            )
        with col2:
            patient_filter = st.text_input(get_text("healthcare.search_name", "🔍 Tìm theo tên"))
        with col3:
            date_range = st.date_input(
                get_text("healthcare.date_range", "📅 Khoảng thời gian"),
                value=(datetime.now().date(), datetime.now().date())
            )

        try:
            # Build query based on filters
            query = """
                SELECT mr.*, 
                    u.full_name as doctor_name,
                    CASE 
                        WHEN mr.patient_type = 'student' THEN s.full_name
                        WHEN mr.patient_type = 'veteran' THEN v.full_name
                    END as patient_name,
                    CASE 
                        WHEN mr.patient_type = 'student' THEN s.email
                        WHEN mr.patient_type = 'veteran' THEN v.email
                    END as patient_email
                FROM medical_records mr
                JOIN users u ON mr.doctor_id = u.id
                LEFT JOIN students s ON mr.patient_id = s.id AND mr.patient_type = 'student'
                LEFT JOIN veterans v ON mr.patient_id = v.id AND mr.patient_type = 'veteran'
                WHERE 1=1
            """
            params = []

            if patient_type != "Tất cả":
                query += " AND mr.patient_type = ?"
                params.append("student" if patient_type == "Sinh viên" else "veteran")

            if patient_filter:
                query += """ AND (
                    (mr.patient_type = 'student' AND s.full_name LIKE ?) OR
                    (mr.patient_type = 'veteran' AND v.full_name LIKE ?)
                )"""
                params.extend([f"%{patient_filter}%"] * 2)

            if len(date_range) == 2:
                query += " AND date(mr.date) BETWEEN ? AND ?"
                params.extend([date_range[0], date_range[1]])

            query += " ORDER BY mr.date DESC"
            records = db.conn.execute(query, params).fetchall()

            if records:
                for record in records:
                    with st.expander(f"{get_text('healthcare.record', '🏥 Hồ sơ')}: {record[-2]} - {record[6].split()[0]}", expanded=False):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**{get_text('healthcare.date', '🗓️ Ngày khám')}:** {record[6]}")
                            st.markdown(f"**{get_text('healthcare.doctor', '👨‍⚕️ Bác sĩ')}:** {record[-3]}")
                            patient_type_text = get_text('healthcare.student', 'Sinh viên') if record[2] == 'student' else get_text('healthcare.veteran', 'Cựu chiến binh')
                            st.markdown(f"**{get_text('healthcare.patient_type_label', '👤 Loại bệnh nhân')}:** {patient_type_text}")

                        with col2:
                            st.markdown(f"**{get_text('healthcare.diagnosis', '📋 Chẩn đoán')}:**")
                            st.info(record[3])
                            st.markdown(f"**{get_text('healthcare.treatment', '💊 Điều trị')}:**")
                            st.info(record[4])

                        if record[7]:  # If there are notes
                            st.markdown(f"**{get_text('healthcare.notes', '📝 Ghi chú')}:**")
                            st.info(record[7])

                        # Email notification section
                        st.markdown(get_text('healthcare.email_section', '---'))
                        if record[-1]:  # If patient has email
                            col3, col4 = st.columns([3, 1])
                            with col3:
                                if not record[8]:  # If notification not sent
                                    st.warning(get_text('healthcare.notification_pending', '⏳ Chưa gửi thông báo'))
                                else:
                                    st.success(get_text('healthcare.notification_sent', '✉️ Đã gửi thông báo'))
                            with col4:
                                if not record[8]:
                                    if st.button(get_text('healthcare.send_notification', '📤 Gửi thông báo'), key=f"notify_{record[0]}"):
                                        if db.send_medical_record_notification(record[0]):
                                            show_success(get_text('healthcare.notification_success', 'Đã gửi thông báo thành công!'))
                                            st.rerun()
                                        else:
                                            show_error(get_text('healthcare.notification_error', 'Không thể gửi thông báo'))
                        else:
                            st.error(get_text('healthcare.no_email', '❌ Không có email bệnh nhân'))
            else:
                st.info(get_text('healthcare.no_records', '🔍 Không tìm thấy hồ sơ y tế nào phù hợp với bộ lọc'))

        except Exception as e:
            st.error(f"{get_text('healthcare.load_error', '❌ Lỗi khi tải dữ liệu')}: {str(e)}")
            print(f"Database error: {str(e)}")

    with tab2:
        st.info(get_text('healthcare.instructions', """
        ℹ️ **Hướng dẫn:**
        1. Chọn loại bệnh nhân (Sinh viên/Cựu chiến binh)
        2. Chọn tên bệnh nhân từ danh sách
        3. Điền thông tin chẩn đoán và điều trị
        4. Thêm ghi chú nếu cần
        5. Tùy chọn gửi thông báo qua email
        """))

        with st.form("add_medical_record", clear_on_submit=True):
            st.subheader(get_text('healthcare.exam_info', "Thông tin khám bệnh"))

            col1, col2 = st.columns(2)
            with col1:
                patient_type = st.selectbox(
                    get_text('healthcare.patient_type', "🏥 Loại bệnh nhân"),
                    ["student", "veteran"],
                    format_func=lambda x: get_text('healthcare.student', "Sinh viên") if x == "student" else get_text('healthcare.veteran', "Cựu chiến binh")
                )

                # Get list of patients based on type
                if patient_type == "student":
                    patients = db.get_students_for_selection()
                else:
                    patients = db.get_veterans_for_selection()

                patient_options = [f"{name} (ID: {id})" for id, name in patients]
                selected_patient = st.selectbox(
                    get_text('healthcare.select_patient', "👤 Chọn bệnh nhân"),
                    options=patient_options,
                    format_func=lambda x: x.split(" (ID: ")[0]
                )

            with col2:
                send_notification = st.checkbox(get_text('healthcare.send_email', "📧 Gửi thông báo email"), value=True)
                st.write("")  # Spacing

            # Extract patient ID from selection
            patient_id = int(selected_patient.split("ID: ")[1].rstrip(")"))

            diagnosis = st.text_area(
                get_text('healthcare.diagnosis', "📋 Chẩn đoán"),
                height=100,
                placeholder=get_text('healthcare.diagnosis_placeholder', "Nhập kết quả chẩn đoán chi tiết...")
            )

            treatment = st.text_area(
                get_text('healthcare.treatment', "💊 Điều trị"),
                height=100,
                placeholder=get_text('healthcare.treatment_placeholder', "Nhập phương pháp điều trị và đơn thuốc...")
            )

            notes = st.text_area(
                get_text('healthcare.notes', "📝 Ghi chú thêm"),
                height=100,
                placeholder=get_text('healthcare.notes_placeholder', "Nhập các ghi chú bổ sung nếu cần...")
            )

            if st.form_submit_button(get_text('healthcare.add_record_button', "✅ Thêm hồ sơ")):
                try:
                    record = {
                        "patient_id": patient_id,
                        "patient_type": patient_type,
                        "diagnosis": diagnosis,
                        "treatment": treatment,
                        "doctor_id": st.session_state.user.id,
                        "notes": notes
                    }
                    record_id = db.add_medical_record(record)

                    if record_id:
                        show_success(get_text('healthcare.add_success', "✨ Thêm hồ sơ y tế thành công!"))
                        if send_notification:
                            if db.send_medical_record_notification(record_id):
                                show_success(get_text('healthcare.notification_success', "📤 Đã gửi thông báo thành công!"))
                            else:
                                show_error(get_text('healthcare.notification_error', "❌ Không thể gửi thông báo"))
                        st.rerun()
                except Exception as e:
                    show_error(f"{get_text('healthcare.add_error', '❌ Lỗi khi thêm hồ sơ y tế')}: {str(e)}")

if __name__ == "__main__":
    render()