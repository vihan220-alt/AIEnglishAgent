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
        /* Make Sidebar Text and Inputs Sharp */
        h1, h2, p, div, span, label { color: white !important; }
        
        /* Style the Rename, Pin, Delete buttons inside the expander */
        [data-testid="stSidebar"] button {
            background-color: #333333 !important;
            color: white !important;
            border: 1px solid #555555 !important;
            width: 100% !important;
            padding: 5px !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #555555 !important;
            border-color: #00ea96 !important;
        }
        </style>
        """, unsafe_allow_html=True)
