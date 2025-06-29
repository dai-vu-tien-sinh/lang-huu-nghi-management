import streamlit as st
from auth import check_auth, check_role
from database import Database
from reports import ReportGenerator
from utils import show_success, show_error, apply_theme
from translations import get_text

def render():
    # Apply theme from session state
    apply_theme()

    check_auth()
    check_role(['admin'])

    st.title(get_text("admin.title", "Bảng Điều Khiển Quản Trị"))

    db = Database()
    report_gen = ReportGenerator()

    tab1, tab2, tab3, tab4 = st.tabs([
        get_text("admin.user_management", "Quản Lý Người Dùng"),
        get_text("admin.interface_customization", "Tùy Chỉnh Giao Diện"),
        get_text("admin.reports", "Báo Cáo"),
        get_text("admin.system_statistics", "Thống Kê Hệ Thống")
    ])

    with tab1:
        st.subheader(get_text("admin.add_user", "Thêm Người Dùng Mới"))
        with st.form("add_user"):
            username = st.text_input(get_text("admin.username", "Tên đăng nhập"))
            password = st.text_input(get_text("admin.password", "Mật khẩu"), type="password")
            role = st.selectbox(get_text("admin.role", "Vai trò"), [
                "admin", "doctor", "teacher", "counselor",
                "administrative", "nurse", "family"
            ])
            full_name = st.text_input(get_text("admin.full_name", "Họ và tên"))

            # Show student selection for family role
            if role == "family":
                students = db.get_students()
                student_options = [f"{s.id} - {s.full_name}" for s in students]
                student_selection = st.selectbox(
                    get_text("admin.select_student", "Chọn học sinh"),
                    [""] + student_options,
                    format_func=lambda x: x.split(" - ")[1] if x else get_text("admin.select_student", "Chọn học sinh")
                )
                student_id = int(student_selection.split(" - ")[0]) if student_selection else None
            else:
                student_id = None

            if st.form_submit_button(get_text("admin.add_user_button", "Thêm người dùng")):
                if db.add_user(username, password, role, full_name, family_student_id=student_id):
                    show_success(get_text("admin.add_success", "Thêm người dùng thành công!"))
                else:
                    show_error(get_text("admin.username_exists", "Tên đăng nhập đã tồn tại"))

    with tab2:
        st.subheader(get_text("admin.customize_sidebar", "Tùy Chỉnh Thanh Menu"))

        # Get current user's preferences
        prefs = db.get_user_sidebar_preferences(st.session_state.user.id)
        available_pages = db.get_available_pages(st.session_state.user.role)

        # Group pages by category
        pages_by_group = {}
        for page in available_pages:
            group = page['group']
            if group not in pages_by_group:
                pages_by_group[group] = []
            pages_by_group[group].append(page)

        st.write(get_text("admin.drag_drop", "Kéo và thả để sắp xếp lại thứ tự các trang:"))

        # Initialize session state for drag and drop
        if 'page_order' not in st.session_state:
            st.session_state.page_order = (
                prefs.page_order if prefs else [p['id'] for p in available_pages]
            )

        if 'hidden_pages' not in st.session_state:
            st.session_state.hidden_pages = (
                prefs.hidden_pages if prefs else []
            )

        # Create sections for each group
        for group, pages in pages_by_group.items():
            st.markdown(f"### {group}")
            for page in pages:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(page['name'])
                with col2:
                    visible = page['id'] not in st.session_state.hidden_pages
                    if st.checkbox(get_text("admin.show", "Hiển thị"), value=visible, key=f"visible_{page['id']}"):
                        if page['id'] in st.session_state.hidden_pages:
                            st.session_state.hidden_pages.remove(page['id'])
                    else:
                        if page['id'] not in st.session_state.hidden_pages:
                            st.session_state.hidden_pages.append(page['id'])

        if st.button(get_text("admin.save_customization", "Lưu Tùy Chỉnh")):
            if db.save_user_sidebar_preferences(
                st.session_state.user.id,
                st.session_state.page_order,
                st.session_state.hidden_pages
            ):
                show_success(get_text("admin.save_success", "Đã lưu tùy chỉnh thành công!"))
                st.rerun()
            else:
                show_error(get_text("admin.save_error", "Không thể lưu tùy chỉnh"))

    with tab3:
        st.subheader(get_text("admin.create_report", "Tạo Báo Cáo"))
        report_type = st.selectbox(get_text("admin.report_type", "Loại báo cáo"), ["students", "veterans"])
        if st.button(get_text("admin.generate_pdf", "Tạo báo cáo PDF")):
            pdf_bytes = report_gen.generate_pdf_summary(report_type)
            st.download_button(
                label=get_text("admin.download_report", "Tải xuống báo cáo"),
                data=pdf_bytes,
                file_name=f"{report_type}_report.pdf",
                mime="application/pdf"
            )

    with tab4:
        st.subheader(get_text("admin.system_stats", "Thống Kê Hệ Thống"))

        # Thống kê học sinh
        student_stats = report_gen.generate_student_statistics()
        st.metric(get_text("admin.total_students", "Tổng số học sinh"), student_stats['total_students'])
        st.plotly_chart(student_stats['health_chart'])
        st.plotly_chart(student_stats['academic_chart'])

        # Thống kê cựu chiến binh
        veteran_stats = report_gen.generate_veteran_statistics()
        st.metric(get_text("admin.total_veterans", "Tổng số cựu chiến binh"), veteran_stats['total_veterans'])
        st.plotly_chart(veteran_stats['health_chart'])

if __name__ == "__main__":
    render()