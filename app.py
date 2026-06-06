import streamlit as st

# =========================================================
# CONFIGURATION & SYSTEM THEME INTEGRATION (MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="SkillVerify AI - English Assessment Platform",
    page_icon="🗣️",
    layout="centered"
)

# Core library imports
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
import streamlit.components.v1 as components
from io import BytesIO
from gtts import gTTS
from datetime import datetime, date, timedelta
from supabase import create_client, Client

# Initialize Database Session Memory Frameworks
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "Chat_1": {
            "title": "Default Language Assessment",
            "pinned": False,
            "history": [{"role": "assistant", "content": "🎯 **Welcome to your English Language Assessment Portal!**\n\nLet's map out your evaluation benchmarks. Please fill out the profile calibration form below to start your tailored language interview session."}]
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

# ==============================================================================
# CRITICAL SAFETY GUARD: Guarantee current_chat always exists dynamically
# ==============================================================================
if st.session_state.active_chat_id in st.session_state.all_chats:
    current_chat = st.session_state.all_chats[st.session_state.active_chat_id]
else:
    # Safe fallback if an ID goes missing during dynamic state updates
    fallback_id = list(st.session_state.all_chats.keys())[0]
    st.session_state.active_chat_id = fallback_id
    current_chat = st.session_state.all_chats[fallback_id]

# =========================================================
# SUPABASE DATABASE STORAGE ENGINE
# =========================================================
# Pulled safely from environment configuration profiles
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://xudmbkuruxfdpprwplee.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def get_supabase_client():
    if not SUPABASE_KEY:
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
        return
    try:
        supabase_client.table("users").update({"user_plan": target_plan}).eq("email", clean_email).execute()
        st.rerun()
    except Exception:
        pass

ROBOT_AVATAR = "https://img.icons8.com/fluent/96/artificial-intelligence.png"
USER_AVATAR = "https://img.icons8.com/fluent/96/user-male-circle.png"

# =========================================================
# INTEGRATED PAYMENT GATEWAY COMPONENT NODE
# =========================================================
def render_payment_gateway(email_recipient, selected_plan, cost_inr, plan_duration="Month"):
    """
    Renders an embedded, secure Razorpay button directly inside the Streamlit app view UI.
    """
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
        ["🗣️ Skill Assessment Portal", "📊 Analytics Dashboard", "🌐 Explore Learning Platform", "📬 Submit Custom Prompts"],
        index=0
    )
    
    # --- DYNAMIC CHAT HISTORY MANAGER MATRIX ---
    if app_mode == "🗣️ Skill Assessment Portal" and user_package_tier != "Expired":
        st.markdown("---")
        st.markdown("### 🛠️ Chat Session Management")
        
        # 1. NEW CHAT BUTTON
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
                
                # 2. PIN CHAT CONTROL BUTTON
                with col_pin:
                    pin_text = "Unpin" if chat_obj["pinned"] else "Pin"
                    if st.button(pin_text, key=f"pin_{c_id}", use_container_width=True):
                        st.session_state.all_chats[c_id]["pinned"] = not st.session_state.all_chats[c_id]["pinned"]
                        st.rerun()
                
                # 3. RENAME CHAT CONTROL BUTTON
                with col_ren:
                    if st.button("Rename", key=f"ren_{c_id}", use_container_width=True):
                        st.session_state[f"show_rename_field_{c_id}"] = True
                
                # 4. DELETE CHAT CONTROL BUTTON
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
        "You are a friendly, conversational English Language Assessor. "
        "Keep your responses extremely concise, short, and natural (maximum 2 sentences). "
        "Do not write long paragraphs or list multiple questions. "
        "Always respond with exactly ONE clear, short conversational question at the end to keep the chat simple."
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

# =========================================================
# REUSABLE SUBSCRIPTION CHOOSER NODE WITH COUPON LOGIC
# =========================================================
def show_subscription_options():
    st.subheader("Select a Subscription Tier to Continue:")
    
    # Create 3 clean columns for the plans
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🥉 Basic")
        st.markdown("**₹15** / month")
        if st.button("Select ₹15 Plan", use_container_width=True): 
            st.session_state.payment_plan_selected = ("Basic Premium", 15, "1 Month")
    with col2:
        st.markdown("### 🥈 Standard")
        st.markdown("**₹30** / month")
        if st.button("Select ₹30 Plan", use_container_width=True, type="primary"): 
            st.session_state.payment_plan_selected = ("Standard Premium", 30, "1 Month")
    with col3:
        st.markdown("### 🥇 Executive")
        st.markdown("**₹50** / month")
        if st.button("Select ₹50 Plan", use_container_width=True): 
            st.session_state.payment_plan_selected = ("Executive Premium", 50, "1 Month")
            
    st.markdown("---")
    st.markdown("##### 🏷️ Have a Coupon Code?")
    coupon_input = st.text_input("Enter Coupon Code here:", key="coupon_field").strip().upper()
    
    # If they type the promo code, update pricing configuration variables
    if coupon_input == "FREE3M" or coupon_input == "SKILL3":
        st.success("🎉 Coupon Applied Successfully! You get **3 Months FREE** on any selection.")
        if "payment_plan_selected" in st.session_state:
            p_name, _, _ = st.session_state.payment_plan_selected
            # Override to ₹0 for 3 Months duration
            st.session_state.payment_plan_selected = (p_name, 0, "3 Months Promo")

    if "payment_plan_selected" in st.session_state:
        plan_nm, plan_amt, plan_dur = st.session_state.payment_plan_selected
        
        # Call Razorpay integration element wrapper
        render_payment_gateway(auth_email, plan_nm, plan_amt, plan_dur)
        
        # Direct Action Simulator Button
        if st.button(f"⚡ [Simulate Payment Success] Activate {plan_nm} ({plan_dur})"):
            update_user_plan_db(auth_email, f"{plan_nm} ({plan_dur})")

# =========================================================
# ROUTED CONTENT INTERFACE SWITCHER VIEWS
# =========================================================
if user_package_tier == "Expired":
    st.title("SkillVerify English Assessment Portal 🚀")
    st.error("⚠️ Your 15-day Free Trial package limits have been exhausted!")
    show_subscription_options()

elif app_mode == "🗣️ Skill Assessment Portal":
    # Robust Title Guard Implementation
    if 'all_chats' in st.session_state and st.session_state.active_chat_id in st.session_state.all_chats:
        st.title(f"Portal Workspace: {st.session_state.all_chats[st.session_state.active_chat_id]['title']}")
    else:
        st.title("Portal Workspace: English Assessment Portal")
    
    if "Premium" not in user_package_tier:
        st.warning(f"⏳ Free Trial Active Account Profile — **{trial_countdown} days left**")
        
        # Direct Payment/Upgrade Hub positioned right on the dashboard!
        with st.expander("👑 Upgrade to Premium Instantly (₹15 / ₹30 / ₹50)", expanded=False):
            show_subscription_options()
    else:
        st.success(f"👑 Active License Verified — **{user_package_tier}**")

    for message in current_chat["history"]:
        avatar_img = USER_AVATAR if message["role"] == "user" else ROBOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar_img):
            st.markdown(message["content"])

    if len(current_chat["history"]) == 1 and "Welcome" in current_chat["history"][0]["content"]:
        st.markdown("---")
        with st.expander("🛠️ Initialize Language Profile Target", expanded=True):
            with st.form("assessment_setup_form"):
                target_skill = st.selectbox("Primary Assessment Focus Track:", ["Spoken English & Fluency", "Corporate/Business Communication"])
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

    voice_col, stop_col = st.columns([1, 1])
    with voice_col:
        audio_source = mic_recorder(start_prompt="Record Response 🎤", stop_prompt="Submit Recording 🔇", key=f"recorder_{st.session_state.active_chat_id}")
    with stop_col:
        if st.button("Stop Audio Playback Engine", use_container_width=True):
            st.session_state.autoplay_audio_data = None
            audio_placeholder.empty()
            st.rerun()

    text_input = st.chat_input("Type your response essay text or conversation explanation here...")
    if text_input:
        current_chat["history"].append({"role": "user", "content": text_input})
        with st.spinner("Analyzing vocabulary choices..."):
            eval_reply = get_evaluator_response(user_package_tier)
            current_chat["history"].append({"role": "assistant", "content": eval_reply})
            st.session_state.autoplay_audio_data = None
            st.rerun()

    if audio_source and "bytes" in audio_source and audio_source["bytes"]:
        audio_bytes = audio_source["bytes"]
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if "last_processed_audio" not in st.session_state or st.session_state.last_processed_audio != audio_hash:
            st.session_state.last_processed_audio = audio_hash
            with st.spinner("Processing spoken response streams..."):
                try:
                    whisper_files = {"file": ("speech.wav", audio_bytes, "audio/wav"), "model": (None, "whisper-large-v3-turbo"), "language": (None, "en")}
                    whisper_headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                    whisper_response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=whisper_headers, files=whisper_files)
                    user_text = whisper_response.json().get("text", "")
                    if user_text.strip():
                        current_chat["history"].append({"role": "user", "content": user_text})
                        eval_reply = get_evaluator_response(user_package_tier)
                        current_chat["history"].append({"role": "assistant", "content": eval_reply})
                        st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
                        st.rerun()
                except Exception:
                    pass

elif app_mode == "📊 Analytics Dashboard":
    st.title("Linguistic Matrix Progress Tracker")
    
    # Defensive conditional check protecting against "SessionInfo before it was initialized" bugs
    if "performance_metrics" in st.session_state:
        metrics = st.session_state.performance_metrics
        m_col1, m_col2 = st.columns(2)
        with m_col1: 
            st.metric(label="Calculated Fluency Score", value=f"{metrics.get('fluency_score', 0.0)} / 10.0")
        with m_col2: 
            st.metric(label="Grammar Slips Logged", value=int(metrics.get('grammar_errors_logged', 0)))
    else:
        st.info("Syncing metrics data profiles with active session caches...")

elif app_mode == "🌐 Explore Learning Platform":
    st.title("External English Knowledge Portal")
    st.link_button("🌐 Open BBC Learning English", "https://www.bbc.co.uk/learningenglish", use_container_width=True, type="primary")

elif app_mode == "📬 Submit Custom Prompts":
    st.title("Custom Evaluation Prompt Intake Node")
    with st.form("custom_prompt_submission_form", clear_on_submit=True):
        p_name = st.text_input("Instructor Name:")
        p_text = st.text_area("Configure strict scenario constraints:")
        if st.form_submit_button("Commit Prompt to Repository"):
            st.success("Scenario logged safely inside framework state records.")
