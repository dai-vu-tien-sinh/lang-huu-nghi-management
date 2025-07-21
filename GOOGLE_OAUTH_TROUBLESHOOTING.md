# Khắc phục sự cố Google OAuth - URL xác thực không hoạt động

## Nguyên nhân có thể

### 1. Client ID hết hạn hoặc bị vô hiệu hóa
- Google Cloud Project bị tạm ngưng
- OAuth Client bị xóa hoặc vô hiệu hóa
- Credentials được tạo lại với ID mới

### 2. Redirect URI không khớp
- URL trong Google Console khác với Streamlit app URL
- Thiếu trailing slash (/) trong redirect URI

### 3. Ứng dụng chưa được verify
- App đang ở chế độ testing
- Cần thêm test users trong Google Console

## Giải pháp từng bước

### Bước 1: Kiểm tra Google Cloud Console
1. Truy cập: https://console.cloud.google.com/
2. Chọn project: `lang-huu-nghi-backup`
3. Vào: **APIs & Services → Credentials**
4. Kiểm tra OAuth 2.0 Client IDs có tồn tại không

### Bước 2: Tạo lại Credentials (nếu cần)
```
Application type: Web application
Name: Lang Huu Nghi Backup Client

Authorized JavaScript origins:
https://your-app-name.streamlit.app

Authorized redirect URIs:
https://your-app-name.streamlit.app/
https://your-app-name.streamlit.app
```

### Bước 3: Cập nhật Streamlit Secrets
1. Vào Streamlit Cloud dashboard
2. Settings → Secrets
3. Cập nhật với Client ID và Secret mới:
```toml
GOOGLE_CLIENT_ID = "your-new-client-id"
GOOGLE_CLIENT_SECRET = "your-new-client-secret"
```

### Bước 4: Thêm Test Users (quan trọng)
1. Trong Google Cloud Console
2. **APIs & Services → OAuth consent screen**
3. Scroll xuống "Test users"
4. Click "ADD USERS"
5. Thêm email address của bạn

### Bước 5: Restart Streamlit App
Sau khi cập nhật secrets, restart app trên Streamlit Cloud

## Kiểm tra nhanh

### Test Client ID format
Client ID phải có định dạng:
```
1234567890-abcdefghijklmnop.apps.googleusercontent.com
```

### Test trong browser
Thử URL này (thay YOUR_CLIENT_ID):
```
https://accounts.google.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&scope=https://www.googleapis.com/auth/drive.file&redirect_uri=https://your-app.streamlit.app
```

## Giải pháp thay thế

### Tùy chọn 1: Tạo project mới
1. Tạo Google Cloud Project mới
2. Enable Google Drive API
3. Tạo OAuth credentials mới
4. Cập nhật Streamlit secrets

### Tùy chọn 2: Sử dụng Service Account (khuyến nghị)
Thay vì OAuth, có thể dùng Service Account:
1. Tạo Service Account trong Google Cloud
2. Download JSON key file
3. Upload vào Streamlit secrets
4. Sửa code để dùng Service Account authentication

### Tùy chọn 3: Tắt backup tạm thời
Nếu cần deploy ngay, có thể tắt Google Drive backup:
```python
# Trong pages/01_Quản_lý_Hệ_thống.py
BACKUP_AVAILABLE = False  # Tắt backup tạm thời
```

## Lệnh kiểm tra
Sau khi cập nhật, kiểm tra logs:
```
INFO:gdrive_backup:Google Drive credentials configured but OAuth authentication required
```

Thay vì:
```
ERROR:gdrive_backup:No valid credentials found
```

Bạn có muốn tôi tạo hướng dẫn Service Account thay thế không?