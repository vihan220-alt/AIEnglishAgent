import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp { 
            background-color: #000000 !important; 
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 150px;
            background-repeat: repeat;
        }
        /* Forces all text, labels, and headers to be white */
        h1, h2, p, div, span, label, .stMarkdown { color: white !important; }
        
        /* Ensures inputs are dark with white text */
        .stTextInput > div > div > input, .stChatInput textarea { 
            background-color: #111 !important; color: white !important; border: 1px solid #444;
        }
        
        /* Style buttons */
        .stButton button { background-color: #222 !important; color: white !important; border: 1px solid #444; }
        </style>
        """, unsafe_allow_html=True)
