import streamlit as st

def apply_custom_theme():
    """
    Forces a high-end, unified dark SaaS design over Streamlit's base styling rules.
    Adds support for rounded, clean visual avatar markers in the chat layout.
    """
    st.markdown("""
        <style>
        /* 1. FORCE GLOBAL APP BACKGROUND AND TEXT COLORS */
        .stApp, [data-testid="stAppViewContainer"] {
            background: #090d16 !important;
            color: #f8fafc !important;
        }
        
        /* Fix text rendering across default paragraph structures */
        .stMarkdown p, span, label, div {
            color: #f8fafc !important;
        }

        /* 2. FIX TITLES AND HEADERS */
        h1 {
            font-size: 36px !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            background: linear-gradient(135deg, #ffffff 40%, #06b6d4 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            margin-bottom: 2px !important;
            padding-bottom: 5px !important;
        }
        
        h3 {
            font-size: 18px !important;
            color: #94a3b8 !important;
            font-weight: 400 !important;
            margin-top: 0px !important;
            margin-bottom: 25px !important;
        }

        /* 3. MODERNIZED SIDEBAR PANEL */
        [data-testid="stSidebar"] {
            background-color: #0b1329 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #ffffff !important;
        }
        
        /* Info alert inside Sidebar */
        div.stAlert {
            background-color: rgba(6, 182, 212, 0.08) !important;
            border: 1px solid rgba(6, 182, 212, 0.2) !important;
            border-radius: 12px !important;
        }
        div.stAlert p {
            color: #cbd5e1 !important;
        }

        /* 4. ROBOT & USER AVATAR CHAT BUBBLES WITH BALANCED FLOW */
        .chat-container-user {
            float: right;
            clear: both;
            display: flex;
            align-items: flex-start;
            justify-content: flex-end;
            max-width: 75%;
            margin: 12px 0;
        }

        .chat-container-coach {
            float: left;
            clear: both;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            max-width: 75%;
            margin: 12px 0;
        }

        .avatar-icon {
            font-size: 24px;
            background: #1e293b;
            padding: 8px;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            width: 42px;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .avatar-icon-coach {
            margin-right: 12px;
            border-color: rgba(6, 182, 212, 0.3);
        }

        .avatar-icon-user {
            margin-left: 12px;
            order: 2; /* Puts user avatar to the right of the text bubble */
        }

        .chat-bubble-user { 
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); 
            padding: 14px 20px; 
            border-radius: 18px 18px 4px 18px; 
            color: #ffffff !important; 
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
            font-size: 15px;
            line-height: 1.5;
            order: 1;
        }
        
        .chat-bubble-coach { 
            background: #1e293b; 
            padding: 14px 20px; 
            border-radius: 18px 18px 18px 4px; 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            color: #f1f5f9 !important; 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            font-size: 15px;
            line-height: 1.5;
        }

        .chat-bubble-coach b, .chat-bubble-user b {
            color: #ffffff !important;
            display: block;
            margin-bottom: 4px;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.8;
        }
        .clear-fix { clear: both; }

        /* 5. INPUT COMPONENT DARKIFY OVERRIDES */
        div[data-testid="stForm"] {
            background-color: #111927 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 14px !important;
            padding: 20px !important;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Fix text field entry styling */
        div[data-testid="stTextInput"] input {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #06b6d4 !important;
            box-shadow: 0 0 0 1px #06b6d4 !important;
        }

        /* 6. CONTROL BUTTONS STYLING */
        button[data-testid="baseButton-secondary"], button[data-testid="baseButton-formSubmit"] {
            background-color: #1e293b !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #f1f5f9 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        button[data-testid="baseButton-secondary"]:hover, button[data-testid="baseButton-formSubmit"]:hover {
            border-color: #06b6d4 !important;
            color: #06b6d4 !important;
            background-color: rgba(6, 182, 212, 0.08) !important;
        }
        
        /* Keep Audio labels clean */
        .control-label {
            font-size: 14px;
            font-weight: 600;
            color: #94a3b8;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
