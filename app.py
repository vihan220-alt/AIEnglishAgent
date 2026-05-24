import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- UI Setup ---
st.set_page_config(layout="wide")

# --- Database Setup ---
DB_FILE = "coach_data.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (room_id TEXT PRIMARY KEY, is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# --- Sidebar: Chat List with 3-Dot Options ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        st.rerun()
    
    st.subheader("Your Conversations")
    # Simulate chat rooms
    rooms = [("Chat 1", 0), ("Chat 2", 0)] 
    
    for r_id, pinned in rooms:
        # Chat Selection Button
        if st.button(f"{'📌 ' if pinned else ''}{r_id}", use_container_width=True):
            st.session_state.active_id = r_id
            st.rerun()
        
        # 3-Dots Options Menu
        if st.session_state.get("active_id") == r_id:
            with st.expander("⋮ Options"):
                col1, col2, col3 = st.columns(3)
                with col1: st.button("📌", key=f"pin_{r_id}")
                with col2: st.button("✏️", key=f"ren_{r_id}")
                with col3: st.button("🗑️", key=f"del_{r_id}")

# --- Main Interface ---
st.title("Fluency Coach")
if "active_id" in st.session_state:
    st.info(f"Active Session: {st.session_state.active_id}")

# Voice & Control Layout
c1, c2 = st.columns([1, 1])
with c1:
    st.write("**Voice Input**")
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with c2:
    st.write("**Controls**")
    if st.button("Stop Audio 🔇"):
        st.rerun()

st.chat_input("Type your message here...")
