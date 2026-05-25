import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Robot face background */
        .stApp {
            background-color: #000000 !important;
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 100px;
            background-repeat: repeat;
        }
        /* Green Chat Bubbles */
        [data-testid="stChatMessage"] {
            background-color: #004d40 !important;
            border-radius: 15px;
            color: white !important;
        }
        /* White text for everything */
        h1, h2, p, div, span, label { color: white !important; }
        .stTextInput > div > div > input { background-color: #222 !important; color: white !important; }
        </style>
        """, unsafe_allow_html=True)
