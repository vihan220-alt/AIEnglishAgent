import streamlit as st

def apply_custom_theme():
    """
    Applies a premium, modern SaaS theme to the Fluency Coach application.
    Features modern fluid gradients, clean micro-interactions, dark mode panel matching,
    and responsive, highly scannable custom message bubbles.
    """
    st.markdown("""
        <style>
        /* Global Background and Typography settings */
        .main { 
            background: linear-gradient(135deg, #090d16 0%, #0f172a 100%); 
            color: #f8fafc; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Premium Gradient Header Styling */
        .stHeading h1 { 
            font-size: 34px; 
            font-weight: 800; 
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #ffffff 30%, #06b6d4 100%); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            margin-bottom: 4px;
        }
        
        .stHeading h3 { 
            font-size: 16px; 
            color: #94a3b8; 
            font-weight: 400; 
            margin-top: 0px;
            margin-bottom: 25px;
        }

        /* Modernized Sidebar Workspace Styling */
        div[data-testid="stSidebar"] {
            background-color: #0b1329 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        div[data-testid="stSidebar"] h2 {
            color: #ffffff;
            font-weight: 700;
        }
        
        /* Redesigned Info Containers with Glow accents */
        div.stAlert {
            background-color: rgba(6, 182, 212, 0.06) !important;
            border: 1px solid rgba(6, 182, 212, 0.15) !important;
            color: #e2e8f0 !important;
            border-radius: 12px;
        }

        /* Smooth UI Input Cards */
        div[data-testid="stForm"] {
            background-color: #111927 !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 14px !important;
            padding: 20px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }

        /* Custom Dynamic Chat Window Bubbles */
        .chat-bubble-user { 
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); 
            padding: 14px 20px; 
            border-radius: 18px 18px 4px 18px; 
            margin: 12px 0; 
            max-width: 75%; 
            float: right; 
            clear: both; 
            color: #ffffff; 
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.15);
            font-size: 15px;
            line-height: 1.5;
        }
        
        .chat-bubble-coach { 
            background: #1e293b; 
            padding: 14px 20px; 
            border-radius: 18px 18px 18px 4px; 
            margin: 12px 0; 
            max-width: 75%; 
            float: left; 
            clear: both; 
            border: 1px solid rgba(255, 255, 255, 0.06); 
            color: #f1f5f9; 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            font-size: 15px;
            line-height: 1.5;
        }

        /* Micro-animations and alignment fixes */
        .clear-fix { clear: both; }
        
        hr {
            border-color: rgba(255, 255, 255, 0.05) !important;
            margin: 30px 0 !important;
        }

        /* Customized Buttons to fit high-end aesthetic */
        button[data-testid="baseButton-secondary"] {
            background-color: #1e293b !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #f1f5f9 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease;
        }
        button[data-testid="baseButton-secondary"]:hover {
            border-color: #06b6d4 !important;
            color: #06b6d4 !important;
            background-color: rgba(6, 182, 212, 0.05) !important;
        }
        </style>
    """, unsafe_allow_html=True)
