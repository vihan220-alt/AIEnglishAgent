import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* 1. BRIGHT MULTICOLOR VECTOR ROBOT WALLPAPER GRID */
        .stApp, [data-testid="stSidebar"] {
            background-color: #0b0f19; /* Deep space canvas */
            background-image: 
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cg opacity='0.22'%3E%3C!-- RED ROBOT --%3E%3Cpath d='M20,25 h30 v25 h-30 z M15,35 h5 M50,35 h5 M25,20 h5 M40,20 h5 M27,33 h4 M41,33 h4 M30,42 h12' stroke='%23ff4b4b' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C!-- BLUE ROBOT --%3E%3Cpath d='M100,25 h30 v25 h-30 z M95,35 h5 M130,35 h5 M105,20 h5 M120,20 h5 M107,33 h4 M121,33 h4 M110,42 h12' stroke='%233b82f6' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C!-- GREEN ROBOT --%3E%3Cpath d='M20,105 h30 v25 h-30 z M15,115 h5 M50,115 h5 M25,100 h5 M40,100 h5 M27,113 h4 M41,113 h4 M30,122 h12' stroke='%2310b981' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C!-- YELLOW ROBOT --%3E%3Cpath d='M100,105 h30 v25 h-30 z M95,115 h5 M130,115 h5 M105,100 h5 M120,100 h5 M107,113 h4 M121,113 h4 M110,122 h12' stroke='%23eab308' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/g%3E%3C/svg%3E");
            background-repeat: repeat;
        }

        /* 2. CHAT BUBBLE SHAPES WITH MATCHING GLOW EFFECTS */
        [data-testid="stChatMessage"] {
            background-color: rgba(22, 30, 49, 0.94) !important;
            border-radius: 20px;
            margin-bottom: 15px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }

        /* Blue glowing border accent for Coach messages */
        [data-testid="stChatMessage"]:nth-child(even) {
            border: 2px solid #3b82f6 !important;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.25);
        }

        /* Green glowing border accent for User messages */
        [data-testid="stChatMessage"]:nth-child(odd) {
            border: 2px solid #10b981 !important;
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.25);
        }

        /* 3. SHARP AND CLEAN CONTRAST FOR TEXT */
        .stMarkdown p {
            color: #ffffff !important;
            font-size: 17px !important;
            font-weight: 500;
            letter-spacing: 0.3px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
