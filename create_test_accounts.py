import hashlib
import sqlite3
import os

def add_user(conn, username, password, role, full_name, email=None):
    try:
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
            (username, password_hash, role, full_name, email)
        )
        conn.commit()
        print(f"Đã tạo tài khoản {username} với vai trò {role}")
        return True
    except sqlite3.IntegrityError as e:
        print(f"Lỗi khi tạo tài khoản {username}: {e}")
        return False

def main():
    # Kết nối đến cơ sở dữ liệu
    conn = sqlite3.connect("lang_huu_nghi.db")
    
    # Danh sách tài khoản cần tạo
    accounts = [
        # Tài khoản y tá
        ("nurse1", "password123", "nurse", "Y tá Hoàng Thị E", "nurse1@langhunghi.edu.vn"),
        ("nurse2", "password123", "nurse", "Y tá Vũ Văn F", "nurse2@langhunghi.edu.vn"),
        
        # Tài khoản nhân viên hành chính
        ("admin1", "password123", "administrative", "Nhân viên Đỗ Thị G", "admin1@langhunghi.edu.vn"),
        ("admin2", "password123", "administrative", "Nhân viên Nguyễn Văn H", "admin2@langhunghi.edu.vn"),
        
        # Tạo thêm tài khoản cho các vai trò khác để có nhiều lựa chọn hơn
        ("teacher2", "password123", "teacher", "Giáo viên Hoàng Thị I", "teacher2@langhunghi.edu.vn"),
        ("counselor2", "password123", "counselor", "Tư vấn Trịnh Văn K", "counselor2@langhunghi.edu.vn"),
    ]
    
    # Tạo các tài khoản
    for username, password, role, full_name, email in accounts:
        add_user(conn, username, password, role, full_name, email)
    
    # Đóng kết nối
    conn.close()
    
    print("Hoàn thành việc tạo các tài khoản thử nghiệm!")

if __name__ == "__main__":
    main()