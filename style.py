import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. Main App Background with Tiled Robot Pattern */
        .stApp {
            background-color: #0e1117 !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM5 10h50v40H5zm2 2v36h46V12zm18-7h10v3H25z' fill='%2330363d' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
            background-repeat: repeat !important;
        }
        
        /* 2. Global Text Overrides for Ultimate Brightness */
        .stApp, .stApp p, span, div, label, li, ul, ol, .stMarkdown {
            color: #ffffff !important;
            font-weight: 500 !important;
        }
        
        /* 3. High-Contrast Chat Message Container Blocks */
        div[data-testid="stChatMessage"] {
            background-color: #161b22 !important;
            border: 2px solid #444c56 !important;
            border-radius: 8px !important;
            padding: 15px !important;
            margin-bottom: 12px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5) !important;
        }
        
        /* Force all chat bubble content to be bright white */
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] span,
        div[data-testid="stChatMessage"] div,
        div[data-testid="stChatMessage"] li,
        div[data-testid="stChatMessage"] ul,
        div[data-testid="stChatMessage"] ol,
        div[data-testid="stChatMessage"] .stMarkdown p {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
        }
        
        /* 4. Headings & Titles Brightness */
        h1, h2, h3, .stApp h1, .stApp h2, [data-testid="stHeader"] {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        /* 5. Fix Chat Input Box Text Color */
        div[data-testid="stChatInput"] textarea {
            color: #ffffff !important;
            background-color: #161b22 !important;
            font-size: 1.05rem !important;
        }
        
        /* 6. Sidebar & Expanders Contrast */
        .stSidebar {
            background-color: #161b22 !important;
            border-right: 1px solid #30363d !important;
        }
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p, .stSidebar label {
            color: #ffffff !important;
        }
        div[data-testid="stExpander"] {
            background-color: #1f242c !important;
            border: 1px solid #444c56 !important;
        }
        
        /* 7. Caption Text Adjustment */
        .stApp .stCaption, .stApp p.caption, div[data-testid="stCaptionContainer"] {
            color: #c9d1d9 !important;
            font-size: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
