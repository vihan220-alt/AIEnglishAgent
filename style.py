import streamlit as st

def apply_custom_theme():
    """
    Applies a clean, modern, and vibrant design theme to the learning application.
    """
    st.markdown(
        """
        <style>
        /* Main canvas container adjustments */
        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Polished Sidebar Panel navigation */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0;
        }
        
        /* Educational Learning Skill Matrix Grid Cards */
        .skill-card {
            background-color: #ffffff;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 16px;
            border: 1px solid #edf2f7;
        }
        
        .skill-title {
            color: #0f172a;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 6px;
        }
        
        .skill-desc {
            color: #475569;
            font-size: 14px;
            line-height: 1.5;
        }
        
        /* Decorative custom badge */
        .hub-badge {
            display: inline-block;
            padding: 5px 12px;
            background-color: #dbeafe;
            color: #1e40af;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        
        /* Global button animations */
        .stButton>button {
            border-radius: 10px !important;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
