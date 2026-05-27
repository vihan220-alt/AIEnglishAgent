import streamlit as st
import json
import os
import time
import io
import hashlib
from groq import Groq
from gtts import gTTS

# --- File Sync Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

st.set_page_config(layout="wide")

# --- Custom CSS for Maximum High-Contrast Bright Text & Robot Background ---
st.markdown("""
    <style>
    /* 1. Main App Background with Tiled Robot Pattern */
    .stApp {
        background-color: #0e1117 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM5 10h50v40H5zm2 2v36h46V12zm18-7h10v3H25z' fill='%2330363d' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
        background-repeat: repeat !important;
    }
    
    /* 2. ULTRABRIGHT GLOBAL TEXT OVERRIDES (Forces everything to bright white) */
    .stApp, .stApp p, span, div, label, .stMarkdown {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* 3. High-Contrast Chat Message Container Blocks */
    div[data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 2px solid #444c56 !important; /* Slightly brighter border for clarity */
        border-radius: 8px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* FORCE ALL CHAT BUBBLE TEXT TO BE PURE GLOWING WHITE */
    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessage"] .stMarkdown p {
        color: #ffffff !important;
        font-weight: 600 !important; /* Bolded slightly for ultimate readability */
        font-size: 1.1rem !important;
        text-shadow: 0px 0px 1px rgba(255, 255, 255, 0.2) !important;
    }
    
    /* 4. Headings & Titles Brightness */
    h1, h2, h3, .stApp h1, .stApp h2, [data-testid="stHeader"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* 5. Fix Chat Input Box Text & Placeholder Colors */
    div
