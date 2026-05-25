import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Robot face wall background design */
        .stApp {
            background-color: #000000 !important;
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 100px;
            background-repeat: repeat;
        }
        /* Green Chat Containers */
        [data-testid="stChatMessage"] {
            background-color: #004d40 !important;
            border-radius: 12px;
            color: #ffffff !important;
            margin-bottom: 10px;
        }
        /* Text visibility overrides */
        h1, h2, h3, p, div, span, label { color: #ffffff !important; }
        
        /* Make sidebar elements distinct and visible */
        [data-testid="stSidebar"] button {
            background-color: #2b2b2b !important;
            color: #ffffff !important;
            border: 1px solid #444444 !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #444444 !important;
            border-color: #00ea96 !important;
        }
        </style>
        """, unsafe_allow_html=True)
