import streamlit as st
import os
from datetime import datetime
from auth import init_auth, check_auth, login, logout
from database import Database
from supabase_keepalive import SupabaseKeepAlive
from translations import get_text, get_current_language, set_language
from utils import apply_theme
import json


def handle_keep_alive_request():
    """Handle Supabase keep-alive API requests without displaying navigation"""
    try:
        # Check if DATABASE_URL is configured
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            error_response = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": "DATABASE_URL environment variable not set",
                "status": "Configuration error - please set DATABASE_URL in Replit Secrets",
                "service": "Supabase Keep-Alive",
                "version": "1.0.0"
            }
            st.json(error_response)
            return

        # Initialize keep-alive service
        keep_alive = SupabaseKeepAlive()

        # Perform the keep-alive operation
        success, messages = keep_alive.run_keep_alive()

        response = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "status": "Database keep-alive completed successfully"
            if success else "Keep-alive failed",
            "messages": messages,
            "service": "Supabase Keep-Alive",
            "version": "1.0.0"
        }

        # Display JSON response
        st.json(response)

        # Log the activity
        print(
            f"Keep-alive API called at {datetime.now()}: {'SUCCESS' if success else 'FAILED'}"
        )

    except ImportError as e:
        if 'psycopg2' in str(e):
            error_response = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": "psycopg2 not installed",
                "status": "Missing dependency - run: pip install psycopg2-binary",
                "service": "Supabase Keep-Alive",
                "version": "1.0.0"
            }
        else:
            error_response = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "Import error",
                "service": "Supabase Keep-Alive",
                "version": "1.0.0"
            }
        st.json(error_response)
        print(f"Keep-alive API import error at {datetime.now()}: {str(e)}")
        
    except Exception as e:
        error_response = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status": "Keep-alive service error",
            "service": "Supabase Keep-Alive",
            "version": "1.0.0"
        }

        st.json(error_response)
        print(f"Keep-alive API error at {datetime.now()}: {str(e)}")


# Set page config first
st.set_page_config(page_title="Hệ thống quản lý dữ liệu Làng Hữu Nghị",
                   page_icon="🏥",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items=None)


def render_sidebar():
    """Render sidebar with language toggle"""
    # Language toggle button
    with st.sidebar:
        st.markdown("---")
        current_lang = get_current_language()
        
        # Create a toggle button for language
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**🌐 Ngôn ngữ / Language:**")
        with col2:
            if st.button("🔄", help="Switch Language / Đổi ngôn ngữ", key="lang_toggle"):
                new_lang = 'en' if current_lang == 'vi' else 'vi'
                set_language(new_lang)
                st.rerun()
        
        # Display current language
        lang_display = "🇻🇳 Tiếng Việt" if current_lang == 'vi' else "🇬🇧 English"
        st.caption(f"Current: {lang_display}")


def main():
    init_auth()
    db = Database()

    # Initialize backup scheduler once
    if 'backup_scheduler_started' not in st.session_state:
        try:
            from local_backup import start_automatic_backups
            start_automatic_backups()
            st.session_state.backup_scheduler_started = True
        except Exception as e:
            if "conflicts with an existing job" not in str(e):
                print(f"Failed to start backup scheduler: {e}")
            else:
                # Scheduler already running, mark as started
                st.session_state.backup_scheduler_started = True

    # Initialize keep-alive daemon for deployed environments
    if 'keep_alive_daemon_started' not in st.session_state:
        try:
            from keep_alive_daemon import start_keep_alive_daemon
            if start_keep_alive_daemon():
                print("Keep-alive daemon started for deployment")
            st.session_state.keep_alive_daemon_started = True
        except Exception as e:
            print(f"Failed to start keep-alive daemon: {e}")

    # Handle keep-alive API requests (hidden from regular navigation)
    if st.query_params.get("keep_alive"):
        handle_keep_alive_request()
        return

    # Initialize session state if needed
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Force Vietnamese language
    set_language('vi')

    # Logo and title on the same line with smaller text
    logo_path = "static/logo.png"

    # Create columns for logo and title alignment
    col1, col2 = st.columns([1, 4])

    with col1:
        try:
            st.image(logo_path, width=80)
            st.markdown(
                "<p style='text-align: center; color: #274B9F; font-size: 10px; margin: -10px 0 0 0;'>Làng Hữu Nghị</p>",
                unsafe_allow_html=True)
        except Exception as e:
            st.write("Logo not found")

    with col2:
        st.markdown("""
        <div style="padding-top: 10px;">
            <h1 style="color: #274B9F; margin: 0; font-size: 1.8rem; font-weight: 600;">
                Trang chủ
            </h1>
            <h2 style="color: #666; margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 400;">
                Hệ thống quản lý dữ liệu Làng Hữu Nghị
            </h2>
        </div>
        """,
                    unsafe_allow_html=True)

    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.subheader(get_text("login.title"))
            username = st.text_input(get_text("common.username"))
            password = st.text_input(get_text("common.password"),
                                     type="password")
            submit = st.form_submit_button(get_text("common.login"))

            if submit:
                if login(username, password):
                    st.success(get_text("login.success"))
                    st.rerun()
                else:
                    st.error(get_text("login.error"))
    else:
        # User info at the top - with custom styling
        with st.sidebar:
            st.markdown(f"""
            <div style="
                padding: 0.25rem 0; 
                margin: 0.1rem 0; 
                pointer-events: none; 
                user-select: none;
                font-size: 1.1rem;
                font-weight: 600;
                line-height: 1.2;
            ">
                {get_text('common.welcome')}, {st.session_state.user.full_name}
            </div>
            <div style="
                padding: 0.1rem 0; 
                margin: 0.1rem 0; 
                pointer-events: none; 
                user-select: none;
                font-size: 0.9rem;
                color: #666;
            ">
                {get_text('common.role')}: {st.session_state.user.role}
            </div>
            """,
                        unsafe_allow_html=True)
            
            # Language toggle button
            render_sidebar()

        # Show restricted access message for family users
        if st.session_state.user.role == 'family':
            st.info(
                get_text(
                    "family.restricted_access",
                    "Bạn chỉ có quyền xem thông tin của học sinh được chỉ định."
                ))

        # Simple welcome message
        st.markdown("### 🏥 Chào mừng đến với hệ thống quản lý")
        st.markdown(
            "Sử dụng menu bên trái để truy cập các chức năng của hệ thống.")

        # Logout button at the bottom
        st.sidebar.markdown("---")
        if st.sidebar.button(get_text("common.logout")):
            logout()
            st.rerun()


if __name__ == "__main__":
    main()
