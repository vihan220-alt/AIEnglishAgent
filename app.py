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
from datetime import datetime, date, timedelta
from supabase import create_client, Client

# =========================================================
# BROWSER LOCALSTORAGE PERSISTENCE ENGINE (ANTI-REFRESH)
# =========================================================
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# CRITICAL: Immediate client-side recovery that prevents brief login UI flash
recovery_control_js = """
<script>
    (function(){
        // Temporarily hide the page until recovery check completes
        function reveal() { try{ document.documentElement.style.visibility = ''; }catch(e){} }
        try {
            document.documentElement.style.visibility = 'hidden';
            const savedEmail = localStorage.getItem("skillverify_user_email");
            const savedLoggedIn = localStorage.getItem("skillverify_is_logged_in");
            const currentUrl = new URL(window.location.href);
            const hasRecoveryParam = currentUrl.searchParams.has('login_recovery_email');

            if (savedLoggedIn === "true" && savedEmail && !hasRecoveryParam) {
                // Add recovery parameter and reload ONCE to allow server-side restore
                currentUrl.searchParams.set('login_recovery_email', encodeURIComponent(savedEmail));
                window.location.replace(currentUrl.toString());
                return;
            }
        } catch(e) {
            // ignore errors and reveal page
        }
        // Reveal the page if no reload was triggered (safety timeout)
        setTimeout(reveal, 600);
    })();
</script>
"""
components.html(recovery_control_js, height=0)

# Debug overlay: shows localStorage & query param status to help diagnose recovery
debug_overlay_html = """
<div id="sv_debug_overlay" style="position:fixed;right:10px;top:72px;z-index:99999;background:rgba(0,0,0,0.65);color:#fff;padding:8px;border-radius:8px;font-family:system-ui, sans-serif;font-size:12px;min-width:220px;">
    <strong style="font-size:13px">Recovery Debug</strong>
    <div id="sv_debug_content" style="margin-top:6px;line-height:1.3"></div>
</div>
<script>
    (function(){
        const box = document.getElementById('sv_debug_content');
        function refresh(){
            try{
                const savedEmail = localStorage.getItem('skillverify_user_email');
                const savedLogged = localStorage.getItem('skillverify_is_logged_in');
                const lastProfile = localStorage.getItem('skillverify_last_profile');
                const qp = new URL(window.location.href).searchParams.get('login_recovery_email');
                box.innerHTML = `savedEmail: <b>${savedEmail||'<i>none</i>'}</b><br>savedLogged: <b>${savedLogged||'<i>none</i>'}</b><br>qp: <b>${qp||'<i>none</i>'}</b><br>lastProfile: <small>${(lastProfile||'<i>none</i>')}</small>`;
            }catch(e){ box.innerText = 'debug error'; }
        }
        refresh();
        setInterval(refresh, 1000);
    })();
</script>
"""
components.html(debug_overlay_html, height=0)

# Restore saved profile fields automatically from localStorage when user returns
profile_restore_js = """
<script>
    (function() {
        let profile = {};
        try {
            profile = JSON.parse(localStorage.getItem("skillverify_last_profile") || "{}");
        } catch (e) {
            profile = {};
        }

        if (profile) {
            const emailInput = document.querySelector('input[placeholder="name@example.com"]');
            const ageInput = document.querySelector('input[type="number"]');
            const intentInput = document.querySelector('textarea[placeholder="Explain why you want to use this service..."]');
            const maleRadio = document.querySelector('input[type="radio"][value="Male"]');
            const femaleRadio = document.querySelector('input[type="radio"][value="Female"]');

            if (emailInput && profile.email && !emailInput.value) {
                emailInput.value = profile.email;
                emailInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (ageInput && profile.age && !ageInput.value) {
                ageInput.value = profile.age;
                ageInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (intentInput && profile.intent && !intentInput.value) {
                intentInput.value = profile.intent;
                intentInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            if (maleRadio && profile.gender === "Male") {
                maleRadio.checked = true;
                maleRadio.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (femaleRadio && profile.gender === "Female") {
                femaleRadio.checked = true;
                femaleRadio.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    })();
</script>
"""
components.html(profile_restore_js, height=0)

# Integrated Cross-Domain Receiver for LocalStorage and Asynchronous Video Handling
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
components.html(receiver_js, height=0, width=0)

# Hidden bridge inputs removed from UI (kept JS handlers intact).
# We keep placeholder variables so downstream logic stays stable.
recovery_data = ""
video_bridge_data = ""

# IMPROVED: Hidden input field that gets populated from localStorage
localstorage_bridge_html = """
<div style="display:none;">
    <input type="hidden" id="skillverify_email_restore" value="">
    <input type="hidden" id="skillverify_logged_in_restore" value="">
</div>
<script>
    // Directly read from localStorage and populate hidden inputs immediately
    const savedEmail = localStorage.getItem("skillverify_user_email");
    const savedLoggedIn = localStorage.getItem("skillverify_is_logged_in");
    
    const emailInput = document.getElementById("skillverify_email_restore");
    const loggedInInput = document.getElementById("skillverify_logged_in_restore");
    
    if (emailInput && savedEmail) {
        emailInput.value = savedEmail;
        emailInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (loggedInInput && savedLoggedIn) {
        loggedInInput.value = savedLoggedIn;
        loggedInInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
</script>
"""
components.html(localstorage_bridge_html, height=0, width=0)

# Check URL params as an alternative recovery method
# Only restore if session is NOT already restored (idempotent)
if "login_recovery_email" in st.query_params and not st.session_state.is_logged_in:
    recovered_email = st.query_params.get("login_recovery_email", "").strip().lower()
    if recovered_email and "@" in recovered_email:
        email_exists = False
        if supabase_client is not None:
            try:
                response = supabase_client.table("users").select("email").eq("email", recovered_email).execute()
                email_exists = len(response.data) > 0
            except Exception:
                email_exists = False

        if email_exists:
            st.session_state.is_logged_in = True
            st.session_state.user_email = recovered_email
            st.rerun()
        else:
            cleanup_js = """
            <script>
                localStorage.removeItem("skillverify_user_email");
                localStorage.removeItem("skillverify_is_logged_in");
            </script>
            """
            components.html(cleanup_js, height=0)
            st.warning("⚠️ Stored login credentials were not valid. Please sign in again or create a new account.")
            st.experimental_set_query_params()
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

if "last_speech_transcript" not in st.session_state:
    st.session_state.last_speech_transcript = ""

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
    # Default: new users get a 10-day free trial
    TRIAL_DAYS = 10
    if not clean_email or supabase_client is None:
        return "Trial", TRIAL_DAYS
    try:
        response = supabase_client.table("users").select("*").eq("email", clean_email).execute()
        user_records = response.data
        if len(user_records) == 0:
            # set trial expiry to TRIAL_DAYS from today
            expiry_dt = date.today() + timedelta(days=TRIAL_DAYS)
            new_profile = {
                "email": clean_email,
                "user_plan": "Trial",
                "signup_date": str(date.today()),
                "plan_start_date": str(date.today()),
                "plan_expiry_date": expiry_dt.strftime("%Y-%m-%d")
            }
            supabase_client.table("users").insert(new_profile).execute()
            return "Trial", TRIAL_DAYS
        user_data = user_records[0]
        assigned_plan = user_data.get("user_plan", "Trial")
        # If there is a plan_expiry_date stored, compute remaining days
        expiry_str = user_data.get("plan_expiry_date")
        if expiry_str:
            try:
                expiry_date_obj = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                days_remaining = (expiry_date_obj - date.today()).days
                if days_remaining <= 0:
                    # mark expired
                    supabase_client.table("users").update({"user_plan": "Expired"}).eq("email", clean_email).execute()
                    return "Expired", 0
                return assigned_plan, days_remaining
            except Exception:
                # malformed expiry, fall back to trial calculation
                pass

        # Fallback: use signup_date for trial calculation
        signup_dt_str = user_data.get("signup_date", str(date.today()))
        signup_date_obj = datetime.strptime(signup_dt_str, "%Y-%m-%d").date()
        days_consumed = (date.today() - signup_date_obj).days
        remaining_trial_days = max(0, TRIAL_DAYS - days_consumed)
        if assigned_plan == "Trial" and remaining_trial_days <= 0:
            supabase_client.table("users").update({"user_plan": "Expired"}).eq("email", clean_email).execute()
            return "Expired", 0
        return assigned_plan, remaining_trial_days
    except Exception:
        return "Trial", TRIAL_DAYS

def update_user_plan_db(email_str, target_plan, months_duration=1):
    """
    Update the user's plan and set expiry based on months_duration.
    months_duration can be 1, 3, 6, etc. Use 0 for non-expiring (rare).
    """
    clean_email = email_str.strip().lower()
    if supabase_client is None:
        return False
    try:
        start_date = date.today()
        # approximate month as 30 days for expiry calculations
        try:
            from datetime import timedelta
            if months_duration and months_duration > 0:
                expiry_date = start_date + timedelta(days=30 * months_duration)
                expiry_str = expiry_date.strftime("%Y-%m-%d")
            else:
                expiry_str = None
        except Exception:
            expiry_str = None

        update_payload = {"user_plan": target_plan, "plan_start_date": str(start_date)}
        if expiry_str:
            update_payload["plan_expiry_date"] = expiry_str

        supabase_client.table("users").update(update_payload).eq("email", clean_email).execute()
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
    components.html(webcam_html, height=340)

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
    fallback_responses = [
        "That is a wonderful perspective on your career growth path. What do you consider your greatest structural strength when communicating in high-pressure team meetings?",
        "Thank you for sharing that clear detail. In business settings, clarity is absolutely vital. Can you describe a complex task you successfully simplified for others?",
        "Excellent vocabulary alignment. To continue our track calibration, how do you typically prepare for an interactive corporate group discussion?"
    ]
    
    if "GROQ_API_KEY" not in st.secrets or st.secrets["GROQ_API_KEY"].strip() == "":
        import random
        selected_fallback = random.choice(fallback_responses)
        parse_and_update_metrics(selected_fallback)
        return f"✨ [Sandbox Mode] {selected_fallback}"

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
        llm_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=llm_headers, json=llm_payload, timeout=8)
        res_data = llm_response.json()
        if isinstance(res_data, dict) and "choices" in res_data:
            response_content = res_data["choices"][0]["message"]["content"]
            parse_and_update_metrics(response_content)
            return response_content
        import random
        return f"✨ [API Schema Fallback] {random.choice(fallback_responses)}"
    except Exception:
        import random
        return f"✨ [Network Fallback] {random.choice(fallback_responses)}"

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
# URL QUERY PARAMETER ROUTER ENGINE (High-Stability Voice Processing)
# =========================================================
if "speech_transit_param" in st.query_params:
    captured_speech_text = st.query_params.get("speech_transit_param").strip()
    if captured_speech_text:
        st.session_state.last_speech_transcript = captured_speech_text
        current_chat["history"].append({"role": "user", "content": captured_speech_text})
        user_package_tier, _ = init_user_and_get_plan(st.session_state.user_email)
        eval_reply = get_evaluator_response(user_package_tier)
        current_chat["history"].append({"role": "assistant", "content": eval_reply})
        st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
        st.query_params.clear()
        st.rerun()

def show_subscription_options():
    st.subheader("Select a Subscription Tier to Continue:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🥉 Basic\n**₹15** / month")
        if st.button("Select ₹15 Plan", use_container_width=True, key="btn_tier_15_select"): 
            st.session_state.payment_plan_selected = ("Basic", 15, "1 Month", 1)
            st.rerun()
    with col2:
        st.markdown("### 🥈 Standard\n**₹30** / month")
        if st.button("Select ₹30 Plan", use_container_width=True, type="primary", key="btn_tier_30_select"): 
            st.session_state.payment_plan_selected = ("Standard", 30, "1 Month", 1)
            st.rerun()
    with col3:
        st.markdown("### 🥇 Epic\n**₹50** / month")
        if st.button("Select ₹50 Plan", use_container_width=True, key="btn_tier_50_select"): 
            st.session_state.payment_plan_selected = ("Epic", 50, "1 Month", 1)
            st.rerun()
            
    st.markdown("---")
    coupon_input = st.text_input("Enter Coupon Code here:", key="coupon_field_intake").strip().upper()
    valid_coupons = {"FREE6M":6, "SKILL6":6}
    if coupon_input:
        if coupon_input in valid_coupons:
            months = valid_coupons[coupon_input]
            st.success(f"🎉 Coupon Applied Successfully! You get **{months} Months FREE**.")
            if st.session_state.payment_plan_selected:
                p_name, _, _, _ = st.session_state.payment_plan_selected
                st.session_state.payment_plan_selected = (p_name, 0, f"{months} Months Promo", months)
        else:
            st.error("❌ Please write valid coupon code.")

    if st.session_state.payment_plan_selected:
        plan_nm, plan_amt, plan_dur, plan_months = st.session_state.payment_plan_selected
        render_payment_gateway(st.session_state.user_email, plan_nm, plan_amt, plan_dur)

        # Option to activate now (skip trial) without using payment gateway
        if st.button(f"Activate Now (Skip Trial) - {plan_nm}", use_container_width=True, key="activate_now_btn"):
            if supabase_client is None:
                st.error("Database initialization failed. Please set up your secrets parameters.")
            else:
                months_to_set = plan_months or 1
                success = update_user_plan_db(st.session_state.user_email, f"{plan_nm} ({plan_dur})", months_duration=months_to_set)
                if success:
                    st.success("Successfully activated plan! Reloading layout...")
                    st.session_state.payment_plan_selected = None
                    st.session_state.iframe_render_idx += 1
                    st.rerun()
                else:
                    st.error("Database storage push failed. Verify connectivity parameters.")

        if st.button(f"⚡ [Simulate Payment Success] Activate {plan_nm}", use_container_width=True, key="payment_simulation_trigger"):
            if supabase_client is None:
                st.error("Database initialization failed. Please set up your secrets parameters.")
            else:
                months_to_set = plan_months or 1
                success = update_user_plan_db(st.session_state.user_email, f"{plan_nm} ({plan_dur})", months_duration=months_to_set)
                if success:
                    st.success("Successfully activated plan! Reloading layout...")
                    st.session_state.payment_plan_selected = None
                    st.session_state.iframe_render_idx += 1
                    st.rerun()
                else:
                    st.error("Database storage push failed. Verify connectivity parameters.")

# =========================================================
# CONDITIONAL ROUTER (ONBOARDING LOGIC WITH HIDDEN DEV BYPASS)
# =========================================================
if not st.session_state.is_logged_in:
    st.title("🔐 Candidate Onboarding & Qualification Portal")
    
    # Initialize login mode state
    if "login_mode" not in st.session_state:
        st.session_state.login_mode = "new"  # 'new' or 'existing'
    
    is_developer = st.query_params.get("dev") == "true"
    
    # Get last email from localStorage if user just logged out
    get_last_email_js = """
    <script>
        const lastEmail = localStorage.getItem("skillverify_last_email");
        if (lastEmail) {
            const input = document.querySelector('input[placeholder="name@example.com"][type="text"]');
            if (input) {
                input.value = lastEmail;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    </script>
    """
    components.html(get_last_email_js, height=0)
    
    # Mode toggle
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 New Account", use_container_width=True, 
                     type="primary" if st.session_state.login_mode == "new" else "secondary"):
            st.session_state.login_mode = "new"
            st.rerun()
    with col2:
        if st.button("🔓 Already Have Account?", use_container_width=True,
                     type="primary" if st.session_state.login_mode == "existing" else "secondary"):
            st.session_state.login_mode = "existing"
            st.rerun()

    # Ensure login form state keys exist before any form render
    if "login_email_persist" not in st.session_state:
        st.session_state.login_email_persist = ""
    if "login_pass_persist" not in st.session_state:
        st.session_state.login_pass_persist = ""
    if "login_age_persist" not in st.session_state:
        st.session_state.login_age_persist = 25
    if "login_intent_persist" not in st.session_state:
        st.session_state.login_intent_persist = ""
    if "login_gender_persist" not in st.session_state:
        st.session_state.login_gender_persist = "Male"

    st.markdown("---")
    
    # ===== NEW ACCOUNT FORM =====
    if st.session_state.login_mode == "new":
        st.markdown("### Create New Account")
        st.markdown("You must complete all onboarding fields to access the main portal dashboard.")
        
        if "onboarding_form_initialized" not in st.session_state:
            st.session_state.onboarding_form_initialized = False

        if not st.session_state.onboarding_form_initialized:
            st.session_state.login_email_persist = ""
            st.session_state.login_pass_persist = ""
            st.session_state.login_age_persist = 25
            st.session_state.login_intent_persist = ""
            st.session_state.login_gender_persist = "Male"
            st.session_state.onboarding_form_initialized = True

        with st.form("onboarding_credential_form"):
            st.text_input("Email ID Address:", placeholder="name@example.com", key="login_email_persist")
            st.text_input("Email Password Account:", type="password", placeholder="••••••••", key="login_pass_persist")
            st.number_input("What is your age?", min_value=1, max_value=120, value=st.session_state.login_age_persist, key="login_age_persist")
            st.text_area("Why do you want to join this assessment platform?", placeholder="Explain why you want to use this service...", key="login_intent_persist")
            st.radio("Select Gender Profile:", ["Male", "Female"], key="login_gender_persist")
            
            if is_developer:
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    submit_clicked = st.form_submit_button("Verify Account & Enter Portal", type="primary", use_container_width=True)
                with btn_col2:
                    lucky_clicked = st.form_submit_button("✨ I'm Feeling Lucky (Bypass)", use_container_width=True)
            else:
                submit_clicked = st.form_submit_button("Verify Account & Enter Portal", type="primary", use_container_width=True)
                lucky_clicked = False

        proceed_to_login = False
        target_email = ""

        if submit_clicked:
            email_clean = st.session_state.login_email_persist.strip()
            password_clean = st.session_state.login_pass_persist.strip()
            intent_clean = st.session_state.login_intent_persist.strip()
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            intent_pattern = r"[a-zA-Z]{2,}\s+[a-zA-Z]{2,}\s+[a-zA-Z]{2,}"

            if not email_clean or not password_clean or not intent_clean:
                st.error("❌ You cannot login without filling out every required field.")
            elif not re.match(email_pattern, email_clean):
                st.error("❌ Invalid Email ID: Please type a valid email format containing an '@' and a proper domain.")
            elif len(password_clean) < 4:
                st.error("❌ Invalid Password: Password must contain at least 4 characters.")
            elif not re.search(intent_pattern, intent_clean):
                st.error("❌ Invalid answer: please provide a meaningful reason for joining.")
            else:
                proceed_to_login = True
                target_email = email_clean.lower()

        elif lucky_clicked and is_developer:
            email_clean = reg_email.strip()
            password_clean = reg_password.strip()
            intent_clean = reg_intent.strip()
            intent_pattern = r"[a-zA-Z]{2,}\s+[a-zA-Z]{2,}\s+[a-zA-Z]{2,}"

            if not email_clean or not password_clean or not intent_clean:
                st.error("❌ You cannot login without filling out every required field.")
            elif not re.search(intent_pattern, intent_clean):
                st.error("❌ Invalid answer: please provide a meaningful reason for joining.")
            else:
                proceed_to_login = True
                target_email = email_clean.lower()

        if proceed_to_login:
            st.session_state.is_logged_in = True
            st.session_state.user_email = target_email
            
            profile_json = json.dumps({
                "email": target_email,
                "age": st.session_state.get("login_age_persist", ""),
                "intent": st.session_state.get("login_intent_persist", ""),
                "gender": st.session_state.get("login_gender_persist", "Male")
            })
            persistence_js = f"""
            <script>
                // Save to localStorage
                localStorage.setItem("skillverify_user_email", "{target_email}");
                localStorage.setItem("skillverify_is_logged_in", "true");
                localStorage.setItem("skillverify_last_profile", {profile_json});
                localStorage.removeItem("skillverify_last_email");
                // Also set cookies as a fallback (7 days)
                document.cookie = "skillverify_user_email={target_email};path=/;max-age=604800";
                document.cookie = "skillverify_is_logged_in=true;path=/;max-age=604800";
                document.cookie = "skillverify_last_profile=" + encodeURIComponent({profile_json}) + ";path=/;max-age=604800";
            </script>
            """
            components.html(persistence_js, height=0, width=0)
            st.success("✓ Identity validated! Redirecting to dashboard...")
            st.rerun()
    
    # ===== QUICK SIGN-IN FORM (EXISTING ACCOUNT) =====
    else:
        st.markdown("### Sign In to Your Account")
        st.markdown("Welcome back! Sign in with your credentials to access your dashboard.")
        
        # Show info about last email if available
        last_email_js = """
        <script>
            const lastEmail = localStorage.getItem("skillverify_last_email");
            if (lastEmail) {
                const infoDiv = document.querySelector('[data-testid="last_email_info"]');
                if (infoDiv) {
                    infoDiv.innerHTML = `💡 Last used email: <strong>${lastEmail}</strong>`;
                }
            }
        </script>
        """
        components.html(last_email_js, height=0)
        
        st.info("💡 Last used email will be pre-filled below", icon="ℹ️")
        
        # Disable browser password save dialog
        disable_autosave_js = """
        <script>
            // Disable browser password save dialog
            document.addEventListener('DOMContentLoaded', function() {
                const forms = document.querySelectorAll('form');
                forms.forEach(form => {
                    form.setAttribute('autocomplete', 'off');
                    form.addEventListener('submit', function(e) {
                        // Prevent browser from offering to save password
                        const inputs = form.querySelectorAll('input');
                        inputs.forEach(input => {
                            input.setAttribute('autocomplete', 'off');
                            input.setAttribute('data-lpignore', 'true');
                            input.setAttribute('data-1p-ignore', 'true');
                        });
                    });
                });
            });
            
            // Also run on page load
            window.addEventListener('load', function() {
                const forms = document.querySelectorAll('form');
                forms.forEach(form => {
                    form.setAttribute('autocomplete', 'off');
                    const inputs = form.querySelectorAll('input[type="password"]');
                    inputs.forEach(input => {
                        input.setAttribute('autocomplete', 'new-password');
                    });
                });
            });
        </script>
        """
        components.html(disable_autosave_js, height=0)
        
        with st.form("quick_signin_form"):
            signin_email = st.text_input("Email ID Address:", placeholder="name@example.com", key="signin_email_persist")
            signin_password = st.text_input("Email Password Account:", type="password", placeholder="••••••••", key="signin_pass_persist")
            
            signin_submit = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)
        
        if signin_submit:
            email_clean = signin_email.strip().lower()
            password_clean = signin_password.strip()
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            
            if not email_clean or not password_clean:
                st.error("❌ Please enter both email and password.")
            elif not re.match(email_pattern, email_clean):
                st.error("❌ Invalid Email ID: Please type a valid email format.")
            elif len(password_clean) < 4:
                st.error("❌ Invalid Password: Password must contain at least 4 characters.")
            else:
                # Check if account exists in database
                account_exists = False
                if supabase_client is None:
                    st.error("❌ Account verification is unavailable because the database client is not configured.")
                else:
                    try:
                        response = supabase_client.table("users").select("*").eq("email", email_clean).execute()
                        if hasattr(response, "error") and response.error:
                            account_exists = False
                        elif isinstance(response.data, list):
                            account_exists = len(response.data) > 0
                        else:
                            account_exists = bool(response.data)
                    except Exception:
                        st.error("⚠️ Could not verify account. Please try again later or create a new account.")
                        account_exists = False

                if not account_exists:
                    st.error(
                        f"❌ No account found for email: {email_clean}.\n\n"
                        "If you don't have an account yet, please switch to 'New Account' and register."
                    )
                else:
                    st.session_state.is_logged_in = True
                    st.session_state.user_email = email_clean
                    
                    persistence_js = f"""
                    <script>
                        localStorage.setItem("skillverify_user_email", "{email_clean}");
                        localStorage.setItem("skillverify_is_logged_in", "true");
                        localStorage.removeItem("skillverify_last_email");
                        document.cookie = "skillverify_user_email={email_clean};path=/;max-age=604800";
                        document.cookie = "skillverify_is_logged_in=true;path=/;max-age=604800";
                    </script>
                    """
                    components.html(persistence_js, height=0, width=0)
                    st.success("✓ Welcome back! Redirecting to dashboard...")
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
            current_email = st.session_state.user_email
            st.session_state.is_logged_in = False
            st.session_state.user_email = ""
            
            profile_json = json.dumps({
                "email": st.session_state.get("login_email_persist", current_email),
                "age": st.session_state.get("login_age_persist", ""),
                "intent": st.session_state.get("login_intent_persist", ""),
                "gender": st.session_state.get("login_gender_persist", "Male")
            })
            logout_js = f"""
            <script>
                // Save the email and profile data for quick restore after logout
                localStorage.setItem("skillverify_last_email", "{current_email}");
                localStorage.setItem("skillverify_last_profile", {profile_json});
                localStorage.removeItem("skillverify_user_email");
                localStorage.removeItem("skillverify_is_logged_in");
                // Cookie fallback: save last profile and expire auth cookies
                document.cookie = "skillverify_last_profile=" + encodeURIComponent({profile_json}) + ";path=/;max-age=604800";
                document.cookie = "skillverify_user_email=;path=/;max-age=0";
                document.cookie = "skillverify_is_logged_in=;path=/;max-age=0";
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
        
        if user_package_tier in ("Trial", "Expired"):
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
                # === Visible Voice Controls + Live Transcript ===
                voice_control_html = """
                <div style='background: linear-gradient(135deg,#0f172a 0%,#111827 100%); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.04);'>
                    <div style='display:flex; gap:10px; align-items:center;'>
                        <button id='btnSpeak' style='background:#10b981;color:#fff;border:none;padding:8px 12px;border-radius:8px;cursor:pointer;'>🎤 Speak</button>
                        <button id='btnStopSpeaking' style='background:#ef4444;color:#fff;border:none;padding:8px 12px;border-radius:8px;cursor:pointer;' disabled>⏹️ Stop Speaking</button>
                        <button id='btnStopVoice' style='background:#4b5563;color:#fff;border:none;padding:8px 12px;border-radius:8px;cursor:pointer;'>🔇 Stop Voice</button>
                        <div id='voiceStatus' style='margin-left:12px;color:#94a3b8;'>Ready to capture speech.</div>
                    </div>
                    <div id='liveTranscript' style='margin-top:10px;padding:10px;background:rgba(255,255,255,0.02);border-radius:8px;color:#e6eef8;min-height:36px;'> </div>
                </div>

                <script>
                    (function(){
                        const speakBtn = document.getElementById('btnSpeak');
                        const stopSpeakBtn = document.getElementById('btnStopSpeaking');
                        const stopVoiceBtn = document.getElementById('btnStopVoice');
                        const status = document.getElementById('voiceStatus');
                        const live = document.getElementById('liveTranscript');

                        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                            status.innerText = 'Speech API not supported in this browser.';
                            speakBtn.disabled = true;
                        } else {
                            const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
                            const recog = new Speech();
                            recog.continuous = true;
                            recog.interimResults = true;
                            recog.lang = 'en-US';
                            let finalText = '';

                            speakBtn.addEventListener('click', ()=>{
                                finalText = '';
                                live.innerText = '';
                                recog.start();
                                speakBtn.disabled = true;
                                stopSpeakBtn.disabled = false;
                                status.innerText = '🎙️ Listening...';
                            });

                            stopSpeakBtn.addEventListener('click', ()=>{ if(recog) recog.stop(); });

                            recog.onresult = (ev)=>{
                                let interim = '';
                                for (let i = ev.resultIndex; i < ev.results.length; ++i) {
                                    const part = ev.results[i][0].transcript;
                                    if (ev.results[i].isFinal) finalText += part + ' ';
                                    else interim += part;
                                }
                                live.innerText = finalText + interim;
                                status.innerText = '✍ Capturing...';
                            };

                            recog.onend = ()=>{
                                speakBtn.disabled = false;
                                stopSpeakBtn.disabled = true;
                                if (finalText.trim() !== '') {
                                    status.innerText = '🚀 Sending transcript...';
                                    const topLoc = window.top.location;
                                    const u = new URL(topLoc.href);
                                    u.searchParams.set('speech_transit_param', finalText.trim());
                                    window.top.location.href = u.toString();
                                } else {
                                    status.innerText = 'No speech captured.';
                                }
                            };

                            recog.onerror = (e)=>{
                                speakBtn.disabled = false;
                                stopSpeakBtn.disabled = true;
                                status.innerText = '⚠️ Speech capture error.';
                            };
                        }

                        stopVoiceBtn.addEventListener('click', ()=>{
                            const audios = document.querySelectorAll('audio');
                            audios.forEach(a=>{ try{ a.pause(); a.currentTime = 0; }catch(e){} });
                            status.innerText = '🔇 AI voice muted.';
                        });
                    })();
                </script>
                """
                components.html(voice_control_html, height=140)

                # show last captured transcript visibly
                if st.session_state.get('last_speech_transcript'):
                        st.markdown(f"**Last captured transcript:** {st.session_state.last_speech_transcript}")

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

        text_input = st.chat_input("Type your translation, essay answer, or session text here...", key="chat_input_terminal_field")
        if text_input:
            # Explicitly reset the transcript here so the boxed layout UI clears on manually typed entries
            st.session_state.last_speech_transcript = "" 
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
