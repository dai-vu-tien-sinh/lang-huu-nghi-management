# Overview

The "Hệ thống quản lý dữ liệu Làng Hữu Nghị" is a comprehensive management system for educational and community data at Làng Hữu Nghị (Lang Huu Nghi). This Vietnamese-language application manages student records, veteran information, medical records, psychological evaluations, class administration, and family data. The system features advanced document processing capabilities, automated backup systems, role-based access control, and multi-language support.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page navigation
- **Internationalization**: Translation system supporting Vietnamese and English through translations.py
- **Theming**: Simplified light theme system with Village-specific branding
- **User Interface**: Tab-based organization within pages for different functionalities
- **Document Processing**: Advanced file upload and preview capabilities for Word, PDF, Excel, and images

## Backend Architecture
- **Database ORM**: SQLAlchemy with SQLite as the primary database
- **Authentication**: Session-based authentication with role-based access control
- **Models**: Dataclass-based models for User, Student, Veteran, MedicalRecord, PsychologicalEvaluation, Family, Class, and other entities
- **Role System**: Multi-tier access control (admin, teacher, doctor, nurse, counselor, family)
- **Keep-Alive Service**: Automated database connection maintenance for deployed environments

## Data Storage Solutions
- **Primary Database**: SQLite with potential PostgreSQL support through Drizzle
- **File Storage**: Local file system for document attachments
- **Backup System**: Dual backup strategy with local automated backups and Google Drive integration
- **Data Export**: Comprehensive export capabilities to Word, PDF, and Excel formats

## Authentication and Authorization
- **Authentication**: Username/password with SHA256 password hashing
- **Session Management**: Streamlit session state for user persistence
- **Role-Based Access**: Page-level and feature-level access control based on user roles
- **Family Access**: Restricted access for family members to specific student information

## External Dependencies
- **Email Service**: SendGrid API integration for appointment notifications and reminders
- **Google Drive API**: Automated backup synchronization to cloud storage
- **Database Keep-Alive**: Supabase keep-alive service to prevent database pausing
- **Document Generation**: ReportLab for PDF generation, python-docx for Word documents
- **Data Visualization**: Plotly for interactive charts and analytics
- **Scheduling**: APScheduler for automated backup and maintenance tasks
- **HTTP Health Checks**: Built-in health check endpoints for monitoring services