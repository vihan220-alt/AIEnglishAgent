import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* Import a clean, premium font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }

        /* 1. Global App Background Overhaul */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        }

        /* 2. Sidebar Premium Styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important; /* Dark Elegant Slate */
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p {
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] .stRadio i {
            color: #38bdf8 !important; /* Bright teal/blue active accents */
        }

        /* 3. Sleek Main Header & Titles */
        h1 {
            color: #1e293b !important;
            font-weight: 700 !important;
            letter-spacing: -0.05em;
            margin-bottom: 0.5rem !important;
        }
        
        /* 4. Beautiful Rounded Chat Bubbles */
        [data-testid="stChatMessage"] {
            border-radius: 16px !important;
            padding: 1.2rem !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px id4px -1px rgba(0, 0, 0, 0.03) !important;
        }
        
        /* User Chat Bubble (Right-aligned look or crisp white) */
        [data-testid="stChatMessageUser"] {
            background-color: #e0f2fe !important; /* Light sky blue */
            border-left: 5px solid #0ea5e9 !important;
        }
        
        /* Assistant Chat Bubble */
        [data-testid="stChatMessageAssistant"] {
            background-color: #ffffff !important;
            border-left: 5px solid #10b981 !important; /* Clean emerald green */
        }

        /* 5. Custom Dashboard Cards (Analytics View) */
        .skill-card {
            background: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            transition: transform 0.2s ease;
            border: 1px solid #e2e8f0;
        }
        .skill-card:hover {
            transform: translateY(-4px);
        }
        .skill-title {
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .skill-desc {
            font-size: 0.9rem;
            color: #64748b;
            line-height: 1.5;
        }
        .skill-blue { border-top: 4px solid #3b82f6; }
        .skill-green { border-top: 4px solid #10b981; }
        .skill-amber { border-top: 4px solid #f59e0b; }
        .skill-purple { border-top: 4px solid #8b5cf6; }

        /* 6. Form Card Configurations */
        [data-testid="stForm"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05) !important;
        }

        /* 7. Premium Action Buttons */
        .stButton>button {
            border-radius: 12px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        /* Input Field Focus styling styling */
        .stTextInput input, .stSelectbox div {
            border-radius: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
