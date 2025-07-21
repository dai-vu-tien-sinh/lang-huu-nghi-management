# Hệ thống quản lý dữ liệu Làng Hữu Nghị

Comprehensive Vietnamese educational data management system built with Streamlit.

## Features

- **Student Management**: Complete profile management with 107+ students
- **Medical Records**: Medical history tracking and documentation
- **Document Management**: Upload/download student documents
- **Class Management**: Teacher notes and class assignments
- **Vietnamese Interface**: Complete Vietnamese language support
- **Role-based Access**: Admin, teacher, doctor, family user roles
- **Reporting**: Excel export and Word report generation
- **Google Drive Backup**: Automated database backup system

## Quick Start

### Streamlit Cloud Deployment

1. **Connect Repository**: Link this GitHub repo to Streamlit Cloud
2. **Set Secrets**: Add environment variables in Streamlit Cloud Settings → Secrets:

```toml
# Database Configuration
DATABASE_URL = "your-supabase-postgresql-url"
PGDATABASE = "postgres"
PGHOST = "your-supabase-host"
PGPORT = "6543"
PGUSER = "your-supabase-user"
PGPASSWORD = "your-supabase-password"

# Google Drive Backup (Optional)
GOOGLE_SERVICE_ACCOUNT_JSON = """your-service-account-json"""
```

3. **Deploy**: App will be available at your-app.streamlit.app

### Local Development

```bash
pip install -r streamlit_requirements.txt
streamlit run Trang_chủ.py --server.port 5000
```

## Login Credentials

**Admin Access:**
- Username: `admin`
- Password: `admin123`

## System Requirements

- Python 3.11+
- Streamlit
- PostgreSQL (Supabase)
- Google Drive API (for backup)

## Database

The system includes `lang_huu_nghi.db` with sample data:
- 107 student records
- Medical history
- User accounts
- Document metadata

For production, connect to Supabase PostgreSQL using the migration scripts provided.

## Google Drive Backup Setup

1. Create Google Cloud Project
2. Enable Google Drive API
3. Create Service Account and download JSON
4. Add JSON to `GOOGLE_SERVICE_ACCOUNT_JSON` secret
5. Create and share Google Drive folder with service account

## Architecture

- `Trang_chủ.py` - Main application entry point
- `pages/` - Individual page modules
- `database.py` - Database operations
- `auth.py` - Authentication system
- `models.py` - Data models
- `translations.py` - Vietnamese language support

## Production Ready

This system is production-ready with:
- Secure authentication
- Role-based permissions
- Database migration support
- Comprehensive error handling
- Vietnamese localization
- Document management
- Automated backups

Perfect for educational institutions and community organizations requiring Vietnamese language support.