import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Force dark background and repeating robot icon */
        .stApp {
            background-color: #000000 !important;
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 100px;
            background-repeat: repeat;
        }
        
        /* Make text white and sidebar distinct */
        h1, h2, p, div, span, label { color: white !important; }
        
        [data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 1px solid #333;
        }
        </style>
        """, unsafe_allow_html=True)
