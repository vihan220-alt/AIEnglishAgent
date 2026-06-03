import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        /* =========================================================
           WHITE SCROLLER (SCROLLBAR) CUSTOMIZATION
           ========================================================= */
        /* Target the main window, sidebar, and text area scrollers */
        ::-webkit-scrollbar {
            width: 10px !important;
            height: 10px !important;
        }
        
        /* Scrollbar Track (The background lane of the scroller) */
        ::-webkit-scrollbar-track {
            background: #0f172a !important; /* Matches dark sidebar, clean contrast on light pages */
            border-radius: 10px !important;
        }
        
        /* Scrollbar Thumb (The moving bar - set to pure white) */
        ::-webkit-scrollbar-thumb {
            background: #ffffff !important;
            border: 2px solid #0f172a !important; /* Creates a beautiful breathing gap around the white bar */
            border-radius: 10px !important;
        }
        
        /* Scrollbar Thumb on Hover (Slightly silver/glowing white) */
        ::-webkit-scrollbar-thumb:hover {
            background: #e2e8f0 !important;
        }

        /* 1. Global Page Reset */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            background-color: #f8fafc !important; 
        }
        
        /* 2. Sleek Modern App Canvas Gradient */
        .stApp {
            background: radial-gradient(at 0% 0%, #f1f5f9 0px, transparent 50%),
                        radial-gradient(at 50% 0%, #eff6ff 0px, transparent 50%) !important;
        }

        /* 3. Deep Slate Dark Mode Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important; 
            border-right: 1px solid #1e293b !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }
        
        /* Radio Workspace Selectors Custom Design */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            padding: 12px 16px !important;
            border-radius: 10px !important;
            margin-bottom: 10px !important;
            transition: all 0.2s ease !important;
            cursor: pointer;
        }
        
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            border-color: #3b82f6 !important;
            background: #273549 !important;
        }

        /* Title text styling */
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em !important;
        }

        /* 4. Beautiful Metric Display Grid Cards */
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
        
        /* Border accents for individual assessment tracks */
        .skill-blue { border-left: 5px solid #2563eb !important; }
        .skill-green { border-left: 5px solid #10b981 !important; }
        .skill-amber { border-left: 5px solid #f59e0b !important; }
        .skill-purple { border-left: 5px solid #8b5cf6 !important; }

        /* 5. Chat Interface Customization */
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

        /* 6. Form Container UI */
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
