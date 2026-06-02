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
        
        /* Make chat bubbles rounded, clean, and spacious */
        [data-testid="stChatMessage"] {
            border-radius: 15px;
            padding: 12px 18px;
            margin-bottom: 12px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
            background-color: #ffffff;
        }

        /* Ensure avatars look circular, crisp, and properly sized */
        [data-testid="stChatMessageAvatar"] img {
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
