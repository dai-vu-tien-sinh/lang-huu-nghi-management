PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        , family_student_id INTEGER REFERENCES students(id), theme_preference TEXT DEFAULT 'Chính thức');
INSERT INTO users VALUES(1,'admin','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','admin','System Administrator','admin@langhunghi.edu.vn','2025-03-11 16:50:05',NULL,'Chính thức');
INSERT INTO users VALUES(2,'doctor1','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','doctor','Bác sĩ Nguyễn Văn A','doctor1@langhunghi.edu.vn','2025-03-11 16:50:05',NULL,'Chính thức');
INSERT INTO users VALUES(3,'doctor2','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','doctor','Bác sĩ Trần Thị B','doctor2@langhunghi.edu.vn','2025-03-11 16:50:05',NULL,'Chính thức');
INSERT INTO users VALUES(4,'teacher1','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','teacher','Giáo viên Phạm Văn C','teacher1@langhunghi.edu.vn','2025-03-11 16:50:05',NULL,'Chính thức');
INSERT INTO users VALUES(5,'counselor1','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','counselor','Tư vấn Lê Thị D','counselor1@langhunghi.edu.vn','2025-03-11 16:50:05',NULL,'Chính thức');
INSERT INTO users VALUES(6,'nurse1','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','nurse','Y tá Hoàng Thị E','nurse1@langhunghi.edu.vn','2025-04-10 15:36:37',NULL,'Chính thức');
INSERT INTO users VALUES(7,'nurse2','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','nurse','Y tá Vũ Văn F','nurse2@langhunghi.edu.vn','2025-04-10 15:36:37',NULL,'Chính thức');
INSERT INTO users VALUES(8,'admin1','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','administrative','Nhân viên Đỗ Thị G','admin1@langhunghi.edu.vn','2025-04-10 15:36:37',NULL,'Chính thức');
INSERT INTO users VALUES(9,'admin2','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','administrative','Nhân viên Nguyễn Văn H','admin2@langhunghi.edu.vn','2025-04-10 15:36:37',NULL,'Chính thức');
INSERT INTO users VALUES(10,'teacher2','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','teacher','Giáo viên Hoàng Thị I','teacher2@langhunghi.edu.vn','2025-04-10 15:36:37',NULL,'Chính thức');
INSERT INTO users VALUES(11,'counselor2','ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','counselor','Tư vấn Trịnh Văn K','counselor2@langhunghi.edu.vn','2025-04-10 15:36:37',NULL,'Chính thức');
CREATE TABLE classes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            academic_year TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        );
INSERT INTO classes VALUES(1,'Lớp 10A',3,'2023-2024','Lớp chất lượng cao');
INSERT INTO classes VALUES(2,'Lớp 11B',3,'2023-2024','Lớp thường');
CREATE TABLE families (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            guardian_name TEXT NOT NULL,
            relationship TEXT NOT NULL,
            occupation TEXT,
            address TEXT,
            phone TEXT,
            household_status TEXT,
            support_status TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        );
CREATE TABLE veterans (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            birth_date DATE NOT NULL,
            service_period TEXT,
            health_condition TEXT,
            address TEXT,
            email TEXT,
            contact_info TEXT,
            profile_image BLOB
        );
INSERT INTO veterans VALUES(1,'Phạm Văn Chiến','1960-05-20','1980-1985','Tốt','Hà Nội','veteran1@langhunghi.edu.vn','0912345678',NULL);
INSERT INTO veterans VALUES(2,'Nguyễn Thị Hòa','1965-11-15','1985-1990','Bình thường','Hồ Chí Minh','veteran2@langhunghi.edu.vn','0923456789',NULL);
INSERT INTO veterans VALUES(3,'Trần Văn Dũng','1963-08-25','1982-1987','Cần theo dõi','Hải Phòng','veteran3@langhunghi.edu.vn','0934567890',NULL);
CREATE TABLE periodic_assessments (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            academic_performance TEXT,
            health_condition TEXT,
            social_behavior TEXT,
            teacher_notes TEXT,
            doctor_notes TEXT,
            counselor_notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        );
CREATE TABLE supports (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            support_type TEXT NOT NULL,
            amount REAL,
            start_date DATE NOT NULL,
            end_date DATE,
            approval_status TEXT NOT NULL,
            approved_by INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        );
CREATE TABLE medical_records (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            patient_type TEXT NOT NULL,
            diagnosis TEXT,
            treatment TEXT,
            doctor_id INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            notification_sent BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        );
INSERT INTO medical_records VALUES(1,1,'student','Cảm cúm thông thường','Nghỉ ngơi và uống thuốc theo đơn',2,'2025-03-11 16:50:05','Theo dõi thêm 3 ngày',0);
INSERT INTO medical_records VALUES(2,2,'student','Đau đầu','Thuốc giảm đau và nghỉ ngơi',2,'2025-03-11 16:50:05','Tái khám sau 1 tuần',0);
INSERT INTO medical_records VALUES(3,1,'veteran','Đau lưng mãn tính','Vật lý trị liệu và thuốc giảm đau',3,'2025-03-11 16:50:05','Cần tập thể dục thường xuyên',0);
INSERT INTO medical_records VALUES(4,2,'veteran','Tăng huyết áp','Điều chỉnh chế độ ăn và thuốc',2,'2025-03-11 16:50:05','Tái khám định kỳ',0);
INSERT INTO medical_records VALUES(5,3,'veteran','Đau khớp','Thuốc giảm đau và vật lý trị liệu',3,'2025-03-11 16:50:05','Theo dõi tiến triển',0);
INSERT INTO medical_records VALUES(6,332,'student','ádf','ádfasdf',1,'2025-04-10 14:22:43','ádfasdf',0);
CREATE TABLE psychological_evaluations (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            evaluator_id INTEGER NOT NULL,
            assessment TEXT,
            recommendations TEXT,
            follow_up_date DATE,
            notification_sent BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (evaluator_id) REFERENCES users (id)
        );
INSERT INTO psychological_evaluations VALUES(1,1,'2025-03-11 16:50:05',5,'Thích nghi tốt với môi trường học tập','Tiếp tục theo dõi và khuyến khích','2024-04-01',0);
INSERT INTO psychological_evaluations VALUES(2,2,'2025-03-11 16:50:05',5,'Lo âu nhẹ về học tập','Cần tư vấn định kỳ và hỗ trợ học tập','2024-03-20',0);
INSERT INTO psychological_evaluations VALUES(3,3,'2025-03-11 16:50:05',5,'Khó khăn trong giao tiếp','Tham gia các hoạt động nhóm và rèn luyện kỹ năng','2024-03-25',0);
INSERT INTO psychological_evaluations VALUES(4,332,'2025-04-10 13:43:36',1,'dddddafadsf','afdasdf','2025-04-10',0);
INSERT INTO psychological_evaluations VALUES(5,332,'2025-04-10 13:43:59',1,'','','2025-04-10',0);
INSERT INTO psychological_evaluations VALUES(6,332,'2025-04-10 13:43:59',1,'','','2025-04-10',0);
INSERT INTO psychological_evaluations VALUES(7,332,'2025-04-10 13:44:03',1,'adsfasdf','aasdfasdfdasf','2025-04-10',0);
INSERT INTO psychological_evaluations VALUES(8,1665,'2025-04-10 13:51:14',1,'','','2025-04-10',0);
INSERT INTO psychological_evaluations VALUES(9,332,'2025-04-10 13:51:17',1,'','','2025-04-10',0);
INSERT INTO psychological_evaluations VALUES(10,332,'2025-04-10 13:51:21',1,'ádf','ádfasdf','2025-04-10',0);
INSERT INTO psychological_evaluations VALUES(11,1685,'2025-04-10 13:51:26',1,'ádf','ádfasdf','2025-04-10',0);
CREATE TABLE sidebar_preferences (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            page_order TEXT,  -- JSON array of page names in order
            hidden_pages TEXT, -- JSON array of hidden page names
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
CREATE TABLE student_class_history (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        );
CREATE TABLE IF NOT EXISTS "students" (
        id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        birth_date DATE,
        address TEXT,
        email TEXT,
        admission_date DATE,
        class_id INTEGER,
        health_status TEXT,
        academic_status TEXT,
        psychological_status TEXT,
        profile_image BLOB,
        gender TEXT,
        phone TEXT,
        year TEXT,
        parent_name TEXT,
        FOREIGN KEY (class_id) REFERENCES classes (id)
    );
INSERT INTO students VALUES(1,'Nguyễn Văn Học','2000-01-15','Hà Nội','student1@langhunghi.edu.vn','2023-09-01',1,'Xuất sắc','Tốt','Ổn định',NULL,'Nam',NULL,NULL,NULL);
INSERT INTO students VALUES(2,'Trần Thị Mai','2001-03-20','Hải Phòng','student2@langhunghi.edu.vn','2023-09-01',1,'Tốt','Bình thường','Tốt',NULL,'Nữ',NULL,NULL,NULL);
INSERT INTO students VALUES(3,'Lê Văn Nam','2000-07-10','Đà Nẵng','student3@langhunghi.edu.vn','2023-09-01',2,'Trung bình','Cần chú ý','Cần theo dõi',NULL,'Nam',NULL,NULL,NULL);
INSERT INTO students VALUES(332,'Bùi  Thị Ngọc Tú','2000-01-01','Quang Yên, Sông Lô, Vĩnh Phúc','bùi.thị.ngọc.tú@langhunghi.edu.vn','2014-04-22',NULL,'Chưa đánh giá','Bình thường','Ổn định',NULL,'Nữ',NULL,NULL,NULL);
INSERT INTO students VALUES(1605,'Bùi Thị Tiềm','1996-01-15','Thôn Yên, Kim Truy, Kim Bôi, Hòa Bình','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2007','Bùi Minh Tươm');
INSERT INTO students VALUES(1606,'Nguyễn T. Vân Long','1905-06-08','Ý Yên, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','1998','');
INSERT INTO students VALUES(1607,'Nguyễn T. Chi Mai',NULL,'SN 127, TDP số 10, đường Phúc Diễn, Bắc Từ Liêm, HN',NULL,'2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0983132004',NULL,'Dương Thúy Loan');
INSERT INTO students VALUES(1608,'Nguyễn T. Linh Mỹ','1996-06-10','Xóm 16, Trực Nội, Trực Ninh, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.350.394.6640','2009','Phạm Thị Tươi');
INSERT INTO students VALUES(1609,'Trần Thị Thu','1996-03-06','Xóm Nhất Nhị, Hương Canh, Bình Xuyên, Vĩnh Phúc','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.2113899392','42009','Trần Văn Kiểm');
INSERT INTO students VALUES(1610,'Trịnh Thị Liên','1983-10-04','Xóm 3, Hoằng Khê, Hoằng Hóa, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2007','Trịnh Xuân Quý');
INSERT INTO students VALUES(1611,'Phạm Thị Nga','1994-07-06','Xóm 4, An Xá, Quốc Tuấn, Nam Sách, Hải Dương','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0936763341','2.7.2010','Phạm Công Hà');
INSERT INTO students VALUES(1612,'Vũ Thị Thu','1905-06-13','Đa Lộc, Ân Thi, Hưng Yên','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.1664336166','17.10.2011','');
INSERT INTO students VALUES(1613,'Lê Thị Ngọc Hân','1992-11-27','Thôn Bãi Sậy I, Tân Dân, Khoái Châu, Hưng Yên','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.986248867','3.9.2012','Lê Minh Ngân');
INSERT INTO students VALUES(1614,'Nguyễn T. Thùy Linh','2004-10-21','SN 8, Ngách 148/42, xóm 3, Hòe Thị, Phương Canh, Nam TL, HN','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0386882173','3.9.2012','Ng. Xuân Cường');
INSERT INTO students VALUES(1615,'Đỗ Phương Dung','1905-06-22','Xuân Đỉnh, Bắc Từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2011','Đỗ Vũ Hùng');
INSERT INTO students VALUES(1616,'Mai Quang Vinh','1996-02-10','Thôn Thuần Hậu, Xuân Minh, Thọ Xuân, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2009','');
INSERT INTO students VALUES(1617,'Nguyễn Hữu Hoài Nam','1905-06-24','Sn21, Ngõ 118, xóm Chùa, Triều Khúc, Tân Triều, Thanh Trì, HN','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.945111819','4.4.2012','Nguyễn Hữu Tấn');
INSERT INTO students VALUES(1618,'Nguyễn Hải Nam','2007-06-11','SN 9, ngách 32/45 phố Viện, tổ 8, P. Đức Thắng, Bắc TL, HN','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0367362169','21.4.2014','Phan Thị Mến');
INSERT INTO students VALUES(1619,'Đỗ Hồng Hà','1999-05-11','Xóm 10, Nam Điền, Nghĩa Hưng, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2016-07-18 00:00:00','B: Đỗ Quang Ổn');
INSERT INTO students VALUES(1620,'Lương Thị Bích','2000-05-20','Bản Na, Mường Na 1, Hữu Kiện, Kỳ Sơn, Nghệ An','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0852568849','2016-09-20 00:00:00','Lương Văn Trọng');
INSERT INTO students VALUES(1621,'Mai Phương Linh','2010-03-12','Thôn Thuần Hậu, Xuân Minh, Thọ Xuân, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2017-02-17 00:00:00','');
INSERT INTO students VALUES(1622,'Lê Thị Hà Vy','2007-01-13','Thôn Thiên Lộc, Xuân Minh, Thọ Xuân, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2017-02-17 00:00:00','');
INSERT INTO students VALUES(1623,'Lê Tuấn Minh','2005-10-22','Sn 64, thôn 3, xã Tân Mỹ, Tp, Bắc Giang, tỉnh Bắc Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0967581212','2022-07-15 00:00:00','Lê Xuân Hùng');
INSERT INTO students VALUES(1624,'Trần Đức Tài','2005-06-15','Tổ 5, Sài Đồng, Long Biên, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.913313041','20.11.2012','Trần Quốc Tuấn');
INSERT INTO students VALUES(1625,'Lê Văn Đô','1905-06-13','An Khang, Yên Sơn, Tuyên Quang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2007','');
INSERT INTO students VALUES(1626,'Trịnh Quốc Bảo','1905-06-17','Thanh Oai, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2005','');
INSERT INTO students VALUES(1627,'Hoàng Trung Kiên','1997-11-29','TDP 12, TT Yên Thế, Lục Yên, Yên Bái','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0393947387','2010','Hoàng Văn Mới');
INSERT INTO students VALUES(1628,'Nguyễn Hồng Việt','1999-11-18','103, B11, TT. Trại Găng, Thanh Nhàn, HN','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.986121572','2012','Diêm Thị Chung');
INSERT INTO students VALUES(1629,'Nguyễn Bá Dương','2004-10-09','Xuân Phương, Nam Từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.975603881','4.4.2012','Nguyễn Bá Nam');
INSERT INTO students VALUES(1630,'Hoàng Minh Tuấn','2002-01-31','Nguyên Xá, Minh Khai, Bắc Từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.1675143539','25.9.2012','Hoàng Minh Trí');
INSERT INTO students VALUES(1631,'Nguyễn Tuấn Dương','2003-10-11','Số 1, Ngõ 66, Ngọc Lâm, Long Biên, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.904026946','25.9.2013','Nguyễn Văn Vinh');
INSERT INTO students VALUES(1632,'Phạm Quang Vinh','2004-01-17','Xóm 8, Thị Cấm, Xuân Phương, Nam TL, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.1656793986','12.3.2014','Phạm Đức Ninh');
INSERT INTO students VALUES(1633,'Nguyễn Bá Hải Đăng','1999-07-03','P1101, Nhà N02, Dịch Vọng, Cầu Giấy, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','13.10.2015','Nguyễn Hồng Hải');
INSERT INTO students VALUES(1634,'Lưu Hồng Anh','2005-09-18','Nhuệ Giang, Tây Mỗ, Nam Từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2015-12-17 00:00:00','Lưu Hồng Hoàng');
INSERT INTO students VALUES(1635,'Lý Bá Đức Khánh','2010-07-21','Thôn Dền, Di Trạch, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.1626889521','2016-08-05 00:00:00','Bùi Thị Phương');
INSERT INTO students VALUES(1636,'Lý Văn Mưu','2010-11-18','Thôn Tam Mò, xã Yên Định, Bắc Mê, Hà Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0367802373','2016-10-12 00:00:00','Lý Văn Dũng');
INSERT INTO students VALUES(1637,'Nguyễn Trọng Vũ ( Khôi)',NULL,'Số 111, đường Phúc Diễn, Bắc Từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0912778401','2017','Phùng Văn Công');
INSERT INTO students VALUES(1638,'Khuất Đình Hồng Phúc','1998-05-21','Cẩm Yên, Thạch Thất, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2018-03-20 00:00:00','Khuất Đình Cát');
INSERT INTO students VALUES(1639,'Bùi Tất Việt','1905-06-30','KĐT Tân Tây Đô, Đan Phượng, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2019','Vũ Thị Thanh Hương');
INSERT INTO students VALUES(1640,'PHạm Đức Quang','2007-01-13','Số 68, ngõ 344, Ngọc Thụy, Long Biên, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2022-05-11 00:00:00','');
INSERT INTO students VALUES(1641,'Phạm Gia Huy','2009-01-05','Thôn Đình Rối, Đại Đồng, Thạch Thất, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.37399369','2019','Kiều Thị Hoa');
INSERT INTO students VALUES(1642,'Hoàng Tiến Đạt','2005-01-07','Thôn Mỹ Cầu, Tân Mỹ, Tp. Bắc Giang, Bắc Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','','');
INSERT INTO students VALUES(1643,'Nguyễn Vũ Anh Kiệt','2012-04-30','Thôn An A, An Thượng, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2022-05-19 00:00:00','');
INSERT INTO students VALUES(1644,'Lê Bảo Châu','1905-06-18','TT. Quế, Kim Bảng, Hà Nam','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2008','');
INSERT INTO students VALUES(1645,'Nguyễn Việt Cường','1983-01-16','Tổ 13, Khu Sa Đéc, P. Hùng Vương, Thị xã Phú Thọ, Phú Thọ','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2023-02-23 00:00:00','');
INSERT INTO students VALUES(1646,'Đoàn Trung Đức','1996-12-20','Tổ 1, Phường Hoàng Diệu, Tp. Thái Bình, Thái Bình','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0378548919','2005','Đoàn Đức Khiêm');
INSERT INTO students VALUES(1647,'Nguyễn Văn Đức','1905-06-20','Nghĩa Châu, Nghĩa Hưng, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2009','Nguyễn Thị Tuyết');
INSERT INTO students VALUES(1648,'Nguyễn Công Hậu','1905-06-14','Gia Sinh, Gia Viễn, Ninh Bình','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.1689486725','21.11.2011','');
INSERT INTO students VALUES(1649,'Lý Đức Giang','2002-10-09','Xóm 1, Lại Yên, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.985520686','18.5.2012','Lý Đức Sơn');
INSERT INTO students VALUES(1650,'Nguyễn Đức Mỵ','1905-06-12','Vị Xuyên, Hà Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2010','');
INSERT INTO students VALUES(1651,'Đỗ Hải Dương','2004-08-20','Minh Khai, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.433997229','3.9.2012','Đỗ Khắc Hiển');
INSERT INTO students VALUES(1652,'Nguyễn Hoàn Năm','2007-01-12','Số 9, dãy T, Khu T2, hậu cần đoàn 5, Phùng Khoang, HN','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.439950878','6.9.2013','Nguyễn Thanh Ngân');
INSERT INTO students VALUES(1653,'Ninh Quốc Trung','2004-08-20','65/29/78 Khương Hạ, Khương Đình, Thanh Xuân, HN','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.978591588','12.3.2014','Phạm Văn Lâm');
INSERT INTO students VALUES(1654,'Trần Văn Đức','1997-10-14','TDP. Cửu Yên 1, Hợp Châu, Tam Đảo, Vĩnh Phúc','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.924428792','22.4.2014','Trần Văn Sáu');
INSERT INTO students VALUES(1655,'Nguyễn Văn Kiên','2001-06-28','Xóm 6, Ứng Hòe, Ninh Giang, Hải Dương','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.1655817115','5.9.2014','Nguyễn Văn Minh');
INSERT INTO students VALUES(1656,'Phạm Văn Ngọc','2001-01-01','Thôn Làng Dò, Cẩm Vân, Cẩm Thủy, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.948619284','7.10.2014','Phạm Văn Tuấn');
INSERT INTO students VALUES(1657,'Nguyễn Văn Anh Đức','2006-06-26','Thôn Nhuệ, Đức Thượng, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.1216084634','20.11.2014','Nguyễn Văn Dũng');
INSERT INTO students VALUES(1658,'Nguyễn Văn Thắng','2004-07-24','Thôn Hát, Xã Việt Lâm, Vị Xuyên, Hà Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0372401716','23.6.2015','Nguyễn Văn Tuyên');
INSERT INTO students VALUES(1659,'Nguyễn Hữu Tất Thành','2006-04-13','Tổ 2, Thị Trấn Kim Bài, Thanh Oai, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0977462118','4.8.2015','Nguyễn Hữu Thư');
INSERT INTO students VALUES(1660,'Nguyễn Đức Thọ','1998-05-08','Thôn Sơn Thịnh, xã Lãng Sơn, Yên Dũng, Bắc Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2018-03-05 00:00:00','Nguyễn Đức Ba');
INSERT INTO students VALUES(1661,'Vũ Viết Cường','2009-08-15','Thôn Thượng, Dương Đức, Lạng Giang, Bắc Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2018-05-03 00:00:00','');
INSERT INTO students VALUES(1662,'Nguyễn Ngọc Đức','2006-10-04','Số 18 ngõ 1, Giảng Võ, Ba Đình, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','','');
INSERT INTO students VALUES(1663,'Nguyễn Trung Đức','2007-01-28','Xóm Ba Giăng, Bản Ngoại, Đại Từ, Thái nguyên','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0979732875','2019-05-06 00:00:00','Nguyễn Khắc Mạnh');
INSERT INTO students VALUES(1664,'Phùng Hoài An','2011-01-21','Cụm 4, Vân Phúc, Phúc Thọ, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0988244261','2019-06-11 00:00:00','Phùng Minh Toàn');
INSERT INTO students VALUES(1665,'Bùi Mạnh Quân','2005-12-16','Vân Lũng, An KHánh, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0327839440','2019-06-11 00:00:00','');
INSERT INTO students VALUES(1666,'Giao Hồng Phúc','2006-09-30','Xóm 7A, Nghĩa Thuận, TX. Thái Hòa, Nghệ An','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0985940884','2020-06-19 00:00:00','Giao Khánh Hưng');
INSERT INTO students VALUES(1667,'Vương Đình Nhất','2001-12-17','Xã Bắc Sơn, Sóc Sơn, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0364326635','2021-04-01 00:00:00','Vương Đình Tầm');
INSERT INTO students VALUES(1668,'Hoàng Hữu Điền','1985-07-02','Thôn Tranh Xuyên, Đồng Tâm, Ninh Giang, Hải Dương','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2023','');
INSERT INTO students VALUES(1669,'Nguyễn Đăng Bảo Việt','2009-07-25','Nguyên Xá, Minh Khai, Bắc Từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2013','Nguyễn Nam Phong');
INSERT INTO students VALUES(1670,'Nguyễn Thị Yến','1987-11-20','Thôn Cẩn Du, xã Quỳnh Sơn, Quỳnh Phụ, Thái Bình','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2004','');
INSERT INTO students VALUES(1671,'Hoàng Thị Hường','1994-05-19','Xóm 2, Hà Thiệp, Võ Ninh, Quảng Bình','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.1686517360','31.3.2013','Hoàng Xuân Hùng');
INSERT INTO students VALUES(1672,'Trần Thị Nguyệt Thương','2003-10-31','Xóm 3, Mỹ Thắng, Mỹ Lộc, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.1289288574','20.8.2013','Trần Ngọc Bích');
INSERT INTO students VALUES(1673,'Ngụy Thị Ngọc Thu','1905-06-25','Yên Dũng, Bắc Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2009','');
INSERT INTO students VALUES(1674,'Nguyễn Thị Vân','1998-06-17','Tổ 12, TT Vị Xuyên, Vị Xuyên, Hà Giang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2007','Nguyễn Sinh Tuyết');
INSERT INTO students VALUES(1675,'Nguyễn Thị Linh','1999-03-28','Xóm 8, xã Vĩnh Hòa, Ninh Giang, Hải Dương','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2010','');
INSERT INTO students VALUES(1676,'Phan T. Lan Hương','2007-09-23','Xóm 8, Đội 11, Nghĩa Phong, Nghĩa Hưng, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2011','Phan Văn Thái');
INSERT INTO students VALUES(1677,'Đặng Thị Nụ','1905-06-20','Thường Tín, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2011','');
INSERT INTO students VALUES(1678,'Phạm Văn Mạnh','2006-11-20','Xóm 7, Xuân Thủy, Xuân Trường, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.1669118837','2.5.2012','Phạm Văn Tường');
INSERT INTO students VALUES(1679,'Đỗ Quang Hưng','1905-06-26','TT. Cầu Diễn, Nam Từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2010','');
INSERT INTO students VALUES(1680,'Bùi Thị Ngọc Tú','1905-06-22','Quang Yên, Sông Lô, Vĩnh Phúc','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.1672789109','22.4.2014','Bùi Đức Toản');
INSERT INTO students VALUES(1681,'Nguyễn Thị Mai Ánh','2003-06-06','Khu Đỗ Xá, P. Tứ Minh, TP.Hải Dương, Hải Dương','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.946240123','5.9.2014','Nguyễn Văn Ba');
INSERT INTO students VALUES(1682,'Nguyễn Bảo Long','2010-04-01','SN 3, dãy B, KTT Đường sắt, Ngọc Khánh, Ba ĐÌnh, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','28.7.2020','Nguyễn Xuân Đông');
INSERT INTO students VALUES(1683,'Nguyễn Tiến Hưng','2006-10-31','Khu 5, Cấp Dẫn, Cẩm Khê, Phú Thọ','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2018-05-08 00:00:00','Nguyễn Trần Tiến');
INSERT INTO students VALUES(1684,'Tần Thị Ngân','1997-09-29','Xóm 4, xã Trung Phúc Cường, Nam Đàn, Nghệ An','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2022-09-12 00:00:00','');
INSERT INTO students VALUES(1685,'Bế Thị Hằng','1984-01-01','Xóm Đầu Cầu 2, Quảng Hưng, Quảng Hòa, Cao Bằng','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2023-01-06 00:00:00','');
INSERT INTO students VALUES(1686,'Lê Văn Hiếu','2007-08-19','Thôn 7, xã Xuân Lai, Thọ Xuân, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2023-02-17 00:00:00','');
INSERT INTO students VALUES(1687,'Vũ Thị Oanh','1989-07-26','9/8/45 Phạm Ngọc Thạch , Phường Lộc Hạ, Tp Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2023-05-23 00:00:00','');
INSERT INTO students VALUES(1688,'Vũ Thị Bình','1996-08-07','Xóm 11, Trực Thanh, Trực Ninh, Nam Định','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2005','Vũ Xuân Thông');
INSERT INTO students VALUES(1689,'Thế Bảo Trâm','1905-06-18','Đan Phượng, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2005','');
INSERT INTO students VALUES(1690,'Nguyễn Thị Chung','1993-12-12','Thôn Trường Cửu, xã Hùng Tiến, Nam Đàn, Nghệ An','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2008','Nguyễn Công Trường');
INSERT INTO students VALUES(1691,'Hà Thị Dung','1999-01-24','Chiêm Hóa, Tuyên Quang','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2009','');
INSERT INTO students VALUES(1692,'Bùi Thị Hóa','1983-07-29','Quảng Trạch, Quảng Bình','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2010','Bùi Vọng');
INSERT INTO students VALUES(1693,'Lê Thị Linh','1995-08-24','Thôn Trung Lập 3, Xuân Lập, Thọ Xuân, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2006','Lê Văn Năm');
INSERT INTO students VALUES(1694,'Nguyễn Thị Nhật Lệ','1905-06-18','Mê Linh, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','0.435250812','2010','Nguyễn Trọng Tuấn');
INSERT INTO students VALUES(1695,'Nguyễn Quỳnh Anh','1905-06-24','Minh Khai, Bắc từ Liêm, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','0.437655309','2012','Nguyễn Trọng Long');
INSERT INTO students VALUES(1696,'Lưu Quỳnh Chi','2007-06-16','Tổ dân phố 2, Miêu Nha, Tây Mỗ, Nam Từ Liêm, HN','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','0.974514972','3.9.2012','Lưu Quang Nhượng');
INSERT INTO students VALUES(1697,'Đinh Văn Hải','1905-06-27','Kim Chung, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','','2012','Đinh Văn Dũng');
INSERT INTO students VALUES(1698,'Trần Sơn Hiếu','2002-01-31','Vân Canh, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nam','0.936728835','3.9.2012','Trần Sơn Thảo');
INSERT INTO students VALUES(1699,'Nguyễn Gia Bảo','2020-09-06','Xóm 7, Nghĩa Thuận, Thái Hòa, Nghệ An','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','0.988511422','2020-06-26 00:00:00','Nguyễn Văn Tư');
INSERT INTO students VALUES(1700,'Đinh Thị Hương','2002-09-02','Hà Vân, Hà Long, Hà Trung, Thanh Hóa','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.3765.53688','15.5.2012','Đinh Công Tuệ');
INSERT INTO students VALUES(1701,'Chu Thị Kim Ngân','2009-12-30','Xóm 4, Ngãi Cầu, An Khánh, Hoài Đức, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','0.984812873','2018-04-11 00:00:00','Chu Hưng Hải');
INSERT INTO students VALUES(1702,'Đoàn Thị Thanh','1997-10-29','Số nhà 25, ngõ 15, Ngô Đức Mai, Xóm 1, Hưng chính, TP Vinh, Nghệ An','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2016-09-20 00:00:00','Đoàn Thanh Bình');
INSERT INTO students VALUES(1703,'Nguyễn T. Phương Hòa','1905-06-30','Ứng Hòa, Hà Nội','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'','','2017','');
INSERT INTO students VALUES(1704,'Hoàng Phương Hà','2008-06-13','Quảng Trạch, Quảng Bình','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2019-12-01 00:00:00','');
INSERT INTO students VALUES(1705,'Trần Thị Mỹ Duyên','2008-02-28','Nam Thung, Vân Diên, Nam Đàn, Nghệ An','','2025-03-27',NULL,'Chưa đánh giá','Bình thường',NULL,NULL,'Nữ','','2019-10-09 00:00:00','');
INSERT INTO students VALUES(1706,'Nguyễn Văn A','2007-10-18','Thị Trấn A, tỉnh b','','2025-04-10',NULL,'Tốt','Xuất sắc','Ổn định',NULL,'Nam','0961933121','2018','Nguyễn Văn B');
COMMIT;
