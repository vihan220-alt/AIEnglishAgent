import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000 !important;
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: cover; /* This makes the image stretch to fill */
            background-position: center;
            background-repeat: no-repeat;
        }
        
        /* Force dark theme for chat messages */
        .stChatMessage {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px;
            padding: 10px;
        }
        
        h1, h2, p, div, span, label { color: white !important; }
        
        .stTextInput > div > div > input, .stChatInput textarea { 
            background-color: #222 !important; color: white !important; 
        }
        </style>
        """, unsafe_allow_html=True)
