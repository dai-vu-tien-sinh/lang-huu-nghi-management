# Hướng dẫn đẩy code lên GitHub

Vì Replit có giới hạn với các thao tác Git, bạn cần thực hiện các bước sau để đẩy database và code lên GitHub:

## Bước 1: Tạo Personal Access Token trên GitHub

1. Đi tới GitHub.com và đăng nhập
2. Vào Settings > Developer settings > Personal access tokens > Tokens (classic)
3. Nhấn "Generate new token" > "Generate new token (classic)"
4. Đặt tên token: "Replit Lang Huu Nghi"
5. Chọn quyền: `repo` (full control of private repositories)
6. Nhấn "Generate token" và **lưu token này** (chỉ hiển thị 1 lần)

## Bước 2: Mở Shell trong Replit

Nhấn vào tab "Shell" trong Replit và chạy các lệnh sau:

```bash
# Xóa file lock nếu bị kẹt
rm -f .git/index.lock .git/config.lock

# Kiểm tra trạng thái
git status

# Thêm tất cả file (bao gồm database)
git add .

# Commit với message mô tả
git commit -m "Add complete Làng Hữu Nghị management system with database

- Complete Vietnamese management system for educational facility
- Student and veteran profile management 
- Medical records and class management
- Document attachment system with separate export
- Role-based access control (admin, teacher, doctor, family)
- Statistics and reporting with Plotly charts
- Google Drive backup integration
- Multi-house support (T2, T3, T4, T5, T6, N02)
- Sample database with Nguyễn Văn Học and attached documents
- Streamlit web interface with Vietnamese language support"
```

## Bước 3: Cấu hình authentication

```bash
# Cấu hình Git với thông tin của bạn
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"

# Push với token (thay YOUR_TOKEN bằng token từ bước 1)
git push https://YOUR_TOKEN@github.com/dai-vu-tien-sinh/lang-huu-nghi-management.git main
```

## Lệnh thay thế nếu cần

Nếu gặp lỗi, thử:

```bash
# Reset nếu cần
git reset --soft HEAD~1

# Force push (cẩn thận!)
git push --force-with-lease origin main
```

## Những gì sẽ được đẩy lên GitHub:

- ✅ Toàn bộ source code Python
- ✅ Database SQLite với dữ liệu mẫu
- ✅ Tài liệu Word đính kèm của Nguyễn Văn Học
- ✅ README.md chi tiết bằng tiếng Việt
- ✅ Các file cấu hình Streamlit
- ✅ Requirements và dependencies
- ✅ Hướng dẫn triển khai

## Xác nhận thành công

Sau khi push thành công, kiểm tra:
1. Vào https://github.com/dai-vu-tien-sinh/lang-huu-nghi-management
2. Xác nhận file `lang_huu_nghi.db` (~485KB) có mặt
3. Xem README.md hiển thị đúng
4. Kiểm tra các file Python và cấu hình

## Lưu ý bảo mật

- Database chứa dữ liệu thật, đảm bảo repository là private nếu cần
- Token GitHub có quyền cao, giữ bí mật
- Backup định kỳ cả code và database