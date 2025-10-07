import streamlit as st
import os
from datetime import datetime
from auth import init_auth, check_auth, login, logout
from database import Database
from supabase_keepalive import SupabaseKeepAlive
from translations import get_text, get_current_language, set_language
from utils import apply_theme
import json
import streamlit.components.v1 as components

def handle_keep_alive_request():
    """Handle Supabase keep-alive API requests without displaying navigation"""
    try:
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

        keep_alive = SupabaseKeepAlive()
        success, messages = keep_alive.run_keep_alive()
        response = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "status": "Database keep-alive completed successfully" if success else "Keep-alive failed",
            "messages": messages,
            "service": "Supabase Keep-Alive",
            "version": "1.0.0"
        }
        st.json(response)
        print(f"Keep-alive API called at {datetime.now()}: {'SUCCESS' if success else 'FAILED'}")

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


# Set page config
st.set_page_config(page_title="Hệ thống quản lý dữ liệu Làng Hữu Nghị",
                   page_icon="🏥",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items=None)

# Setting language attributes using HTML meta tags
components.html("""
<meta charset="UTF-8">
<meta http-equiv="Content-Language" content="vi">
<meta name="google" content="notranslate">
<html lang="vi" xml:lang="vi">
</html>
""", height=0)

def render_sidebar():
    """Render sidebar with language toggle."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("**🌐 Ngôn ngữ / Language:**")

        # Instructions for translation functionality.
        st.info("""
        **Dịch sang tiếng Anh / Translate to English:**
        
        To translate the page, you can right-click anywhere on the page and select "Translate to English" from the browser context menu.

        You can also use Google Translate by clicking the "Translate" button in the top-right corner of the browser address bar and selecting "English" as the target language.

        If you have any issues: switch to Microsoft Edge for the best experience.
        """)

def main():
    init_auth()
    db = Database()

    if 'backup_scheduler_started' not in st.session_state:
        try:
            from local_backup import start_automatic_backups
            start_automatic_backups()
            st.session_state.backup_scheduler_started = True
        except Exception as e:
            if "conflicts with an existing job" not in str(e):
                print(f"Failed to start backup scheduler: {e}")
            else:
                st.session_state.backup_scheduler_started = True

    if 'keep_alive_daemon_started' not in st.session_state:
        try:
            from keep_alive_daemon import start_keep_alive_daemon
            if start_keep_alive_daemon():
                print("Keep-alive daemon started for deployment")
            st.session_state.keep_alive_daemon_started = True
        except Exception as e:
            print(f"Failed to start keep-alive daemon: {e}")

    if st.query_params.get("keep_alive"):
        handle_keep_alive_request()
        return

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    set_language('vi')

    logo_path = "static/logo.png"
    col1, col2 = st.columns([1, 4])

    with col1:
        try:
            st.image(logo_path, width=80)
            st.markdown("<p style='text-align: center; color: #274B9F; font-size: 10px; margin: -10px 0 0 0;'>Làng Hữu Nghị</p>", unsafe_allow_html=True)
        except Exception as e:
            st.write("Logo not found")

    with col2:
        st.markdown("""
        <div style="padding-top: 10px;">
            <h1 style="color: #274B9F; margin: 0; font-size: 1.8rem; font-weight: 600;">Trang chủ</h1>
            <h2 style="color: #666; margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 400;">Hệ thống quản lý dữ liệu Làng Hữu Nghị</h2>
        </div>
        """, unsafe_allow_html=True)

    if not st.session_state.authenticated:
        render_sidebar()

        with st.form("login_form"):
            st.subheader(get_text("login.title"))
            username = st.text_input(get_text("common.username"))
            password = st.text_input(get_text("common.password"), type="password")
            submit = st.form_submit_button(get_text("common.login"))

            if submit:
                if login(username, password):
                    st.success(get_text("login.success"))
                    st.rerun()
                else:
                    st.error(get_text("login.error"))
    else:
        st.sidebar.markdown(f"<div>Welcome, {st.session_state.user.full_name}</div>", unsafe_allow_html=True)
        render_sidebar()

        if st.session_state.user.role == 'family':
            st.info(get_text("family.restricted_access", "Bạn chỉ có quyền xem thông tin của học sinh được chỉ định."))

        st.markdown("### 🏥 Chào mừng đến với hệ thống quản lý")
        st.markdown("Sử dụng menu bên trái để truy cập các chức năng của hệ thống.")

        st.sidebar.markdown("---")
        if st.sidebar.button(get_text("common.logout")):
            logout()
            st.rerun()

if __name__ == "__main__":
    main()
