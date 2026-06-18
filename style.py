import streamlit as st

def apply_custom_css():
    """
    Injects high-visibility CSS styling to transform the Streamlit interface.
    Forces all text targets, selectbox labels, radio items, descriptions, and 
    captions into clear high-contrast white/light-slate ranges.
    """
    custom_css = """
    <style>
        /* Global Background & App Workspace Canvas */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
            background-attachment: fixed;
            color: #f1f5f9 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Sidebar Styling Override & Text Visibility */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border-right: 1px solid rgba(99, 102, 241, 0.2);
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
            color: #f1f5f9 !important;
        }

        /* Header / Toolbar Hidden Clean Up */
        header {
            background: transparent !important;
        }
        
        /* Styled Dynamic Containers & Cards */
        div[data-testid="stElementContainer"] > div.stBlock {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            margin-bottom: 1rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        /* Container Highlight/Hover Effects */
        div[data-testid="stElementContainer"] > div.stBlock:hover {
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.1);
        }

        /* CRITICAL: Force All Standard Forms, Dropdowns, Radios, and Inline Text Labels to White */
        label, p, span, .stText, [data-testid="stMarkdownContainer"] p {
            color: #f1f5f9 !important;
        }
        
        /* Low-Contrast Captions Upgrade */
        .stCaption, caption, small, [data-testid="stCaptionContainer"] {
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
        }

        /* Typography Heading Formatting Fixes */
        h1 {
            color: #ffffff !important;
            font-weight: 800 !important;
            letter-spacing: -0.025em !important;
            background: linear-gradient(to right, #ffffff, #c7d2fe, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding-bottom: 0.5rem;
        }

        h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
        }

        /* Form Subbox Containment Fix */
        div[data-testid="stForm"] {
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(99, 102, 241, 0.25) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        /* Primary Action Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.025em !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
            border-color: rgba(255, 255, 255, 0.2) !important;
        }

        /* Custom Input Node Overrides (Dropdown Options & Forms) */
        div[data-baseweb="select"] > div {
            background-color: #0f172a !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 8px !important;
        }
        
        /* Target dropdown expanded options panel menu */
        div[data-baseweb="menu"] li {
            color: #ffffff !important;
            background-color: #0f172a !important;
        }
        div[data-baseweb="menu"] li:hover {
            background-color: #312e81 !important;
        }

        input, textarea {
            background-color: #0f172a !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 8px !important;
        }

        input:focus, textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        }

        /* Chat Input Sticky Tray UI Fix */
        div[data-testid="stChatInput"] textarea {
            background-color: #1e293b !important;
            color: #ffffff !important;
        }
        div[data-testid="stChatInput"] {
            background-color: #1e293b !important;
            border: 1px solid rgba(99, 102, 241, 0.3) !important;
            border-radius: 12px !important;
            box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.4) !important;
        }

        /* Metrics Widget Alignment Text Accent */
        div[data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetricLabel"] p {
            color: #94a3b8 !important;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
