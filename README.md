# Hệ thống quản lý dữ liệu Làng Hữu Nghị

Hệ thống quản lý toàn diện cho dữ liệu giáo dục và cộng đồng tại Làng Hữu Nghị với khả năng xử lý tài liệu nâng cao.

## Tính năng chính

### 🏠 Quản lý hồ sơ
- Quản lý thông tin học sinh và cựu chiến binh
- Theo dõi lịch sử lớp học và ghi chú giáo viên
- Tải lên và quản lý tài liệu đính kèm
- Xuất báo cáo Word toàn diện

### 🏥 Y tế
- Quản lý hồ sơ y tế của học sinh và cựu chiến binh
- Theo dõi chẩn đoán, điều trị và đơn thuốc
- Lập lịch tái khám và ghi chú bác sĩ

### 🎓 Lớp học
- Quản lý thông tin lớp và giáo viên
- Ghi chú chi tiết cho từng học sinh
- Phân loại ghi chú theo danh mục và mức độ quan trọng

### 📊 Thống kê và báo cáo
- Biểu đồ phân tích dữ liệu
- Xuất dữ liệu Excel với định dạng chuyên nghiệp
- Báo cáo tổng hợp và thống kê

### 🔒 Hệ thống phân quyền
- **Admin**: Toàn quyền truy cập
- **Giáo viên**: Quản lý lớp học và học sinh
- **Bác sĩ**: Quản lý hồ sơ y tế
- **Gia đình**: Xem thông tin con em

## Công nghệ sử dụng

- **Python 3.11**
- **Streamlit** - Framework ứng dụng web
- **SQLAlchemy** - ORM cơ sở dữ liệu  
- **PostgreSQL/SQLite** - Cơ sở dữ liệu
- **Google Drive API** - Sao lưu tự động
- **Plotly** - Biểu đồ tương tác

## Tính năng đặc biệt

### 📎 Quản lý tài liệu
- Tải lên nhiều loại file (Word, PDF, Excel, hình ảnh)
- Xem trước tài liệu trực tiếp trong hệ thống
- Xuất tài liệu riêng biệt khi tạo báo cáo

### 🏘️ Hỗ trợ đa nhà
- Quản lý học sinh theo các nhà (T2, T3, T4, T5, T6, N02)
- Tự động phát hiện và phân bổ nhà khi import Excel
- Thống kê theo từng nhà

### 🌍 Đa ngôn ngữ
- Hỗ trợ tiếng Việt đầy đủ với dấu thanh
- Giao diện thân thiện và dễ sử dụng

## Cài đặt và chạy

### Trên Replit
1. Fork project này
2. Cấu hình biến môi trường cần thiết
3. Chạy: `streamlit run Trang_chủ.py`

### Local Development
```bash
# Clone repository
git clone https://github.com/dai-vu-tien-sinh/lang-huu-nghi-management.git
cd lang-huu-nghi-management

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
streamlit run Trang_chủ.py
```

## Triển khai

### Trên Supabase
- Tương thích với PostgreSQL
- Hướng dẫn chi tiết trong `SUPABASE_BACKUP_GUIDE.md`
- Tính năng sao lưu tự động

### Trên Replit
- Sẵn sàng triển khai
- Cấu hình tự động
- Hỗ trợ SQLite và PostgreSQL

## Bảo mật

- Xác thực dựa trên vai trò
- Mã hóa mật khẩu
- Kiểm soát truy cập chi tiết
- Sao lưu dữ liệu an toàn

## Hỗ trợ

Để được hỗ trợ kỹ thuật hoặc đóng góp cho dự án, vui lòng:
1. Tạo Issue trên GitHub
2. Fork và gửi Pull Request
3. Liên hệ qua email hỗ trợ

## Giấy phép

Dự án này được phát triển cho Làng Hữu Nghị với mục đích giáo dục và cộng đồng.

---

**Phiên bản hiện tại**: 2.0  
**Cập nhật cuối**: Tháng 7/2025  
**Tác giả**: Đại Vũ Tiến Sinh