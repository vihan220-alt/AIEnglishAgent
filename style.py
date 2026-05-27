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
        
        /* 2. Fix Layout Padding to prevent header overlap */
        .block-container {
            padding-top: 4.5rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* 3. Modern Chat Alignment System (Left/Right) */
        div[data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
            padding: 0rem !important;
            margin-bottom: 1rem !important;
            display: flex !important;
            width: 100% !important;
        }

        /* Target the internal container to force alignment width */
        div[data-testid="stChatMessage"] > div {
            max-width: 75% !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.3) !important;
        }

        /* --- USER MESSAGE STYLE (Right Aligned) --- */
        div[data-testid="stChatMessage"]:has(img[alt="user"]),
        div[data-testid="stChatMessage"]:has(span:contains("👤")),
        div[data-testid="stChatMessage"][aria-label="user"] {
            justify-content: flex-end !important;
            margin-left: auto !important;
        }
        
        div[data-testid="stChatMessage"]:has(img[alt="user"]) > div,
        div[data-testid="stChatMessage"]:has(span:contains("👤")) > div,
        div[data-testid="stChatMessage"][aria-label="user"] > div {
            background-color: #1f293d !important; /* Elegant slate blue/dark grey */
            border: 1px solid #2d3d5a !important;
        }

        /* --- ASSISTANT MESSAGE STYLE (Left Aligned) --- */
        div[data-testid="stChatMessage"]:has(img[alt="assistant"]),
        div[data-testid="stChatMessage"]:has(span:contains("🤖")),
        div[data-testid="stChatMessage"][aria-label="assistant"] {
            justify-content: flex-start !important;
            margin-right: auto !important;
        }
        
        div[data-testid="stChatMessage"]:has(img[alt="assistant"]) > div,
        div[data-testid="stChatMessage"]:has(span:contains("🤖")) > div,
        div[data-testid="stChatMessage"][aria-label="assistant"] > div {
            background-color: #161b22 !important; /* Clean dark grey background */
            border: 1px solid #30363d !important;
        }

        /* 4. Global Text Visibility inside Bubbles */
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] span,
        div[data-testid="stChatMessage"] div,
        div[data-testid="stChatMessage"] .stMarkdown p {
            color: #ffffff !important;
            font-weight: 500 !important;
            font-size: 1.05rem !important;
            line-height: 1.5 !important;
        }

        /* Hide avatar icons if you want a pure message box layout like the screenshot */
        div[data-testid="stChatMessageAvatar"] {
            display: none !important;
        }
        
        /* 5. Interface Headings & Headers */
        h1, h2, h3, [data-testid="stHeader"] {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        /* 6. Fix Chat Input Box Styling */
        div[data-testid="stChatInput"] textarea {
            color: #ffffff !important;
            background-color: #161b22 !important;
            font-size: 1.05rem !important;
        }
        
        /* 7. Sidebar Panel Contrast */
        .stSidebar {
            background-color: #161b22 !important;
            border-right: 1px solid #30363d !important;
        }
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p, .stSidebar label {
            color: #ffffff !important;
        }
        div[data-testid="stExpander"] {
            background-color: #1f242c !important;
            border: 1
