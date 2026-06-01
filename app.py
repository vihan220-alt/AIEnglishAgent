import streamlit as st
import json
import os
from groq import Groq
from gtts import gTTS
import io

# Page Config
st.set_page_config(page_title="AI Coach", layout="wide")

# Custom CSS (Robot Face Background)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM
