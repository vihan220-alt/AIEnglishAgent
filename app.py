import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
import sqlite3
from io import BytesIO
from gtts import gTTS

# =========================================================
# CONFIGURATION & CSS THEME INTEGRATION
# =========================================================
st.set_page_config(
    page_title="SkillVerify AI - English Language Assessment Platform",
    page_icon="🗣️",
    layout="centered"
)

# Seamlessly connects your app logic to the fixed style engine
try:
    from style import apply_custom_theme
    apply_custom_theme()
except ImportError:
    pass

# =========================================================
# DATABASE STORAGE ENGINE (Skill Assessments Management)
# =========================================================
DB_FILE = "skills_assessment_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            session_id TEXT PRIMARY KEY,
            history_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_pinned INTEGER DEFAULT 0
        )
    ''')
    try:
        c.execute("ALTER TABLE assessments ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def get_all_sessions():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT session_id, is_pinned FROM assessments ORDER BY is_pinned DESC, updated_at DESC")
    sessions = c.fetchall()
    conn.close()
    return sessions

def load_session_history(session_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT history_json FROM assessments WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return [
        {"role": "assistant", "content": "🎯 **Welcome to your English Language Assessment Portal!**\n\nLet's map out your evaluation benchmarks. Please fill out the configuration card below to launch your tailored language interview session."}
    ]

def save_session_history(session_id, history):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    history_string = json.dumps(history, ensure_ascii=False)
    c.execute('''
        INSERT INTO assessments (session_id, history_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            history_json = excluded.history_json,
            updated_at = CURRENT_TIMESTAMP
    ''', (session_id, history_string))
    conn.commit()
    conn.close()

def rename_session(old_id, new_id):
    if not new_id.strip() or old_id == new_id:
        return
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("UPDATE assessments SET session_id = ? WHERE session_id = ?", (new_id, old_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def toggle_pin_session(session_id, current_pin_status):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    new_status = 1 if current_pin_status == 0 else 0
    c.execute("UPDATE assessments SET is_pinned = ? WHERE session_id = ?", (new_status, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM assessments WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# =========================================================
# SYSTEM CONTROL RUNTIME STATES
# =========================================================
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

existing_sessions_data = get_all_sessions()

if not existing_sessions_data:
    save_session_history("English Communication Core", [{"role": "assistant", "content": "🎯 **Welcome to your English Language Assessment Portal!**\n\nLet's map out your evaluation benchmarks. Please fill out the configuration card below to launch your tailored language interview session."}])
    existing_sessions_data = [("English Communication Core", 0)]

session_ids_list = [row[0] for row in existing_sessions_data]

if "active_id" not in st.session_state or st.session_state.active_id not in session_ids_list:
    st.session_state.active_id = session_ids_list[0]

current_history = load_session_history(st.session_state.active_id)

# Avatars for UI
ROBOT_AVATAR = "https://img.icons8.com/isometric/512/brain.png"
USER_AVATAR = "https://img.icons8.com/isometric/512/checked-user-male.png"

is_currently_pinned = 0
for s_id, p_val in existing_sessions_data:
    if s_id == st.session_state.active_id:
        is_currently_pinned = p_val
        break

# =========================================================
# THE SIDEBAR MANAGEMENT & ROUTING PANEL
# =========================================================
with st.sidebar:
    st.markdown("### 🏢 Core Enterprise Platform")
    app_mode = st.radio(
        "Select Portal Workspace:",
        ["🗣️ Skill Assessment Portal", "📊 Analytics Dashboard", "🌐 Explore Learning Platform", "📬 Submit Custom Prompts"],
        index=0
    )
    
    if app_mode == "🗣️ Skill Assessment Portal":
        st.markdown("---")
        st.markdown("### 🛠️ Active Evaluations")
        
        if st.button("➕ Start New Assessment", use_container_width=True, type="primary"):
            from datetime import datetime
            time_stamp = datetime.now().strftime('%b %d, %H:%M')
            new_uid = "Language Bench " + str(time_stamp)
            save_session_history(new_uid, [{"role": "assistant", "content": "🎯 **Welcome to your English Language Assessment Portal!**\n\nLet's map out your evaluation benchmarks. Please fill out the configuration card below to launch your tailored language interview session."}])
            st.session_state.active_id = new_uid
            st.session_state.autoplay_audio_data = None
            st.rerun()
            
        st.markdown("---")
        st.write("##### Recent Logs")
        
        for session_title, pin_status in existing_sessions_data:
            is_current = (session_title == st.session_state.active_id)
            prefix = "📌 👉" if pin_status == 1 else "👉" if is_current else "📌 📄" if pin_status == 1 else "📄"
            button_label = f"{prefix} {session_title}"
            
            nav_col, del_col = st.columns([0.82, 0.18])
            
            with nav_col:
                if st.button(button_label, key=f"nav_{session_title}", use_container_width=True):
                    st.session_state.active_id = session_title
                    st.session_state.autoplay_audio_data = None
                    st.rerun()
                    
            with del_col:
                if st.button("🗑️", key=f"del_{session_title}", help=f"Delete assessment tracking data '{session_title}'"):
                    delete_session(session_title)
                    remaining_sessions = get_all_sessions()
                    if remaining_sessions:
                        st.session_state.active_id = remaining_sessions[0][0]
                    else:
                        default_title = "General English Audit"
                        save_session_history(default_title, [{"role": "assistant", "content": "🎯 **Welcome to your English Language Assessment Portal!**\n\nLet's map out your evaluation benchmarks. Please fill out the configuration card below to launch your tailored language interview session."}])
                        st.session_state.active_id = default_title
                    
                    st.session_state.autoplay_audio_data = None
                    st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        st.write("##### ⚙️ Session Options")
        
        pin_btn_label = "📌 Unpin Session" if is_currently_pinned == 1 else "📌 Pin Session to Top"
        if st.button(pin_btn_label, use_container_width=True):
            toggle_pin_session(st.session_state.active_id, is_currently_pinned)
            st.rerun()
            
        new_name_input = st.text_input("Modify Track Label Name:", value=st.session_state.active_id)
        if st.button("💾 Save Session Title", use_container_width=True):
            if new_name_input.strip() and new_name_input != st.session_state.active_id:
                rename_session(st.session_state.active_id, new_name_input.strip())
                st.session_state.active_id = new_name_input.strip()
                st.rerun()

# =========================================================
# BACKEND AI CONNECTIVITY ENGINE (Groq Interfacing)
# =========================================================
def get_evaluator_response():
    if "GROQ_API_KEY" not in st.secrets:
        return "Configuration Key Error: Please register GROQ_API_KEY in your deployment environment secrets panel."

    messages_payload = [
        {
            "role": "system",
            "content": """You are an elite, highly professional English Language Assessor and CEFR Communication Expert.
            Your job is to rigorously evaluate the user's English language proficiency based on the parameters provided in the profile configuration card.
            
            RULES OF ENGAGEMENT:
            1. If the user presents a brief greeting or single comment, immediately reply with an encouraging but direct language evaluation question or situational scenario mapped to their targeted proficiency domain.
            2. For standard interactions, provide concise, constructive feedback regarding their grammar, vocabulary usage, sentence structure, and coherence. 
            3. Point out subtle mistakes gently, and praise excellent phrasing or precise vocabulary choices.
            4. Always conclude your feedback message explicitly with **exactly one practical conversational question, prompt, or situational riddle** for them to address next to continue the evaluation."""
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
            return f"Backend Service Exception: {res_data['error'].get('message', 'Validation Failed')}"
        else:
            return "Server payload parsing mismatch. Could not capture evaluation text choices safely."
    except Exception as e:
        return f"Network or execution failure during model request generation: {str(e)}"

def text_to_speech_bytes(text_payload):
    try:
        cleaned_text = re.sub(r'[*_#`\-]+', ' ', text_payload)
        sentences = re.split(r'(?<=[.!?])\s+|\n+', cleaned_text)
        chunks = [st_item.strip() for st_item in sentences if st_item.strip()]
        
        combined_fp = BytesIO()
        for chunk in chunks[:3]: 
            tts_chunk = gTTS(text=chunk, lang='en', slow=False)
            chunk_fp = BytesIO()
            tts_chunk.write_to_fp(chunk_fp)
            chunk_fp.seek(0)
            combined_fp.write(chunk_fp.read())
            
        combined_fp.seek(0)
        return combined_fp.read()
    except Exception:
        return None

# =========================================================
# ROUTED CONTENT FRAMES VIEW SWITCHER
# =========================================================

# MODULE 1: INTERACTIVE SKILL ASSESSMENT PORTAL VIEW
if app_mode == "🗣️ Skill Assessment Portal":
    st.title("SkillVerify Language Assessment Portal")
    st.write(f"Active Assessment Space: **{st.session_state.active_id}**")

    # Render Historical Logs
    for message in current_history:
        if message["role"] == "user":
            with st.chat_message("user", avatar=USER_AVATAR):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ROBOT_AVATAR):
                st.markdown(message["content"])

    # Show Multi-Stage Setup Questionnaire Card if it's a completely fresh session
    if len(current_history) == 1 and "Welcome" in current_history[0]["content"]:
        st.markdown("---")
        with st.expander("🛠️ Initialize Language Profile Target", expanded=True):
            st.markdown("##### Calibrate system parameters below to generate your specific evaluation matrix:")
            
            with st.form("assessment_setup_form"):
                target_skill = st.selectbox(
                    "Core Domain Under Review:",
                    ["Spoken English & Fluency", "Business & Corporate Communication", "Grammar, Structure & Vocabulary", "Professional Writing Proficiency"]
                )
                
                experience_tier = st.selectbox(
                    "Target Proficiency Level:",
                    ["Beginner / Elementary (CEFR A1 - A2)", "Intermediate / Independent (CEFR B1 - B2)", "Advanced / Proficient (CEFR C1 - C2)"]
                )
                
                specialized_focus = st.text_input(
                    "Provide specific focus metrics or targets:", 
                    placeholder="e.g., Pronunciation, Public Speaking, Academic Writing, IELTS/TOEFL Prep, Interview Readiness"
                )
                
                submit_onboarding = st.form_submit_button("🔥 Launch Language Evaluation Environment", type="primary")
                
                if submit_onboarding:
                    context_injection = (
                        f"🎯 **Language Assessment Profile Registered** 🎯\n\n"
                        f"* **Target Domain:** {target_skill}\n"
                        f"* **Target Proficiency Level:** {experience_tier}\n"
                        f"* **Focus Metrics:** {specialized_focus if specialized_focus.strip() else 'General Fluency Standards'}"
                    )
                    
                    current_history.append({"role": "user", "content": context_injection})
                    save_session_history(st.session_state.active_id, current_history)
                    
                    with st.spinner("Compiling language assessment framework..."):
                        eval_reply = get_evaluator_response()
                        current_history.append({"role": "assistant", "content": eval_reply})
                        save_session_history(st.session_state.active_id, current_history)
                        
                        audio_data = text_to_speech_bytes(eval_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()

    audio_placeholder = st.empty()
    if st.session_state.autoplay_audio_data:
        audio_placeholder.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

    # Audio Recording UI Inputs
    voice_col, stop_col = st.columns([1, 1])
    with voice_col:
        st.write("**🎙️ Speak Your Answer:**")
        audio_source = mic_recorder(start_prompt="Record Answer 🎤", stop_prompt="Submit Audio 🔇", key="recorder")

    with stop_col:
        st.write("**🛑 Controls:**")
        if st.button("Stop Playback Audio", use_container_width=True):
            st.session_state.autoplay_audio_data = None
            audio_placeholder.empty()
            st.rerun()

    # Chat Input submission handling
    text_input = st.chat_input("Type your response explanation or text sample here...")
    if text_input:
        current_history.append({"role": "user", "content": text_input})
        save_session_history(st.session_state.active_id, current_history)
        with st.spinner("Analyzing parameters and computing coherence scores..."):
            eval_reply = get_evaluator_response()
            current_history.append({"role": "assistant", "content": eval_reply})
            save_session_history(st.session_state.active_id, current_history)
            st.session_state.autoplay_audio_data = None
            st.rerun()

    # Voice to Text Audio parsing submission
    if audio_source and "bytes" in audio_source hoarding and audio_source["bytes"]:
        audio_bytes = audio_source["bytes"]
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.last_processed_audio != audio_hash:
            st.session_state.last_processed_audio = audio_hash
            with st.spinner("Decoding spoken response streams..."):
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
                        save_session_history(st.session_state.active_id, current_history)
                        eval_reply = get_evaluator_response()
                        current_history.append({"role": "assistant", "content": eval_reply})
                        save_session_history(st.session_state.active_id, current_history)
                        
                        audio_data = text_to_speech_bytes(eval_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()
                except Exception as e:
                    st.error(f"Whisper Speech Decoding Failure: {str(e)}")

# MODULE 2: ANALYTICS DASHBOARD
elif app_mode == "📊 Analytics Dashboard":
    st.title("Performance Analytics Tracker")
    st.write("Visualize core English language competencies and progress benchmarks.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="skill-card skill-blue">
                <div class="skill-title">🗣️ Fluency & Pronunciation</div>
                <div class="skill-desc">Measures rhythm, speed accuracy, speech pauses, and phonetic clarity metrics.</div>
            </div>
            <div class="skill-card skill-green">
                <div class="skill-title">📖 Grammar & Sentence Structure</div>
                <div class="skill-desc">Tracks syntactic accuracy, correct use of tenses, active/passive voice, and structural variations.</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="skill-card skill-amber">
                <div class="skill-title">📚 Vocabulary & Lexical Resource</div>
                <div class="skill-desc">Evaluates contextual appropriateness, use of idioms, collocations, and dynamic word choices.</div>
            </div>
            <div class="skill-card skill-purple">
                <div class="skill-title">📈 Coherence & Task Completion</div>
                <div class="skill-desc">Tracks logical content flow, connectivity of ideas, and clarity when answering structural prompts.</div>
            </div>
            """, unsafe_allow_html=True
        )

# MODULE 3: IFRAME PORTAL INTEGRATION (FIXED FOR LANGUAGE PORTALS)
elif app_mode == "🌐 Explore Learning Platform":
    st.title("External Knowledge Ecosystem")
    st.write("Access interactive reading prompts, dictionaries, and practice materials straight inside your active view canvas framework.")
    st.markdown("---")
    
    # Updated default to a real language hub (BBC Learning English)
    target_url = st.text_input("Enter Target English Learning Hub/Reading Article URL:", value="https://www.bbc.co.uk/learningenglish")
    if target_url:
        if not re.match(r'^https?://', target_url):
            target_url = "https://" + target_url
        try:
            st.markdown(
                f'<iframe src="{target_url}" width="100%" height="600" style="border:1px solid #e2e8f0; border-radius:12px;"></iframe>', 
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Failed to securely mount canvas frame layout: {str(e)}")

# MODULE 4: QUERY SUBMISSIONS INTAKE FORM
elif app_mode == "📬 Submit Custom Prompts":
    st.title("Custom Evaluation Prompts Engine")
    st.write("Want to submit a custom language challenge statement to our evaluation pool? Lodge it here.")
    st.markdown("---")
    
    with st.form("custom_prompt_submission_form", clear_on_submit=True):
        candidate_name = st.text_input("Author Name:")
        candidate_email = st.text_input("Contact Email:")
        assessment_category = st.selectbox("Benchmark Category Domain:", ["Conversational Scenario", "Grammar Diagnostics", "Writing Essay Prompt"])
        prompt_content = st.text_area("Provide raw scenario conditions or prompt conversation context block:")
        
        submit_btn = st.form_submit_button("Lodge Challenge to System Engine", type="primary")
        
        if submit_btn:
            if candidate_name.strip() and candidate_email.strip() and prompt_content.strip():
                st.success(f"Thank you, {candidate_name}! Your custom challenge for {assessment_category} has been logged safely.")
            else:
                st.warning("All mandatory fields must be completed prior to submitting challenge details to the database.")
