import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000;
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 80px;
        }
        /* Make all text white and input fields black */
        h1, h2, p, div, span, label { color: white !important; }
        .stTextInput > div > div > input { background-color: black !important; color: white !important; }
        .stChatInput textarea { background-color: black !important; color: white !important; }
        .stButton button { background-color: #222 !important; color: white !important; }
        </style>
        """, unsafe_allow_html=True)
