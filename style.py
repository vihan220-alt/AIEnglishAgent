import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* Apply a repeating robot face pattern across the main background and sidebar */
        .stApp, [data-testid="stSidebar"] {
            background-color: #0e1117;
            background-image: url("https://www.transparenttextures.com/patterns/black-thread.png"), 
                              url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Ctext x='20' y='50' font-size='40' style='fill: %23ffffff; opacity: 0.04; font-family: sans-serif;'%3E🤖%3C/text%3E%3C/svg%3E");
            background-repeat: repeat;
        }

        /* Keep chat bubbles clear and readable over the background robot shapes */
        [data-testid="stChatMessage"] {
            background-color: rgba(23, 28, 41, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
