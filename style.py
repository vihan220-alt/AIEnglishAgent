import streamlit as st

def apply_custom_theme():
    """
    Applies a clean, modern, enterprise design theme to the skills assessment application.
    """
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            font-family: 'Inter', sans-serif;
        }
        
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0;
        }
        
        .skill-card-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .skill-card {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border-top: 5px solid #3b82f6;
            margin-bottom: 16px;
        }
        
        .skill-blue { border-top-color: #3b82f6; }
        .skill-green { border-top-color: #10b981; }
        .skill-amber { border-top-color: #f59e0b; }
        .skill-purple { border-top-color: #8b5cf6; }
        
        .skill-title {
            color: #0f172a;
            font-size: 18px;
            font-weight: 700;
            margin: 0 0 8px 0;
        }
        
        .skill-desc {
            color: #475569;
            font-size: 14px;
            line-height: 1.6;
            margin: 0;
        }
        
        .hub-badge {
            display: inline-flex;
            align-items: center;
            padding: 6px 14px;
            background-color: #e0f2fe;
            color: #0369a1;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 20px;
            border: 1px solid #bae6fd;
        }
        
        .stButton>button {
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
