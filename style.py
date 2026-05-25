import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Force the main app background to black */
        .stApp { 
            background-color: #000000 !important; 
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 100px;
            background-repeat: repeat;
        }
        
        /* Force all text elements to white */
        h1, h2, h3, p, div, span, label { 
            color: #ffffff !important; 
        }
        
        /* Force inputs and text areas to be dark with white text */
        .stTextInput > div > div > input, .stChatInput textarea { 
            background-color: #1a1a1a !important; 
            color: white !important; 
            border: 1px solid #444 !important;
        }
        
        /* Force buttons to be dark */
        .stButton button { 
            background-color: #262626 !important; 
            color: white !important; 
            border: 1px solid #444 !important; 
        }
        </style>
        """, unsafe_allow_html=True)
