# --- Custom CSS for Dark Theme with Robot Face Background ---
st.markdown("""
    <style>
    /* Main App Background with SVG Robot Face Pattern */
    .stApp {
        background-color: #0e1117 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM5 10h50v40H5zm2 2v36h46V12zm18-7h10v3H25z' fill='%231f242c' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
        background-repeat: repeat !important;
        color: #ffffff;
    }
    
    /* Sidebar Background styling */
    .stSidebar {
        background-color: #161b22 !important;
    }
    
    /* Expander boxes styling */
    div[data-testid="stExpander"] {
        background-color: #1f242c !important;
        border: 1px solid #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)
