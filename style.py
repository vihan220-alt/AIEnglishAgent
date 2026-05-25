import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Force the entire page background to dark black */
        .stApp {
            background-color: #000000 !important;
            /* New URL with high-contrast, clean robot faces */
            background-image: url("https://cdn-icons-png.flaticon.com/512/2040/2040901.png");
            background-size: 80px;
            background-repeat: repeat;
            opacity: 0.85; /* Makes text easier to read */
        }
        
        /* Ensure all text is bright white */
        h1, h2, h3, p, div, span, label, .stMarkdown { 
            color: #ffffff !important; 
        }
        
        /* Style input fields (chat input, text boxes) to be dark */
        .stTextInput > div > div > input, .stChatInput textarea { 
            background-color: #1a1a1a !important; 
            color: #ffffff !important; 
            border: 1px solid #444 !important;
        }
        
        /* Style buttons to be visible but dark */
        .stButton button { 
            background-color: #333333 !important; 
            color: #ffffff !important; 
            border: 1px solid #555 !important; 
        }
        
        /* Specifically target chat messages to have dark backgrounds */
        .stChatMessage {
            background-color: rgba(26, 26, 26, 0.9) !important;
            border-radius: 10px;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
