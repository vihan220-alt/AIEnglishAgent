import streamlit as st

def apply_custom_theme():
    """
    Applies a clean dark theme with animated colorful floating robot background accents.
    """
    st.markdown("""
        <style>
        /* Base page canvas container styling */
        .stApp {
            background-color: #0e1117 !important;
            position: relative;
            overflow: hidden;
        }

        /* --- COLORFUL ROBOT BACKGROUND LAYER --- */
        /* Robot 1: Neon Cyan/Blue vibe */
        .stApp::before {
            content: "🤖";
            position: absolute;
            font-size: 140px;
            top: 15%;
            left: 8%;
            opacity: 0.15;
            filter: drop-shadow(0 0 20px #00d2ff) drop-shadow(0 0 40px #0066ff);
            animation: floatCyan 20s ease-in-out infinite alternate;
            pointer-events: none;
            z-index: 0;
        }

        /* Robot 2: Neon Purple/Pink vibe */
        .stApp::after {
            content: "🤖";
            position: absolute;
            font-size: 110px;
            bottom: 20%;
            right: 10%;
            opacity: 0.12;
            filter: drop-shadow(0 0 20px #ff007f) drop-shadow(0 0 40px #9900ff);
            animation: floatPink 25s ease-in-out infinite alternate;
            pointer-events: none;
            z-index: 0;
        }

        /* Dynamic keyframes to handle custom movement & color shifting glow */
        @keyframes floatCyan {
            0% { 
                transform: translateY(0px) rotate(0deg) scale(1); 
                filter: drop-shadow(0 0 15px #00d2ff) hue-rotate(0deg);
            }
            50% { 
                transform: translateY(35px) rotate(10deg) scale(1.05); 
                filter: drop-shadow(0 0 30px #00ffaa) hue-rotate(45deg);
            }
            100% { 
                transform: translateY(-15px) rotate(-8deg) scale(0.95); 
                filter: drop-shadow(0 0 15px #0066ff) hue-rotate(-30deg);
            }
        }

        @keyframes floatPink {
            0% { 
                transform: translateY(0px) rotate(0deg) scale(1); 
                filter: drop-shadow(0 0 15px #ff007f) hue-rotate(0deg);
            }
            50% { 
                transform: translateY(-40px) rotate(-12deg) scale(0.9); 
                filter: drop-shadow(0 0 25px #ffaa00) hue-rotate(90deg);
            }
            100% { 
                transform: translateY(25px) rotate(8deg) scale(1.05); 
                filter: drop-shadow(0 0 20px #9900ff) hue-rotate(-45deg);
            }
        }

        /* Force main application elements to render clearly above background filters */
        .stMainBlockContainer {
            position: relative;
            z-index: 1;
            background: rgba(14, 17, 23, 0.6);
            border-radius: 16px;
            padding: 20px !important;
        }

        /* Sidebar container details */
        section[data-testid="stSidebar"] {
            background-color: #161b22 !important;
            border-right: 1px solid #30363d !important;
            z-index: 2;
        }
        
        /* Fix text contrast rules */
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #f0f6fc !important;
        }

        /* Clear chat component structures */
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] span, 
        div[data-testid="stChatMessage"] {
            color: #ffffff !important;
            font-size: 16px !important;
        }
        
        div[data-testid="stChatMessage"] {
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 12px !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
        }
        
        div[data-testid="stChatMessageUser"] {
            background-color: #1f242c !important;
        }

        .stButton>button {
            border-radius: 8px !important;
            color: #ffffff !important;
            background-color: #21262d !important;
            border: 1px solid #30363d !important;
        }
        
        .stButton>button:hover {
            border-color: #8b949e !important;
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)
