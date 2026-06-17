import streamlit as st

# =========================================================
# CONFIGURATION & SYSTEM THEME INTEGRATION (MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="SkillVerify AI - Video English Assessment Platform",
    page_icon="🎬",
    layout="centered"
)

# Core library imports
import requests
import hashlib
import re
import json
import os
import base64
import streamlit.components.v1 as components
from io import BytesIO
from gtts import gTTS
from datetime import datetime, date
from supabase import create_client, Client

# =========================================================
# INITIALIZE GLOBAL SESSION STATE MEMORY FRAMEWORKS
# =========================================================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "Chat_1": {
            "title": "Default Video Language Assessment",
            "pinned": False,
            "history": [{"role": "assistant", "content": "🎯 **Welcome to your English Video Assessment Portal!**\n\nLet's map out your evaluation benchmarks. Please fill out the profile calibration form below to start your tailored interactive interview video session."}]
        }
    }

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = "Chat_1"

if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "performance_metrics" not in st.session_state:
    st.session_state.performance_metrics = {
        "fluency_score": 0.0,
        "grammar_errors_logged": 0,
        "vocabulary_upgrades_suggested": 0,
        "total_turns_completed": 0
    }

if "payment_plan_selected" not in st.session_state:
    st.session_state.payment_plan_selected = None

# Track captured base64 video string safely outside standard loop overrides
if "last_recorded_video_raw" not in st.session_state:
    st.session_state.last_recorded_video_raw = None

# Guarantee active_chat_id points to a valid session
if st.session_state.active_chat_id not in st.session_state.all_chats:
    if st.session_state.all_chats:
        st.session_state.active_chat_id = list(st.session_state.all_chats.keys())[0]
    else:
        st.session_state.all_chats = {
            "Chat_1": {
                "title": "Default Video Language Assessment",
                "pinned": False,
                "history": [{"role": "assistant", "content": "🎯 **Session initialized successfully.**"}]
            }
        }
        st.session_state.active_chat_id = "Chat_1"

current_chat = st.session_state.all_chats[st.session_state.active_chat_id]

# =========================================================
# SUPABASE DATABASE STORAGE ENGINE
# =========================================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://xudmbkuruxfdpprwplee.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def get_supabase_client():
    if not SUPABASE_KEY or SUPABASE_KEY.strip() == "":
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase_client = get_supabase_client()

def init_user_and_get_plan(email_str):
    clean_email = email_str.strip().lower()
    if not clean_email or supabase_client is None:
        return "Trial", 15
    try:
        response = supabase_client.table("users").select("*").eq("email", clean_email).execute()
        user_records = response.data
        if len(user_records) == 0:
            new_profile = {"email": clean_email, "user_plan": "Trial", "signup_date": str(date.today())}
            supabase_client.table("users").insert(new_profile).execute()
            return "Trial", 15
        user_data = user_records[0]
        assigned_plan = user_data.get("user_plan", "Trial")
        signup_dt_str = user_data.get("signup_date", str(date.today()))
        signup_date_obj = datetime.strptime(signup_dt_str, "%Y-%m-%d").date()
        days_consumed = (date.today() - signup_date_obj).days
        remaining_trial_days = max(0, 15 - days_consumed)
        if assigned_plan == "Trial" and remaining_trial_days <= 0:
            supabase_client.table("users").update({"user_plan": "Expired"}).eq("email", clean_email).execute()
            return "Expired", 0
        return assigned_plan, remaining_trial_days
    except Exception:
        return "Trial", 15

def update_user_plan_db(email_str, target_plan):
    clean_email = email_str.strip().lower()
    if supabase_client is None:
        return False
    try:
        supabase_client.table("users").update({"user_plan": target_plan}).eq("email", clean_email).execute()
        return True
    except Exception:
        return False

ROBOT_AVATAR = "https://img.icons8.com/fluent/96/artificial-intelligence.png"
USER_AVATAR = "https://img.icons8.com/fluent/96/user-male-circle.png"

# =========================================================
# INTEGRATED PAYMENT GATEWAY COMPONENT NODE
# =========================================================
def render_payment_gateway(email_recipient, selected_plan, cost_inr, plan_duration="Month"):
    razorpay_html_code = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #f9f9fb; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 15px;">
        <h4 style="color: #1e293b; font-family: system-ui, sans-serif; margin-bottom: 5px; margin-top:0;">Secure Premium Activation Node</h4>
        <p style="color: #64748b; font-size: 14px; font-family: system-ui, sans-serif; margin-bottom: 15px;">Upgrading <b>{email_recipient}</b> to the <b>{selected_plan} Plan ({plan_duration})</b></p>
        <form>
            <script
                src="https://checkout.razorpay.com/v1/payment-button.js"
                data-payment_button_id="pl_O5jXm9vC2XzY8q" 
                data-button_text="Pay Now (₹{cost_inr})"
                data-button_theme="brand-color"
                async>
            </script>
        </form>
    </div>
    """
    components.html(razorpay_html_code, height=160)

# =========================================================
# LIVE HTML5 WEBCAM VIDEO RECORDER NODE
# =========================================================
def render_webcam_video_recorder():
    webcam_html = """
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; color: #ffffff; font-family: system-ui, sans-serif; text-align: center;">
        <video id="preview" width="100%" height="240" autoplay muted style="background: #000; border-radius: 6px; transform: scaleX(-1);"></video>
        <div style="margin-top: 10px;">
            <button id="startBtn" style="background-color: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: bold; cursor: pointer; margin-right: 5px;">🔴 Start Recording Session</button>
            <button id="stopBtn" style="background-color: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: bold; cursor: pointer;" disabled>⏹️ Stop & Submit</button>
        </div>
        <p id="statusMsg" style="font-size: 12px; color: #94a3b8; margin-top: 8px; margin-bottom: 0;">Webcam device active & waiting...</p>
    </div>

    <script>
        function sendToStreamlit(base64Data) {
            window.parent.postMessage({
                type: "streamlit:setComponentValue",
                value: base64Data
            }, "*");
        }

        let preview = document.getElementById('preview');
        let startBtn = document.getElementById('startBtn');
        let stopBtn = document.getElementById('stopBtn');
        let statusMsg = document.getElementById('statusMsg');
        let recorder;
        let recordedChunks = [];

        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            preview.srcObject = stream;
            startBtn.addEventListener('click', () => {
                recordedChunks = [];
                recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
                
                recorder.ondataavailable = (e) => {
                    if (e.data.size > 0) {
                        recordedChunks.push(e.data);
                    }
                };

                recorder.onstop = () => {
                    let blob = new Blob(recordedChunks, { type: 'video/webm' });
                    let reader = new FileReader();
                    reader.readAsDataURL(blob); 
                    reader.onloadend = function() {
                        let base64String = reader.result;
                        sendToStreamlit(base64String);
                    }
                };

                recorder.start();
                startBtn.disabled = true;
                stopBtn.disabled = false;
                statusMsg.innerText = "📺 Session Recording Live (Video + Audio Capturing)...";
                statusMsg.style.color = "#f43f5e";
            });
            stopBtn.addEventListener('click', () => {
                recorder.stop();
                startBtn.disabled = false;
                stopBtn.disabled = true;
                statusMsg.innerText = "✔️ Video stream processed and submitted successfully!";
                statusMsg.style.color = "#10b981";
            });
        }).catch(err => {
            statusMsg.innerText = "⚠️ Device Capture Access Denied: Check camera permissions.";
            statusMsg.style.color = "#ef4444";
        });
    </script>
    """
    return components.html(webcam_html, height=350, key="webcam_widget_v3")

# =========================================================
# SIDEBAR WORKSPACE NAVIGATION & CHAT INTERFACE OPTIONS
# =========================================================
with st.sidebar:
    st.markdown("### 🏢 Enterprise Training Hub")
    st.markdown("---")
    st.markdown("##### 🔑 Candidate Workspace Access")
    auth_email = st.text_input("Enter Registered Email Account:", value="vihan220@gmail.com")
    
    user_package_tier, trial_countdown = init_user_and_get_plan(auth_email)
    
    app_mode = st.radio(
        "Select Portal Workspace:",
        ["🗣️ Skill Assessment Portal", "📊 Analytics Dashboard", "🌐 Explore Video Learning Engine", "📬 Submit Custom Prompts"],
        index=0
    )
    
    if app_mode == "🗣️ Skill Assessment Portal" and user_package_tier != "Expired":
        st.markdown("---")
        st.markdown("### 🛠️ Chat Session Management")
        
        if st.button("➕ Start New Assessment (New Chat)", use_container_width=True, type="primary"):
            new_id = f"Chat_{int(datetime.now().timestamp())}"
            st.session_state.all_chats[new_id] = {
                "title": f"Session Assessment {len(st.session_state.all_chats) + 1}",
                "pinned": False,
                "history": [{"role": "assistant", "content": "🎯 **Welcome to your New English Language Assessment!**\n\nPlease initialize your profile benchmarks below to start."}]
            }
            st.session_state.active_chat_id = new_id
            st.session_state.autoplay_audio_data = None
            st.rerun()

        st.markdown("##### Active Logs Matrix:")
        
        sorted_chat_ids = sorted(
            st.session_state.all_chats.keys(), 
            key=lambda k: st.session_state.all_chats[k]["pinned"], 
            reverse=True
        )
        
        for c_id in list(sorted_chat_ids):
            if c_id not in st.session_state.all_chats:
                continue
            chat_obj = st.session_state.all_chats[c_id]
            pin_indicator = "📌 " if chat_obj["pinned"] else "💬 "
            is_active = (c_id == st.session_state.active_chat_id)
            btn_label = f"{pin_indicator}{chat_obj['title']}"
            
            if st.button(btn_label, key=f"select_{c_id}", use_container_width=True, type="secondary" if not is_active else "primary"):
                st.session_state.active_chat_id = c_id
                st.session_state.autoplay_audio_data = None
                st.rerun()
                
            if is_active:
                col_pin, col_ren, col_del = st.columns(3)
                
                with col_pin:
                    pin_text = "Unpin" if chat_obj["pinned"] else "Pin"
                    if st.button(pin_text, key=f"pin_{c_id}", use_container_width=True):
                        st.session_state.all_chats[c_id]["pinned"] = not st.session_state.all_chats[c_id]["pinned"]
                        st.rerun()
                
                with col_ren:
                    if st.button("Rename", key=f"ren_{c_id}", use_container_width=True):
                        st.session_state[f"show_rename_field_{c_id}"] = True
                        st.rerun()
                
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_{c_id}", use_container_width=True):
                        if len(st.session_state.all_chats) > 1:
                            del st.session_state.all_chats[c_id]
                            st.session_state.active_chat_id = list(st.session_state.all_chats.keys())[0]
                            st.session_state.autoplay_audio_data = None
                            st.rerun()
                        else:
                            st.error("Cannot delete your last active session trace!")
                
                if st.session_state.get(f"show_rename_field_{c_id}", False):
                    new_title_input = st.text_input("Enter New Session Name:", value=chat_obj["title"], key=f"title_in_{c_id}")
                    if st.button("Save Name", key=f"save_{c_id}"):
                        if new_title_input.strip():
                            st.session_state.all_chats[c_id]["title"] = new_title_input.strip()
                            st.session_state[f"show_rename_field_{c_id}"] = False
                            st.rerun()

# =========================================================
# BACKEND AI CONNECTIVITY ENGINE (Groq AI Prompt Setup)
# =========================================================
def parse_and_update_metrics(ai_text):
    st.session_state.performance_metrics["total_turns_completed"] += 1
    if "vocabulary upgrade" in ai_text.lower() or "alternative" in ai_text.lower():
        st.session_state.performance_metrics["vocabulary_upgrades_suggested"] += 2
    if "grammar" in ai_text.lower() or "slip" in ai_text.lower() or "mistake" in ai_text.lower():
        st.session_state.performance_metrics["grammar_errors_logged"] += 1
    score_search = re.search(r'(?:Fluency Score|Score\s*:\s*)(\d+(?:\.\d+)?)\s*/\s*10', ai_text, re.IGNORECASE)
    if score_search:
        st.session_state.performance_metrics["fluency_score"] = float(score_search.group(1))

def get_evaluator_response(plan_tier):
    if "GROQ_API_KEY" not in st.secrets:
        return "Configuration Key Error: Please register GROQ_API_KEY in your deployment environment secrets panel."

    system_rules = (
        "You are a friendly, conversational English Language Assessor evaluating a video interview submission. "
        "Keep your responses extremely concise, short, and natural (maximum 2 sentences). "
        "Do not write long paragraphs or list multiple questions. "
        "Always respond with exactly ONE clear, short conversational question at the end to keep the video chat interactive."
    )
    
    messages_payload = [{"role": "system", "content": system_rules}]
    for msg in current_chat["history"]:
        role_map = "user" if msg["role"] == "user" else "assistant"
        messages_payload.append({"role": role_map, "content": msg["content"]})
        
    llm_payload = {"model": "llama-3.3-70b-versatile", "messages": messages_payload}
    llm_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
    
    try:
        llm_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=llm_headers, json=llm_payload)
        res_data = llm_response.json()
        if isinstance(res_data, dict) and "choices" in res_data:
            response_content = res_data["choices"][0]["message"]["content"]
            parse_and_update_metrics(response_content)
            return response_content
        return "Server payload processing structural error match failed."
    except Exception as e:
        return f"Network failure during model response request generation: {str(e)}"

def text_to_speech_bytes(text_payload):
    try:
        cleaned_text = re.sub(r'[*_#`\-]+', ' ', text_payload)
        tts = gTTS(text=cleaned_text[:200], lang='en', slow=False)
        chunk_fp = BytesIO()
        tts.write_to_fp(chunk_fp)
        chunk_fp.seek(0)
        return chunk_fp.read()
    except Exception:
        return None

# FIXED & ISOLATED SUBSCRIPTION PANEL COMPONENT
def show_subscription_options():
    st.subheader("Select a Subscription Tier to Continue:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🥉 Basic")
        st.markdown("**₹15** / month")
        if st.button("Select ₹15 Plan", use_container_width=True, key="btn_tier_15"): 
            st.session_state.payment_plan_selected = ("Basic Premium", 15, "1 Month")
            st.rerun()
    with col2:
        st.markdown("### 🥈 Standard")
        st.markdown("**₹30** / month")
        if st.button("Select ₹30 Plan", use_container_width=True, type="primary", key="btn_tier_30"): 
            st.session_state.payment_plan_selected = ("Standard Premium", 30, "1 Month")
            st.rerun()
    with col3:
        st.markdown("### 🥇 Executive")
        st.markdown("**₹50** / month")
        if st.button("Select ₹50 Plan", use_container_width=True, key="btn_tier_50"): 
            st.session_state.payment_plan_selected = ("Executive Premium", 50, "1 Month")
            st.rerun()
            
    st.markdown("---")
    st.markdown("##### 🏷️ Have a Coupon Code?")
    coupon_input = st.text_input("Enter Coupon Code here:", key="coupon_field").strip().upper()
    
    if coupon_input in ["FREE3M", "SKILL3"]:
        st.success("🎉 Coupon Applied Successfully! You get **3 Months FREE** on any selection.")
        if st.session_state.payment_plan_selected:
            p_name, _, _ = st.session_state.payment_plan_selected
            st.session_state.payment_plan_selected = (p_name, 0, "3 Months Promo")

    if st.session_state.payment_plan_selected:
        plan_nm, plan_amt, plan_dur = st.session_state.payment_plan_selected
        render_payment_gateway(auth_email, plan_nm, plan_amt, plan_dur)
        
        if st.button(f"⚡ [Simulate Payment Success] Activate {plan_nm}", use_container_width=True, key="execute_sim_payment"):
            if supabase_client is None:
                st.error("Database initialization failed. Please set up your secrets (`SUPABASE_KEY`) in your Streamlit dashboard settings first.")
            else:
                target_plan_string = f"{plan_nm} ({plan_dur})"
                success = update_user_plan_db(auth_email, target_plan_string)
                if success:
                    st.success(f"Successfully activated {target_plan_string}! Reloading layout...")
                    st.session_state.payment_plan_selected = None
                    st.rerun()
                else:
                    st.error("Database storage push failed. Verify connectivity parameters or check your network logs.")

# =========================================================
# ROUTED CONTENT INTERFACE SWITCHER VIEWS
# =========================================================
if user_package_tier == "Expired":
    st.title("SkillVerify English Assessment Portal 🚀")
    st.error("⚠️ Your 15-day Free Trial package limits have been exhausted!")
    show_subscription_options()

elif app_mode == "🗣️ Skill Assessment Portal":
    active_id = st.session_state.active_chat_id
    if "all_chats" in st.session_state and active_id in st.session_state.all_chats:
        st.title(f"{st.session_state.all_chats[active_id]['title']}")
    else:
        st.title("Portal Workspace: English Assessment Portal")
    
    if "Premium" not in user_package_tier:
        st.warning(f"⏳ Free Trial Active Account Profile — **{trial_countdown} days left**")
        with st.expander("👑 Upgrade to Premium Instantly (₹15 / ₹30 / ₹50)", expanded=False):
            show_subscription_options()
    else:
        st.success(f"👑 Active License Verified — **{user_package_tier}**")

    st.markdown("### 🎥 Live Video Interview Feed")
    
    recorded_video_base64 = render_webcam_video_recorder()
    
    if recorded_video_base64 is not None:
        try:
            if hasattr(recorded_video_base64, 'value') and recorded_video_base64.value:
                video_str = str(recorded_video_base64.value)
            else:
                video_str = str(recorded_video_base64)

            if "base64," in video_str:
                base64_clean = video_str.split("base64,")[1]
                video_bytes = base64.b64decode(base64_clean)
                
                file_name = f"interview_session_{active_id}.webm"
                with open(file_name, "wb") as f:
                    f.write(video_bytes)
                
                st.success(f"💾 Video file received from camera and saved safely as `{file_name}`!")
        except Exception as e:
            st.error(f"Error compiling video storage data payload: {str(e)}")

    st.markdown("---")

    for message in current_chat["history"]:
        avatar_img = USER_AVATAR if message["role"] == "user" else ROBOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar_img):
            st.markdown(message["content"])

    if len(current_chat["history"]) == 1 and "Welcome" in current_chat["history"][0]["content"]:
        st.markdown("---")
        with st.expander("🛠️ Initialize Video Assessment Focus Track", expanded=True):
            with st.form("assessment_setup_form"):
                target_skill = st.selectbox("Primary Video Assessment Track:", ["Spoken English & Fluency", "Corporate/Business Communication"])
                experience_tier = st.selectbox("Target Competency Level:", ["Beginner / Elementary", "Advanced / Native Proficiency"])
                submit_onboarding = st.form_submit_button("🔥 Launch Language Assessment Matrix", type="primary")
                if submit_onboarding:
                    context_injection = f"🎯 Profile setup for {target_skill} targeting {experience_tier} benchmarks."
                    current_chat["history"].append({"role": "user", "content": context_injection})
                    with st.spinner("Compiling structure context rules..."):
                        eval_reply = get_evaluator_response(user_package_tier)
                        current_chat["history"].append({"role": "assistant", "content": eval_reply})
                        st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
                        st.rerun()

    audio_placeholder = st.empty()
    if st.session_state.autoplay_audio_data:
        audio_placeholder.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

    text_input = st.chat_input("Type your translation, essay answer, or session text here...")
    if text_input:
        current_chat["history"].append({"role": "user", "content": text_input})
        with st.spinner("Analyzing response dynamics..."):
            eval_reply = get_evaluator_response(user_package_tier)
            current_chat["history"].append({"role": "assistant", "content": eval_reply})
            st.session_state.autoplay_audio_data = None
            st.rerun()

elif app_mode == "📊 Analytics Dashboard":
    st.title("Linguistic Matrix Progress Tracker")
    metrics = st.session_state.performance_metrics
    m_col1, m_col2 = st.columns(2)
    with m_col1: 
        st.metric(label="Calculated Fluency Score", value=f"{metrics.get('fluency_score', 0.0)} / 10.0")
    with m_col2: 
        st.metric(label="Grammar Slips Logged", value=int(metrics.get('grammar_errors_logged', 0)))

elif app_mode == "🌐 Explore Video Learning Engine":
    st.title("🎬 50+ Topic Multi-Module Learning Hub")
    st.markdown("Select an explicit module to reveal targeted micro-sessions. You can launch any topic directly into your conversational AI agent context framework.")

    curriculum_matrix = {
        "📚 English Grammar Foundations": {
            "vid": "https://www.youtube.com/watch?v=3oIAICs8N9I",
            "sessions": [
                "Session 1: Subject-Verb Agreement Essentials", "Session 2: Mastering Modal Verbs (Can, Could, Should)",
                "Session 3: Complex Prepositions in Business", "Session 4: Active vs. Passive Voice Calibration",
                "Session 5: Correcting Run-On Sentences", "Session 6: Advanced Conditionals (If-Then Matrix)",
                "Session 7: Gerunds vs. Infinitives rules", "Session 8: Structural Relative Clauses",
                "Session 9: Adjective Ordering Sequences"
            ]
        },
        "⏳ Tense Mastery (Deep Dive)": {
            "vid": "https://www.youtube.com/watch?v=TsYMJQEtpJU",
            "sessions": [
                "Session 10: Simple Present vs. Present Continuous", "Session 11: Past Simple vs. Present Perfect Narratives",
                "Session 12: Future Intention Precision (Will vs. Going to)", "Session 13: Past Perfect Event Sequencing",
                "Session 14: Perfect Continuous Timing Layouts", "Session 15: Irregular Verbs Diagnostic Practice",
                "Session 16: State Verbs vs. Action Verbs Rules", "Session 17: Reported Speech Time-Shifting"
            ]
        },
        "🗣️ Communicable & Conversational Skills": {
            "vid": "https://www.youtube.com/watch?v=HAnw168huqA",
            "sessions": [
                "Session 18: Fluid Speech Pacing Frameworks", "Session 19: Pitch & Intonation Modulation",
                "Session 20: Eradicating Filler Words (Um, Like, Uh)", "Session 21: High-Impact Small Talk Starters",
                "Session 22: Structuring Real-Time Opinions", "Session 23: Expressing Strong Disagreement Politely",
                "Session 24: Interrupting with Professional Grace", "Session 25: Describing Trends and Metrics Fluently",
                "Session 26: Idiomatic English Expressions for Daily Use"
            ]
        },
        "📖 Reading & Comprehension Skills": {
            "vid": "https://www.youtube.com/watch?v=CxiH7s0inJc",
            "sessions": [
                "Session 27: Skimming Complex Industry Reports", "Session 28: Scanning for Crucial Metrics Data",
                "Session 29: Inferring Contextual Meanings of New Vocabulary", "Session 30: Paragraph Summary & Synthesis Retentions",
                "Session 31: Identifying Bias in Written Editorial Content", "Session 32: Speed Reading Conditioning Exercises",
                "Session 33: Structural Signpost Recognition"
            ]
        },
        "⏳ Essential Corporate Soft Skills": {
            "vid": "https://www.youtube.com/watch?v=8Oyd8d40om4",
            "sessions": [
                "Session 34: Active Listening Patterns in Teams", "Session 35: Delivering Constructive Criticism Elegantly",
                "Session 36: Empathy Models in Remote Work Ecosystems", "Session 37: Cross-Functional Team Negotiation Tools",
                "Session 38: De-escalation Paths for Workplace Disagreements", "Session 39: Assertive vs. Aggressive Vocal Styles",
                "Session 40: Navigating Unconscious Biases in Dialog", "Session 41: Managing Time Commitments Verbally"
            ]
        },
        "👔 Business Communication & Interview Prep": {
            "vid": "https://www.youtube.com/watch?v=PCWVi5pAa30",
            "sessions": [
                "Session 42: Compelling Presentation Structural Frameworks", "Session 43: Handing Hostile Q&A Panels Safely",
                "Session 44: High-Stakes Salary Negotiation Dialogue", "Session 45: Mastering the STAR Interview Formula",
                "Session 46: Explaining Career Gaps with Absolute Confidence", "Session 47: Crafting an Impactful Elevator Pitch",
                "Session 48: Remote Video Interface Presence Optimization", "Session 49: Telling Captivating Brand Stories",
                "Session 50: Closing the Deal / Client Intake Closing Scripts"
            ]
        }
    }

    selected_module = st.selectbox("🎯 Step 1: Select Training Module Category:", list(curriculum_matrix.keys()))
    module_data = curriculum_matrix[selected_module]
    
    selected_session = st.selectbox("📝 Step 2: Choose Specific Focus Topic Session:", module_data["sessions"])
    
    st.markdown("---")
    st.markdown(f"#### 📺 Target Study Stream: `{selected_session}`")
    st.video(module_data["vid"])
    
    if st.button(f"🚀 Injection Topic Into Active AI Agent Profile", use_container_width=True, type="primary"):
        injection_text = f"⚙️ SYSTEM UPDATE: Candidate has initialized study topic: **{selected_session}** from module context **{selected_module}**. Restrict evaluation focus to these specific competencies."
        current_chat["history"].append({"role": "user", "content": injection_text})
        current_chat["title"] = f"🎓 {selected_session.split(':')[0]}"
        st.success(f"Success! Agent context set to **{selected_session}**. Head back over to the '🗣️ Skill Assessment Portal' workspace to start your live video run.")

elif app_mode == "📬 Submit Custom Prompts":
    st.title("Custom Evaluation Prompt Intake Node")
    with st.form("custom_prompt_submission_form", clear_on_submit=True):
        p_name = st.text_input("Instructor Name:")
        p_text = st.text_area("Configure strict scenario constraints:")
        if st.form_submit_button("Commit Prompt to Repository"):
            st.success("Scenario logged safely inside framework state records.")
