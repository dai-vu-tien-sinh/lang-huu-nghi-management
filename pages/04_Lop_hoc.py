import streamlit as st 
import pandas as pd
from database import Database
from auth import check_auth, check_role, check_student_access, can_edit_student_info
from utils import show_success, show_error, apply_theme
from datetime import datetime, timedelta
from translations import get_text

def render():
    # Apply theme from session state
    apply_theme()

    # Set current page for role checking
    st.session_state.current_page = "04_Lop_hoc"

    check_auth()

    # Allow access for family users and other relevant roles
    check_role(['admin', 'teacher', 'family'])

    st.title(get_text("pages.classes.title", "Thông Tin Lớp Học"))

    db = Database()

    # Get current user's role and access level
    user_role = st.session_state.user.role
    family_student_id = st.session_state.user.family_student_id if user_role == 'family' else None

    # Add new class button (only for admin and teachers)
    if user_role in ['admin', 'teacher'] and st.button(get_text("pages.classes.add_new_class", "➕ Thêm Lớp Mới")):
        st.session_state.adding_new_class = True

    # Form to add new class
    if user_role in ['admin', 'teacher'] and st.session_state.get('adding_new_class', False):
        with st.form("add_class_form"):
            st.subheader(get_text("pages.classes.add_class_title", "Thêm Lớp Mới"))

            # Get list of teachers
            teachers = db.get_teachers()
            teacher_options = [f"{t.full_name} (ID: {t.id})" for t in teachers]

            class_name = st.text_input(get_text("pages.classes.class_name", "Tên lớp"), key=f"new_class_name")
            teacher = st.selectbox(
                get_text("pages.classes.teacher", "Giáo viên chủ nhiệm"),
                options=teacher_options,
                format_func=lambda x: x.split(" (ID: ")[0],
                key=f"new_class_teacher"
            )
            academic_year = st.text_input(get_text("pages.classes.academic_year", "Năm học"), key=f"new_class_year")
            notes = st.text_area(get_text("pages.classes.notes", "Ghi chú"), key=f"new_class_notes")

            if st.form_submit_button(get_text("pages.classes.add_class_button", "Thêm lớp")):
                try:
                    teacher_id = int(teacher.split("ID: ")[1].rstrip(")"))
                    class_data = {
                        "name": class_name,
                        "teacher_id": teacher_id,
                        "academic_year": academic_year,
                        "notes": notes
                    }
                    if db.add_class(class_data):
                        show_success(get_text("pages.classes.add_success", "Thêm lớp mới thành công!"))
                        st.session_state.adding_new_class = False
                        st.rerun()
                    else:
                        show_error(get_text("pages.classes.add_error", "Không thể thêm lớp mới"))
                except Exception as e:
                    show_error(f"Lỗi: {str(e)}")

    if user_role == 'family':
        # For family users, only show their student's class
        student = db.get_students(user_role=user_role, family_student_id=family_student_id)[0]
        class_id = student.class_id
        classes = [db.get_class(class_id)] if class_id else []
    else:
        # For other users, show all classes
        classes = db.get_classes()

    if not classes:
        st.warning(get_text("pages.classes.no_class_info", "Không có thông tin lớp học."))
        return

    # Display class information
    for class_info in classes:
        with st.expander(f"🏫 {class_info.name} - Năm học {class_info.academic_year}", expanded=True):
            tabs = st.tabs([
                get_text("pages.classes.general_info", "Thông tin chung"), 
                get_text("pages.classes.student_list", "Danh sách học sinh"), 
                get_text("pages.classes.academic_history", "Lịch sử học tập")
            ])

            # Tab Thông tin chung
            with tabs[0]:
                # Teacher information
                teacher = db.get_user_by_id(class_info.teacher_id)

                # Edit class button (only for admin and teachers)
                if user_role in ['admin', 'teacher']:
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button(get_text("pages.classes.edit_class", "✏️ Chỉnh sửa"), key=f"edit_{class_info.id}"):
                            st.session_state[f'editing_class_{class_info.id}'] = True

                # Edit class form
                if user_role in ['admin', 'teacher'] and st.session_state.get(f'editing_class_{class_info.id}', False):
                    with st.form(f"edit_class_{class_info.id}"):
                        st.subheader("Chỉnh sửa thông tin lớp")

                        # Get list of teachers
                        teachers = db.get_teachers()
                        teacher_options = [f"{t.full_name} (ID: {t.id})" for t in teachers]
                        current_teacher = f"{teacher.full_name} (ID: {teacher.id})"

                        new_name = st.text_input("Tên lớp", value=class_info.name, key=f"edit_name_{class_info.id}")
                        new_teacher = st.selectbox(
                            "Giáo viên chủ nhiệm",
                            options=teacher_options,
                            index=teacher_options.index(current_teacher),
                            key=f"edit_teacher_{class_info.id}"
                        )
                        new_academic_year = st.text_input("Năm học", value=class_info.academic_year, key=f"edit_year_{class_info.id}")
                        new_notes = st.text_area("Ghi chú", value=class_info.notes, key=f"edit_notes_{class_info.id}")

                        if st.form_submit_button("Lưu thay đổi"):
                            try:
                                teacher_id = int(new_teacher.split("ID: ")[1].rstrip(")"))
                                class_data = {
                                    "name": new_name,
                                    "teacher_id": teacher_id,
                                    "academic_year": new_academic_year,
                                    "notes": new_notes
                                }
                                if db.update_class(class_info.id, class_data):
                                    show_success("Cập nhật thông tin lớp thành công!")
                                    st.session_state[f'editing_class_{class_info.id}'] = False
                                    st.rerun()
                                else:
                                    show_error("Không thể cập nhật thông tin lớp")
                            except Exception as e:
                                show_error(f"Lỗi: {str(e)}")

                # Display current teacher info
                st.subheader("👨‍🏫 Giáo viên chủ nhiệm")
                st.write(f"Họ và tên: {teacher.full_name}")
                st.write(f"Email: {teacher.email if teacher.email else 'Chưa cập nhật'}")

            # Tab Danh sách học sinh
            with tabs[1]:
                students = db.get_students_by_class(class_info.id)

                if not students:
                    st.info("Chưa có học sinh trong lớp")
                    if user_role in ['admin', 'teacher']:
                        if st.button("➕ Thêm học sinh", key=f"add_student_{class_info.id}"):
                            st.session_state[f'adding_student_{class_info.id}'] = True

                # Form to add student to class
                if user_role in ['admin', 'teacher'] and st.session_state.get(f'adding_student_{class_info.id}', False):
                    st.subheader("Thêm học sinh vào lớp")
                    # Get list of unassigned students
                    all_students = db.get_students()
                    unassigned_students = [s for s in all_students if not s.class_id]
                    student_options = [f"{s.full_name} (ID: {s.id})" for s in unassigned_students]

                    if student_options:
                        selected_student = st.selectbox(
                            "Chọn học sinh",
                            options=student_options,
                            format_func=lambda x: x.split(" (ID: ")[0]
                        )

                        if st.button("Thêm vào lớp"):
                            try:
                                student_id = int(selected_student.split("ID: ")[1].rstrip(")"))
                                if db.update_student_class(student_id, class_info.id):
                                    show_success("Thêm học sinh vào lớp thành công!")
                                    st.session_state[f'adding_student_{class_info.id}'] = False
                                    st.rerun()
                                else:
                                    show_error("Không thể thêm học sinh vào lớp")
                            except Exception as e:
                                show_error(f"Lỗi: {str(e)}")
                    else:
                        st.info("Không có học sinh chưa được phân lớp")

                # Display student list in a table format
                if students:
                    student_data = []
                    for student in students:
                        # Only include student in list if user has access
                        if check_student_access(student.id):
                            student_data.append({
                                "Họ và tên": student.full_name,
                                "Tình trạng học tập": student.academic_status,
                                "Tình trạng sức khỏe": student.health_status,
                                "Email": student.email,
                            })

                    if student_data:
                        # Display student table
                        st.table(pd.DataFrame(student_data))

                        # Add remove student buttons
                        if user_role in ['admin', 'teacher']:
                            st.write("##### Xóa học sinh khỏi lớp")
                            for student in students:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(student.full_name)
                                with col2:
                                    if st.button("❌", key=f"remove_{student.id}"):
                                        if db.update_student_class(student.id, None):
                                            show_success("Đã xóa học sinh khỏi lớp!")
                                            st.rerun()
                                        else:
                                            show_error("Không thể xóa học sinh khỏi lớp")
                    else:
                        st.info("Không có quyền xem thông tin học sinh trong lớp này")

            # Tab Lịch sử học tập
            with tabs[2]:
                if user_role in ['admin', 'teacher']:
                    st.markdown("### 📚 Lịch sử học tập")

                    # Search filters
                    st.markdown("#### 🔍 Bộ lọc tìm kiếm")
                    col1, col2 = st.columns(2)
                    with col1:
                        search_name = st.text_input("Tên học sinh", key=f"search_student_name_history_class_{class_info.id}")
                    with col2:
                        use_date_filter = st.checkbox("Lọc theo thời gian", key=f"date_filter_history_class_{class_info.id}")
                        if use_date_filter:
                            date_range = st.date_input(
                                "Khoảng thời gian",
                                value=(datetime.now() - timedelta(days=365), datetime.now()),
                                key=f"date_range_history_class_{class_info.id}"
                            )

                    students = db.get_students_by_class(class_info.id)

                    # Search history
                    history_filters = {}
                    if search_name:
                        history_filters['student_name'] = search_name
                    if use_date_filter and len(date_range) == 2:
                        history_filters['from_date'] = date_range[0].isoformat()
                        history_filters['to_date'] = date_range[1].isoformat()

                    # Display history for each student
                    for student in students:
                        if check_student_access(student.id):
                            st.markdown(f"#### 📋 {student.full_name}")
                            history = db.search_student_class_history(
                                student_id=student.id,
                                **history_filters
                            )
                            if history:
                                history_data = pd.DataFrame(history)
                                st.table(history_data)
                            else:
                                st.info("Không tìm thấy lịch sử lớp học phù hợp")

if __name__ == "__main__":
    render()