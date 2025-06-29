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
    st.session_state.current_page = "03_Tam_ly"

    check_auth()
    # Allow both counselor, admin and family roles
    check_role(['counselor', 'admin', 'family'])

    st.title(get_text("pages.psychology.title", "Psychological Assessment"))

    db = Database()

    tab1, tab2 = st.tabs([
        f"📋 {get_text('pages.psychology.view_tab', 'View Assessments')}", 
        f"➕ {get_text('pages.psychology.add_tab', 'Add Assessment')}"
    ])

    with tab1:
        # Add filters
        st.subheader(get_text("common.filters", "Bộ lọc"))
        col1, col2 = st.columns(2)
        with col1:
            student_filter = st.text_input(get_text("pages.psychology.search_student", "🔍 Search by student name"))
        with col2:
            date_range = st.date_input(
                get_text("common.date_range", "📅 Khoảng thời gian"),
                value=(datetime.now().date(), datetime.now().date())
            )

        try:
            # Build query based on filters
            query = """
                SELECT pe.*, u.full_name as evaluator_name, s.full_name as student_name, s.email, s.id as student_id
                FROM psychological_evaluations pe
                JOIN users u ON pe.evaluator_id = u.id
                JOIN students s ON pe.student_id = s.id
                WHERE 1=1
            """
            params = []

            # For family users, only show their student's evaluations
            if st.session_state.user.role == 'family':
                query += " AND s.id = ?"
                params.append(st.session_state.user.family_student_id)

            if student_filter:
                query += " AND s.full_name LIKE ?"
                params.append(f"%{student_filter}%")

            if len(date_range) == 2:
                query += " AND date(pe.evaluation_date) BETWEEN ? AND ?"
                params.extend([date_range[0], date_range[1]])

            # Đầu tiên sắp xếp theo học sinh, sau đó theo ngày đánh giá (mới nhất lên đầu)
            query += " ORDER BY s.full_name, pe.evaluation_date DESC"

            evaluations = db.conn.execute(query, params).fetchall()

            if evaluations:
                # Nhóm các đánh giá theo học sinh
                evaluations_by_student = {}
                for eval in evaluations:
                    student_name = eval[-3]  # Tên học sinh
                    student_id = eval[-1]    # ID học sinh
                    
                    if student_id not in evaluations_by_student:
                        evaluations_by_student[student_id] = {
                            'name': student_name,
                            'evaluations': []
                        }
                    
                    evaluations_by_student[student_id]['evaluations'].append(eval)
                
                # Hiển thị đánh giá theo từng học sinh
                for student_id, data in evaluations_by_student.items():
                    student_name = data['name']
                    student_evals = data['evaluations']
                    
                    st.write(f"### 👤 {student_name}")
                    
                    for eval in student_evals:
                        with st.expander(f"📝 Đánh giá ngày: {eval[2].split()[0]}", expanded=False):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown(f"**🗓️ Ngày đánh giá:** {eval[2]}")
                                st.markdown(f"**👤 Người đánh giá:** {eval[-2]}")
                                if eval[6]:  # follow_up_date
                                    st.markdown(f"**📅 Ngày theo dõi tiếp:** {eval[6]}")

                            with col2:
                                st.markdown("**📋 Đánh giá:**")
                                st.info(eval[4])
                                st.markdown("**💡 Khuyến nghị:**")
                                st.info(eval[5])

                            # Email notification section (only show for non-family users)
                            if st.session_state.user.role != 'family':
                                st.markdown("---")
                                if eval[-2]:  # If student has email (check student_name position)
                                    col3, col4 = st.columns([3, 1])
                                    with col3:
                                        if not eval[7]:  # If notification not sent
                                            st.warning("⏳ Chưa gửi thông báo")
                                        else:
                                            st.success("✉️ Đã gửi thông báo")
                                    with col4:
                                        if not eval[7]:
                                            if st.button("📤 Gửi thông báo", key=f"notify_{eval[0]}"):
                                                if db.send_psychological_evaluation_notification(eval[0]):
                                                    show_success("Đã gửi thông báo thành công!")
                                                    st.rerun()
                                                else:
                                                    show_error("Không thể gửi thông báo")
                                else:
                                    st.error("❌ Không có email học sinh")
            else:
                st.info(get_text("pages.psychology.no_evaluations_found", "🔍 No psychological evaluations found matching the filters"))

        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu: {str(e)}")
            print(f"Database error: {str(e)}")

    # Only show add evaluation tab for counselor and admin
    if st.session_state.user.role in ['counselor', 'admin']:
        with tab2:
            st.info(get_text("pages.psychology.instructions", """
            ℹ️ **Instructions:**
            1. Select student to evaluate
            2. Fill in assessment and recommendations
            3. Select follow-up date (if needed)
            4. Optionally send email notification
            """))

            with st.form("add_psychological_evaluation", clear_on_submit=True):
                st.subheader(get_text("pages.psychology.evaluation_info", "Evaluation Information"))

                # Get list of students for selection
                students = db.get_students_for_selection()
                student_options = [f"{name} (ID: {id})" for id, name in students]

                col1, col2 = st.columns(2)
                with col1:
                    selected_student = st.selectbox(
                        get_text("pages.psychology.select_student", "🎓 Select Student"),
                        options=student_options,
                        format_func=lambda x: x.split(" (ID: ")[0]
                    )
                    follow_up_date = st.date_input(get_text("pages.psychology.follow_up_date", "📅 Follow-up Date"))
                with col2:
                    send_notification = st.checkbox(get_text("common.send_email_notification", "📧 Gửi thông báo email"), value=True)
                    st.write("") # Spacing

                # Extract student ID from selection
                student_id = int(selected_student.split("ID: ")[1].rstrip(")"))

                assessment = st.text_area(get_text("pages.psychology.assessment", "📝 Assessment"), height=100,
                    placeholder=get_text("pages.psychology.assessment_placeholder", "Enter detailed assessment of the student's psychological state..."))

                recommendations = st.text_area(get_text("pages.psychology.recommendations", "💡 Recommendations"), height=100,
                    placeholder=get_text("pages.psychology.recommendations_placeholder", "Enter specific recommendations and guidance..."))

                if st.form_submit_button(get_text("pages.psychology.add_evaluation", "✅ Add Evaluation")):
                    try:
                        eval_data = {
                            "student_id": student_id,
                            "evaluator_id": st.session_state.user.id,
                            "assessment": assessment,
                            "recommendations": recommendations,
                            "follow_up_date": follow_up_date,
                        }
                        eval_id = db.add_psychological_evaluation(eval_data)

                        if eval_id:
                            show_success("✨ Thêm đánh giá tâm lý thành công!")
                            if send_notification:
                                if db.send_psychological_evaluation_notification(eval_id):
                                    show_success("📤 Đã gửi thông báo thành công!")
                                else:
                                    show_error("❌ Không thể gửi thông báo")
                            st.rerun()
                    except Exception as e:
                        show_error(f"❌ Lỗi khi thêm đánh giá: {str(e)}")
    else:
        with tab2:
            st.warning(get_text("pages.psychology.add_permission_denied", "⚠️ You don't have permission to add new psychological evaluations"))

if __name__ == "__main__":
    render()