# Khắc phục lỗi Redirect URI - Google OAuth

## Lỗi hiện tại
```
Bạn không thể đăng nhập vào ứng dụng này vì ứng dụng không tuân thủ chính sách OAuth 2.0 của Google.
Request details: redirect_uri=http://localhost:8080
```

## Nguyên nhân
Redirect URI trong Google Cloud Console đang được cấu hình cho development (localhost:8080) thay vì production Streamlit Cloud URL.

## Giải pháp từng bước

### Bước 1: Truy cập Google Cloud Console
1. Đi tới: https://console.cloud.google.com/
2. Chọn project của bạn
3. Vào: **APIs & Services → Credentials**

### Bước 2: Sửa OAuth 2.0 Client
1. Tìm OAuth 2.0 Client ID đã tạo
2. Click vào tên để edit
3. Xem phần **Authorized redirect URIs**

### Bước 3: Cập nhật Redirect URIs
**Xóa:**
```
http://localhost:8080
```

**Thêm (thay your-app-name bằng tên app thực):**
```
https://your-app-name.streamlit.app
https://your-app-name.streamlit.app/
```

**Ví dụ nếu app của bạn là "lang-huu-nghi":**
```
https://lang-huu-nghi.streamlit.app
https://lang-huu-nghi.streamlit.app/
```

### Bước 4: Lưu thay đổi
Click **Save** trong Google Cloud Console

### Bước 5: Restart Streamlit App
1. Vào Streamlit Cloud dashboard
2. Tìm app của bạn
3. Click ⋮ → Reboot

## Kiểm tra URL app của bạn

Để tìm chính xác URL Streamlit Cloud:
1. Vào https://share.streamlit.io/
2. Tìm app "lang-huu-nghi-management" 
3. URL sẽ có dạng: `https://[random-name].streamlit.app`

## Cấu hình đầy đủ trong Google Cloud

**Authorized JavaScript origins:**
```
https://your-app-name.streamlit.app
```

**Authorized redirect URIs:**
```
https://your-app-name.streamlit.app
https://your-app-name.streamlit.app/
```

## Test sau khi sửa

1. Vào System Management trong app
2. Click "Lấy URL xác thực"
3. URL sẽ redirect đúng về Streamlit app thay vì localhost
4. Hoàn thành OAuth flow thành công

## Lưu ý quan trọng

- **Không sử dụng localhost** trong production
- **Phải match chính xác** với URL Streamlit Cloud
- **Có thể mất 5-10 phút** để Google cập nhật thay đổi
- **Thêm cả hai dạng** (có và không có trailing slash)

Sau khi sửa xong, Google Drive backup sẽ hoạt động hoàn hảo!