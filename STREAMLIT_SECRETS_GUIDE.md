# Hướng dẫn cấu hình Streamlit Secrets cho Google Drive

## Vấn đề hiện tại
```
Service Account JSON Invalid
GOOGLE_SERVICE_ACCOUNT_JSON trong Streamlit Secrets có vấn đề
```

## Nguyên nhân
- JSON bị thiếu hoặc không đúng format
- Copy/paste bị lỗi khi thêm vào Streamlit Secrets
- Thiếu các field bắt buộc trong Service Account JSON

## Giải pháp từng bước

### Bước 1: Tạo Service Account (nếu chưa có)
1. Vào: https://console.cloud.google.com/
2. Tạo project mới hoặc chọn project hiện có
3. **IAM & Admin → Service Accounts**
4. **CREATE SERVICE ACCOUNT**
   - Name: `lang-huu-nghi-backup`
   - Description: `Google Drive backup service`
5. **Keys → ADD KEY → Create new key → JSON**
6. Download file JSON

### Bước 2: Enable Google Drive API
1. **APIs & Services → Library**
2. Tìm "Google Drive API"
3. Click **ENABLE**

### Bước 3: Chia sẻ Google Drive folder
1. Tạo folder: "Lang Huu Nghi Database Backups"
2. Right-click → Share
3. Thêm email service account (từ JSON: `client_email`)
4. Quyền: **Editor**

### Bước 4: Cấu hình Streamlit Secrets
1. Vào Streamlit Cloud app dashboard
2. **Settings → Secrets**
3. Thêm secret mới:

**Key:** `GOOGLE_SERVICE_ACCOUNT_JSON`

**Value:** (toàn bộ nội dung file JSON)
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "1234567890abcdef",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "lang-huu-nghi-backup@your-project.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lang-huu-nghi-backup%40your-project.iam.gserviceaccount.com"
}
```

## Lưu ý quan trọng

### ❌ Lỗi thường gặp:
- **Thiếu dấu ngoặc:** Phải bắt đầu `{` và kết thúc `}`
- **Escape characters:** `\n` trong private_key phải được giữ nguyên
- **Trailing comma:** Không có dấu phẩy thừa ở cuối
- **Quote marks:** Tất cả strings phải có dấu ngoặc kép

### ✅ Cách kiểm tra:
1. Copy JSON vào online validator: https://jsonlint.com/
2. Đảm bảo có đủ các field bắt buộc:
   - `type`: "service_account"
   - `project_id`: string
   - `private_key`: string (có \\n)
   - `client_email`: email ending với .iam.gserviceaccount.com

### 🔧 Test trong app:
1. Sau khi cập nhật secrets, restart Streamlit app
2. Vào **System Management → Google Drive Backup**
3. Nhấn **"Test JSON Format"** để kiểm tra
4. Nếu thành công, nhấn **"Sao lưu ngay"**

## Kết quả mong đợi

**Trước khi sửa:**
```
🔧 Service Account JSON không hợp lệ
❌ Sao lưu thất bại
```

**Sau khi sửa:**
```
✅ Google Drive đã kết nối: Service Account Ready
✅ Sao lưu thành công lên Google Drive!
```

## Backup không cần OAuth

Service Account có ưu điểm:
- ✅ Không cần OAuth flow
- ✅ Không có redirect URI issues  
- ✅ Hoạt động ngay lập tức
- ✅ Phù hợp với production
- ✅ Tự động backup theo lịch