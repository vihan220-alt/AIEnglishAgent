import streamlit as st

def apply_custom_theme():
    """
    Applies an ultra-premium, dark-mode SaaS UI tailored for interactive learning.
    Includes avatar micro-animations, clear scannable spacing, and glowing indicators.
    """
    st.markdown("""
        <style>
        /* 1. GLOBAL WORKSPACE DESIGN */
        .stApp, [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top, #0f172a 0%, #090d16 100%) !important;
            color: #f8fafc !important;
        }
        
        .stMarkdown p, span, label, div {
            color: #f8fafc !important;
        }

        /* 2. PREMIUM TYPOGRAPHY & TITLES */
        h1 {
            font-size: 38px !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
            background: linear-gradient(135deg, #ffffff 20%, #22d3ee 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            margin-bottom: 4px !important;
            padding-bottom: 8px !important;
        }
        
        h3 {
            font-size: 16px !important;
            color: #94a3b8 !important;
            font-weight: 400 !important;
            letter-spacing: 0.05em !important;
            margin-top: 0px !important;
            margin-bottom: 35px !important;
        }

        /* 3. SIDEBAR PANEL INTEGRATION */
        [data-testid="stSidebar"] {
            background-color: #070a13 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #e2e8f0 !important;
        }
        
        div.stAlert {
            background: rgba(34, 211, 238, 0.05) !important;
            border: 1px solid rgba(34, 211, 238, 0.15) !important;
            border-radius: 14px !important;
        }

        /* 4. CHAT ECOSYSTEM WITH AVATARS & MICRO-GLOW */
        .chat-container-user {
            float: right;
            clear: both;
            display: flex;
            align-items: flex-start;
            justify-content: flex-end;
            max-width: 80%;
            margin: 16px 0;
        }

        .chat-container-coach {
            float: left;
            clear: both;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            max-width: 80%;
            margin: 16px 0;
        }

        .avatar-icon {
            font-size: 22px;
            background: #1e293b;
            padding: 8px;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.08);
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        /* Special pulse aura glow around the AI robot */
        .avatar-icon-coach {
            margin-right: 14px;
            border-color: rgba(34, 211, 238, 0.4);
            box-shadow: 0 0 15px rgba(34, 211, 238, 0.2);
            background: #0f172a;
        }

        .avatar-icon-user {
            margin-left: 14px;
            order: 2;
            border-color: rgba(2, 132, 199, 0.4);
            background: #0c4a6e;
        }

        .chat-bubble-user { 
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); 
            padding: 14px 20px; 
            border-radius: 20px 20px 4px 20px; 
            color: #ffffff !important; 
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
            font-size: 15px;
            line-height: 1.6;
            order: 1;
        }
        
        .chat-bubble-coach { 
            background: #111927; 
            padding: 14px 20px; 
            border-radius: 20px 20px 20px 4px; 
            border: 1px solid rgba(255, 255, 255, 0.06); 
            color: #f1f5f9 !important; 
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
            font-size: 15px;
            line-height: 1.6;
        }

        .chat-bubble-coach b, .chat-bubble-user b {
            color: #94a3b8 !important;
            display: block;
            margin-bottom: 6px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        .chat-bubble-user b {
            color: #bae6fd !important;
            text-align: right;
        }
        .clear-fix { clear: both; }

        /* 5. FLOATING BOTTOM CONTROL CARD OVERRIDES */
        div[data-testid="stForm"] {
            background: linear-gradient(180deg, #111927 0%, #0b1329 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-top: 2px solid rgba(34, 211, 238, 0.3) !important; /* Premium Cyan Accent Line */
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
        }
        
        div[data-testid="stTextInput"] input {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            padding: 12px !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #22d3ee !important;
            box-shadow: 0 0 8px rgba(34, 211, 238, 0.2) !important;
        }

        /* 6. BUTTON STATES & ALIGNMENT HACKS */
        button[data-testid="baseButton-secondary"], button[data-testid="baseButton-formSubmit"] {
            background: #1e293b !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #f1f5f9 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 8px 16px !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        button[data-testid="baseButton-secondary"]:hover, button[data-testid="baseButton-formSubmit"]:hover {
            border-color: #22d3ee !important;
            color: #22d3ee !important;
            background: rgba(34, 211, 238, 0.06) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(34, 211, 238, 0.1);
        }
        
        .control-label {
            font-size: 13px;
            font-weight: 600;
            color: #94a3b8;
            margin-bottom: 10px;
            letter-spacing: 0.02em;
        }
        
        hr {
            border-color: rgba(255, 255, 255, 0.06) !important;
        }
        </style>
    """, unsafe_allow_html=True)
