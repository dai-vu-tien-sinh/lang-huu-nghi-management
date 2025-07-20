from typing import Dict, Any
import streamlit as st

# Simplified theme system - only light and dark modes
VILLAGE_THEMES_LIGHT = {
    "Light": {
        "primaryColor": "#274B9F",  # Royal blue from logo
        "backgroundColor": "#FFFFFF",  # White background
        "secondaryBackgroundColor": "#F8F9FA",  # Light gray
        "textColor": "#2C3E50",  # Dark blue-gray for text
        "font": "sans serif"
    }
}




def get_theme_config(theme_name: str = "Light") -> Dict[str, Any]:
    """Get Streamlit theme configuration for selected theme"""
    # Always use Light theme
    return VILLAGE_THEMES_LIGHT["Light"]

def get_available_themes() -> list:
    """Get list of available theme names"""
    return list(VILLAGE_THEMES_LIGHT.keys())

def get_user_theme_preference(user_id: int = None) -> Dict[str, Any]:
    """Get user's theme preference from database - simplified to always return Light theme"""
    return {"theme": "Light"}

def save_user_theme_preference(user_id: int, theme: str = "Light") -> bool:
    """Save user's theme preference to database - simplified to only save Light theme"""
    # No longer needed as we're using default Streamlit theme only
    return True

def apply_theme_to_streamlit(theme_name: str = "Light"):
    """Apply theme configuration to Streamlit"""
    theme_config = get_theme_config(theme_name)
    
    # Custom CSS for enhanced theming
    css = f"""
    <style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {{
        --primary-color: {theme_config['primaryColor']};
        --background-color: {theme_config['backgroundColor']};
        --secondary-background-color: {theme_config['secondaryBackgroundColor']};
        --text-color: {theme_config['textColor']};
        --font-family: 'Inter', sans-serif;
    }}
    
    /* Main app styling */
    .stApp {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* All text elements */
    * {{
        font-family: var(--font-family) !important;
    }}
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc, .css-1544g2n, .css-1cypcdb {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Sidebar content */
    .css-1d391kg .css-1v3fvcr {{
        color: var(--text-color) !important;
    }}
    
    /* Main content area */
    .css-18e3th9, .css-1d391kg, .main .block-container, .main, .stMain {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Main content wrapper */
    .css-1d391kg .css-12oz5g7 {{
        background-color: var(--background-color) !important;
    }}
    
    /* Content area */
    .css-1629p8f {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* Paragraphs and text */
    p, span, div, label {{
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: var(--primary-color) !important;
        color: white !important;
        border: 1px solid var(--primary-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    .stButton > button:hover {{
        background-color: var(--primary-color) !important;
        opacity: 0.8;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > input,
    .stDateInput > div > div > input {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--primary-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* Selectbox options */
    .stSelectbox > div > div > div {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: var(--primary-color) !important;
        color: white !important;
    }}
    
    /* Data frames and tables */
    .stDataFrame {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Metrics */
    .css-1r6slb0, .css-1xarl3l {{
        background-color: var(--secondary-background-color) !important;
        border: 1px solid var(--primary-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Success/Error messages */
    .stAlert {{
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* Sidebar navigation */
    .css-1d391kg a {{
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
        text-decoration: none;
    }}
    
    .css-1d391kg a:hover {{
        color: var(--primary-color) !important;
    }}
    
    /* Checkbox and radio */
    .stCheckbox > label > span {{
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    .stRadio > label > span {{
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* Form labels */
    .css-1cpxqw2 label {{
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* Chart backgrounds */
    .js-plotly-plot .plotly .main-svg {{
        background-color: var(--background-color) !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* File uploader */
    .css-1cpxqw2 .stFileUploader {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        font-family: var(--font-family) !important;
    }}
    
    /* Additional comprehensive styling for dark mode */
    .stApp, .stApp > div, .stApp > div > div, .stApp > div > div > div {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Root app container */
    .stApp {{
        background-color: var(--background-color) !important;
    }}
    
    /* Main page content after login */
    .stApp .main {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* All main content containers */
    .stApp .main > div {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Main container */
    .css-1y4p8pa {{
        background-color: var(--background-color) !important;
    }}
    
    /* Block container */
    .css-k1vhr4 {{
        background-color: var(--background-color) !important;
    }}
    
    /* All text elements */
    .css-1v3fvcr p, .css-1v3fvcr span, .css-1v3fvcr div {{
        color: var(--text-color) !important;
    }}
    
    /* Form containers */
    .css-1v3fvcr {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Widget containers */
    .css-1cpxqw2 {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Override any white backgrounds in dark mode */
    .css-1v3fvcr .css-1cpxqw2 {{
        background-color: var(--background-color) !important;
    }}
    
    /* Title and header containers */
    .css-1v3fvcr .css-1cpxqw2 h1, 
    .css-1v3fvcr .css-1cpxqw2 h2,
    .css-1v3fvcr .css-1cpxqw2 h3 {{
        color: var(--text-color) !important;
    }}
    
    /* Login form styling */
    .css-1v3fvcr .css-1cpxqw2 .stForm {{
        background-color: var(--secondary-background-color) !important;
        border: 1px solid var(--primary-color) !important;
    }}
    
    /* Info messages */
    .css-1v3fvcr .css-1cpxqw2 .stInfo {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Force main content area styling */
    .stApp .main .block-container {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Content wrapper */
    .stApp .main .block-container > div {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* All content divs */
    .stApp .main .block-container > div > div {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Header and title areas */
    .stApp .main h1, .stApp .main h2, .stApp .main h3 {{
        color: var(--text-color) !important;
    }}
    
    /* Navigation and main content */
    .stApp .main .css-1v3fvcr {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Ensure all paragraphs and text inherit colors */
    .stApp .main p, .stApp .main span, .stApp .main div {{
        color: var(--text-color) !important;
    }}
    
    /* Override specific white background classes */
    .css-1v3fvcr, .css-1cpxqw2, .css-k1vhr4 {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Force all containers to use theme colors */
    .stApp * {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Button styling - improved visibility and contrast */
    .stApp button {{
        background-color: var(--primary-color) !important;
        color: white !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    
    .stApp button:hover {{
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }}
    
    /* Input fields styling */
    .stApp input, .stApp select, .stApp textarea {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
    }}
    
    .stApp input:focus, .stApp select:focus, .stApp textarea:focus {{
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(39, 75, 159, 0.2) !important;
    }}
    
    /* Selectbox styling */
    .stSelectbox > div > div {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 6px !important;
    }}
    
    /* Checkbox styling */
    .stCheckbox > label {{
        color: var(--text-color) !important;
        font-weight: 500 !important;
    }}
    
    /* Form submit button */
    .stForm button {{
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
    }}
    
    .stForm button:hover {{
        background-color: #1e3a7a !important;
        transform: translateY(-1px) !important;
    }}
    
    /* Password visibility toggle button - make it square and smaller */
    .stTextInput button {{
        width: 2.5rem !important;
        height: 2.5rem !important;
        min-width: 2.5rem !important;
        min-height: 2.5rem !important;
        padding: 0 !important;
        background-color: var(--primary-color) !important;
        color: white !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    .stTextInput button:hover {{
        background-color: #1e3a7a !important;
        border-color: #1e3a7a !important;
    }}
    
    /* Login button text color consistency */
    .stForm button span {{
        color: white !important;
    }}
    
    /* Enhanced sidebar styling with blue outline highlighting */
    .stApp .css-1d391kg {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Reset sidebar content */
    .stApp .css-1d391kg * {{
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
    }}
    
    /* Sidebar navigation items - reduced padding, blue color matching login button */
    .stApp [data-testid="stSidebar"] .stRadio > div {{
        border: 2px solid transparent !important;
        border-radius: 6px !important;
        padding: 0.25rem !important;
        margin: 0.1rem 0 !important;
        transition: all 0.3s ease !important;
    }}
    
    .stApp [data-testid="stSidebar"] .stRadio > div:hover {{
        border: 2px solid #2E5BBA !important;
        background-color: rgba(46, 91, 186, 0.1) !important;
        box-shadow: 0 0 6px rgba(46, 91, 186, 0.3) !important;
    }}
    
    /* Active/selected navigation item */
    .stApp [data-testid="stSidebar"] .stRadio input:checked + div {{
        border: 2px solid #2E5BBA !important;
        background-color: rgba(46, 91, 186, 0.15) !important;
        box-shadow: 0 0 8px rgba(46, 91, 186, 0.4) !important;
    }}
    
    /* General sidebar button highlighting */
    .stApp [data-testid="stSidebar"] button {{
        border: 2px solid transparent !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        margin: 0.1rem 0 !important;
        padding: 0.25rem 0.5rem !important;
    }}
    
    .stApp [data-testid="stSidebar"] button:hover {{
        border: 2px solid #2E5BBA !important;
        box-shadow: 0 0 6px rgba(46, 91, 186, 0.3) !important;
        background-color: rgba(46, 91, 186, 0.1) !important;
    }}
    
    /* Sidebar selectbox highlighting */
    .stApp [data-testid="stSidebar"] .stSelectbox > div > div {{
        border: 2px solid transparent !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        margin: 0.1rem 0 !important;
        padding: 0.25rem !important;
    }}
    
    .stApp [data-testid="stSidebar"] .stSelectbox > div > div:hover {{
        border: 2px solid #2E5BBA !important;
        box-shadow: 0 0 6px rgba(46, 91, 186, 0.3) !important;
        background-color: rgba(46, 91, 186, 0.1) !important;
    }}
    
    /* Sidebar link styling */
    .stApp [data-testid="stSidebar"] a {{
        border: 2px solid transparent !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        display: block !important;
        padding: 0.25rem 0.5rem !important;
        margin: 0.1rem 0 !important;
        text-decoration: none !important;
    }}
    
    .stApp [data-testid="stSidebar"] a:hover {{
        border: 2px solid #2E5BBA !important;
        box-shadow: 0 0 6px rgba(46, 91, 186, 0.3) !important;
        background-color: rgba(46, 91, 186, 0.1) !important;
    }}
    
    /* User info section - reduced padding and non-clickable */
    .stApp [data-testid="stSidebar"] h1 {{
        padding: 0.25rem 0 !important;
        margin: 0.1rem 0 !important;
        pointer-events: none !important;
        user-select: none !important;
        font-size: 1.1rem !important;
    }}
    
    .stApp [data-testid="stSidebar"] .element-container:first-child h1 {{
        padding: 0.25rem 0 !important;
        margin: 0.1rem 0 !important;
        pointer-events: none !important;
        user-select: none !important;
    }}
    
    .stApp [data-testid="stSidebar"] .stText {{
        padding: 0.1rem 0 !important;
        margin: 0.1rem 0 !important;
        pointer-events: none !important;
        user-select: none !important;
    }}
    
    /* Error message styling - make errors stand out */
    .stApp .stAlert[data-baseweb="alert"] {{
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }}
    
    /* Error alerts - red background */
    .stApp .stAlert[data-baseweb="alert"][data-testid="stAlert"] {{
        background-color: #ff4444 !important;
        color: white !important;
        border: 2px solid #cc0000 !important;
    }}
    
    /* Success alerts - green background */
    .stApp .stSuccess {{
        background-color: #28a745 !important;
        color: white !important;
        border: 2px solid #1e7e34 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }}
    
    /* Warning alerts - yellow background */
    .stApp .stWarning {{
        background-color: #ffc107 !important;
        color: #212529 !important;
        border: 2px solid #d39e00 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }}
    
    /* Info alerts - blue background */
    .stApp .stInfo {{
        background-color: #17a2b8 !important;
        color: white !important;
        border: 2px solid #138496 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }}
    
    /* Consistent button styling - all buttons same color */
    .stApp button[kind="primary"], 
    .stApp button[kind="secondary"],
    .stApp .stButton > button {{
        background-color: var(--primary-color) !important;
        color: white !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    
    .stApp button[kind="primary"]:hover,
    .stApp button[kind="secondary"]:hover,
    .stApp .stButton > button:hover {{
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }}
    
    /* Navigation buttons - consistent styling */
    .stApp .css-1d391kg button {{
        background-color: var(--primary-color) !important;
        color: white !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .stApp .css-1d391kg button:hover {{
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }}
    
    /* Tab navigation buttons - make them visible */
    .stApp .stTabs [data-baseweb="tab-list"] button {{
        background-color: var(--primary-color) !important;
        color: white !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        margin-right: 0.5rem !important;
    }}
    
    .stApp .stTabs [data-baseweb="tab-list"] button:hover {{
        background-color: #1e3a7a !important;
        color: white !important;
    }}
    
    .stApp .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: #1e3a7a !important;
        color: white !important;
        border-color: #1e3a7a !important;
    }}
    

    
    /* Style only the radio button circles */
    .stApp .stRadio input[type="radio"] {{
        appearance: none !important;
        -webkit-appearance: none !important;
        width: 16px !important;
        height: 16px !important;
        border: 2px solid #ccc !important;
        border-radius: 50% !important;
        margin-right: 8px !important;
        position: relative !important;
        cursor: pointer !important;
        outline: none !important;
    }}
    
    .stApp .stRadio input[type="radio"]:checked {{
        border-color: #87CEEB !important;
        background-color: #87CEEB !important;
    }}
    
    .stApp .stRadio input[type="radio"]:checked::after {{
        content: '' !important;
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: white !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }}
    
    /* Keep text styling normal */
    .stApp .stRadio label {{
        color: inherit !important;
        font-weight: normal !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .stApp div[role="radiogroup"] {{
        display: flex !important;
        gap: 1rem !important;
    }}
    
    .stApp div[role="radiogroup"] label {{
        color: inherit !important;
        font-weight: normal !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        background: none !important;
        border-radius: 0 !important;
    }}
    
    .stApp div[role="radiogroup"] input[type="radio"] {{
        appearance: none !important;
        -webkit-appearance: none !important;
        width: 16px !important;
        height: 16px !important;
        border: 2px solid #ccc !important;
        border-radius: 50% !important;
        margin-right: 8px !important;
        position: relative !important;
        cursor: pointer !important;
        outline: none !important;
    }}
    
    .stApp div[role="radiogroup"] input[type="radio"]:checked {{
        border-color: #87CEEB !important;
        background-color: #87CEEB !important;
    }}
    
    .stApp div[role="radiogroup"] input[type="radio"]:checked::after {{
        content: '' !important;
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: white !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }}
    
    /* Prevent selection of radio group label */
    .stApp .stRadio > label:first-child {{
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        cursor: default !important;
    }}
    
    /* Make radio group label non-selectable */
    .stApp .stRadio > div:first-child {{
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        cursor: default !important;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    # Also set Streamlit config
    try:
        st._config.set_option('theme.primaryColor', theme_config['primaryColor'])
        st._config.set_option('theme.backgroundColor', theme_config['backgroundColor'])
        st._config.set_option('theme.secondaryBackgroundColor', theme_config['secondaryBackgroundColor'])
        st._config.set_option('theme.textColor', theme_config['textColor'])
        st._config.set_option('theme.font', theme_config['font'])
    except Exception as e:
        # Config options might not be settable at runtime, continue with CSS only
        pass