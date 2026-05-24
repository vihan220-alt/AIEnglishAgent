import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3
import json

# --- 1. Background & Theme ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-size: 80px;
    }
    h1, h2, h3, p, div { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Database Reset (Fixes the OperationalError) ---
DB_FILE = "coach_data.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # This force-clears the broken database structure
    c.execute('DROP TABLE IF EXISTS conversations')
    c.execute('''CREATE TABLE conversations (
                    room_id TEXT PRIMARY KEY, 
                    history TEXT, 
                    is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. Sidebar (Chat List) ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.active_id = "New Chat"
        st.rerun()

    st.subheader("Your Chats")
    # Display logic here...
    st.write("Click 'New Chat' to start.")

# --- 4. Main Chat Interface ---
st.title("Fluency Coach")
st.write(f"Active: {st.session_state.get('active_id', 'None')}")

c1, c2 = st.columns(2)
with c1:
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
with c2:
    if st.button("Stop Audio 🔇"): st.rerun()

st.chat_input("Type your message here...")
