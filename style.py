import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117 !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM5 10h50v40H5zm2 2v36h46V12zm18-7h10v3H25z' fill='%2330363d' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
        }
        div[data-testid="stChatMessage"] {
            background-color: #161b22 !important;
            border: 2px solid #444c56 !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)
