import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000 !important;
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 80px;
            background-repeat: repeat;
        }
        h1, h2, p, div, span, label { color: white !important; }
        .stTextInput > div > div > input, .stChatInput textarea { 
            background-color: #222 !important; color: white !important; 
        }
        </style>
        """, unsafe_allow_html=True)
