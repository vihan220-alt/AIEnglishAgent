import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* 1. BRIGHT MULTICOLOR ROBOT WALLPAPER GRID */
        .stApp, [data-testid="stSidebar"] {
            background-color: #0b0f19; /* Deep space background to make colors pop */
            background-image: 
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140' viewBox='0 0 140 140'%3E%3Ctext x='15' y='45' font-size='32' style='fill: %23ff4b4b; opacity: 0.18;'%3E🤖%3C/text%3E%3Ctext x='85' y='45' font-size='32' style='fill: %231d4ed8; opacity: 0.18;'%3E🤖%3C/text%3E%3Ctext x='15' y='115' font-size='32' style='fill: %2310b981; opacity: 0.18;'%3E🤖%3C/text%3E%3Ctext x='85' y='115' font-size='32' style='fill: %23eab308; opacity: 0.18;'%3E🤖%3C/text%3E%3C/svg%3E");
            background-repeat: repeat;
        }

        /* 2. CHAT BUBBLE SHAPES WITH GLOW EFFECTS */
        [data-testid="stChatMessage"] {
            background-color: rgba(22, 30, 49, 0.92) !important;
            border-radius: 20px;
            margin-bottom: 15px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }

        /* Red-to-Blue glowing border accent for Coach messages */
        [data-testid="stChatMessage"]:nth-child(even) {
            border: 2px solid #3b82f6 !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
        }

        /* Green-to-Yellow glowing border accent for User messages */
        [data-testid="stChatMessage"]:nth-child(odd) {
            border: 2px solid #10b981 !important;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
        }

        /* 3. SHARP AND CLEAN CONTRAST FOR TEXT */
        .stMarkdown p {
            color: #ffffff !important;
            font-size: 17px !important;
            font-weight: 500;
            letter-spacing: 0.3px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
