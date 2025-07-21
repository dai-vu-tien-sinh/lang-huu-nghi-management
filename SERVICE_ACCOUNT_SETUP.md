# Giải pháp Service Account cho Google Drive Backup

## Vì sao chuyển sang Service Account?

OAuth có nhiều vấn đề:
- ❌ Redirect URI phức tạp
- ❌ Cần verify app với Google
- ❌ Phải thêm test users
- ❌ Token hết hạn thường xuyên

Service Account đơn giản hơn:
- ✅ Không cần OAuth flow
- ✅ Không cần redirect URI
- ✅ Hoạt động ngay lập tức
- ✅ Phù hợp với production

## Cách setup Service Account

### Bước 1: Tạo Service Account
1. Vào: https://console.cloud.google.com/
2. Chọn project của bạn (hoặc tạo mới)
3. **IAM & Admin → Service Accounts**
4. Click **CREATE SERVICE ACCOUNT**

**Service account details:**
- Service account name: `lang-huu-nghi-backup`
- Service account ID: `lang-huu-nghi-backup`
- Description: `Google Drive backup for Lang Huu Nghi system`

### Bước 2: Tạo Key
1. Click vào service account vừa tạo
2. **Keys tab → ADD KEY → Create new key**
3. Chọn **JSON**
4. Download file JSON

### Bước 3: Enable Google Drive API
1. **APIs & Services → Library**
2. Tìm "Google Drive API"
3. Click **ENABLE**

### Bước 4: Chia sẻ Google Drive folder
1. Tạo folder trên Google Drive: "Lang Huu Nghi Database Backups"
2. Right-click → Share
3. Thêm email service account (từ JSON file)
4. Quyền: **Editor**

### Bước 5: Cập nhật Streamlit Secrets
Thay vì GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET, thêm:

```toml
GOOGLE_SERVICE_ACCOUNT_JSON = """{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "lang-huu-nghi-backup@your-project.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lang-huu-nghi-backup%40your-project.iam.gserviceaccount.com"
}"""
```

**Lưu ý:** Copy toàn bộ nội dung file JSON vào giá trị của GOOGLE_SERVICE_ACCOUNT_JSON

## Ưu điểm của Service Account

1. **Không cần OAuth** - Hoạt động ngay lập tức
2. **Không có redirect URI** - Không bị lỗi mismatch
3. **Không cần verify app** - Google không yêu cầu verification
4. **Tự động backup** - Scheduler hoạt động ổn định
5. **Production ready** - Phù hợp với Streamlit Cloud

## Implementation

Tôi sẽ tạo code mới sử dụng Service Account thay vì OAuth flow phức tạp.

Bạn có muốn tôi implement Service Account approach này không?