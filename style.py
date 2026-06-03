import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300..700&family=Nunito:wght@400;600;700;900&display=swap');

        /* 1. Global App Viewport Setup */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewMain"], [data-testid="stMain"] {
            background: linear-gradient(135deg, #f3f7fa 0%, #eef3f8 100%) !important;
            font-family: 'Nunito', sans-serif !important;
        }
        
        /* 2. Primary Layout Typography Formatting */
        h1, h2, h3, .stTitle {
            font-family: 'Fredoka', sans-serif !important;
            color: #2c3e50 !important;
            font-weight: 600 !important;
        }
        
        /* 3. Elegant Premium Sidebar Styling */
        [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
            color: #f8fafc !important;
        }
        
        /* Sidebar Text Elements */
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] write {
            color: #cbd5e1 !important;
            font-family: 'Nunito', sans-serif !important;
        }

        /* 4. Chat Message Container Overhauls */
        [data-testid="stChatMessage"] {
            border-radius: 20px !important;
            padding: 16px 22px !important;
            margin-bottom: 16px !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            transition: all 0.3s ease-in-out !important;
        }

        /* Differentiate User Messages vs Coach Responses */
        [data-testid="stChatMessage"]:has(img[src*="female-profile"]) {
            background-color: #ffffff !important;
            box-shadow: 0px 4px 15px rgba(148, 163, 184, 0.08) !important;
        }

        [data-testid="stChatMessage"]:has(img[src*="bot"]) {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
            box-shadow: 0px 6px 20px rgba(74, 144, 226, 0.06) !important;
            border-left: 5px solid #3b82f6 !important;
        }

        /* Bubble Hover Animating Effect */
        [data-testid="stChatMessage"]:hover {
            transform: translateY(-2px);
            box-shadow: 0px 8px 24px rgba(148, 163, 184, 0.15
