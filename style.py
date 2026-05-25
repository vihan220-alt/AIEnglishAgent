import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000 !important;
            /* Using a high-quality robot-themed background */
            background-image: url("https://img.freepik.com/free-vector/digital-technology-background-with-abstract-robot-head_23-2148425143.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        
        /* Darken the overlay so white text is always readable */
        .stApp::before {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: -1;
        }

        h1, h2, p, div, span, label { color: #ffffff !important; }
        
        [data-testid="stSidebar"] {
            background-color: #1a1a1a !important;
        }
        </style>
        """, unsafe_allow_html=True)
