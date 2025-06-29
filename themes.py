from typing import Dict, Any

# Village-inspired color palettes based on logo
VILLAGE_THEMES = {
    "Chính thức": {
        "primaryColor": "#274B9F",  # Royal blue from logo
        "backgroundColor": "#FFFFFF",  # White background
        "secondaryBackgroundColor": "#F8F9FA",  # Light gray
        "textColor": "#2C3E50",  # Dark blue-gray for text
        "font": "sans serif"
    },
    "Hữu nghị": {
        "primaryColor": "#F4D03F",  # Golden yellow from logo
        "backgroundColor": "#FFFFFF",  # White background
        "secondaryBackgroundColor": "#E8F4FD",  # Very light blue
        "textColor": "#274B9F",  # Royal blue for text
        "font": "sans serif"
    },
    "Xanh dương": {  # Soft Blue theme
        "primaryColor": "#6F8FAF",  # Pastel blue
        "backgroundColor": "#F0F8FF",  # Alice blue
        "secondaryBackgroundColor": "#E6F3FF",  # Lighter blue
        "textColor": "#2C3E50",  # Dark blue-gray
        "font": "sans serif"
    },
    "Xanh lá": {  # Gentle Green theme
        "primaryColor": "#98CF90",  # Pastel green
        "backgroundColor": "#F0FFF0",  # Honeydew
        "secondaryBackgroundColor": "#E8F5E9",  # Lighter green
        "textColor": "#2E5A1C",  # Dark green
        "font": "sans serif"
    },
    "Đỏ nhẹ": {  # Warm Red theme
        "primaryColor": "#E6A4A4",  # Pastel red
        "backgroundColor": "#FFF5F5",  # Light pink
        "secondaryBackgroundColor": "#FFE8E8",  # Lighter pink
        "textColor": "#8B3A3A",  # Dark red
        "font": "sans serif"
    },
    "Vàng nhạt": {  # Soft Yellow theme
        "primaryColor": "#FFD700",  # Soft gold
        "backgroundColor": "#FFFDF0",  # Very light yellow
        "secondaryBackgroundColor": "#FFF8DC",  # Cornsilk
        "textColor": "#8B7355",  # Warm brown
        "font": "sans serif"
    }
}

def get_theme_config(theme_name: str) -> Dict[str, Any]:
    """Get Streamlit theme configuration for selected theme"""
    if theme_name not in VILLAGE_THEMES:
        theme_name = "Chính thức"  # Default theme

    return VILLAGE_THEMES[theme_name]

def get_available_themes() -> list:
    """Get list of available theme names"""
    return list(VILLAGE_THEMES.keys())