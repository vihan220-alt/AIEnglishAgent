import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- 1. Background Style ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-size: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Database Setup ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Drops the old table and makes a new one that matches the code
    c.execute('DROP TABLE IF EXISTS conversations')
    c.execute('CREATE TABLE conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, pinned INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# Always run init to ensure structure
init_db()

# --- 3. Sidebar (Chat Management) ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO conversations (name) VALUES (?)", ("New Chat",))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
    chats = conn.execute("SELECT id, name, pinned FROM conversations").fetchall()
    conn.close()

    for chat_id, name, pinned in chats:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.button(f"{'📌' if pinned else ''} {name}", key=f"btn_{chat_id}", use_container_width=True)
        with col2:
            with st.popover("⋮"):
                if st.button("📌 Pin", key=f"pin_{chat_id}"): st.rerun()
                if st.button("✏️ Rename", key=f"ren_{chat_id}"): st.rerun()
                if st.button("🗑️ Delete", key=f"del_{chat_id}"):
                    conn = sqlite3.connect(DB_FILE)
                    conn.execute("DELETE FROM conversations WHERE id = ?", (chat_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()

# --- 4. Main Interface ---
st.title("Fluency Coach")
col1, col2 = st.columns(2)
with col1:
    st.write("**🎙️ Voice Control**")
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.write("**🛑 Controls**")
    st.button("Stop Audio 🔇")

st.chat_input("Type your message here...")
