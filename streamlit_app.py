#!/usr/bin/env python3
"""
Hệ thống quản lý dữ liệu Làng Hữu Nghị
Entry point that redirects to Vietnamese homepage
"""

import streamlit as st

# Set minimal page config
st.set_page_config(
    page_title="Làng Hữu Nghị",
    page_icon="🏥",
    layout="wide"
)

# Auto-redirect to Trang chủ page
st.markdown(
    """
    <script>
    window.location.replace("/00_Trang_chủ");
    </script>
    """, 
    unsafe_allow_html=True
)

# Fallback content while redirecting
st.markdown("### 🔄 Đang chuyển hướng đến Trang chủ...")
st.markdown("**[Nhấn vào đây nếu không tự động chuyển hướng](/00_Trang_chủ)**")