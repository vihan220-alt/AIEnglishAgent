import streamlit as st
import json
import os
import io
import time
import base64
import speech_recognition as sr
from gtts import gTTS
from style import apply_custom_theme

# Apply CSS styles
apply_custom_theme()

DATA_FILE = "chat_history.json"

def load_data():
    if os.path.exists(DATA
