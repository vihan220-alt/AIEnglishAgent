import streamlit as st
import json
import os
from streamlit_mic_recorder import mic_recorder
from style import apply_custom_theme

# Now that 'st' is imported, these commands will work:
apply_custom_theme()

# Initialize your state
if "chats" not in st.session_state:
    # ... your initialization logic ...
