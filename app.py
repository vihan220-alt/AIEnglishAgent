import streamlit as st

# =========================================================
# CONFIGURATION & SYSTEM THEME INTEGRATION (MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="SkillVerify AI - Video English Assessment Platform",
    page_icon="🤖",
    layout="centered"
)

# 🎨 IMPORT AND APPLY THE NEW DESIGN SKIN FROM STYLE.PY
try:
    from style import apply_custom_css
    apply_custom_css()
except ImportError:
    pass

# Core library imports follow below...
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

# NATIVE SECURE STREAMLIT WEBRTC COMPONENT ENGINE
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

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

# Fallback structure validation to prevent empty state drops
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
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #1e1b4b; padding: 20px; border-radius: 12px; border: 1px solid rgba(99,102,241,0.3); margin-top: 15px; color: white;">
        <h4 style="font-family: system-ui, sans-serif; margin-bottom: 5px; margin-top:0;">Secure Premium Activation Node</h4>
        <p style="color: #cbd5e1; font-size: 14px; font-family: system-ui, sans-serif; margin-bottom: 15px;">Upgrading <b>{email_recipient}</b> to the <b>{selected_plan} Plan ({plan_duration})</b></p>
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
    razorpay_key = f"razorpay_frame_{hashlib.md5(email_recipient.encode()).hexdigest()}"
    components.html(razorpay_html_code, height=160, key=razorpay_key)

# =========================================================
# SIDEBAR WORKSPACE NAVIGATION & CHAT INTERFACE OPTIONS
# =========================================================
with st.sidebar:
    st.markdown("### 🏢 Enterprise Training Hub")
    st.markdown("---")
    st.markdown("##### 🔑 Candidate Workspace Access")
    
    auth_email = st.text_input("Enter Registered Email Account:", value="vihan220@gmail.com", key="auth_email_persistent_field")
    
    user_package_tier, trial_countdown = init_user_and_get_plan(auth_email)
    
    app_mode = st.radio(
        "Select Portal Workspace:",
        ["🗣️ Skill Assessment Portal", "📊 Analytics Dashboard", "🌐 Explore Video Learning Engine", "📬 Submit Custom Prompts"],
        key="app_navigation_rail_index"
    )
    
    if app_mode == "🗣️ Skill Assessment Portal" and user_package_tier != "Expired":
        st.markdown("---")
        st.markdown("### 🛠️ Chat Session Management")
        
        if st.button("➕ Start New Assessment (New Chat)", use_container_width=True, type="primary", key="global_new_chat_trigger"):
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
        sorted_chat_ids = sorted(st.session_state.all_chats.keys(), key=lambda k: st.session_state.all_chats[k]["pinned"], reverse=True)
        
        for c_id in list(sorted_chat_ids):
            if c_id not in st.session_state.all_chats:
                continue
            chat_obj = st.session_state.all_chats[c_id]
            pin_indicator = "📌 " if chat_obj["pinned"] else "💬 "
            is_active = (c_id == st.session_state.active_chat_id)
            btn_label = f"{pin_indicator}{chat_obj['title']}"
            
            if st.button(btn_label, key=f"select_row_{c_id}", use_container_width=True, type="secondary" if not is_active else "primary"):
                st.session_state.active_chat_id = c_id
                st.session_state.autoplay_audio_data = None
                st.rerun()
                
            if is_active:
                col_pin, col_ren, col_del = st.columns(3)
                with col_pin:
                    if st.button("Unpin" if chat_obj["pinned"] else "Pin", key=f"btn_pin_action_{c_id}", use_container_width=True):
                        st.session_state.all_chats[c_id]["pinned"] = not st.session_state.all_chats[c_id]["pinned"]
                        st.rerun()
                with col_ren:
                    if st.button("Rename", key=f"btn_rename_action_{c_id}", use_container_width=True):
                        st.session_state[f"show_rename_field_{c_id}"] = True
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"btn_delete_action_{c_id}", use_container_width=True):
                        if len(st.session_state.all_chats) > 1:
                            del st.session_state.all_chats[c_id]
                            st.session_state.active_chat_id = list(st.session_state.all_chats.keys())[0]
                            st.session_state.autoplay_audio_data = None
                            st.rerun()
                        else:
                            st.error("Cannot delete your last active session trace!")
                
                if st.session_state.get(f"show_rename_field_{c_id}", False):
                    new_title_input = st.text_input("Enter New Session Name:", value=chat_obj["title"], key=f"title_input_field_{c_id}")
                    if st.button("Save Name", key=f"btn_save_name_action_{c_id}"):
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
        return "Configuration Key Error: Please register GROQ_API_KEY in secrets."

    system_rules = (
        "You are a friendly, conversational English Language Assessor evaluating a video interview submission. "
        "Keep your responses extremely concise, short, and natural (maximum 2 sentences). "
        "Always respond with exactly ONE clear, short conversational question at the end to keep the video chat interactive."
    )
    
    messages_payload = [{"role": "system", "content": system_rules}]
    for msg in current_chat["history"]:
        messages_payload.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
        
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
        return f"Network failure: {str(e)}"

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

def show_subscription_options():
    st.subheader("Select a Subscription Tier to Continue:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🥉 Basic\n**₹15** / month")
        if st.button("Select ₹15 Plan", use_container_width=True, key="btn_tier_15_select"): 
            st.session_state.payment_plan_selected = ("Basic Premium", 15, "1 Month")
            st.rerun()
    with col2:
        st.markdown("### 🥈 Standard\n**₹30** / month")
        if st.button("Select ₹30 Plan", use_container_width=True, type="primary", key="btn_tier_30_select"): 
            st.session_state.payment_plan_selected = ("Standard Premium", 30, "1 Month")
            st.rerun()
    with col3:
        st.markdown("### 🥇 Executive\n**₹50** / month")
        if st.button("Select ₹50 Plan", use_container_width=True, key="btn_tier_50_select"): 
            st.session_state.payment_plan_selected = ("Executive Premium", 50, "1 Month")
            st.rerun()
            
    st.markdown("---")
    coupon_input = st.text_input("Enter Coupon Code here:", key="coupon_field_intake").strip().upper()
    if coupon_input in ["FREE3M", "SKILL3"]:
        st.success("🎉 Coupon Applied Successfully! You get **3 Months FREE**.")
        if st.session_state.payment_plan_selected:
            p_name, _, _ = st.session_state.payment_plan_selected
            st.session_state.payment_plan_selected = (p_name, 0, "3 Months Promo")

    if st.session_state.payment_plan_selected:
        plan_nm, plan_amt, plan_dur = st.session_state.payment_plan_selected
        render_payment_gateway(auth_email, plan_nm, plan_amt, plan_dur)
        
        if st.button(f"⚡ [Simulate Payment Success] Activate {plan_nm}", use_container_width=True, key="payment_simulation_trigger"):
            if supabase_client is None:
                st.error("Database initialization failed. Please set up your secrets parameters.")
            else:
                success = update_user_plan_db(auth_email, f"{plan_nm} ({plan_dur})")
                if success:
                    st.success("Successfully activated plan! Reloading layout...")
                    st.session_state.payment_plan_selected = None
                    st.rerun()
                else:
                    st.error("Database storage push failed. Verify connectivity parameters.")

# =========================================================
# ROUTED CONTENT INTERFACE SWITCHER VIEWS
# =========================================================
if user_package_tier == "Expired":
    st.title("SkillVerify English Assessment Portal 🚀")
    st.error("⚠️ Your 15-day Free Trial package limits have been exhausted!")
    show_subscription_options()

elif app_mode == "🗣️ Skill Assessment Portal":
    active_id = st.session_state.active_chat_id
    st.title(f"{st.session_state.all_chats[active_id]['title'] if active_id in st.session_state.all_chats else 'English Assessment Portal'}")
    
    if "Premium" not in user_package_tier:
        st.warning(f"⏳ Free Trial Active Account Profile — **{trial_countdown} days left**")
        with st.expander("👑 Upgrade to Premium Instantly", expanded=False):
            show_subscription_options()
    else:
        st.success(f"👑 Active License Verified — **{user_package_tier}**")

    # =========================================================
    # NATIVE SECURE WEBCAM MODULE (FIXED ERROR-FREE INJECTION)
    # =========================================================
    st.markdown("### 🎥 Live Video Interview Feed")
    
    # Clean Google public STUN connectivity context
    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    # Replaces the buggy document listeners with secure, native layouts
    webrtc_streamer(
        key=f"interview_webcam_instance_{active_id}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        media_stream_constraints={"video": True, "audio": True},
        async_processing=True
    )

    st.markdown("---")

    for message in current_chat["history"]:
        avatar_img = USER_AVATAR if message["role"] == "user" else ROBOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar_img):
            st.markdown(message["content"])

    if len(current_chat["history"]) == 1 and "Welcome" in current_chat["history"][0]["content"]:
        st.markdown("---")
        with st.expander("🛠️ Initialize Video Assessment Focus Track", expanded=True):
            with st.form("assessment_setup_form"):
                target_skill = st.selectbox("Primary Video Assessment Track:", ["Spoken English & Fluency", "Corporate/Business Communication"], key="setup_target_skill")
                experience_tier = st.selectbox("Target Competency Level:", ["Beginner / Elementary", "Advanced / Native Proficiency"], key="setup_experience_tier")
                if st.form_submit_button("🔥 Launch Language Assessment Matrix", type="primary"):
                    current_chat["history"].append({"role": "user", "content": f"🎯 Profile setup for {target_skill} targeting {experience_tier} benchmarks."})
                    eval_reply = get_evaluator_response(user_package_tier)
                    current_chat["history"].append({"role": "assistant", "content": eval_reply})
                    st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
                    st.rerun()

    if st.session_state.autoplay_audio_data:
        st.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)
        st.session_state.autoplay_audio_data = None

    text_input = st.chat_input("Type your translation, essay answer, or session text here...", key="chat_input_terminal_field")
    if text_input:
        current_chat["history"].append({"role": "user", "content": text_input})
        eval_reply = get_evaluator_response(user_package_tier)
        current_chat["history"].append({"role": "assistant", "content": eval_reply})
        st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
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
    st.title("🎬 Topic Multi-Module Learning Hub")
    st.markdown("Select a track and a specialized focus session from over 50+ available learning modules.")

    curriculum_matrix = {
        "📚 Grammar & Structural Accuracy Foundations": {
            "vid": "https://www.youtube.com/watch?v=3oIAICs8N9I",
            "sessions": [
                "Session 1: Subject-Verb Agreement Principles",
                "Session 2: Mastering Modal Verbs for Obligation & Permission",
                "Session 3: Present Perfect vs. Past Simple Tense Transitions",
                "Session 4: Conditional Clauses (Type 1, 2, and 3 Mechanics)",
                "Session 5: Prepositions of Place, Time, and Direction",
                "Session 6: Active vs. Passive Voice in Corporate Reporting",
                "Session 7: Gerunds and Infinitives Diagnostic Rules",
                "Session 8: Correcting Common Dangling Modifiers",
                "Session 9: Relative Clauses and Pronoun Alignment"
            ]
        },
        "💼 Corporate Accent Modulation & Phonetics": {
            "vid": "https://www.youtube.com/watch?v=M2L76qM2sZ0",
            "sessions": [
                "Session 10: Professional Intonation & Sentence Stress Pacing",
                "Session 11: Overcoming Mother Tongue Influence (MTI) Variables",
                "Session 12: Vowel Sounds: Long vs. Short Monophthongs",
                "Session 13: Consonant Clusters and Crisp Endings",
                "Session 14: Connected Speech & Linking Words Seamlessly",
                "Session 15: Pitch Shifts for Emphasizing Key Business Metrics",
                "Session 16: Diaphragmatic Breathing for Vocal Clarity",
                "Session 17: Eliminating Fillers (Um, Ah, Like) via Pausing",
                "Session 18: Neutralizing Regional Dialect Pitch Drops"
            ]
        },
        "🚀 Advanced Interview Sentence Structures": {
            "vid": "https://www.youtube.com/watch?v=gaI7vXvSExA",
            "sessions": [
                "Session 19: High-Impact Project Pitch Starters",
                "Session 20: Formulating STAR-Method Behavioral Responses",
                "Session 21: Diplomatic Redirection Patterns for Difficult Queries",
                "Session 22: Highlighting Leadership Trajectories Verbally",
                "Session 23: Expressing Salary Expectations Confidently",
                "Session 24: Explaining Career Gaps Using Growth Assertions",
                "Session 25: Vocabulary Filters to Sound Executive and Mature",
                "Session 26: Constructing Persuasive Value Proposition Hooks",
                "Session 27: Executive Presence & Concluding Impact Statements"
            ]
        },
        "🤝 Professional Negotiation & Client Communication": {
            "vid": "https://www.youtube.com/watch?v=3oIAICs8N9I",
            "sessions": [
                "Session 28: Softening Assertions using Hedging Language",
                "Session 29: Handling Objections with Conversational Empathy",
                "Session 30: Framing Deadlines Positively without Friction",
                "Session 31: Setting Clear Boundaries on Scope Creep",
                "Session 32: Conceding Points Strategically in Real-time",
                "Session 33: Anchoring Price Discussions and Terms",
                "Session 34: Regaining Control of Derailing Client Meetings",
                "Session 35: Summarizing Action Items for Alignment Checks",
                "Session 36: Closing Enterprise Deals with Firm Vocabulary"
            ]
        },
        "📊 Technical Presentation & Data Storytelling": {
            "vid": "https://www.youtube.com/watch?v=M2L76qM2sZ0",
            "sessions": [
                "Session 37: Describing Trends, Graphs, and Market Spikes",
                "Session 38: Transitioning Between Complex Data Visuals",
                "Session 39: Translating Technical Metrics for Non-Tech Stakeholders",
                "Session 40: Simplifying Complex Software Architectures Verbally",
                "Session 41: Managing Q&A Sessions and Hecklers Gracefully",
                "Session 42: Narrative Arc Strategies for Technical Case Studies",
                "Session 43: Engaging Remote Audiences During Slide Runs",
                "Session 44: Emphasizing Risk Metrics using Comparative Phrases",
                "Session 45: Converting Static Features into Active Business Value"
            ]
        },
        "☕ Everyday Office Idioms & Socializing Vocabulary": {
            "vid": "https://www.youtube.com/watch?v=gaI7vXvSExA",
            "sessions": [
                "Session 46: Casual English vs. Formal Office Interventions",
                "Session 47: Watercooler Conversations and Polite Small Talk",
                "Session 48: Navigating Cross-Cultural Greetings with Care",
                "Session 49: Correct Use of Common Corporate Idioms",
                "Session 50: Polite Interruptions During Heated Discussions",
                "Session 51: Expressing Disagreement Constructively",
                "Session 52: Pitching Casual Ideas During Brainstorming Rounds",
                "Session 53: Writing & Verbally Validating Peer Praises",
                "Session 54: Closing Casual Virtual Sync-Ups Smoothly"
            ]
        }
    }

    with st.container(border=True):
        selected_module = st.selectbox(
            "🎯 Step 1: Select Training Module Category:", 
            options=list(curriculum_matrix.keys()),
            key="learning_hub_category_selector"
        )
        
        selected_session = st.selectbox(
            "📝 Step 2: Choose Specific Focus Topic Session:", 
            options=curriculum_matrix[selected_module]["sessions"],
            key=f"session_select_node_{selected_module}"
        )

    st.markdown("---")
    st.markdown(f"### 📺 Now Playing: **{selected_session}**")
    st.caption(f"Curriculum Track: {selected_module}")
    st.video(curriculum_matrix[selected_module]["vid"])

elif app_mode == "📬 Submit Custom Prompts":
    st.title("Custom Evaluation Prompt Intake Node")
    with st.form("custom_prompt_submission_form_fixed", clear_on_submit=True):
        p_name = st.text_input("Instructor Name:", key="intake_instructor_name")
        st.form_submit_button("Submit")
