
# 🚀 Hướng dẫn cài đặt Google Drive Backup

## Tổng quan
Hệ thống sao lưu tự động sẽ tạo bản sao dữ liệu lên Google Drive mỗi tuần và cho phép sao lưu thủ công bất cứ lúc nào.

---

## 📋 Bước 1: Tạo Google Cloud Project

### 1.1 Truy cập Google Cloud Console
- Mở trình duyệt và đi tới: **https://console.cloud.google.com/**
- Đăng nhập bằng tài khoản Google của bạn

### 1.2 Tạo Project mới
1. Click vào dropdown "Select a project" ở góc trên bên trái
2. Click **"NEW PROJECT"**
3. Đặt tên project: `Lang Huu Nghi Backup`
4. Click **"CREATE"**
5. Chờ vài giây để project được tạo
6. Chọn project vừa tạo từ dropdown

---

## 🔌 Bước 2: Kích hoạt Google Drive API

### 2.1 Vào trang APIs & Services
1. Từ menu bên trái, click **"APIs & Services"**
2. Click **"Library"**

### 2.2 Tìm và kích hoạt Google Drive API
1. Tìm kiếm **"Google Drive API"**
2. Click vào kết quả **"Google Drive API"**
3. Click nút **"ENABLE"** màu xanh
4. Chờ vài giây để API được kích hoạt

---

## 🔐 Bước 3: Tạo OAuth 2.0 Credentials

### 3.1 Cấu hình OAuth Consent Screen (lần đầu)
1. Từ menu bên trái, click **"APIs & Services"** → **"OAuth consent screen"**
2. Chọn **"External"** user type
3. Click **"CREATE"**
4. Điền thông tin:
   - **App name**: `Làng Hữu Nghị Database Backup`
   - **User support email**: Email của bạn
   - **Developer contact information**: Email của bạn
5. Click **"SAVE AND CONTINUE"**
6. Trang **"Scopes"**: Click **"SAVE AND CONTINUE"** (để trống)
7. Trang **"Test users"**: 
   - Click **"ADD USERS"**
   - Thêm email của bạn
   - Click **"SAVE AND CONTINUE"**
8. Review và click **"BACK TO DASHBOARD"**

### 3.2 Tạo OAuth 2.0 Client ID
1. Từ menu bên trái, click **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Chọn **"OAuth 2.0 Client IDs"**
4. Chọn Application type: **"Desktop application"**
5. Name: `Lang Huu Nghi Backup Client`
6. Click **"CREATE"**

### 3.3 Tải credentials.json
1. Sau khi tạo xong, sẽ xuất hiện popup với Client ID và Client Secret
2. Click **"DOWNLOAD JSON"**
3. File sẽ có tên dạng `client_secret_xxx.json`
4. **Đổi tên file thành `credentials.json`**
5. **Di chuyển file vào thư mục gốc của project** (cùng thư mục với file `Trang_chủ.py`)

---

## ⚙️ Bước 4: Cài đặt trong hệ thống

### 4.1 Kiểm tra file credentials.json
- Đảm bảo file `credentials.json` nằm trong thư mục gốc
- File cần có cấu trúc JSON với các key: `client_id`, `client_secret`, etc.

### 4.2 Khởi tạo hệ thống backup
1. Vào trang **"Quản lý Hệ thống"** trong ứng dụng
2. Chọn tab **"💾 Sao lưu & Khôi phục"**
3. Click nút **"🔧 Khởi tạo hệ thống sao lưu"**
4. Lần đầu sẽ mở trình duyệt để xác thực Google Drive
5. Đăng nhập và cho phép ứng dụng truy cập Google Drive
6. Quay lại ứng dụng và kiểm tra thông báo thành công

### 4.3 Thử nghiệm sao lưu thủ công
1. Click nút **"📤 Sao lưu ngay"**
2. Chờ quá trình sao lưu hoàn thành
3. Kiểm tra Google Drive của bạn - sẽ có thư mục mới tên **"Lang Huu Nghi Database Backups"**

---

## 🔒 Bảo mật và Lưu ý

### Quan trọng
- ⚠️ **KHÔNG** chia sẻ file `credentials.json` với ai
- ⚠️ **KHÔNG** commit file `credentials.json` lên Git/GitHub
- ⚠️ File `token.json` sẽ được tạo tự động - cũng không được chia sẻ

### Các file quan trọng
- `credentials.json`: Thông tin xác thực từ Google Cloud
- `token.json`: Token truy cập (tự động tạo)
- `last_backup.json`: Metadata về lần sao lưu cuối

### Tính năng tự động
- 📅 **Sao lưu hàng tuần**: Mỗi Chủ nhật lúc 2:00 AM
- 🗂️ **Quản lý dung lượng**: Chỉ giữ 10 bản sao lưu mới nhất
- 🔄 **Tự động xóa**: Các bản cũ sẽ được xóa tự động

---

## 🆘 Khắc phục sự cố

### Lỗi "credentials.json not found"
- Kiểm tra file có đúng tên và vị trí
- Đảm bảo file nằm cùng thư mục với `Trang_chủ.py`

### Lỗi xác thực Google
- Xóa file `token.json` và thử lại
- Kiểm tra email có trong danh sách Test Users

### Lỗi "Access denied"
- Kiểm tra Google Drive API đã được enable
- Kiểm tra OAuth consent screen đã được cấu hình đúng

### Cần hỗ trợ thêm?
- Kiểm tra logs trong tab Console của trình duyệt
- Đảm bảo có kết nối internet ổn định
- Thử tạo credentials mới nếu vẫn lỗi
