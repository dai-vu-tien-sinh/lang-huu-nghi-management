import streamlit as st
from auth import check_auth, check_role, can_edit_student_info, can_edit_veteran_info
from database import Database
from models import Student, Veteran
from utils import show_success, show_error, apply_theme
from translations import get_text
import pandas as pd
from io import BytesIO
from datetime import datetime
import base64

def display_student_details(student, db):
    """Hiển thị thông tin chi tiết của học sinh"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Hiển thị ảnh học sinh nếu có
        if student.profile_image:
            try:
                # Kiểm tra kiểu dữ liệu và chuyển đổi nếu cần
                if isinstance(student.profile_image, str):
                    st.warning(get_text('common.invalid_image', 'Dữ liệu ảnh không hợp lệ'))
                    st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
                else:
                    img_data = base64.b64encode(student.profile_image).decode()
                    st.markdown(
                        f'<img src="data:image/jpeg;base64,{img_data}" width="150" style="border-radius: 10px;">',
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.warning(f"{get_text('common.image_display_error', 'Không thể hiển thị ảnh')}: {str(e)}")
                st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
        else:
            st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
    
    with col2:
        col_a, col_b = st.columns(2)
        not_updated = get_text('common.not_updated', 'Chưa cập nhật')
        
        with col_a:
            st.markdown(f"**🎂 {get_text('profile.birth_date', 'Ngày sinh')}:** {student.birth_date or not_updated}")
            st.markdown(f"**⚧ {get_text('profile.gender', 'Giới tính')}:** {student.gender or not_updated}")
            st.markdown(f"**📱 {get_text('profile.phone', 'Điện thoại')}:** {student.phone or not_updated}")
            st.markdown(f"**📍 {get_text('profile.address', 'Địa chỉ')}:** {student.address or not_updated}")
        
        with col_b:
            # Lấy thông tin lớp học nếu có
            class_info = get_text('profile.no_class', 'Chưa phân lớp')
            if student.class_id:
                class_data = db.get_class(student.class_id)
                if class_data:
                    class_info = f"{class_data.name} ({class_data.academic_year})"
                    
            st.markdown(f"**👨‍🏫 {get_text('profile.class', 'Lớp')}:** {class_info}")
            st.markdown(f"**📧 {get_text('profile.email', 'Email')}:** {student.email or not_updated}")
            st.markdown(f"**👪 {get_text('profile.parent', 'Phụ huynh')}:** {student.parent_name or not_updated}")
            st.markdown(f"**📅 {get_text('profile.admission_date', 'Ngày nhập học')}:** {student.admission_date or not_updated}")
    
    # Hiển thị thông tin tình trạng
    st.markdown(f"##### 🏥 {get_text('profile.status', 'Tình trạng')}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**{get_text('profile.academic', 'Học tập')}:** {student.academic_status or not_updated}")
    with col2:
        st.markdown(f"**{get_text('profile.health', 'Sức khỏe')}:** {student.health_status or not_updated}")
    with col3:
        st.markdown(f"**{get_text('profile.psychological', 'Tâm lý')}:** {student.psychological_status or get_text('common.not_evaluated', 'Chưa đánh giá')}")

def display_veteran_details(veteran, db):
    """Hiển thị thông tin chi tiết của cựu chiến binh"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Hiển thị ảnh cựu chiến binh nếu có
        if veteran.profile_image:
            try:
                # Kiểm tra kiểu dữ liệu và chuyển đổi nếu cần
                if isinstance(veteran.profile_image, str):
                    st.warning(get_text('common.invalid_image', 'Dữ liệu ảnh không hợp lệ'))
                    st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
                else:
                    img_data = base64.b64encode(veteran.profile_image).decode()
                    st.markdown(
                        f'<img src="data:image/jpeg;base64,{img_data}" width="150" style="border-radius: 10px;">',
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.warning(f"{get_text('common.image_display_error', 'Không thể hiển thị ảnh')}: {str(e)}")
                st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
        else:
            st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
    
    with col2:
        col_a, col_b = st.columns(2)
        not_updated = get_text('common.not_updated', 'Chưa cập nhật')
        
        with col_a:
            st.markdown(f"**🎂 {get_text('profile.birth_date', 'Ngày sinh')}:** {veteran.birth_date or not_updated}")
            st.markdown(f"**🏅 {get_text('profile.service_period', 'Thời gian phục vụ')}:** {veteran.service_period or not_updated}")
            st.markdown(f"**📍 {get_text('profile.address', 'Địa chỉ')}:** {veteran.address or not_updated}")
        
        with col_b:
            st.markdown(f"**📧 {get_text('profile.email', 'Email')}:** {veteran.email or not_updated}")
            st.markdown(f"**📞 {get_text('profile.contact', 'Liên hệ')}:** {veteran.contact_info or not_updated}")
            st.markdown(f"**🏥 {get_text('profile.health_condition', 'Tình trạng sức khỏe')}:** {veteran.health_condition or not_updated}")

def handle_student_edit(student, db):
    """Xử lý chỉnh sửa thông tin học sinh"""
    st.subheader(f"✏️ {get_text('profile.edit_information', 'Chỉnh sửa thông tin')}")
    
    # Hiển thị ảnh hiện tại và tùy chọn tải lên ảnh mới
    uploaded_image = None
    col_img1, col_img2 = st.columns([1, 2])
    
    with col_img1:
        # Hiển thị ảnh học sinh nếu có
        if student.profile_image:
            try:
                # Kiểm tra kiểu dữ liệu và chuyển đổi nếu cần
                if isinstance(student.profile_image, str):
                    st.warning("Dữ liệu ảnh không hợp lệ")
                    st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
                else:
                    img_data = base64.b64encode(student.profile_image).decode()
                    st.markdown(
                        f'<img src="data:image/jpeg;base64,{img_data}" width="150" style="border-radius: 10px;">',
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.warning(f"Không thể hiển thị ảnh: {str(e)}")
                st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
        else:
            st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
    
    with col_img2:
        # Tải lên ảnh mới
        uploaded_image = st.file_uploader(get_text("profile.upload_new_image", "Tải lên ảnh mới"), type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            # Hiển thị ảnh đã tải lên
            st.image(uploaded_image, width=200)
            
            # Lưu ảnh vào cơ sở dữ liệu khi nhấn nút
            if st.button(get_text("profile.save_image", "Lưu ảnh"), key="save_student_image"):
                try:
                    # Đọc dữ liệu ảnh
                    image_bytes = uploaded_image.getvalue()
                    # Lưu vào cơ sở dữ liệu
                    if db.save_student_image(student.id, image_bytes):
                        show_success("✅ Đã cập nhật ảnh thành công!")
                        st.rerun()  # Reload để hiển thị ảnh mới
                    else:
                        show_error("❌ Không thể cập nhật ảnh")
                except Exception as e:
                    show_error(f"❌ Lỗi khi cập nhật ảnh: {str(e)}")
    
    # Tạo form chỉnh sửa
    with st.form("edit_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(get_text("profile.full_name", "Họ và tên"), value=student.full_name)
            birth_date = st.text_input(get_text("profile.birth_date", "Ngày sinh"), value=student.birth_date or "", 
                                      help=get_text("profile.date_format_help", "Định dạng: YYYY-MM-DD"))
            gender = st.selectbox(get_text("profile.gender", "Giới tính"), 
                                options=[get_text("gender.male", "Nam"), get_text("gender.female", "Nữ"), get_text("gender.other", "Khác")],
                                index=[get_text("gender.male", "Nam"), get_text("gender.female", "Nữ"), get_text("gender.other", "Khác")].index(student.gender) if student.gender in [get_text("gender.male", "Nam"), get_text("gender.female", "Nữ"), get_text("gender.other", "Khác")] else 0)
            phone = st.text_input("Số điện thoại", value=student.phone or "")
            address = st.text_input("Địa chỉ", value=student.address or "")
        
        with col2:
            email = st.text_input("Email", value=student.email or "")
            parent_name = st.text_input("Phụ huynh", value=student.parent_name or "")
            year = st.text_input("Năm học", value=student.year or "")
            
            # Lấy danh sách lớp học
            classes = db.get_classes()
            class_options = [(0, "Không phân lớp")] + [(c.id, f"{c.name} ({c.academic_year})") for c in classes]
            
            # Tìm vị trí của lớp học hiện tại trong danh sách
            selected_index = 0
            for i, (class_id, _) in enumerate(class_options):
                if student.class_id == class_id:
                    selected_index = i
                    break
            
            class_id = st.selectbox(
                "Lớp", 
                options=range(len(class_options)),
                format_func=lambda i: class_options[i][1],
                index=selected_index
            )
            class_id = class_options[class_id][0] if class_id is not None else None
            
            # Convert class_id = 0 to None
            if class_id == 0:
                class_id = None
            
            # Đổi định dạng ngày nhập học từ text sang date_input
            admission_date = None
            try:
                if student.admission_date:
                    admission_date = datetime.strptime(student.admission_date, "%Y-%m-%d").date()
            except:
                pass
            
            admission_date = st.date_input("Ngày nhập học", value=admission_date or datetime.now().date())
        
        # Tình trạng
        st.subheader("Tình trạng")
        col1, col2 = st.columns(2)
        
        with col1:
            health_status = st.selectbox(
                "Tình trạng sức khỏe",
                ["Tốt", "Bình thường", "Ổn định", "Cần chú ý"],
                index=["Tốt", "Bình thường", "Ổn định", "Cần chú ý"].index(student.health_status) if student.health_status in ["Tốt", "Bình thường", "Ổn định", "Cần chú ý"] else 1
            )
        
        with col2:
            academic_status = st.selectbox(
                "Tình trạng học tập",
                ["Xuất sắc", "Tốt", "Trung bình", "Cần cải thiện", "Chưa đánh giá"],
                index=["Xuất sắc", "Tốt", "Trung bình", "Cần cải thiện", "Chưa đánh giá"].index(student.academic_status) if student.academic_status in ["Xuất sắc", "Tốt", "Trung bình", "Cần cải thiện", "Chưa đánh giá"] else 4
            )
            
            psychological_status = st.selectbox(
                "Tình trạng tâm lý",
                ["Ổn định", "Cần theo dõi", "Cần hỗ trợ", "Tốt", "Chưa đánh giá"],
                index=["Ổn định", "Cần theo dõi", "Cần hỗ trợ", "Tốt", "Chưa đánh giá"].index(student.psychological_status) if student.psychological_status in ["Ổn định", "Cần theo dõi", "Cần hỗ trợ", "Tốt", "Chưa đánh giá"] else 0
            )
            
        if st.form_submit_button("💾 Lưu thay đổi"):
            student_data = {
                "full_name": full_name,
                "birth_date": birth_date,
                "gender": gender,
                "phone": phone,
                "address": address,
                "email": email,
                "parent_name": parent_name,
                "year": year,
                "admission_date": admission_date.strftime("%Y-%m-%d"),
                "class_id": class_id,
                "health_status": health_status,
                "academic_status": academic_status,
                "psychological_status": psychological_status
            }
            
            try:
                if db.update_student(student.id, student_data):
                    # Ghi nhận lịch sử thay đổi lớp học nếu lớp học thay đổi
                    if student.class_id != class_id:
                        db.update_student_class(student.id, class_id)
                    
                    show_success("✅ Đã cập nhật thông tin học sinh thành công!")
                    st.rerun()
                else:
                    show_error("❌ Không thể cập nhật thông tin học sinh")
            except Exception as e:
                show_error(f"❌ Lỗi khi cập nhật: {str(e)}")

def handle_veteran_edit(veteran, db):
    """Xử lý chỉnh sửa thông tin cựu chiến binh"""
    st.subheader("✏️ Chỉnh sửa thông tin")
    
    # Hiển thị ảnh hiện tại và tùy chọn tải lên ảnh mới
    uploaded_image = None
    col_img1, col_img2 = st.columns([1, 2])
    
    with col_img1:
        # Hiển thị ảnh cựu chiến binh nếu có
        if veteran.profile_image:
            try:
                # Kiểm tra kiểu dữ liệu và chuyển đổi nếu cần
                if isinstance(veteran.profile_image, str):
                    st.warning("Dữ liệu ảnh không hợp lệ")
                    st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
                else:
                    img_data = base64.b64encode(veteran.profile_image).decode()
                    st.markdown(
                        f'<img src="data:image/jpeg;base64,{img_data}" width="150" style="border-radius: 10px;">',
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.warning(f"Không thể hiển thị ảnh: {str(e)}")
                st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
        else:
            st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", width=150)
    
    with col_img2:
        # Tải lên ảnh mới
        uploaded_image = st.file_uploader(get_text("profile.upload_new_image", "Tải lên ảnh mới"), type=["jpg", "jpeg", "png"], key="upload_veteran_image")
        if uploaded_image is not None:
            # Hiển thị ảnh đã tải lên
            st.image(uploaded_image, width=200)
            
            # Lưu ảnh vào cơ sở dữ liệu khi nhấn nút
            if st.button(get_text("profile.save_image", "Lưu ảnh"), key="save_veteran_image"):
                try:
                    # Đọc dữ liệu ảnh
                    image_bytes = uploaded_image.getvalue()
                    # Lưu vào cơ sở dữ liệu
                    if db.save_veteran_image(veteran.id, image_bytes):
                        show_success("✅ Đã cập nhật ảnh thành công!")
                        st.rerun()  # Reload để hiển thị ảnh mới
                    else:
                        show_error("❌ Không thể cập nhật ảnh")
                except Exception as e:
                    show_error(f"❌ Lỗi khi cập nhật ảnh: {str(e)}")
    
    # Tạo form chỉnh sửa
    with st.form("edit_veteran_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Họ và tên", value=veteran.full_name)
            birth_date = st.text_input("Ngày sinh", value=veteran.birth_date or "", 
                                      help="Định dạng: YYYY-MM-DD")
            service_period = st.text_input("Thời gian phục vụ", value=veteran.service_period or "")
            address = st.text_input("Địa chỉ", value=veteran.address or "")
        
        with col2:
            health_condition = st.text_input("Tình trạng sức khỏe", value=veteran.health_condition or "")
            email = st.text_input("Email", value=veteran.email or "")
            contact_info = st.text_input("Thông tin liên hệ", value=veteran.contact_info or "")
            
        if st.form_submit_button("💾 Lưu thay đổi"):
            veteran_data = {
                "full_name": full_name,
                "birth_date": birth_date,
                "service_period": service_period,
                "address": address,
                "health_condition": health_condition,
                "email": email,
                "contact_info": contact_info
            }
            
            try:
                if db.update_veteran(veteran.id, veteran_data):
                    show_success("✅ Đã cập nhật thông tin cựu chiến binh thành công!")
                    st.rerun()
                else:
                    show_error("❌ Không thể cập nhật thông tin cựu chiến binh")
            except Exception as e:
                show_error(f"❌ Lỗi khi cập nhật: {str(e)}")

def add_new_student(db):
    """Thêm học sinh mới"""
    st.subheader("➕ Thêm học sinh mới")
    
    # Tải lên ảnh cho học sinh mới
    uploaded_image = st.file_uploader("Tải lên ảnh học sinh", type=["jpg", "jpeg", "png"], key="upload_new_student_image")
    if uploaded_image is not None:
        st.image(uploaded_image, width=200)
        st.info("Ảnh sẽ được lưu sau khi bạn thêm học sinh")
    
    with st.form("add_student_form"):
        # Thông tin cơ bản
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Họ và tên", key="add_full_name")
            birth_date = st.text_input("Ngày sinh", key="add_birth_place", 
                                     help="Định dạng: YYYY-MM-DD")
            gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"], key="add_gender")
            phone = st.text_input("Số điện thoại", key="add_phone")
            address = st.text_input("Địa chỉ thường trú", key="add_address")
        
        with col2:
            email = st.text_input("Email", key="add_email")
            parent_name = st.text_input("Phụ huynh", key="add_parent_name")
            year = st.text_input("Năm học", key="add_year")
            admission_date = st.date_input("Ngày nhập học", key="add_admission_date")

            # Lấy danh sách lớp học
            classes = db.get_classes()
            class_options = [(0, "Không phân lớp")] + [(c.id, f"{c.name} ({c.academic_year})") for c in classes]
            
            class_id = st.selectbox(
                "Lớp",
                options=range(len(class_options)),
                format_func=lambda i: class_options[i][1],
                key="add_class_id"
            )
            class_id = class_options[class_id][0] if class_id is not None else None
            
            # Convert class_id = 0 to None
            if class_id == 0:
                class_id = None

        # Tình trạng
        st.subheader("Tình trạng")
        col1, col2 = st.columns(2)
        
        with col1:
            health_status = st.selectbox(
                "Tình trạng sức khỏe",
                ["Tốt", "Bình thường", "Ổn định", "Cần chú ý"],
                key="add_health_status"
            )
        
        with col2:
            academic_status = st.selectbox(
                "Tình trạng học tập",
                ["Xuất sắc", "Tốt", "Trung bình", "Cần cải thiện", "Chưa đánh giá"],
                key="add_academic_status"
            )
            
            psychological_status = st.selectbox(
                "Tình trạng tâm lý",
                ["Ổn định", "Cần theo dõi", "Cần hỗ trợ", "Tốt", "Chưa đánh giá"],
                key="add_psychological_status"
            )

        if st.form_submit_button("Thêm học sinh"):
            student_data = {
                "full_name": full_name,
                "birth_date": birth_date,
                "gender": gender,
                "phone": phone,
                "address": address,
                "email": email,
                "parent_name": parent_name,
                "year": year,
                "admission_date": admission_date.strftime("%Y-%m-%d"),
                "health_status": health_status,
                "academic_status": academic_status,
                "psychological_status": psychological_status,
                "class_id": class_id
            }
            
            if not full_name:
                show_error("Vui lòng nhập họ và tên học sinh")
            else:
                try:
                    student_id = db.add_student(student_data)
                    if student_id:
                        # Nếu có lớp học, cập nhật lịch sử lớp học
                        if class_id:
                            db.update_student_class(student_id, class_id)
                        
                        # Nếu có tải lên ảnh, lưu ảnh vào cơ sở dữ liệu
                        if 'upload_new_student_image' in st.session_state and st.session_state.upload_new_student_image is not None:
                            uploaded_image = st.session_state.upload_new_student_image
                            image_bytes = uploaded_image.getvalue()
                            if db.save_student_image(student_id, image_bytes):
                                show_success(f"Đã thêm học sinh {full_name} và lưu ảnh thành công!")
                            else:
                                show_success(f"Đã thêm học sinh {full_name} thành công, nhưng không thể lưu ảnh!")
                        else:
                            show_success(f"Đã thêm học sinh {full_name} thành công!")
                            
                        st.rerun()
                    else:
                        show_error("Không thể thêm học sinh")
                except Exception as e:
                    show_error(f"Lỗi khi thêm học sinh: {str(e)}")

def add_new_veteran(db):
    """Thêm cựu chiến binh mới"""
    st.subheader("➕ Thêm cựu chiến binh mới")
    
    # Tải lên ảnh cho cựu chiến binh mới
    uploaded_image = st.file_uploader("Tải lên ảnh cựu chiến binh", type=["jpg", "jpeg", "png"], key="upload_new_veteran_image")
    if uploaded_image is not None:
        st.image(uploaded_image, width=200)
        st.info("Ảnh sẽ được lưu sau khi bạn thêm cựu chiến binh")
    
    with st.form("add_veteran_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Họ và tên", key="add_vet_name")
            birth_date = st.text_input("Ngày sinh", key="add_vet_birth", 
                                     help="Định dạng: YYYY-MM-DD")
            service_period = st.text_input("Thời gian phục vụ", key="add_vet_service")
            address = st.text_input("Địa chỉ", key="add_vet_address")
        
        with col2:
            health_condition = st.text_input("Tình trạng sức khỏe", key="add_vet_health")
            email = st.text_input("Email", key="add_vet_email")
            contact_info = st.text_input("Thông tin liên hệ", key="add_vet_contact")
            
        if st.form_submit_button("Thêm cựu chiến binh"):
            if not full_name:
                show_error("Vui lòng nhập họ và tên")
            else:
                veteran_data = {
                    "full_name": full_name,
                    "birth_date": birth_date,
                    "service_period": service_period,
                    "address": address,
                    "health_condition": health_condition,
                    "email": email,
                    "contact_info": contact_info
                }
                
                try:
                    veteran_id = db.add_veteran(veteran_data)
                    if veteran_id:
                        # Nếu có tải lên ảnh, lưu ảnh vào cơ sở dữ liệu
                        if 'upload_new_veteran_image' in st.session_state and st.session_state.upload_new_veteran_image is not None:
                            uploaded_image = st.session_state.upload_new_veteran_image
                            image_bytes = uploaded_image.getvalue()
                            if db.save_veteran_image(veteran_id, image_bytes):
                                show_success(f"Đã thêm cựu chiến binh {full_name} và lưu ảnh thành công!")
                            else:
                                show_success(f"Đã thêm cựu chiến binh {full_name} thành công, nhưng không thể lưu ảnh!")
                        else:
                            show_success(f"Đã thêm cựu chiến binh {full_name} thành công!")
                            
                        st.rerun()
                    else:
                        show_error("Không thể thêm cựu chiến binh")
                except Exception as e:
                    show_error(f"Lỗi khi thêm cựu chiến binh: {str(e)}")

def render():
    # Apply theme from session state
    apply_theme()
    
    # Set current page for role checking
    st.session_state.current_page = "03_Quan_ly_ho_so"
    
    check_auth()
    
    db = Database()
    
    st.title(f"👥 {get_text('profile.title', 'Quản Lý Hồ Sơ')}")
    
    # Tạo tabs cho học sinh và cựu chiến binh
    entity_type = st.radio(
        get_text('profile.select_type', 'Chọn loại hồ sơ'), 
        [get_text('common.student', 'Học sinh'), get_text('common.veteran', 'Cựu chiến binh')], 
        horizontal=True
    )
    
    if entity_type == get_text('common.student', 'Học sinh'):
        student_tabs = st.tabs([
            f"🔍 {get_text('common.list', 'Danh sách')}", 
            f"➕ {get_text('common.add_new', 'Thêm mới')}"
        ])
        
        with student_tabs[0]:
            st.subheader(f"📋 {get_text('profile.student_list', 'Danh sách học sinh')}")
            
            # Thêm ô tìm kiếm
            search_query = st.text_input(
                f"🔍 {get_text('common.search_by_name', 'Tìm kiếm theo tên')}", 
                key="search_student"
            )
            
            # Lấy danh sách học sinh
            students = db.get_students()
            
            # Lọc học sinh theo tìm kiếm nếu có
            if search_query:
                search_query = search_query.lower()
                students = [s for s in students if search_query in s.full_name.lower()]
            
            # Hiển thị số lượng học sinh
            st.info(f"📊 {get_text('common.total', 'Tổng số')}: {len(students)} {get_text('common.student', 'học sinh')}")
            
            # Hiển thị danh sách học sinh trong các expanders
            for student in students:
                with st.expander(f"👨‍🎓 {student.full_name}"):
                    # Thông tin chi tiết học sinh
                    display_student_details(student, db)
                    
                    # Nút chỉnh sửa
                    if can_edit_student_info():
                        if st.button(f"✏️ {get_text('common.edit', 'Chỉnh sửa')}", key=f"edit_student_{student.id}"):
                            st.session_state.edit_student_id = student.id
                            st.rerun()
            
            # Hiển thị form chỉnh sửa nếu đã chọn học sinh
            if hasattr(st.session_state, 'edit_student_id'):
                for student in students:
                    if student.id == st.session_state.edit_student_id:
                        handle_student_edit(student, db)
                        break
                
                # Nút hủy chỉnh sửa
                if st.button(f"❌ {get_text('common.cancel_edit', 'Hủy chỉnh sửa')}"):
                    del st.session_state.edit_student_id
                    st.rerun()
        
        with student_tabs[1]:
            # Kiểm tra quyền thêm học sinh mới
            if can_edit_student_info():
                add_new_student(db)
            else:
                st.warning(get_text("profile.student_add_permission_denied", "Bạn không có quyền thêm học sinh mới"))
    
    else:  # Cựu chiến binh
        veteran_tabs = st.tabs([
            f"🔍 {get_text('common.list', 'Danh sách')}", 
            f"➕ {get_text('common.add_new', 'Thêm mới')}"
        ])
        
        with veteran_tabs[0]:
            st.subheader(f"📋 {get_text('profile.veteran_list', 'Danh sách cựu chiến binh')}")
            
            # Thêm ô tìm kiếm
            search_query = st.text_input(
                f"🔍 {get_text('common.search_by_name', 'Tìm kiếm theo tên')}", 
                key="search_veteran"
            )
            
            # Lấy danh sách cựu chiến binh
            veterans = db.get_veterans()
            
            # Lọc cựu chiến binh theo tìm kiếm nếu có
            if search_query:
                search_query = search_query.lower()
                veterans = [v for v in veterans if search_query in v.full_name.lower()]
            
            # Hiển thị số lượng cựu chiến binh
            st.info(f"📊 {get_text('common.total', 'Tổng số')}: {len(veterans)} {get_text('common.veteran', 'cựu chiến binh')}")
            
            # Hiển thị danh sách cựu chiến binh trong các expanders
            for veteran in veterans:
                with st.expander(f"🎖️ {veteran.full_name}"):
                    # Thông tin chi tiết cựu chiến binh
                    display_veteran_details(veteran, db)
                    
                    # Nút chỉnh sửa
                    if can_edit_veteran_info():
                        if st.button(f"✏️ {get_text('common.edit', 'Chỉnh sửa')}", key=f"edit_veteran_{veteran.id}"):
                            st.session_state.edit_veteran_id = veteran.id
                            st.rerun()
            
            # Hiển thị form chỉnh sửa nếu đã chọn cựu chiến binh
            if hasattr(st.session_state, 'edit_veteran_id'):
                for veteran in veterans:
                    if veteran.id == st.session_state.edit_veteran_id:
                        handle_veteran_edit(veteran, db)
                        break
                
                # Nút hủy chỉnh sửa
                if st.button(f"❌ {get_text('common.cancel_edit', 'Hủy chỉnh sửa')}", key="cancel_veteran_edit"):
                    del st.session_state.edit_veteran_id
                    st.rerun()
        
        with veteran_tabs[1]:
            # Kiểm tra quyền thêm cựu chiến binh mới
            if can_edit_veteran_info():
                add_new_veteran(db)
            else:
                st.warning(get_text("profile.veteran_add_permission_denied", "Bạn không có quyền thêm cựu chiến binh mới"))

if __name__ == "__main__":
    render()