import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* 1. VIBRANT MULTICOLOR ROBOT PATTERN BACKGROUND */
        .stApp, [data-testid="stSidebar"] {
            background-color: #0f172a; /* Rich, dark midnight canvas */
            background-image: 
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ctext x='10' y='40' font-size='28' style='fill: %2338bdf8; opacity: 0.15;'%3E🤖%3C/text%3E%3Ctext x='70' y='40' font-size='28' style='fill: %234ade80; opacity: 0.15;'%3E🤖%3C/text%3E%3Ctext x='40' y='95' font-size='28' style='fill: %23a855f7; opacity: 0.15;'%3E🤖%3C/text%3E%3Ctext x='100' y='95' font-size='28' style='fill: %23facc15; opacity: 0.15;'%3E🤖%3C/text%3E%3C/svg%3E");
            background-repeat: repeat;
        }

        /* 2. CHAT BUBBLES WITH COLORFUL GLOWING BORDERS */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 41, 59, 0.9) !important;
            border-radius: 16px;
            margin-bottom: 14px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        /* Distinct border color for the Coach */
        [data-testid="stChatMessage"]:nth-child(even) {
            border: 2px solid #38bdf8 !important; /* Cool Blue Border */
        }

        /* Distinct border color for the User */
        [data-testid="stChatMessage"]:nth-child(odd) {
            border: 2px solid #a855f7 !important; /* Fun Purple Border */
        }

        /* 3. BRIGHTENING THE TEXT FOR READABILITY */
        .stMarkdown p {
            color: #f8fafc !important;
            font-size: 17px !important;
            font-weight: 500;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
