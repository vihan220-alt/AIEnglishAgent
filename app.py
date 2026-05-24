import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- 1. Robot Background Styling ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-size: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Database Setup (Self-Healing) ---
DB_FILE = "coach_data.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Forces the table to match exactly what the code expects
    c.execute('DROP TABLE IF EXISTS conversations')
    c.execute('''CREATE TABLE conversations 
                 (room_id TEXT PRIMARY KEY, is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. Sidebar (Chat Management) ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        new_id = f"Chat {len(list(conn.execute('SELECT room_id FROM conversations')))+1}"
        conn.execute("INSERT INTO conversations (room_id) VALUES (?)", (new_id,))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
    chats = conn.execute("SELECT room_id, is_pinned FROM conversations").fetchall()
    conn.close()

    for room_id, pinned in chats:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"{'📌' if pinned else ''} {room_id}", key=f"btn_{room_id}", use_container_width=True):
                st.session_state.active_id = room_id
        with col2:
            with st.popover("⋮"):
                if st.button("📌 Pin", key=f"pin_{room_id}"): st.rerun()
                if st.button("✏️ Rename", key=f"ren_{room_id}"): st.rerun()
                if st.button("🗑️ Delete", key=f"del_{room_id}"):
                    conn = sqlite3.connect(DB_FILE)
                    conn.execute("DELETE FROM conversations WHERE room_id = ?", (room_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()

# --- 4. Main Interface ---
st.title("Fluency Coach")
st.write(f"Active Session: **{st.session_state.get('active_id', 'None')}**")

col1, col2 = st.columns(2)
with col1:
    st.write("**🎙️ Voice Control**")
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.write("**🛑 Controls**")
    if st.button("Stop Audio 🔇"): st.rerun()

st.chat_input("Type your message here...")
