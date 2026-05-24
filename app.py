import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3
import json

# --- 1. Styling (Robot Background) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-size: 80px;
    }
    h1, h2, h3, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Database Engine (Self-Healing) ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ensure table exists
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (room_id TEXT PRIMARY KEY, is_pinned INTEGER DEFAULT 0)''')
    # Add is_pinned column if missing (Fixes OperationalError)
    try:
        c.execute("ALTER TABLE conversations ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

# --- 3. Sidebar (Chat List) ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        new_id = f"Chat {len(list(conn.execute('SELECT room_id FROM conversations')))+1}"
        conn.execute("INSERT OR IGNORE INTO conversations (room_id) VALUES (?)", (new_id,))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
    chats = conn.execute("SELECT room_id, is_pinned FROM conversations").fetchall()
    conn.close()

    for room_id, pinned in chats:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.button(f"{'📌' if pinned else ''} {room_id}", key=f"btn_{room_id}", use_container_width=True)
        with c2:
            with st.popover("⋮"):
                if st.button("🗑️ Delete", key=f"del_{room_id}"):
                    conn = sqlite3.connect(DB_FILE)
                    conn.execute("DELETE FROM conversations WHERE room_id = ?", (room_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()

# --- 4. Main Chat Interface ---
st.title("Fluency Coach")

c1, c2 = st.columns(2)
with c1:
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
with c2:
    st.button("Stop Audio 🔇")

st.chat_input("Type your message here...")
