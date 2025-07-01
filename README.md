# Hệ thống quản lý dữ liệu Làng Hữu Nghị

A comprehensive Streamlit application for multilingual data management in educational and organizational contexts.

## Features

- **Role-based Access Control**: Different permission levels for admin, teachers, doctors, nurses, counselors, and family users
- **Multilingual Support**: Vietnamese and English language support
- **Data Management**: Student, veteran, medical, and psychological record management
- **Search & Analytics**: Advanced search functionality with statistical visualizations
- **Export Capabilities**: PDF and Excel export functionality
- **Theme Support**: Multiple UI themes

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install streamlit pandas plotly openpyxl reportlab sendgrid twilio anthropic python-dotenv psycopg2-binary sqlalchemy
   ```

3. Set up environment variables:
   ```bash
   DATABASE_URL=your_postgresql_connection_string
   SENDGRID_API_KEY=your_sendgrid_key (optional)
   TWILIO_ACCOUNT_SID=your_twilio_sid (optional)
   TWILIO_AUTH_TOKEN=your_twilio_token (optional)
   TWILIO_PHONE_NUMBER=your_twilio_phone (optional)
   ANTHROPIC_API_KEY=your_anthropic_key (optional)
   ```

4. Run the application:
   ```bash
   streamlit run main.py
   ```

### Deployment on Supabase

1. **Database Setup**:
   - Create a new Supabase project
   - Get your database connection string from Project Settings > Database
   - Format: `postgresql://postgres:[password]@[host]:5432/postgres`

2. **Deploy to Streamlit Cloud**:
   - Fork this repository to your GitHub account
   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository
   - Set the main file as `streamlit_app.py`
   - Add your environment variables in the Secrets section

3. **Environment Variables**:
   ```toml
   DATABASE_URL = "your_supabase_connection_string"
   # Optional services
   SENDGRID_API_KEY = "your_sendgrid_key"
   TWILIO_ACCOUNT_SID = "your_twilio_sid"
   TWILIO_AUTH_TOKEN = "your_twilio_token"
   TWILIO_PHONE_NUMBER = "your_twilio_phone"
   ANTHROPIC_API_KEY = "your_anthropic_key"
   ```

## User Accounts

The system includes test accounts for different roles:

- **Admin**: `admin/admin123` - Full system access
- **Teacher**: `teacher1/password123` - Student and class management
- **Doctor**: `doctor1/password123` - Medical records and patient management
- **Nurse**: `nurse1/password123` - Medical records access
- **Counselor**: `counselor1/password123` - Psychological evaluations
- **Administrative**: `admin1/password123` - Full administrative access

## Architecture

- `main.py` - Application entry point and navigation
- `auth.py` - Authentication and role-based permissions
- `database.py` - Database operations and management
- `models.py` - Data model definitions
- `pages/` - Feature-specific page modules
- `translations.py` - Internationalization support
- `themes.py` - UI theme management

## License

This project is developed for Làng Hữu Nghị educational management purposes.
