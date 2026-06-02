import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* Force the entire main background to be pure white */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewMain"], [data-testid="stMain"] {
            background-color: #ffffff !important;
        }
        
        /* Sidebar layout styling - kept slightly off-white for nice contrast */
        [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] {
            background-color: #f0f2f6 !important;
        }
        
        /* Make chat bubbles light gray with rounded corners so they stand out on the white background */
        [data-testid="stChatMessage"] {
            border-radius: 15px !important;
            padding: 12px 18px !important;
            margin-bottom: 12px !important;
            box-shadow: 0px 1px 3px rgba(0,0,0,0.05) !important;
            background-color: #f8f9fa !important;
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
