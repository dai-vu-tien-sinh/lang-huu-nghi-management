# This file serves as the entry point for Streamlit Cloud deployment
# It imports and runs the Vietnamese homepage application

import os
import sys

# Add current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Direct execution of the main application
try:
    # Execute Trang_chủ.py directly
    exec(open("Trang_chủ.py").read())
except Exception as e:
    import streamlit as st
    st.error("🚨 Lỗi khi tải ứng dụng chính")
    st.error(f"Chi tiết lỗi: {str(e)}")
    
    # Show debugging information
    with st.expander("🔍 Thông tin debug"):
        st.write("**Thư mục hiện tại:**", os.getcwd())
        st.write("**Danh sách file:**")
        try:
            files = os.listdir(".")
            for file in sorted(files):
                if file.endswith(".py"):
                    st.write(f"- {file}")
        except Exception as list_error:
            st.write(f"Không thể liệt kê file: {list_error}")
    
    st.info("💡 Vui lòng kiểm tra file Trang_chủ.py có tồn tại trong repository")