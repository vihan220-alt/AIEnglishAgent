import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Main page background */
        .stApp {
            background-color: #F4F7F6;
        }
        
        /* Chat Input Styling */
        .stChatInputContainer {
            padding-bottom: 20px;
        }
        
        /* Sidebar styling styling */
        section[data-testid="stSidebar"] {
            background-color: #E8ECEB !important;
        }
        
        /* Titles and text coloring */
        h1, h2, h3, h5, p {
            color: #2C3E50;
        }
        </style>
    """, unsafe_allow_html=True)
