import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* Target the main app container and sidebar background */
        .stApp, [data-testid="stSidebar"] {
            background-color: #0e1117;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Ctext x='15' y='40' font-size='30' opacity='0.08'%3E🤖%3C/text%3E%3C/svg%3E");
            background-repeat: repeat;
        }

        /* Make sure chat bubbles stand out clearly over the background pattern */
        [data-testid="stChatMessage"] {
            background-color: rgba(23, 28, 41, 0.85) !important;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
