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
# BROWSER LOCALSTORAGE PERSISTENCE ENGINE (ANTI-REFRESH)
# =========================================================
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# JavaScript to bridge the browser's localStorage back into Streamlit seamlessly
storage_bridge_html = """
<script>
    const savedEmail = localStorage.getItem("skillverify_user_email");
    const savedLoggedIn = localStorage.getItem("skillverify_is_logged_in");
    
    if (savedLoggedIn === "true" && savedEmail) {
        // Send the credentials back to Streamlit app via a postMessage event
        window.parent.postMessage({
            type: 'LOCAL_STORAGE_RECOVERY_EVENT',
            email: savedEmail
        }, '*');
    }
</script>
"""
# FIX: Removed static 'key' to prevent internal metric gathering TypeErrors
components.html(storage_bridge_html, height=0, width=0)

# Integrated Cross-Domain Receiver for LocalStorage Recovery
receiver_js = """
<script>
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'LOCAL_STORAGE_RECOVERY_EVENT') {
            const recoveredEmail = event.data.email;
            const hiddenRecoveryInput = window.parent.document.getElementById("hidden_storage_recovery_input");
            if (hiddenRecoveryInput && hiddenRecoveryInput.value !== recoveredEmail) {
                hiddenRecoveryInput.value = recoveredEmail;
                hiddenRecoveryInput.dispatchEvent(new Event('input', { bubbles: true }));
                hiddenRecoveryInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        if (event.data && event.data.type === 'STREAMLIT_VIDEO_TRANSFER_EVENT') {
            const b64Data = event.data.data;
            const hiddenVideoInput = window.parent.document.getElementById("hidden_video_bridge_input");
            if (hiddenVideoInput) {
                hiddenVideoInput.value = b64Data;
                hiddenVideoInput.dispatchEvent(new Event('input', { bubbles: true }));
                hiddenVideoInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    });
</script>
"""
# FIX: Removed static 'key' to prevent internal metric gathering TypeErrors
components.html(receiver_js, height=0, width=0)

# Hidden inputs used to capture asynchronous JavaScript events cleanly
with st.expander("👁️ System Bridge Channels", expanded=False):
    recovery_data = st.text_input("Storage Recovery Node", key="hidden_storage_recovery_input")
    video_bridge_data = st.text_input("Internal Video Sync Node", key="hidden_video_bridge_input")

if recovery_data and not st.session_state.is_logged_in:
    st.session_state.is_logged_in = True
    st.session_state.user_email = recovery_data.strip().lower()
    st.rerun()

# =========================================================
# INITIALIZE GLOBAL SESSION STATE MEMORY FRAMEWORKS
# =========================================================
if "iframe_render_idx" not in st.session_state:
    st.session_state.iframe_render_idx = 0

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

if "incoming_video_payload" not in st.session_state:
    st.session_state.incoming_video_payload = None

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
    components.html(razorpay_html_code, height=160, key="razorpay_node_static")

# =========================================================
# HTML5 WEBCAM VIDEO RECORDING CONTROLLER
# =========================================================
def render_webcam_video_recorder():
    webcam_html = """
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; color: #ffffff; font-family: system-ui, sans-serif; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
        <video id="preview" width="100%" height="240" autoplay muted style="background: #000; border-radius: 6px; transform: scaleX(-1);"></video>
        <div style="margin-top: 10px;">
            <button id="startBtn" style="background-color: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: bold; cursor: pointer; margin-right: 5px;">🔴 Start Recording Session</button>
            <button id="stopBtn" style="background-color: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: bold; cursor: pointer;" disabled>⏹️ Stop & Submit</button>
        </div>
        <p id="statusMsg" style="font-size: 12px; color: #94a3b8; margin-top: 8px; margin-bottom: 0;">Webcam device active & waiting...</p>
    </div>

    <script>
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
                let options = { mimeType: 'video/webm;codecs=vp8,opus' };
                recorder = new MediaRecorder(stream, options);
                
                recorder.ondataavailable = (e) => {
                    if (e.data && e.data.size > 0) recordedChunks.push(e.data);
                };

                recorder.onstop = () => {
                    let blob = new Blob(recordedChunks, { type: 'video/webm' });
                    let reader = new FileReader();
                    reader.readAsDataURL(blob); 
                    reader.onloadend = function() {
                        let base64String = reader.result;
                        window.parent.postMessage({
                            type: 'STREAMLIT_VIDEO_TRANSFER_EVENT',
                            data: base64String
                        }, '*');
                    }
                };

                recorder.start(1000);
                startBtn.disabled = true;
                stopBtn.disabled = false;
                statusMsg.innerText = "📺 Session Recording Live (Video + Audio Capturing)...";
                statusMsg.style.color = "#f43f5e";
            });
            
            stopBtn.addEventListener('click', () => {
                if(recorder && recorder.state !== "inactive") recorder.stop();
                startBtn.disabled = false;
                stopBtn.disabled = true;
                statusMsg.innerText = "✔️ Processing data strings...";
                statusMsg.style.color = "#10b981";
            });
        }).catch(err => {
            statusMsg.innerText = "⚠️ Device Capture Access Denied: Check camera permissions.";
            statusMsg.style.color = "#ef4444";
        });
    </script>
    """
    components.html(webcam_html, height=340, key="webcam_panel_fixed_key")

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
        render_payment_gateway(st.session_state.user_email, plan_nm, plan_amt, plan_dur)
        
        if st.button(f"⚡ [Simulate Payment Success] Activate {plan_nm}", use_container_width=True, key="payment_simulation_trigger"):
            if supabase_client is None:
                st.error("Database initialization failed. Please set up your secrets parameters.")
            else:
                success = update_user_plan_db(st.session_state.user_email, f"{plan_nm} ({plan_dur})")
                if success:
                    st.success("Successfully activated plan! Reloading layout...")
                    st.session_state.payment_plan_selected = None
                    st.session_state.iframe_render_idx += 1
                    st.rerun()
                else:
                    st.error("Database storage push failed. Verify connectivity parameters.")

# =========================================================
# CONDITIONAL ROUTER (ONBOARDING LOGIC WITH BYPASS & FORMS)
# =========================================================
if not st.session_state.is_logged_in:
    st.title("🔐 Candidate Onboarding & Qualification Portal")
    st.markdown("You must complete all onboarding fields or use the quick bypass option to access your AI environment.")
    
    # Wrap user inputs inside a clean Streamlit form block to prevent data-sync delays
    with st.form("onboarding_credential_form"):
        reg_email = st.text_input("Email ID Address:", placeholder="name@example.com", key="login_email_persist")
        reg_password = st.text_input("Email Password Account:", type="password", placeholder="••••••••", key="login_pass_persist")
        reg_age = st.number_input("What is your age?", min_value=1, max_value=120, value=25, key="login_age_persist")
        reg_intent = st.text_area("Why do you want to join this assessment platform?", placeholder="Explain why you want to use this service...", key="login_intent_persist")
        reg_gender = st.radio("Select Gender Profile:", ["Male", "Female"], key="login_gender_persist")
        
        # Display validation and bypass controls side-by-side inside the form grid
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            submit_clicked = st.form_submit_button("Verify Account & Enter Portal", type="primary", use_container_width=True)
        with btn_col2:
            lucky_clicked = st.form_submit_button("✨ I'm Feeling Lucky (Bypass & Enter)", use_container_width=True)

    # Temporary parameters used to sequence the authentication stage
    proceed_to_login = False
    target_email = ""

    # Sequence A: Standard Validation Routine
    if submit_clicked:
        email_clean = reg_email.strip()
        password_clean = reg_password.strip()
        intent_clean = reg_intent.strip()
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        
        is_meaningful = bool(re.search(r'[a-zA-Z]{2,}\s+[a-zA-Z]{2,}\s+[a-zA-Z]{2,}', intent_clean))
        
        if not email_clean or not password_clean or not intent_clean:
            st.error("❌ **Submission Blocked:** All input rows must be filled. You cannot proceed with blank fields.")
        elif not re.match(email_pattern, email_clean):
            st.error("❌ **Invalid Email ID:** Please type a valid email format containing an '@' and a proper domain.")
        elif len(password_clean) < 4:
            st.error("❌ **Invalid Password:** Password string must contain a minimum of 4 characters.")
        elif not is_meaningful or len(intent_clean) < 12:
            st.error("❌ **Validation Failed:** Please write a valid sentence explaining your intent. Random characters or short gibberish lines are blocked.")
        else:
            proceed_to_login = True
            target_email = email_clean.lower()

    # Sequence B: Quick Dev Bypass Routine
    elif lucky_clicked:
        proceed_to_login = True
        target_email = reg_email.strip().lower() if reg_email.strip() else "developer_sandbox@skillverify.ai"

    # Save Session Attributes & Inject localStorage Script tags
    if proceed_to_login:
        st.session_state.is_logged_in = True
        st.session_state.user_email = target_email
        
        persistence_js = f"""
        <script>
            localStorage.setItem("skillverify_user_email", "{target_email}");
            localStorage.setItem("skillverify_is_logged_in", "true");
        </script>
        """
        components.html(persistence_js, height=0, width=0)
        st.success("✓ Identity validated! Redirecting to dashboard...")
        st.rerun()
else:
    # =========================================================
    # SIDEBAR WORKSPACE NAVIGATION & CHAT INTERFACE OPTIONS
    # =========================================================
    with st.sidebar:
        st.markdown("### 🏢 Enterprise Training Hub")
        st.markdown("---")
        st.markdown(f"##### 🔑 Profile Active: `{st.session_state.user_email}`")
        
        if st.button("🚪 Log Out / Switch Account", use_container_width=True):
            st.session_state.is_logged_in = False
            st.session_state.user_email = ""
            
            logout_js = """
            <script>
                localStorage.removeItem("skillverify_user_email");
                localStorage.removeItem("skillverify_is_logged_in");
            </script>
            """
            components.html(logout_js, height=0, width=0)
            st.rerun()
        
        user_package_tier, trial_countdown = init_user_and_get_plan(st.session_state.user_email)
        
        if "active_nav_mode" not in st.session_state:
            st.session_state.active_nav_mode = "🗣️ Skill Assessment Portal"

        app_mode = st.radio(
            "Select Portal Workspace:",
            ["🗣️ Skill Assessment Portal", "📊 Analytics Dashboard", "🌐 Explore Video Learning Engine", "📬 Submit Custom Prompts"],
            key="app_navigation_rail_index"
        )
        
        if app_mode != st.session_state.active_nav_mode:
            st.session_state.active_nav_mode = app_mode
            st.session_state.iframe_render_idx += 1
            st.rerun()
        
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
                st.session_state.incoming_video_payload = None
                st.session_state.iframe_render_idx += 1 
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
                    st.session_state.incoming_video_payload = None
                    st.session_state.iframe_render_idx += 1 
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
                                st.session_state.incoming_video_payload = None
                                st.session_state.iframe_render_idx += 1
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

        st.markdown("### 🎥 Live Video Interview Feed")

        render_webcam_video_recorder()

        if video_bridge_data and "base64," in video_bridge_data:
            try:
                base64_clean = video_bridge_data.split("base64,")[1]
                video_bytes = base64.b64decode(base64_clean)
                file_name = f"interview_session_{active_id}.webm"
                with open(file_name, "wb") as f:
                    f.write(video_bytes)
                st.success(f"💾 Video session captured and saved safely as `{file_name}`!")
                
                st.session_state["hidden_video_bridge_input"] = ""
                st.session_state.iframe_render_idx += 1
                st.rerun()
            except Exception as e:
                st.error(f"Error compiling video payload: {str(e)}")

        st.markdown("---")

        # RENDER CONVERSATION HISTORY
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

        # FIXED VOICE DICTATION NODE WITH STOP AND TRANSMIT CONTROL
        st.markdown("##### 🎙️ Voice Dictation Integration (Speak Options)")
        Micro_Speech_Bridge_Html = """
        <div style="background-color: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; gap: 10px; margin-bottom: 5px;">
            <div style="display: flex; gap: 10px; align-items: center;">
                <button id="sttMicBtn" style="background-color: #10b981; color: white; border: none; padding: 8px 14px; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 13px;">
                    🎤 Start Speaking
                </button>
                <button id="sttStopBtn" style="background-color: #ef4444; color: white; border: none; padding: 8px 14px; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 13px;" disabled>
                    ⏹️ Stop & Send Message
                </button>
            </div>
            <span id="sttStatusText" style="color: #94a3b8; font-size: 12px; font-family: system-ui, sans-serif;">Microphone engine standby...</span>
        </div>

        <script>
            const micBtnElement = document.getElementById('sttMicBtn');
            const stopBtnElement = document.getElementById('sttStopBtn');
            const statusLabelElement = document.getElementById('sttStatusText');
            let activeRecognitionInstance = null;
            let finalTranscribedPhrase = "";
            
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                statusLabelElement.innerText = "⚠️ Speech capture API unsupported by current browser runtime.";
                micBtnElement.disabled = true;
                stopBtnElement.disabled = true;
            } else {
                const SpeechRecognitionEngine = window.SpeechRecognition || window.webkitSpeechRecognition;
                activeRecognitionInstance = new SpeechRecognitionEngine();
                activeRecognitionInstance.continuous = true;
                activeRecognitionInstance.interimResults = true;
                activeRecognitionInstance.lang = 'en-US';

                micBtnElement.addEventListener('click', () => {
                    try {
                        finalTranscribedPhrase = "";
                        activeRecognitionInstance.start();
                        micBtnElement.disabled = true;
                        stopBtnElement.disabled = false;
                        statusLabelElement.innerText = "🎙️ Listening... Talk freely. When finished, click 'Stop & Send Message'.";
                        statusLabelElement.style.color = "#f43f5e";
                    } catch(e) {}
                });

                activeRecognitionInstance.onresult = (event) => {
                    let interimTranscript = "";
                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            finalTranscribedPhrase += event.results[i][0].transcript + " ";
                        } else {
                            interimTranscript += event.results[i][0].transcript;
                        }
                    }
                    
                    const nativeChatFieldTextArea = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                    if (nativeChatFieldTextArea) {
                        nativeChatFieldTextArea.value = finalTranscribedPhrase + interimTranscript;
                        nativeChatFieldTextArea.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                };

                stopBtnElement.addEventListener('click', () => {
                    if (activeRecognitionInstance) {
                        activeRecognitionInstance.stop();
                    }
                });

                activeRecognitionInstance.onend = () => {
                    micBtnElement.disabled = false;
                    stopBtnElement.disabled = true;
                    statusLabelElement.innerText = "✓ Voice dispatch completed cleanly! Text sent to main field interface below.";
                    statusLabelElement.style.color = "#10b981";
                    
                    setTimeout(() => {
                        const targetChatButton = window.parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
                        if (targetChatButton && !targetChatButton.disabled) {
                            targetChatButton.click();
                        }
                    }, 400);
                };

                activeRecognitionInstance.onerror = () => {
                    micBtnElement.disabled = false;
                    stopBtnElement.disabled = true;
                    statusLabelElement.innerText = "⚠️ Speech pipeline error/timeout detected.";
                    statusLabelElement.style.color = "#ef4444";
                };
            }
        </script>
        """
        components.html(Micro_Speech_Bridge_Html, height=95, key="stt_panel_fixed_key")

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
            "📚 Module 1: Grammar Foundations & Structural Accuracy": {
                "sessions": {
                    "Session 1: Subject-Verb Agreement Principles": "3QUvK9459w8",
                    "Session 2: Mastering Modal Verbs for Obligation & Permission": "NkYox74b89A",
                    "Session 3: Present Perfect vs. Past Simple Tense Transitions": "g2bA7A1GE94"
                }
            },
            "💼 Module 2: Accent Modulation & Corporate Phonetics": {
                "sessions": {
                    "Session 4: Professional Intonation & Sentence Stress Pacing": "F4N95-G77qE",
                    "Session 5: Overcoming Mother Tongue Influence (MTI) Variables": "n_w9mR47gXw"
                }
            }
        }

        with st.container(border=True):
            selected_module = st.selectbox(
                "🎯 Step 1: Select Training Module Category:", 
                options=list(curriculum_matrix.keys()),
                key="learning_hub_category_selector"
            )
            
            session_options = list(curriculum_matrix[selected_module]["sessions"].keys())
            selected_session = st.selectbox(
                "📝 Step 2: Choose Specific Focus Topic Session:", 
                options=session_options,
                key=f"session_select_node_{selected_module.replace(' ', '_')}"
            )

        video_id = curriculum_matrix[selected_module]["sessions"][selected_session]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        st.markdown("---")
        st.markdown(f"### 📺 Now Playing: **{selected_session}**")
        st.caption(f"Curriculum Track: {selected_module}")
        st.video(video_url)

    elif app_mode == "📬 Submit Custom Prompts":
        st.title("Custom Evaluation Prompt Intake Node")
        with st.form("custom_prompt_submission_form_fixed", clear_on_submit=True):
            p_name = st.text_input("Instructor Name:", key="intake_instructor_name")
            st.form_submit_button("Submit")
