# Hệ thống quản lý dữ liệu Làng Hữu Nghị

## Overview
Comprehensive Streamlit application for multilingual data management in educational and organizational contexts, with advanced user role-based access control and intelligent record processing.

The system emphasizes granular user permissions, multilingual support, and adaptive administrative tools for diverse organizational needs.

## Key Technologies
- Python 3.11
- Streamlit framework
- Role-based authentication
- Plotly for interactive visualizations
- SQLAlchemy for database interactions
- i18n internationalization support

## Recent Changes
- **2025-04-10**: Implemented comprehensive role-based permissions system
- **2025-04-10**: Updated all user roles to have access to statistics, search, and print functionality (except family users)
- **2025-04-10**: Merged administrative role with admin to have full permissions
- **2025-04-10**: Enhanced search and print functionality to respect user role permissions

## User Role Permissions
- **Admin/Administrative**: Full access to all features
- **Teacher**: Class management, students, search students/psychological evaluations, statistics, print, data management
- **Doctor**: Medical records, students, veterans, search medical records, statistics, print, data management
- **Nurse**: Medical records, search students/veterans/medical records, statistics, print
- **Counselor**: Psychological evaluations, students, search students/psychological evaluations, statistics, print
- **Family**: View own child's information and general statistics only

## Project Architecture
- `main.py`: Main application entry point with navigation
- `auth.py`: Role-based authentication and permission system
- `database.py`: Database operations and data management
- `models.py`: Data model definitions
- `pages/`: Individual page modules for different features
- `translations.py`: Internationalization support
- `themes.py`: UI theme management

## Deployment Notes
- Currently running on Replit with PostgreSQL database
- User requesting deployment to Supabase
- All environment variables configured for PostgreSQL connection