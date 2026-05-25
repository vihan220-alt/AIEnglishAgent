import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }
        h1, h2, p, div, span { color: #ffffff !important; }
        </style>
        """, unsafe_allow_html=True)
