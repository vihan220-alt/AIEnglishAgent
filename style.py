import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* Target all primary Streamlit container view depths for background consistency */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewMain"] {
            background-color: #f7f9fc !important;
        }
        
        /* Sidebar container layout styling */
        [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] {
            background-color: #ebf0f6 !important;
        }
        
        /* Make chat bubbles rounded, clean, and spacious */
        [data-testid="stChatMessage"] {
            border-radius: 15px !important;
            padding: 12px 18px !important;
            margin-bottom: 12px !important;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05) !important;
            background-color: #ffffff !important;
        }

        /* Ensure avatars look circular, crisp, and properly sized */
        [data-testid="stChatMessageAvatar"] img, 
        div[data-testid="stChatMessageAvatar"] {
            border-radius: 50% !important;
            width: 42px !important;
            height: 42px !important;
            object-fit: cover !important;
            border: 2px solid #4A90E2 !important;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.12) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
