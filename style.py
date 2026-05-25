import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000 !important;
            /* Use the clean robot face icon */
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 80px;
            background-repeat: repeat;
            /* Makes the icon subtle so text remains readable */
            background-blend-mode: overlay;
        }
        
        /* Ensure everything else stays dark and readable */
        h1, h2, p, div, span, label { color: white !important; }
        
        [data-testid="stSidebar"] {
            background-color: #1a1a1a !important;
        }
        </style>
        """, unsafe_allow_html=True)
