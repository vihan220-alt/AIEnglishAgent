import streamlit as st

def apply_custom_theme():
    """
    Applies a clean dark theme and styled chat bubbles to the Streamlit app.
    """
    st.markdown("""
        <style>
        /* Main background color */
        .stApp {
            background-color: #0e1117 !important;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #161b22 !important;
            border-right: 1px solid #30363d !important;
        }
        
        /* Chat container styling */
        div[data-testid="stChatMessage"] {
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 12px !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
        }
        
        /* User chat message specific styling */
        div[data-testid="stChatMessageUser"] {
            background-color: #1f242c !important;
        }
        
        /* Custom heading colors */
        h1, h2, h3, h4, h5, h6, p {
            color: #c9d1d9 !important;
        }
        
        /* Custom style for standard action buttons */
        .stButton>button {
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)
