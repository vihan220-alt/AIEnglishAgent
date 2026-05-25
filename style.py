import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
            background-size: 80px;
        }
        h1, h2, p { color: white !important; }
        </style>
        """, unsafe_allow_html=True)
