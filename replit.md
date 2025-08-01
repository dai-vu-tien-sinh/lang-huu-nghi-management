# Hệ thống quản lý dữ liệu Làng Hữu Nghị

## Overview
This project is a comprehensive Streamlit application designed for multilingual data management within educational and organizational contexts. Its primary purpose is to provide advanced user role-based access control and intelligent record processing, particularly for institutions like Làng Hữu Nghị. The system focuses on granular user permissions, multilingual support, and adaptive administrative tools to cater to diverse organizational needs, aiming to streamline data handling and reporting.

## User Preferences
- **User management**: Only the main admin account (username: 'admin') can access user management. Other admin and administrative accounts are restricted. Counselor and nurse roles are removed from the system.
- **Data Entry**: Medical information management is redirected to a dedicated medical page. AI-generated summaries are replaced with handwritten note sections using blank lines for manual completion in reports.
- **Interface**: Google Drive backup functionality is moved to the system management page and removed from the homepage. User management tab is removed from the spreadsheet data management section. Simplified spreadsheet management to only include students, veterans, and medical records. System management tabs are reordered to: user management, spreadsheet management, Excel import, backup & restore. Admin functionality is merged into the system management page. Page order is reorganized so system management appears directly under homepage. All navigation menu items are removed from the sidebar, resulting in an empty sidebar. The separate search and print page is removed, and advanced search functionality is integrated directly into the profile management page with a dropdown interface. Manual database management is transformed into a safe spreadsheet-style interface with separate tabs for users, students, veterans, and medical records. The dangerous SQL query interface is replaced with controlled spreadsheet editing capabilities with proper data validation. Administration page is simplified by removing statistics, reports, and interface customization tabs, now only containing user management functionality. Statistics functionality is merged into the profile management page as a new "📊 Thống kê và báo cáo" tab. A separate "📤 Xuất dữ liệu" tab is added in profile management with Excel export capabilities. All English translation support is removed; the system is simplified to Vietnamese-only mode. Language selector and English translation dictionaries are eliminated. Navigation system is streamlined to use only Vietnamese names with proper diacritical marks. All page files are renamed to use proper Vietnamese diacritical marks. The psychology page is converted to a comprehensive medical records management page. Password visibility button is made smaller and square-shaped. Field label "Thông tin nhà chữ T" is simplified to "Nhà".
- **Reports**: Comprehensive Word report generation includes all student information, with medical history and teacher notes sections always displayed (even when empty). Field mapping issues in reports are corrected; gender field display is fixed, and "ID bệnh nhân" labels are changed to "ID học sinh". Class history tracking in reports is upgraded to include teacher names and detailed notes columns. Initial characteristics field ("Đặc điểm sơ bộ của bệnh nhân/cựu chiến binh khi vào làng") is added to both Student and Veteran models.
- **Backup**: Backup compatibility is enhanced for Supabase PostgreSQL database using custom SQL export instead of pg_dump. Backup system creates both SQL dumps and metadata fallbacks. Backup file formats are updated from .db to .sql/.json for better Supabase integration. Automatic weekly scheduling (Sundays 2AM) for backups is implemented, with a 10-backup limit.

## System Architecture
The application is built using the Streamlit framework with Python 3.11.
- **UI/UX Decisions**:
    - Comprehensive dark mode support and individual user theme preferences are implemented, with a `dark_mode` column in the `users` table for persistent theme preferences.
    - Theme system includes separate light/dark mode color palettes for all themes.
    - Page names and navigation elements are in Vietnamese with proper diacritical marks.
    - Password viewing capability is added for admin users with security warnings and role-based access control.
    - Enhanced user management interface with password visibility toggle and security warnings.
    - Integrated advanced search functionality directly into profile management with a dropdown interface.
    - Patient ID is displayed prominently in profile management and search results.
    - Medical records date display bug is fixed, using proper Vietnamese date format (DD/MM/YYYY).
    - Excel export functionality includes professional formatting, proper headers, merged cells, and auto-adjusted column widths.
    - System title throughout the application is "Hệ thống quản lý dữ liệu Làng Hữu Nghị".
- **Technical Implementations**:
    - **Authentication**: Role-based authentication and permission system (`auth.py`). Dynamic page access control based on user roles, ensuring pages only appear for authorized users.
    - **Database Management**: SQLAlchemy for database interactions, with `database.py` handling operations and `models.py` defining data models. PostgreSQL is the target database, with existing functionality for SQLite.
    - **Data Handling**:
        - Comprehensive student document management is included in the profile management page with upload, download, and delete capabilities.
        - Excel export includes all student and veteran fields for comprehensive data export.
        - Smart house detection and assignment for Excel imports automatically detects multiple houses in files and assigns students to correct houses based on proximity and pattern recognition. Optimized house detection system for specific organizational houses (T2, T3, T4, T5, T6) with smart pattern recognition, multiple house detection, dropdown selection, and custom house support.
        - Comprehensive student notes system in class management with categorized notes (Học tập, Hành vi, Sức khỏe, Gia đình, Khác), importance marking, role-based permissions for viewing/deleting, and teacher attribution. A `student_notes` database table is added with proper relationships.
    - **Reporting**:
        - Word document report generation functionality is implemented, including comprehensive document previews for images, PDFs, Word docs, Excel spreadsheets, and PowerPoint presentations with actual file content.
        - Plotly for interactive visualizations, with charts for class distribution.
        - PDF report generation includes student class assignments and class distribution data.
    - **Backup & Deployment**:
        - Service Account solution for Google Drive backup, avoiding OAuth redirect URI issues, suitable for Streamlit Cloud.
        - Supabase deployment package includes migration script with sample data and setup instructions.
        - Supabase Keep-Alive service is integrated to prevent database pausing.
- **Feature Specifications**:
    - **User Roles**:
        - **Admin (main account only)**: Full access including user management.
        - **Admin (other accounts)**: Full access except user management.
        - **Administrative**: Full access except user management.
        - **Teacher**: Class management, students, search students/psychological evaluations, statistics, print, data management.
        - **Doctor**: Medical records, students, veterans, search medical records, statistics, print, data management.
        - **Family**: View own child's information and general statistics only.
    - **Core Features**: Student and veteran record management, medical records management, class management, user management, data import/export (Excel), comprehensive reporting (Word, PDF), and system backup/restore.
    - **Language Support**: Vietnamese only.
- **System Design Choices**:
    - Modular architecture with `pages/` for individual features.
    - `i18n` for internationalization, though currently configured for Vietnamese only.
    - `config.toml` for Streamlit Cloud deployment settings (e.g., port 8501).
    - Environment variables used for sensitive information like database credentials and Google API keys.
    - Removal of direct SQL execution in favor of controlled spreadsheet-like interfaces for data integrity and security.

## External Dependencies
- **Streamlit**: Main application framework.
- **Plotly**: For interactive data visualizations and charting.
- **SQLAlchemy**: ORM for database interactions.
- **Google Drive API**: Used for backup functionality (via Service Account method).
- **Supabase**: Target PostgreSQL database for deployment, requiring specific SQL dump and backup strategies.
- **python-docx**: For generating Word documents.
- **pandas**: For Excel import/export functionalities.
- **kaleido**: For chart generation (specific version 0.2.1 for compatibility).