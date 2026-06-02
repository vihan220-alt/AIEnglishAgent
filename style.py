import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* Main page background */
        .stApp {
            background-color: #f7f9fc;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #ebf0f6;
        }

        /* FORCE COLORFUL ROBOT FACES IN THE BACKGROUND */
        /* This replaces the default gray assistant icon with a bright, colorful robot face */
        [data-testid="stChatMessageAvatarAssistant"] div, 
        [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] svg,
        img[alt="assistant avatar"] {
            display: none !important;
        }
        
        [data-testid="stChatMessageAvatarAssistant"] {
            background-image: url('https://img.icons8.com/fluent/512/futurama-bender.png') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            border: 2px solid #4A90E2 !important;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.15) !important;
        }
        
        /* Make chat bubbles rounded and clean */
        [data-testid="stChatMessage"] {
            border-radius: 15px;
            padding: 10px 15px;
            margin-bottom: 10px;
            box-shadow: 0px 1px 3px rgba(0,0,0,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
