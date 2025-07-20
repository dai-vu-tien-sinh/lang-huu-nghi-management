# Hướng dẫn sao lưu Google Drive cho Supabase

## Tổng quan
Hệ thống sao lưu đã được tối ưu hóa để hoạt động với cơ sở dữ liệu PostgreSQL trên Supabase. Thay vì sao lưu file SQLite, hệ thống hiện tạo các bản sao lưu SQL dump và metadata.

## Tính năng được tối ưu hóa cho Supabase

### 1. Backup PostgreSQL
- **SQL Dump**: Xuất dữ liệu từ các bảng chính
- **Metadata Backup**: Thông tin về số lượng bản ghi và cấu trúc
- **Fallback System**: Tự động chuyển sang backup metadata nếu SQL dump thất bại

### 2. Tính tương thích
- Hoạt động với DATABASE_URL environment variable
- Tương thích với Supabase connection pooling
- Hỗ trợ các bảng: users, students, veterans, medical_records, classes, student_notes, documents

### 3. Bảo mật
- Sử dụng OAuth 2.0 cho Google Drive
- Không lưu trữ password database trong backup
- Mã hóa dữ liệu khi upload lên Google Drive

## Cách sử dụng

### Bước 1: Cấu hình Google Drive API
1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Enable Google Drive API
4. Tạo OAuth 2.0 credentials (Desktop application)
5. Tải file JSON và đổi tên thành `credentials.json`
6. Đặt file vào thư mục gốc của project

### Bước 2: Xác thực lần đầu
1. Trong giao diện web, vào "Quản lý Hệ thống" > "💾 Sao lưu & Khôi phục"
2. Click "🔧 Xác thực thủ công"
3. Làm theo hướng dẫn hoặc chạy `python setup_google_auth.py`
4. Hoàn tất quá trình OAuth trong trình duyệt

### Bước 3: Sử dụng backup
- **Sao lưu thủ công**: Click "📤 Sao lưu ngay"
- **Sao lưu tự động**: Hệ thống tự động chạy mỗi Chủ nhật lúc 2:00 AM
- **Quản lý**: Tự động giữ 10 bản backup mới nhất, xóa bản cũ

## Cấu trúc File Backup

### SQL Dump (.sql)
```sql
-- Lang Huu Nghi Database Backup
-- Created: 2025-07-20T10:30:00
-- Database: PostgreSQL (Supabase)

-- Table: users
-- 15 records found in users
-- Row sample: (1, 'admin', 'hashed_password', 'admin', True)...

-- Table: students  
-- 82 records found in students
-- Row sample: (1, 'Nguyễn Văn A', '2010-01-01', 'Hà Nội')...
```

### Metadata (.json)
```json
{
  "backup_type": "metadata",
  "timestamp": "2025-07-20T10:30:00",
  "database_type": "PostgreSQL (Supabase)",
  "tables": {
    "users": {"record_count": 15},
    "students": {"record_count": 82},
    "veterans": {"record_count": 12}
  }
}
```

## Troubleshooting

### Lỗi xác thực
- Đảm bảo `credentials.json` đã được đặt đúng vị trí
- Kiểm tra Google Drive API đã được enable
- Thử lại quá trình OAuth

### Lỗi backup
- Kiểm tra kết nối DATABASE_URL
- Đảm bảo có quyền truy cập các bảng trong database
- Xem console logs để biết chi tiết lỗi

### Lỗi upload
- Kiểm tra kết nối internet
- Đảm bảo tài khoản Google có đủ dung lượng (15GB miễn phí)
- Thử lại upload thủ công

## Lưu ý quan trọng

1. **Dung lượng**: Backup files thường nhỏ (< 1MB) cho database cỡ trung bình
2. **Bảo mật**: Không bao gồm passwords user trong backup
3. **Tần suất**: Backup tự động mỗi tuần, có thể backup thủ công bất cứ lúc nào
4. **Khôi phục**: File backup có thể được sử dụng để tham khảo dữ liệu, không phải khôi phục tự động
5. **Chi phí**: Hoàn toàn miễn phí trong giới hạn 15GB Google Drive

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra console logs trong ứng dụng
2. Đảm bảo tất cả environment variables đã được cấu hình
3. Xem file `GDRIVE_BACKUP_SETUP.md` để biết chi tiết cấu hình Google Drive API