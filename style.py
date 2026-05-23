import streamlit as st

def apply_custom_theme():
    """
    Applies a premium dark theme to Streamlit's native chat architecture.
    Ensures input text fields are visible, highly legible, and correctly padded.
    """
    st.markdown("""
        <style>
        /* 1. GLOBAL WORKSPACE DARK MODE */
        .stApp, [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top, #0f172a 0%, #090d16 100%) !important;
            color: #f8fafc !important;
        }
        
        .stMarkdown p, span, label, div {
            color: #f8fafc !important;
        }

        /* 2. GRADIENT TITLES */
        h1 {
            font-size: 36px !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #ffffff 20%, #22d3ee 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            margin-bottom: 2px !important;
        }
        
        h3 {
            font-size: 16px !important;
            color: #94a3b8 !important;
            font-weight: 400 !important;
            margin-top: 0px !important;
            margin-bottom: 30px !important;
        }

        /* 3. SIDEBAR PANEL */
        [data-testid="stSidebar"] {
            background-color: #070a13 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
        }
        
        div.stAlert {
            background: rgba(34, 211, 238, 0.05) !important;
            border: 1px solid rgba(34, 211, 238, 0.15) !important;
            border-radius: 12px !important;
        }

        /* 4. NATIVE CHAT BUBBLE CUSTOM COLORING */
        [data-testid="stChatMessage"] {
            background-color: #111927 !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 16px !important;
            margin-bottom: 12px !important;
            padding: 12px 16px !important;
        }
        
        /* Give user messages a distinct premium accent shade */
        [data-testid="stChatMessageUser"] {
            background-color: #0c4a6e !important;
            border-color: rgba(2, 132, 199, 0.3) !important;
        }
        
        /* Make sure avatar images fit perfectly and look crisp */
        [data-testid="stChatMessageAvatar"] img {
            border-radius: 50% !important;
            object-fit: cover !important;
        }

        /* 5. INPUT PANEL & FORM ADJUSTMENTS */
        div[data-testid="stForm"] {
            background: #111927 !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-top: 2px solid rgba(34, 211, 238, 0.4) !important;
            border-radius: 14px !important;
            padding: 16px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important;
        }
        
        div[data-testid="stTextInput"] input {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
        }

        /* 6. CONTROL BUTTONS */
        button[data-testid="baseButton-secondary"], button[data-testid="baseButton-formSubmit"] {
            background: #1e293b !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #f1f5f9 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        button[data-testid="baseButton-secondary"]:hover, button[data-testid="baseButton-formSubmit"]:hover {
            border-color: #22d3ee !important;
            color: #22d3ee !important;
            background: rgba(34, 211, 238, 0.06) !important;
        }
        
        .control-label {
            font-size: 13px;
            font-weight: 600;
            color: #94a3b8;
            margin-bottom: 6px;
        }
        </style>
    """, unsafe_allow_html=True)
