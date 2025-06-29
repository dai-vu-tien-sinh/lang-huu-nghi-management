import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from auth import check_auth
from database import Database
import pandas as pd
from io import BytesIO
from visualizations import ChartCustomizer
from utils import apply_theme
from translations import get_text

def render():
    check_auth()

    # Apply theme from session state
    apply_theme()

    st.title(get_text("pages.statistics.title", "Thống Kê và Phân Tích Dữ Liệu"))

    db = Database()
    chart_customizer = ChartCustomizer()

    # Sidebar filters
    st.sidebar.header(get_text("pages.statistics.filters", "Bộ lọc"))

    date_range = st.sidebar.date_input(
        get_text("pages.statistics.date_range", "Khoảng thời gian"),
        value=(datetime.now() - timedelta(days=365), datetime.now())
    )

    # Overview statistics
    col1, col2, col3, col4 = st.columns(4)

    total_students = len(db.get_students())
    total_veterans = len(db.get_veterans())

    medical_records = db.conn.execute("SELECT COUNT(*) FROM medical_records").fetchone()[0]
    psych_evals = db.conn.execute("SELECT COUNT(*) FROM psychological_evaluations").fetchone()[0]

    with col1:
        st.metric("Tổng số sinh viên", total_students)
    with col2:
        st.metric("Tổng số cựu chiến binh", total_veterans)
    with col3:
        st.metric("Số hồ sơ y tế", medical_records)
    with col4:
        st.metric("Số đánh giá tâm lý", psych_evals)

    # Tùy chỉnh biểu đồ
    st.subheader("📊 Tùy chỉnh biểu đồ")

    # Chọn loại dữ liệu
    data_type = st.selectbox(
        "Chọn loại dữ liệu",
        ["Tình trạng sức khỏe", "Kết quả học tập", "Hồ sơ y tế", "Đánh giá tâm lý"]
    )

    # Layout tùy chỉnh
    col1, col2 = st.columns(2)
    with col1:
        chart_type = st.selectbox(
            "Loại biểu đồ",
            chart_customizer.get_available_chart_types()
        )
        color_scheme = st.selectbox(
            "Bảng màu",
            chart_customizer.get_available_color_schemes()
        )
    with col2:
        show_grid = st.checkbox("Hiển thị lưới", value=True)
        orientation = st.selectbox(
            "Hướng biểu đồ",
            ["vertical", "horizontal"]
        )

    # Get and prepare data based on selection
    if data_type == "Tình trạng sức khỏe":
        data = db.conn.execute("""
            SELECT health_status, COUNT(*) as count
            FROM students
            GROUP BY health_status
        """).fetchall()
        df = pd.DataFrame(data, columns=['status', 'count'])

        # Create customizable chart
        fig = chart_customizer.create_customizable_chart(
            data=df,
            chart_type=chart_type,
            x_column='status',
            y_column='count',
            title='Phân Bố Tình Trạng Sức Khỏe Sinh Viên',
            color_scheme=color_scheme,
            orientation=orientation,
            show_grid=show_grid
        )
        if fig:
            st.plotly_chart(fig)

    elif data_type == "Kết quả học tập":
        data = db.conn.execute("""
            SELECT academic_status, COUNT(*) as count
            FROM students
            GROUP BY academic_status
        """).fetchall()
        df = pd.DataFrame(data, columns=['status', 'count'])

        fig = chart_customizer.create_customizable_chart(
            data=df,
            chart_type=chart_type,
            x_column='status',
            y_column='count',
            title='Phân Bố Kết Quả Học Tập',
            color_scheme=color_scheme,
            orientation=orientation,
            show_grid=show_grid
        )
        if fig:
            st.plotly_chart(fig)

    elif data_type == "Hồ sơ y tế":
        data = db.conn.execute("""
            SELECT DATE(date) as record_date, COUNT(*) as count
            FROM medical_records
            WHERE date(date) BETWEEN ? AND ?
            GROUP BY DATE(date)
            ORDER BY record_date
        """, (date_range[0], date_range[1])).fetchall()

        if data:
            df = pd.DataFrame(data, columns=['date', 'count'])
            fig = chart_customizer.create_customizable_chart(
                data=df,
                chart_type=chart_type,
                x_column='date',
                y_column='count',
                title='Số Lượng Hồ Sơ Y Tế Theo Ngày',
                color_scheme=color_scheme,
                orientation=orientation,
                show_grid=show_grid
            )
            if fig:
                st.plotly_chart(fig)

    elif data_type == "Đánh giá tâm lý":
        data = db.conn.execute("""
            SELECT 
                DATE(evaluation_date) as eval_date,
                COUNT(*) as total_evals,
                SUM(CASE WHEN notification_sent THEN 1 ELSE 0 END) as notified
            FROM psychological_evaluations
            WHERE date(evaluation_date) BETWEEN ? AND ?
            GROUP BY DATE(evaluation_date)
            ORDER BY eval_date
        """, (date_range[0], date_range[1])).fetchall()

        if data:
            df = pd.DataFrame(data, columns=['date', 'total', 'notified'])

            # Create comparison chart
            fig = chart_customizer.create_comparison_chart(
                data1=df,
                data2=df,
                x_column='date',
                y_column='total',
                y2_column='notified',
                label1='Tổng số đánh giá',
                label2='Đã gửi thông báo',
                title='Thống Kê Đánh Giá Tâm Lý và Thông Báo'
            )
            st.plotly_chart(fig)

    # Export functionality
    st.markdown("---")
    st.subheader("📥 Xuất dữ liệu")

    with st.expander("⚙️ Tùy chọn xuất dữ liệu"):
        export_type = st.multiselect(
            "Chọn loại dữ liệu cần xuất",
            ["Sinh viên", "Cựu chiến binh", "Hồ sơ y tế", "Đánh giá tâm lý"],
            default=["Sinh viên"]
        )

        if st.button("📊 Tạo file Excel"):
            try:
                # Create Excel writer
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='openpyxl')

                # Export students
                if "Sinh viên" in export_type:
                    # Chỉ định rõ các cột cần lấy thay vì SELECT *
                    students = db.conn.execute("""
                        SELECT 
                            s.id, 
                            s.full_name, 
                            s.birth_date, 
                            s.address, 
                            s.email,
                            s.admission_date, 
                            s.class_id, 
                            s.health_status, 
                            s.academic_status,
                            s.psychological_status, 
                            c.name as class_name, 
                            c.academic_year
                        FROM students s
                        LEFT JOIN classes c ON s.class_id = c.id
                    """).fetchall()
                    if students:
                        # Đảm bảo số cột trong columns là đúng với số cột trong truy vấn SQL
                        df_students = pd.DataFrame(students, columns=[
                            'ID', 'Họ và tên', 'Ngày sinh', 'Địa chỉ', 'Email',
                            'Ngày nhập học', 'Lớp ID', 'Sức khỏe', 'Học tập',
                            'Tâm lý', 'Tên lớp', 'Năm học'
                        ])
                        df_students.to_excel(writer, sheet_name='Sinh viên', index=False)

                # Export veterans
                if "Cựu chiến binh" in export_type:
                    # Chỉ định rõ các cột cần lấy
                    veterans = db.conn.execute("""
                        SELECT 
                            id, 
                            full_name, 
                            birth_date, 
                            service_period, 
                            health_condition, 
                            address, 
                            email, 
                            contact_info
                        FROM veterans
                    """).fetchall()
                    if veterans:
                        df_veterans = pd.DataFrame(veterans, columns=[
                            'ID', 'Họ và tên', 'Ngày sinh', 'Thời gian phục vụ',
                            'Tình trạng sức khỏe', 'Địa chỉ', 'Email', 'Liên hệ'
                        ])
                        df_veterans.to_excel(writer, sheet_name='Cựu chiến binh', index=False)

                # Save the file
                writer.close()

                # Create download button
                filename = f"du_lieu_lang_huu_nghi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                st.download_button(
                    label="⬇️ Tải xuống file Excel",
                    data=output.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("✅ File Excel đã được tạo thành công!")

            except Exception as e:
                st.error(f"❌ Lỗi khi tạo file Excel: {str(e)}")
                print(f"Export error: {str(e)}")

if __name__ == "__main__":
    render()