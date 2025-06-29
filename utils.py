from datetime import datetime
import streamlit as st
import plotly.express as px
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
import tempfile
from themes import get_theme_config

def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")

def create_chart(data: pd.DataFrame, chart_type: str, title: str):
    if chart_type == 'bar':
        fig = px.bar(data, title=title)
    elif chart_type == 'line':
        fig = px.line(data, title=title)
    elif chart_type == 'pie':
        fig = px.pie(data, title=title)
    return fig

def generate_pdf_report(data: dict, title: str, include_charts: bool = True, language: str = "vi") -> bytes:
    from translations import get_text
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Use proper fonts for Vietnamese
    # Use Helvetica for now as we don't have Vietnamese fonts
    font_name = "Helvetica"
    
    # Translate title if in Vietnamese
    if language == "vi":
        # Map some common titles
        title_map = {
            "Student Statistics Report": "Báo Cáo Thống Kê Học Sinh",
            "Veteran Statistics Report": "Báo Cáo Thống Kê Cựu Chiến Binh",
            "Medical Records Report": "Báo Cáo Hồ Sơ Y Tế",
            "Psychological Evaluation Report": "Báo Cáo Đánh Giá Tâm Lý"
        }
        if title in title_map:
            title = title_map[title]
    
    # Add title
    c.setFont(f"{font_name}-Bold", 16)
    c.drawString(50, 750, title)
    
    # Add content
    c.setFont(font_name, 12)
    y = 700
    
    # Translate data keys if in Vietnamese
    translated_data = {}
    if language == "vi":
        key_map = {
            "Total Students": "Tổng số học sinh",
            "Total Veterans": "Tổng số cựu chiến binh",
            "Report Generated": "Báo cáo được tạo lúc",
            "Health Status Distribution": "Phân bố tình trạng sức khỏe",
            "Academic Status Distribution": "Phân bố tình trạng học tập"
        }
        
        for key, value in data.items():
            trans_key = key_map.get(key, key)
            translated_data[trans_key] = value
    else:
        translated_data = data
    
    # Add data text content
    for key, value in translated_data.items():
        # Skip chart data for text display
        if key in ['health_chart', 'academic_chart']:
            continue
        c.drawString(50, y, f"{key}: {value}")
        y -= 20
    
    # Add charts if included and available
    if include_charts:
        y -= 20
        
        # Add health chart if available
        if 'health_chart' in data and data['health_chart'] is not None:
            chart_title = "Phân bố tình trạng sức khỏe" if language == "vi" else "Health Status Distribution"
            c.drawString(50, y, chart_title)
            y -= 20
            
            # Save chart to temp file
            chart = data['health_chart']
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            chart.write_image(temp_file.name, width=500, height=300)
            
            # Add to PDF
            c.drawImage(temp_file.name, 50, y - 300, width=500, height=300)
            y -= 320
            
            # Clean up temp file
            temp_file.close()
            os.unlink(temp_file.name)
        
        # Add academic chart if available
        if 'academic_chart' in data and data['academic_chart'] is not None:
            chart_title = "Phân bố tình trạng học tập" if language == "vi" else "Academic Status Distribution"
            c.drawString(50, y, chart_title)
            y -= 20
            
            # Save chart to temp file
            chart = data['academic_chart']
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            chart.write_image(temp_file.name, width=500, height=300)
            
            # Add to PDF
            c.drawImage(temp_file.name, 50, y - 300, width=500, height=300)
            
            # Clean up temp file
            temp_file.close()
            os.unlink(temp_file.name)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def show_success(message: str):
    st.success(message)

def show_error(message: str):
    st.error(message)

def apply_theme():
    """Apply the current theme from session state to the page"""
    # Ensure theme is initialized
    if 'theme_name' not in st.session_state:
        print("Initializing theme to default")
        st.session_state.theme_name = 'Chính thức'

    # Get theme configuration
    theme_config = get_theme_config(st.session_state.theme_name)
    print(f"Applying theme: {st.session_state.theme_name}")

    # Apply comprehensive theme styling
    theme_css = f"""
        <style>
            /* Global styles */
            .stApp {{
                background-color: {theme_config['backgroundColor']} !important;
                color: {theme_config['textColor']};
            }}

            /* Button styles */
            .stButton>button {{
                background-color: {theme_config['primaryColor']} !important;
                color: white !important;
                border-color: {theme_config['primaryColor']} !important;
            }}

            /* Input styles */
            .stTextInput>div>div>input,
            .stSelectbox>div>div>input,
            .stNumberInput>div>div>input {{
                color: {theme_config['textColor']} !important;
                border-color: {theme_config['primaryColor']} !important;
            }}

            /* Text and markdown */
            .stMarkdown, 
            .stText,
            .stCode {{
                color: {theme_config['textColor']} !important;
            }}

            /* Sidebar */
            .stSidebar {{
                background-color: {theme_config['secondaryBackgroundColor']} !important;
            }}

            /* Plot container */
            .plot-container {{
                background-color: {theme_config['backgroundColor']} !important;
            }}

            /* Form elements */
            div.row-widget.stRadio > div,
            div.row-widget.stCheckbox > div {{
                color: {theme_config['textColor']} !important;
            }}

            /* Date input */
            .stDateInput > div > div > input {{
                color: {theme_config['textColor']} !important;
            }}

            /* Text area */
            .stTextArea > div > div > textarea {{
                color: {theme_config['textColor']} !important;
            }}

            /* Progress bar */
            .stProgress > div > div > div > div {{
                background-color: {theme_config['primaryColor']} !important;
            }}

            /* Header text */
            h1, h2, h3, h4, h5, h6 {{
                color: {theme_config['textColor']} !important;
            }}
        </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)