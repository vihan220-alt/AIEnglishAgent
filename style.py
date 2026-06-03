import streamlit as st

def apply_custom_theme():
    """
    Applies a clean, modern, and vibrant design theme to the application interface.
    """
    st.markdown(
        """
        <style>
        /* Main background and font styling */
        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e0e6ed;
        }
        
        /* Modern Card Containers */
        .custom-card {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 20px;
            border: 1px solid #eef2f6;
        }
        
        .card-title {
            color: #1e293b;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .card-desc {
            color: #64748b;
            font-size: 14px;
            line-height: 1.5;
        }
        
        /* Glowing Header Badge */
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            background-color: #e0f2fe;
            color: #0369a1;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        
        /* Button overrides */
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
