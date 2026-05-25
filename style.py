import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            /* New robot face below */
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 80px;
            background-repeat: repeat;
            opacity: 0.8;
        }
        h1, h2, p { color: white !important; }
        </style>
        """, unsafe_allow_html=True)
