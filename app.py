import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
import sqlite3
from io import BytesIO
from gtts import gTTS

# Connects your application logic to the style engine
from style import apply_custom_theme

st.set_page_config(
    page_title="Fluency Coach - AI Speaking Companion",
    page_icon="🤖",
    layout="centered"
)

# Run design customizations safely
apply_custom_theme()

# =========================================================
# DATABASE STORAGE ENGINE (With Deletion Support)
# =========================================================
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            room_id TEXT PRIMARY KEY,
            history_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_pinned INTEGER DEFAULT 0
        )
    ''')
    try:
        c.execute("ALTER TABLE conversations ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def get_all_rooms():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT room_id, is_pinned FROM conversations ORDER BY is_pinned DESC, updated_at DESC")
    rooms = c.fetchall()
    conn.close()
    return rooms

def load_room_history(room_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT history_json FROM conversations WHERE room_id = ?", (room_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return [
        {"role": "assistant", "content": "Hello! Welcome to your language learning room. Speak or type to practice your English!"}
    ]

def save_room_history(room_id, history):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    history_string = json.dumps(history, ensure_ascii=False)
    c.execute('''
        INSERT INTO conversations (room_id, history_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(room_id) DO UPDATE SET
            history_json = excluded.history_json,
            updated_at = CURRENT_TIMESTAMP
    ''', (room_id, history_string))
    conn.commit()
    conn.close()

def rename_room(old_id, new_id):
    if not new_id.strip() or old_id == new_id:
        return
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("UPDATE conversations SET room_id = ? WHERE room_id = ?", (new_id, old_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def toggle_pin_room(room_id, current_pin_status):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    new_status = 1 if current_pin_status == 0 else 0
    c.execute("UPDATE conversations SET is_pinned = ? WHERE room_id = ?", (new_status, room_id))
    conn.commit()
    conn.close()

def delete_room(room_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()

# =========================================================
# SYSTEM CONTROL RUNTIME STATES
# =========================================================
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

existing_rooms_data = get_all_rooms()

if not existing_rooms_data:
    save_room_history("Conversation 1", [{"role": "assistant", "content": "Hello! Welcome to your language learning room. Speak or type to practice your English!"}])
    existing_rooms_data = [("Conversation 1", 0)]

room_ids_list = [row[0] for row in existing_rooms_data]

if "active_id" not in st.session_state or st.session_state.active_id not in room_ids_list:
    st.session_state.active_id = room_ids_list[0]

current_history = load_room_history(st.session_state.active_id)

# Avatars
ROBOT_AVATAR = "https://img.icons8.com/isometric/512/bot.png"
USER_AVATAR = "https://img.icons8.com/isometric/512/female-profile.png"

is_currently_pinned = 0
for r_id, p_val in existing_rooms_data:
    if r_id == st.session_state.active_id:
        is_currently_pinned = p_val
        break

# =========================================================
# THE SIDEBAR MANAGEMENT & ROUTING PANEL
# =========================================================
with st.sidebar:
    st.markdown("### 🏢 Core Learning Hub")
    app_mode = st.radio(
        "Select Portal Workspace:",
        ["💬 Fluency Coach Bot", "📚 Skills Dashboard", "🌐 Explore Learning Platform", "📬 Query Submissions"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🤖 Coach Workspace")
    
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        from datetime import datetime
        time_stamp = datetime.now().strftime('%b %d, %H:%M')
        new_uid = "Chat " + str(time_stamp)
        save_room_history(new_uid, [{"role": "assistant", "content": "Hello! Let's start a brand new conversation room. Speak or type to begin!"}])
        st.session_state.active_id = new_uid
        st.session_state.autoplay_audio_data = None
        st.rerun()
        
    st.markdown("---")
    st.write("##### Recents")
    
    for room_title, pin_status in existing_rooms_data:
        is_current = (room_title == st.session_state.active_id)
        prefix = "📌 👉" if pin_status == 1 else "👉" if is_current else "📌 💬" if pin_status == 1 else "💬"
        button_label = f"{prefix} {room_title}"
        
        nav_col, del_col = st.columns([0.82, 0.18])
        
        with nav_col:
            if st.button(button_label, key=f"nav_{room_title}", use_container_width=True):
                st.session_state.active_id = room_title
                st.session_state.autoplay_audio_data = None
                st.rerun()
                
        with del_col:
            if st.button("🗑️", key=f"del_{room_title}", help=f"Delete '{room_title}'"):
                delete_room(room_title)
                remaining_rooms = get_all_rooms()
                if remaining_rooms:
                    st.session_state.active_id = remaining_rooms[0][0]
                else:
                    default_title = "Conversation 1"
                    save_room_history(default_title, [{"role": "assistant", "content": "Hello! Let's start a brand new conversation room. Speak or type to begin!"}])
                    st.session_state.active_id = default_title
                
                st.session_state.autoplay_audio_data = None
                st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("##### 🛠️ Current Chat Actions")
    
    pin_btn_label = "📌 Unpin from Top" if is_currently_pinned == 1 else "📌 Pin to Top"
    if st.button(pin_btn_label, use_container_width=True):
        toggle_pin_room(st.session_state.active_id, is_currently_pinned)
        st.rerun()
        
    new_name_input = st.text_input("Rename Current Chat:", value=st.session_state.active_id)
    if st.button("💾 Save Title Name", use_container_width=True):
        if new_name_input.strip() and new_name_input != st.session_state.active_id:
            rename_room(st.session_state.active_id, new_name_input.strip())
            st.session_state.active_id = new_name_input.strip()
            st.rerun()

# =========================================================
# SECURED BACKEND API CONNECTIONS
# =========================================================
def get_coach_response():
    if "GROQ_API_KEY" not in st.secrets:
        return "System Config Error: Please add GROQ_API_KEY to your Streamlit secrets settings panel."

    messages_payload = [
        {
            "role": "system",
            "content": """You are an engaging, supportive English language and communication coach.
            Your role is to help users improve their Communication Skills, Vocabulary, Grammar Tenses, and Soft Skills.
            CRITICAL INSTRUCTION FOR SHORT GREETINGS: 
            If the user simply says 'hello', 'hi', or a basic greeting, respond dynamically with a short, welcoming one-sentence greeting.
            INSTRUCTION FOR PRACTICE QUESTIONS:
            Provide a balanced, medium-length paragraph response explaining concepts clearly with practical conversational examples, and always close with one simple interactive practice question."""
        }
    ]
    for msg in current_history:
        role_map = "user" if msg["role"] == "user" else "assistant"
        messages_payload.append({"role": role_map, "content": msg["content"]})
        
    llm_payload = {"model": "llama-3.3-70b-versatile", "messages": messages_payload}
    llm_headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"
    }
    
    try:
        llm_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=llm_headers, json=llm_payload)
        res_data = llm_response.json()
        
        if isinstance(res_data, dict) and "choices" in res_data:
            return res_data["choices"][0]["message"]["content"]
        elif isinstance(res_data, dict) and "error" in res_data:
            return f"Groq Error Notification: {res_data['error'].get('message', 'Validation Error')}"
        else:
            return "API Connection anomaly. Server failed to return conversational chat selections."
    except Exception as e:
        return f"Failed to retrieve dynamic reply content. Exception trace: {str(e)}"

def text_to_speech_bytes(text_payload):
    try:
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text_payload)
        chunks = [st_item.strip() for st_item in sentences if st_item.strip()]
        
        combined_fp = BytesIO()
        for chunk in chunks:
            tts_chunk = gTTS(text=chunk, lang='en', slow=False)
            chunk_fp = BytesIO()
            tts_chunk.write_to_fp(chunk_fp)
            chunk_fp.seek(0)
            combined_fp.write(chunk_fp.read())
            
        combined_fp.seek(0)
        return combined_fp.read()
    except Exception as e:
        return None

# =========================================================
# ROUTED CONTENT FRAMES VIEW SWITCHER
# =========================================================

# MODE 1: ORIGINAL FLUENCY COACH CHATBOT FRAME
if app_mode == "💬 Fluency Coach Bot":
    st.title("Fluency Coach AI")
    st.write(f"Active Session: **{st.session_state.active_id}**")

    for message in current_history:
        if message["role"] == "user":
            with st.chat_message("user", avatar=USER_AVATAR):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ROBOT_AVATAR):
                st.markdown(message["content"])

    audio_placeholder = st.empty()
    if st.session_state.autoplay_audio_data:
        audio_placeholder.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

    # User Interaction Inputs
    voice_col, stop_col = st.columns([1, 1])
    with voice_col:
        st.write("**🎙️ Voice Practice:**")
        audio_source = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="recorder")

    with stop_col:
        st.write("**🛑 Controls:**")
        if st.button("Stop Audio 🔇", use_container_width=True):
            st.session_state.autoplay_audio_data = None
            audio_placeholder.empty()
            st.rerun()

    # Text Submission Handling
    text_input = st.chat_input("Ask about vocabulary, tenses, or soft skills...")
    if text_input:
        current_history.append({"role": "user", "content": text_input})
        save_room_history(st.session_state.active_id, current_history)
        with st.spinner("Thinking..."):
            coach_reply = get_coach_response()
            current_history.append({"role": "assistant", "content": coach_reply})
            save_room_history(st.session_state.active_id, current_history)
            st.session_state.autoplay_audio_data = None
            st.rerun()

    # Microphone Voice Submission Handling
    if audio_source and "bytes" in audio_source and audio_source["bytes"]:
        audio_bytes = audio_source["bytes"]
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.last_processed_audio != audio_hash:
            st.session_state.last_processed_audio = audio_hash
            with st.spinner("Processing speech..."):
                try:
                    whisper_files = {
                        "file": ("speech.wav", audio_bytes, "audio/wav"), 
                        "model": (None, "whisper-large-v3-turbo"), 
                        "language": (None, "en")
                    }
                    whisper_headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    whisper_response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=whisper_headers, files=whisper_files)
                    user_text = whisper_response.json().get("text", "")
                    
                    if user_text.strip():
                        current_history.append({"role": "user", "content": user_text})
                        save_room_history(st.session_state.active_id, current_history)
                        coach_reply = get_coach_response()
                        current_history.append({"role": "assistant", "content": coach_reply})
                        
                        # FIXED: Resolved unclosed parenthesis compile fault safely
                        save_room_history(st.session_state.active_id, current_history)
                        
                        audio_data = text_to_speech_bytes(coach_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()
                except Exception as e:
                    st.error(f"Audio Processing Error: {str(e)}")

# MODE 2: SKILLS DASHBOARD
elif app_mode == "📚 Skills Dashboard":
    st.markdown('<div class="hub-badge">🟢 Learning Hub Active</div>', unsafe_allow_html=True)
    st.title("Communication Skills Matrix")
    st.write("Track your progress across core language pillars and corporate interpersonal soft skills.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="skill-card">
                <div class="skill-title">🗣️ Communication Skills</div>
                <div class="skill-desc">Practice sentence pacing, clarity, public presentation patterns, and active speaking exercises.</div>
            </div>
            <div class="skill-card">
                <div class="skill-title">⏳ Grammar & Tenses</div>
                <div class="skill-desc">Understand past, present, and future timelines clearly to build structurally accurate responses.</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="skill-card">
                <div class="skill-title">📖 Vocabulary Building</div>
                <div class="skill-desc">Learn idioms, powerful professional active verbs, and functional vocabulary alternatives.</div>
            </div>
            <div class="skill-card">
                <div class="skill-title">🤝 Interpersonal Soft Skills</div>
                <div class="skill-desc">Polish your interview readiness, body language cue interpretations, and leadership presence.</div>
            </div>
            """, unsafe_allow_html=True
        )

# MODE 3: WEBSITE IFRAME ACCESS
elif app_mode == "🌐 Explore Learning Platform":
    st.title("Portal Integration View")
    st.write("Access your core educational web resources directly through your live dashboard canvas framework.")
    st.markdown("---")
    
    target_url = st.text_input("Enter Target Website URL:", value="https://example.com")
    if target_url:
        if not re.match(r'^https?://', target_url):
            target_url = "https://" + target_url
        try:
            st.markdown(
                f'<iframe src="{target_url}" width="100%" height="600" style="border:1px solid #e2e8f0; border-radius:12px;"></iframe>', 
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Unable to safely anchor frame viewport: {str(e)}")

# MODE 4: CLIENT DIRECT INTAKE SUPPORT SHEET (FIXED TYPO)
elif app_mode == "📬 Query Submissions":
    st.title("Student & User Support")
    st.write("Have a question about a grammar rule or interview prep? Submit it directly below.")
    st.markdown("---")
    
    with st.form("support_form", clear_on_submit=True):
        user_name = st.text_input("Full Name:")
        user_email = st.text_input("Email Address:")
        user_topic = st.selectbox("Focus Learning Domain:", ["Communication Skills", "Vocabulary", "Tenses Mastery", "Soft Skills / Interview Prep"])
        user_msg = st.text_area("What specific questions can our team clarify for you?")
        
        submit_btn = st.form_submit_button("Send Query Securely", type="primary")
        
        if submit_btn:
            if user_name.strip() and user_email.strip() and user_msg.strip():
                st.success(f"Thank you, {user_name}! Your request regarding {user_topic} has been logged.")
            else:
                st.warning("Please fill out all mandatory fields before processing details.")
