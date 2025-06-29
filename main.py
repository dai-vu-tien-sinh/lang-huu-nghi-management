import streamlit as st
from auth import init_auth, login, logout
from database import Database
from translations import get_text, set_language, get_current_language
from themes import get_theme_config, get_available_themes
from utils import apply_theme
import base64
from pathlib import Path

def get_base64_encoded_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")
        return None

# Set page config first
st.set_page_config(
    page_title=get_text("app.title", "Hệ Thống Quản Lý Làng Hữu Nghị"),
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

def render_sidebar():
    """Render the sidebar based on user preferences"""
    db = Database()
    from translations import get_text

    # Get user's sidebar preferences if authenticated
    if st.session_state.authenticated:
        prefs = db.get_user_sidebar_preferences(st.session_state.user.id)
        available_pages = db.get_available_pages(st.session_state.user.role)

        # If no preferences exist, use default order
        page_order = prefs.page_order if prefs else [p['id'] for p in available_pages]
        hidden_pages = prefs.hidden_pages if prefs else []

        # Group pages by category
        pages_by_group = {}
        for page in available_pages:
            if page['id'] not in hidden_pages:  # Skip hidden pages
                group = page['group']
                if group not in pages_by_group:
                    pages_by_group[group] = []
                pages_by_group[group].append(page)

        # Sort pages within each group based on custom order
        for group in pages_by_group:
            pages_by_group[group].sort(
                key=lambda x: page_order.index(x['id']) if x['id'] in page_order else float('inf')
            )

        # Display pages by group
        for group, pages in pages_by_group.items():
            # Translate group name
            translated_group = get_text(f"groups.{group.lower().replace(' ', '_')}", group)
            st.sidebar.markdown(f"### {translated_group}", unsafe_allow_html=True)
            for page in pages:
                # Kiểm tra ngôn ngữ hiện tại và áp dụng tên phù hợp
                if get_current_language() == 'en':
                    # Tên tiếng Anh cho các menu
                    english_names = {
                        "01_Quan_tri": "Administration",
                        "02_Y_te": "Healthcare",
                        "03_Quan_ly_ho_so": "Records Management",
                        "03_Tam_ly": "Psychological Support",
                        "04_Lop_hoc": "Classes", 
                        "05_Tim_kiem_va_In": "Search & Print",
                        "06_Quan_ly_Database": "Data Management",
                        "07_Quan_ly_He_thong": "System Management",
                        "08_Thong_ke": "Statistics & Analytics",
                        "main": "Login Page"
                    }
                    translated_name = english_names.get(page['id'], page['name'])
                else:
                    translated_name = page['name']
                
                page_link = f"<a href='/{page['id']}' target='_self' style='text-decoration: none; color: inherit;'>- {translated_name}</a>"
                st.sidebar.markdown(page_link, unsafe_allow_html=True)

def main():
    init_auth()
    db = Database()

    # Initialize session state for theme if not exists
    if 'theme_name' not in st.session_state:
        st.session_state.theme_name = 'Chính thức'
        print("Initializing theme state")

    # Apply current theme first
    apply_theme()

    # Add logo using Streamlit's image display
    logo_path = "static/logo.png"
    try:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.image(logo_path, width=100, use_container_width=True)
            st.markdown("<p style='text-align: center; color: #274B9F; font-size: 12px; margin-top: -15px;'>Làng Hữu Nghị</p>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying logo: {str(e)}")

    # Theme selector in sidebar (always available)
    st.sidebar.title(f"🎨 {get_text('common.theme', 'Giao diện')}")
    new_theme = st.sidebar.selectbox(
        get_text('common.choose_theme', 'Chọn giao diện'),
        get_available_themes(),
        index=get_available_themes().index(st.session_state.theme_name),
        key='theme_selector'
    )

    # Update theme if changed
    if new_theme != st.session_state.theme_name:
        print(f"Theme changed from {st.session_state.theme_name} to {new_theme}")
        st.session_state.theme_name = new_theme
        st.rerun()

    # Language selector
    current_lang = "Tiếng Việt" if get_current_language() == 'vi' else "English"
    language = st.sidebar.selectbox(
        "Language/Ngôn ngữ",
        ["Tiếng Việt", "English"],
        index=["Tiếng Việt", "English"].index(current_lang)
    )

    if language == "English":
        set_language('en')
    else:
        set_language('vi')

    st.title(get_text("app.title_full", "Hệ Thống Quản Lý Làng Hữu Nghị - Lang Huu Nghi Management System"))

    if not st.session_state.authenticated:
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
        # User info at the top
        st.sidebar.title(f"{get_text('common.welcome')}, {st.session_state.user.full_name}")
        st.sidebar.text(f"{get_text('common.role')}: {st.session_state.user.role}")

        # Show restricted access message for family users
        if st.session_state.user.role == 'family':
            st.info(get_text("family.restricted_access", "Bạn chỉ có quyền xem thông tin của học sinh được chỉ định."))

        # Render sidebar based on user preferences
        render_sidebar()

        # Logout button at the bottom
        st.sidebar.markdown("---")
        if st.sidebar.button(get_text("common.logout")):
            logout()
            st.rerun()

if __name__ == "__main__":
    main()