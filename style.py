import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=300;400;500;600;700&display=swap');
        
        /* =========================================================
           1. GLOBAL SCROLLBARS (CLEAN WHITE ON DARK SLATE)
           ========================================================= */
        ::-webkit-scrollbar {
            width: 10px !important;
            height: 10px !important;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a !important; 
            border-radius: 10px !important;
        }
        ::-webkit-scrollbar-thumb {
            background: #ffffff !important;
            border: 2px solid #0f172a !important; 
            border-radius: 10px !important;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #e2e8f0 !important;
        }

        /* =========================================================
           2. GLOBAL CANVAS & SIDEBAR CORE LAYOUT
           ========================================================= */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            background-color: #f8fafc !important; 
        }
        
        .stApp {
            background: radial-gradient(at 0% 0%, #f1f5f9 0px, transparent 50%),
                        radial-gradient(at 50% 0%, #eff6ff 0px, transparent 50%) !important;
        }

        [data-testid="stSidebar"] {
            background-color: #0f172a !important; 
            border-right: 1px solid #1e293b !important;
        }
        
        /* Headers and basic text layout definitions inside the sidebar */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] h4, 
        [data-testid="stSidebar"] h5, 
        [data-testid="stSidebar"] h6, 
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown {
            color: #f1f5f9 !important;
        }

        /* =========================================================
           3. SIDEBAR ELEMENT TEXT CONTRAST FIXES (CRITICAL)
           ========================================================= */
        
        /* Fix text color inside standard buttons inside the sidebar */
        [data-testid="stSidebar"] .stButton > button {
            background-color: #ffffff !important;
            color: #0f172a !important; /* Sharp dark text on white button canvas */
            border: 1px solid #cbd5e1 !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #f8fafc !important;
            border-color: #3b82f6 !important;
            color: #2563eb !important;
        }

        /* Fix text color inside interactive text input boxes inside the sidebar */
        [data-testid="stSidebar"] .stTextInput input {
            background-color: #ffffff !important;
            color: #0f172a !important; /* Visible dark typed text */
            border: 1px solid #334155 !important;
        }

        /* Fix text color for placeholder hints inside text fields */
        [data-testid="stSidebar"] .stTextInput input::placeholder {
            color: #94a3b8 !important; 
        }

        /* Fix Radio Workspace Selectors text/labels alignment */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            padding: 12px 16px !important;
            border-radius: 10px !important;
            margin-bottom: 10px !important;
            transition: all 0.2s ease !important;
            cursor: pointer;
        }
        
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
            color: #f1f5f9 !important; /* Clear white text inside dark options rows */
        }
        
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            border-color: #3b82f6 !important;
            background: #273549 !important;
        }

        /* =========================================================
           4. MAIN CONTENT PANEL LAYOUT STYLING
           ========================================================= */
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em !important;
        }

        .skill-card {
            background: #ffffff !important;
            padding: 24px !important;
            border-radius: 14px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            margin-bottom: 16px !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        
        .skill-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        }
        
        .skill-title {
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            color: #0f172a !important;
            margin-bottom: 6px !important;
        }
        
        .skill-desc {
            font-size: 0.92rem !important;
            color: #475569 !important;
            line-height: 1.5 !important;
        }
        
        .skill-blue { border-left: 5px solid #2563eb !important; }
        .skill-green { border-left: 5px solid #10b981 !important; }
        .skill-amber { border-left: 5px solid #f59e0b !important; }
        .skill-purple { border-left: 5px solid #8b5cf6 !important; }

        [data-testid="stChatMessage"] {
            border-radius: 12px !important;
            padding: 1.25rem !important;
            margin-bottom: 12px !important;
        }
        [data-testid="stChatMessageUser"] {
            background-color: #eff6ff !important;
            border: 1px solid #dbeafe !important;
        }
        [data-testid="stChatMessageAssistant"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
        }

        [data-testid="stForm"] {
            background-color: #ffffff !important;
            border-radius: 14px !important;
            padding: 24px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
