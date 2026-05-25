import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Dark background with a single, centered robot face */
        .stApp {
            background-color: #000000 !important;
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 200px; /* Adjust this to make the face larger or smaller */
            background-repeat: no-repeat;
            background-position: center;
        }
        
        /* Ensure chat bubbles are distinct and readable */
        .stChatMessage {
            background-color: rgba(30, 30, 30, 0.8) !important;
            border: 1px solid #444;
            color: #ffffff !important;
        }

        /* Ensure all text is white */
        h1, h2, p, div, span, label { color: #ffffff !important; }
        
        /* Dark inputs */
        .stTextInput > div > div > input, .stChatInput textarea { 
            background-color: #1a1a1a !important; 
            color: white !important; 
        }
        </style>
        """, unsafe_allow_html=True)
