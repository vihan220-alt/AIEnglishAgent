import streamlit as st

def apply_custom_theme():
    """
    Applies a clean dark theme with an animated floating robot face background.
    Fixes contrast visibility for chat contents and action buttons.
    """
    st.markdown("""
        <style>
        /* Base application background setup */
        .stApp {
            background-color: #0e1117 !important;
            position: relative;
            overflow: hidden;
        }

        /* --- ROBOT BACKGROUND ANIMATION LAYER --- */
        .stApp::before {
            content: "🤖";
            position: absolute;
            font-size: 150px;
            opacity: 0.04;
            top: 10%;
            left: 5%;
            animation: floatFirst 25s ease-in-out infinite alternate;
            pointer-events: none;
            z-index: 0;
        }

        .stApp::after {
            content: "🤖";
            position: absolute;
            font-size: 120px;
            opacity: 0
