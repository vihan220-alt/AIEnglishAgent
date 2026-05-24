import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- 1. Robot Background Styling ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-repeat: repeat;
        background-size: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Database Reset & Setup ---
DB_FILE = "coach_data.db"

def reset_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS conversations')
    c.execute('CREATE TABLE conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, pinned INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# Initialize only if needed
reset_db()

# --- 3. Sidebar (Chat Management) ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
    chats = conn.execute("SELECT id, name, pinned FROM conversations").fetchall()
    conn.close()

    for chat_id, name, pinned in chats:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.button(f"{'📌' if pinned else ''} {name}", key=f"btn_{chat_id}")
        with col2:
            with st.popover("⋮"):
                if st.button("📌 Pin", key=f"pin_{chat_id}"): st.rerun()
                if st.button("✏️ Rename", key=f"ren_{chat_id}"): st.rerun()
                if st.button("🗑️ Delete", key=f"del_{chat_id}"): st.rerun()

# --- 4. Main Interface ---
st.title("Fluency Coach")
col1, col2 = st.columns(2)
with col1:
    st.write("**Voice Control**")
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.write("**Audio Controls**")
    if st.button("Stop Audio 🔇"): st.rerun()

st.chat_input("Type your message here...")
