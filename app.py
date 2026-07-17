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
        function reveal() { try{ document.documentElement.style.visibility = ''; }catch(e){} }
        try {
            document.documentElement.style.visibility = 'hidden';
            const currentUrl = new URL(window.location.href);
            const hasRecoveryParam = currentUrl.searchParams.has('login_recovery_email');

            let savedEmail = localStorage.getItem("skillverify_user_email");
            let savedLoggedIn = localStorage.getItem("skillverify_is_logged_in");

            if ((!savedEmail || !savedLoggedIn) && document.cookie) {
                const cookieEntries = document.cookie.split(';').map(c => c.trim());
                const cookieMap = {};
                cookieEntries.forEach(entry => {
                    const [name, value] = entry.split('=');
                    cookieMap[name] = value;
                });
                if (!savedEmail && cookieMap.skillverify_user_email) {
                    savedEmail = decodeURIComponent(cookieMap.skillverify_user_email);
                }
                if (!savedLoggedIn && cookieMap.skillverify_is_logged_in) {
                    savedLoggedIn = decodeURIComponent(cookieMap.skillverify_is_logged_in);
                }
            }

            if (savedLoggedIn === "true" && savedEmail && !hasRecoveryParam) {
                currentUrl.searchParams.set('login_recovery_email', encodeURIComponent(savedEmail));
                window.location.replace(currentUrl.toString());
                return;
            }
        } catch(e) {
            // ignore errors and reveal page
        }
        setTimeout(reveal, 2000);
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
            const savedState = JSON.parse(localStorage.getItem('skillverify_saved_state') || '{}');
            profile = savedState.last_profile || JSON.parse(localStorage.getItem('skillverify_last_profile') || '{}');
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

# Auto-save form and login state to localStorage continuously
autosave_state_js = """
<script>
    (function() {
        const STORAGE_KEY = 'skillverify_saved_state';

        function getSaved() {
            try {
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
            } catch (e) {
                return {};
            }
        }

        function saveState(state) {
            try {
                const next = Object.assign(getSaved(), state || {});
                localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
            } catch (e) {
                // ignore storage write failures
            }
        }

        function saveProfileFields() {
            const emailInput = document.querySelector('input[placeholder="name@example.com"]');
            const ageInput = document.querySelector('input[type="number"]');
            const intentInput = document.querySelector('textarea[placeholder="Explain why you want to use this service..."]');
            const maleRadio = document.querySelector('input[type="radio"][value="Male"]');
            const femaleRadio = document.querySelector('input[type="radio"][value="Female"]');
            const profile = {};
            if (emailInput && emailInput.value) profile.email = emailInput.value;
            if (ageInput && ageInput.value) profile.age = ageInput.value;
            if (intentInput && intentInput.value) profile.intent = intentInput.value;
            if (maleRadio && maleRadio.checked) profile.gender = 'Male';
            if (femaleRadio && femaleRadio.checked) profile.gender = 'Female';
            if (Object.keys(profile).length > 0) {
                saveState({ last_profile: profile });
            }
        }

        function attachInput(selector) {
            const element = document.querySelector(selector);
            if (!element) return;
            element.addEventListener('input', saveProfileFields);
            element.addEventListener('change', saveProfileFields);
        }

        function tryAttach() {
            attachInput('input[placeholder="name@example.com"]');
            attachInput('input[type="number"]');
            attachInput('textarea[placeholder="Explain why you want to use this service..."]');
            attachInput('input[type="radio"][value="Male"]');
            attachInput('input[type="radio"][value="Female"]');
        }

        tryAttach();
        setTimeout(tryAttach, 800);
        window.addEventListener('beforeunload', saveProfileFields);
    })();
</script>
"""
components.html(autosave_state_js, height=0)

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

# Check URL params as an alternative recovery method
# Only restore if session is NOT already restored (idempotent)
if "login_recovery_email" in st.query_params and not st.session_state.is_logged_in:
    recovered_email = st.query_params.get("login_recovery_email", "").strip().lower()
    if recovered_email and "@" in recovered_email:
        email_exists = False
        if supabase_client is not None:
            try:
                response = supabase_client.table("users").select("email, age, intent, gender").eq("email", recovered_email).execute()
                email_exists = isinstance(response.data, list) and len(response.data) > 0
            except Exception:
                email_exists = False

        if email_exists:
            st.session_state.is_logged_in = True
            st.session_state.user_email = recovered_email
            try:
                profile_row = response.data[0]
                st.session_state.login_email_persist = profile_row.get("email", recovered_email)
                st.session_state.login_age_persist = profile_row.get("age", st.session_state.get("login_age_persist", 25))
                st.session_state.login_intent_persist = profile_row.get("intent", st.session_state.get("login_intent_persist", ""))
                st.session_state.login_gender_persist = profile_row.get("gender", st.session_state.get("login_gender_persist", "Male"))
            except Exception:
                pass
            st.query_params.clear()
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
            st.query_params.clear()
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

def normalize_plan_name(plan_name):
    if not plan_name:
        return plan_name
    normalized = plan_name.strip().lower()
    if "exclusive" in normalized or "epic" in normalized or "executive" in normalized:
        return "Exclusive"
    if "standard" in normalized:
        return "Standard"
    if "basic" in normalized:
        return "Basic"
    if "trial" in normalized:
        return "Trial"
    if "expired" in normalized:
        return "Expired"
    return plan_name


def init_user_and_get_plan(email_str):
    clean_email = email_str.strip().lower()

    # The owner account has free, unlimited access and never needs a paid plan.
    if clean_email == "vihan220@gmail.com":
        return "Exclusive", 999999

    # Allow a temporary per-user expire override for the current session.
    if st.session_state.get("force_expire_for_me", False) and clean_email and clean_email == st.session_state.get("user_email", "").strip().lower():
        return "Expired", 0
    # Default: new users get a 15-day free trial
    TRIAL_DAYS = 15
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
        assigned_plan = normalize_plan_name(user_data.get("user_plan", "Trial"))
        # If there is a plan_expiry_date stored, compute remaining days
        expiry_str = user_data.get("plan_expiry_date")
        if expiry_str:
            try:
                expiry_date_obj = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                # ensure trial expiry uses at least the current 15-day policy for older accounts
                signup_dt_str = user_data.get("signup_date", str(date.today()))
                signup_date_obj = datetime.strptime(signup_dt_str, "%Y-%m-%d").date()
                trial_max_expiry = signup_date_obj + timedelta(days=TRIAL_DAYS)
                if assigned_plan == "Trial" and expiry_date_obj < trial_max_expiry:
                    expiry_date_obj = trial_max_expiry
                    supabase_client.table("users").update({"plan_expiry_date": expiry_date_obj.strftime("%Y-%m-%d")}).eq("email", clean_email).execute()

                days_remaining = (expiry_date_obj - date.today()).days
                if days_remaining <= 0:
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
        target_plan = normalize_plan_name(target_plan)
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


def save_profile_to_db(email_str, profile_dict):
    """Insert or update the user's profile fields in the users table."""
    clean_email = (email_str or "").strip().lower()
    if not clean_email or supabase_client is None:
        return False
    try:
        # Check existing
        resp = supabase_client.table("users").select("email").eq("email", clean_email).execute()
        payload = profile_dict.copy()
        payload["email"] = clean_email
        if resp and getattr(resp, 'data', None) and len(resp.data) > 0:
            supabase_client.table("users").update(payload).eq("email", clean_email).execute()
        else:
            # ensure signup_date and default plan if not provided
            if "signup_date" not in payload:
                payload["signup_date"] = str(date.today())
            if "user_plan" not in payload:
                payload["user_plan"] = "Trial"
            supabase_client.table("users").insert(payload).execute()
        return True
    except Exception:
        return False

TRIAL_AI_QUESTION_LIMIT = 20

def get_trial_ai_question_usage(email_str):
    clean_email = (email_str or "").strip().lower()
    if not clean_email:
        return 0
    if supabase_client is not None:
        try:
            response = (
                supabase_client.table("users")
                .select("trial_ai_questions_used")
                .eq("email", clean_email)
                .execute()
            )
            if response.data:
                return int(response.data[0].get("trial_ai_questions_used") or 0)
        except Exception:
            pass
    return int(st.session_state.get("trial_ai_questions_used", 0))

def consume_ai_question(plan_tier, email_str):
    if plan_tier == "Expired":
        return False, 0

    if plan_tier != "Trial":
        return True, None

    used = get_trial_ai_question_usage(email_str)
    if used >= TRIAL_AI_QUESTION_LIMIT:
        return False, 0

    next_used = used + 1
    st.session_state.trial_ai_questions_used = next_used
    if supabase_client is not None:
        try:
            (
                supabase_client.table("users")
                .update({"trial_ai_questions_used": next_used})
                .eq("email", (email_str or "").strip().lower())
                .execute()
            )
        except Exception:
            pass
    return True, TRIAL_AI_QUESTION_LIMIT - next_used

def render_trial_ai_limit_notice():
    st.warning(
        "Your free trial AI access has ended. "
        "Choose a paid plan for unlimited AI questions."
    )
    show_subscription_options()

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
    components.html(razorpay_html_code, height=160)

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
        user_package_tier, _ = init_user_and_get_plan(st.session_state.user_email)
        allowed, _ = consume_ai_question(
            user_package_tier, st.session_state.user_email
        )
        if allowed:
            current_chat["history"].append({"role": "user", "content": captured_speech_text})
            eval_reply = get_evaluator_response(user_package_tier)
            current_chat["history"].append({"role": "assistant", "content": eval_reply})
            st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
            st.query_params.clear()
            st.rerun()
        else:
            st.query_params.clear()
            render_trial_ai_limit_notice()

def show_subscription_options():
    st.subheader("Choose a Monthly Pass")

    monthly_plans = {
        "Basic - Rs. 15 / month": ("Basic", 15),
        "Standard - Rs. 30 / month": ("Standard", 30),
        "Exclusive - Rs. 50 / month": ("Exclusive", 50),
    }
    selected_plan_label = st.radio(
        "Monthly pass",
        options=list(monthly_plans.keys()),
        key="monthly_pass_selector",
    )
    plan_name, plan_amount = monthly_plans[selected_plan_label]

    # Store the choice without rerunning, so it remains selected on the page.
    st.session_state.payment_plan_selected = (plan_name, plan_amount, "1 Month", 1)
    st.caption("Each paid pass expires 30 days after successful payment.")

    coupon_input = st.text_input(
        "Coupon code",
        key="coupon_field_intake",
    ).strip().upper()
    valid_coupons = {"FREE6M": 6, "SKILL6": 6}
    coupon_is_valid = not coupon_input or coupon_input in valid_coupons

    if coupon_input and not coupon_is_valid:
        st.error("This coupon code is not valid. Please enter a valid code or leave the field empty.")

    if coupon_is_valid:
        if coupon_input:
            promo_months = valid_coupons[coupon_input]
            st.success(f"Coupon applied: {promo_months} months free.")
            st.info("The promotion is activated by the platform administrator after verification.")
        else:
            st.markdown("---")
            st.caption(
                "Payment is processed by Razorpay and sent to the merchant account "
                "configured for this platform. Settlement details are available in "
                "the owner's Razorpay dashboard."
            )
            render_payment_gateway(
                st.session_state.user_email,
                plan_name,
                plan_amount,
                "1 Month",
            )

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

        # FIXED: Resolved reference errors where reg_* variables were non-existent
        elif lucky_clicked and is_developer:
            email_clean = st.session_state.login_email_persist.strip()
            password_clean = st.session_state.login_pass_persist.strip()
            intent_clean = st.session_state.login_intent_persist.strip()
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
            # Persist profile to DB (insert/update)
            try:
                profile_payload = {
                    "age": st.session_state.get("login_age_persist", ""),
                    "intent": st.session_state.get("login_intent_persist", ""),
                    "gender": st.session_state.get("login_gender_persist", "Male"),
                    "user_plan": "Trial",
                    "plan_start_date": str(date.today())
                }
                # set expiry for a 15-day trial
                from datetime import timedelta
                profile_payload["plan_expiry_date"] = (date.today() + timedelta(days=15)).strftime("%Y-%m-%d")
                save_profile_to_db(target_email, profile_payload)
            except Exception:
                pass
            persistence_js = f"""
            <script>
                const savedState = JSON.parse(localStorage.getItem('skillverify_saved_state') || '{{}}');
                savedState.user_email = '{target_email}';
                savedState.is_logged_in = 'true';
                savedState.last_profile = {profile_json};
                localStorage.setItem('skillverify_saved_state', JSON.stringify(savedState));
                localStorage.setItem('skillverify_user_email', '{target_email}');
                localStorage.setItem('skillverify_is_logged_in', 'true');
                localStorage.setItem('skillverify_last_profile', {profile_json});
                localStorage.removeItem('skillverify_last_email');
                document.cookie = 'skillverify_user_email={target_email};path=/;max-age=604800';
                document.cookie = 'skillverify_is_logged_in=true;path=/;max-age=604800';
                document.cookie = 'skillverify_last_profile=' + encodeURIComponent({profile_json}) + ';path=/;max-age=604800';
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
                    st.error(f"❌ No account found for email: {email_clean}. We don't have any account like that.")
                    st.session_state.signin_missing_email = email_clean
                else:
                    st.session_state.signin_missing_email = ""
                    # load saved profile values from database before login
                    try:
                        profile_row = response.data[0] if isinstance(response.data, list) and len(response.data) > 0 else None
                        if profile_row:
                            st.session_state.login_email_persist = profile_row.get("email", email_clean)
                            st.session_state.login_age_persist = profile_row.get("age", st.session_state.get("login_age_persist", 25))
                            st.session_state.login_intent_persist = profile_row.get("intent", st.session_state.get("login_intent_persist", ""))
                            st.session_state.login_gender_persist = profile_row.get("gender", st.session_state.get("login_gender_persist", "Male"))
                    except Exception:
                        pass
                    st.session_state.is_logged_in = True
                    st.session_state.user_email = email_clean
                    
                    persistence_js = f"""
                    <script>
                        const savedState = JSON.parse(localStorage.getItem('skillverify_saved_state') || '{{}}');
                        savedState.user_email = '{email_clean}';
                        savedState.is_logged_in = 'true';
                        localStorage.setItem('skillverify_saved_state', JSON.stringify(savedState));
                        localStorage.setItem('skillverify_user_email', '{email_clean}');
                        localStorage.setItem('skillverify_is_logged_in', 'true');
                        localStorage.removeItem('skillverify_last_email');
                        document.cookie = 'skillverify_user_email={email_clean};path=/;max-age=604800';
                        document.cookie = 'skillverify_is_logged_in=true;path=/;max-age=604800';
                    </script>
                    """
                    components.html(persistence_js, height=0, width=0)
                    st.success("✓ Welcome back! Redirecting to dashboard...")
                    st.rerun()

        if st.session_state.get("signin_missing_email"):
            if st.button("Create New Account with this email", key="btn_create_new_from_signin"):
                st.session_state.login_mode = "new"
                st.session_state.login_email_persist = st.session_state.signin_missing_email
                st.session_state.signin_missing_email = ""
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
            # Persist profile to DB before logout
            try:
                profile_payload = {
                    "age": st.session_state.get("login_age_persist", ""),
                    "intent": st.session_state.get("login_intent_persist", ""),
                    "gender": st.session_state.get("login_gender_persist", "Male")
                }
                save_profile_to_db(current_email, profile_payload)
            except Exception:
                pass

            st.session_state.is_logged_in = False
            st.session_state.user_email = ""
            st.session_state.force_expire_for_me = False
            
            profile_json = json.dumps({
                "email": st.session_state.get("login_email_persist", current_email),
                "age": st.session_state.get("login_age_persist", ""),
                "intent": st.session_state.get("login_intent_persist", ""),
                "gender": st.session_state.get("login_gender_persist", "Male")
            })
            logout_js = f"""
            <script>
                const savedState = JSON.parse(localStorage.getItem('skillverify_saved_state') || '{{}}');
                savedState.last_profile = {profile_json};
                savedState.is_logged_in = 'false';
                savedState.user_email = '';
                localStorage.setItem('skillverify_saved_state', JSON.stringify(savedState));
                localStorage.setItem('skillverify_last_email', '{current_email}');
                localStorage.setItem('skillverify_last_profile', {profile_json});
                localStorage.removeItem('skillverify_user_email');
                localStorage.removeItem('skillverify_is_logged_in');
                document.cookie = 'skillverify_last_profile=' + encodeURIComponent({profile_json}) + ';path=/;max-age=604800';
                document.cookie = 'skillverify_user_email=;path=/;max-age=0';
                document.cookie = 'skillverify_is_logged_in=;path=/;max-age=0';
            </script>
            """
            components.html(logout_js, height=0, width=0)
            st.rerun()
        
        user_package_tier, trial_countdown = init_user_and_get_plan(st.session_state.user_email)
        
        if "active_nav_mode" not in st.session_state:
            st.session_state.active_nav_mode = "🗣️ Skill Assessment Portal"

        workspace_options = [
            "🗣️ Skill Assessment Portal",
            "📊 Analytics Dashboard",
            "🌐 Explore Video Learning Engine",
            "📬 Submit Custom Prompts",
        ]
        if st.session_state.user_email.strip().lower() == "vihan220@gmail.com":
            workspace_options.append("🛡️ Admin Dashboard")

        app_mode = st.radio(
            "Select Portal Workspace:",
            workspace_options,
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
    if app_mode == "🗣️ Skill Assessment Portal":
        active_id = st.session_state.active_chat_id
        st.title(f"{st.session_state.all_chats[active_id]['title'] if active_id in st.session_state.all_chats else 'English Assessment Portal'}")
        
        if user_package_tier == "Trial":
            st.info(f"🆓 Free trial is active — **{trial_countdown} days left**")
            with st.expander("💳 Pay to Continue", expanded=False):
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

        # FIXED: Relocated voice control panel block out from structural exception scopes so it renders independently
        voice_control_html = """
        <div style='background: linear-gradient(135deg,#0f172a 0%,#111827 100%); padding:12px; border-radius:10px; border:1px solid rgba(255,255,255,0.04); margin-top: 15px;'>
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

        # Show last captured transcript visibly
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
                        allowed, _ = consume_ai_question(
                            user_package_tier, st.session_state.user_email
                        )
                        if allowed:
                            eval_reply = get_evaluator_response(user_package_tier)
                            current_chat["history"].append({"role": "assistant", "content": eval_reply})
                            st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
                            st.rerun()
                        else:
                            render_trial_ai_limit_notice()

        text_input = st.chat_input("Type your translation, essay answer, or session text here...", key="chat_input_terminal_field")
        if text_input:
            # Explicitly reset the transcript here so the boxed layout UI clears on manually typed entries
            st.session_state.last_speech_transcript = "" 
            allowed, _ = consume_ai_question(
                user_package_tier, st.session_state.user_email
            )
            if allowed:
                current_chat["history"].append({"role": "user", "content": text_input})
                eval_reply = get_evaluator_response(user_package_tier)
                current_chat["history"].append({"role": "assistant", "content": eval_reply})
                st.session_state.autoplay_audio_data = text_to_speech_bytes(eval_reply)
                st.rerun()
            else:
                render_trial_ai_limit_notice()

    elif app_mode == "📊 Analytics Dashboard":
        st.title("Linguistic Matrix Progress Tracker")
        metrics = st.session_state.performance_metrics
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Calculated Fluency Score", value=f"{metrics.get('fluency_score', 0.0)} / 10.0")
        with m_col2:
            st.metric(label="Grammar Slips Logged", value=int(metrics.get('grammar_errors_logged', 0)))

    elif app_mode == "🛡️ Admin Dashboard":
        st.title("Admin Dashboard")
        st.caption("Private account overview. Only the administrator can see this page.")

        if st.session_state.user_email.strip().lower() != "vihan220@gmail.com":
            st.error("This dashboard is available only to the administrator.")
        elif supabase_client is None:
            st.error("The registered-user information is not available right now.")
        else:
            try:
                user_rows = supabase_client.table("users").select("*").execute().data or []
                people_by_email = {
                    row.get("email", "").strip().lower(): row
                    for row in user_rows
                    if row.get("email")
                }
                learner_accounts = {
                    email: row
                    for email, row in people_by_email.items()
                    if email != "vihan220@gmail.com"
                }
                st.metric("Registered people", len(learner_accounts))
                st.caption("Your administrator account is not included in this count.")
                if st.button("Reset registered people", type="secondary", key="reset_test_accounts"):
                    test_emails = list(learner_accounts)
                    try:
                        for test_email in test_emails:
                            supabase_client.table("users").delete().eq(
                                "email", test_email
                            ).execute()
                        st.success("Registered people were reset. Your administrator account is not counted.")
                        st.rerun()
                    except Exception:
                        st.error("The test accounts could not be reset right now.")

                overview_rows = []
                today = date.today()
                for email, row in sorted(learner_accounts.items()):
                    plan = normalize_plan_name(row.get("user_plan", "Trial")) or "Trial"
                    expiry = row.get("plan_expiry_date", "")
                    status = "Paid pass"
                    if plan == "Trial":
                        status = "Free trial"
                    elif plan == "Expired":
                        status = "Expired"
                    elif expiry:
                        try:
                            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
                            if expiry_date < today:
                                status = "Expired"
                        except (TypeError, ValueError):
                            pass

                    overview_rows.append(
                        {
                            "Email": email,
                            "Access": status,
                            "Pass": plan,
                            "Pass / trial ends": expiry or "Not set",
                        }
                    )

                st.subheader("Registered accounts")
                if overview_rows:
                    st.dataframe(overview_rows, use_container_width=True, hide_index=True)
                else:
                    st.info("No registered accounts yet.")
            except Exception:
                st.error("The registered-user information is not available right now.")

    elif app_mode == "🌐 Explore Video Learning Engine":
        st.title("English Video Learning Library")
        st.caption("Only approved English lessons for the selected topic are available in this agent.")

        # Every playable video must be deliberately listed here. Do not accept URLs or
        # IDs from the browser, a query string, or an arbitrary user input.
        # Each topic uses an approved BBC Learning English lesson. Sessions open
        # different lesson segments, so learners do not receive the same session.
        def build_approved_sessions(start_number, topic_name, lesson):
            return {
                f"Session {number}: {topic_name} - Part {part}": {
                    **lesson,
                    "start_seconds": (part - 1) * 30,
                }
                for part, number in enumerate(range(start_number, start_number + 6), start=1)
            }

        subject_verb = {
            "video_id": "yY89V2jX36E",
            "topic_terms": ("subject", "verb", "agreement"),
            "approved_source": "bbc learning english",
        }
        schwa = {
            "video_id": "I0EGFlffmcY",
            "topic_terms": ("schwa", "speech"),
            "approved_source": "bbc learning english",
        }
        cycling = {
            "video_id": "hb1CBEENiPQ",
            "topic_terms": ("cycle",),
            "approved_source": "bbc learning english",
        }
        fluency = {
            "video_id": "LDkvRFCm8No",
            "topic_terms": ("speak", "fluently"),
            "approved_source": "bbc learning english",
        }
        reading = {
            "video_id": "h_pvijqmolQ",
            "topic_terms": ("read", "books"),
            "approved_source": "bbc learning english",
        }
        environment = {
            "video_id": "JXxnEhD-25Q",
            "topic_terms": ("environmental", "english"),
            "approved_source": "bbc learning english",
        }

        approved_english_library = {
            "Subject-Verb Agreement": build_approved_sessions(1, "Subject-Verb Agreement", subject_verb),
            "Agreement Rules": build_approved_sessions(7, "Agreement Rules", subject_verb),
            "Schwa Pronunciation": build_approved_sessions(13, "Schwa Pronunciation", schwa),
            "Fast Speech Listening": build_approved_sessions(19, "Fast Speech Listening", schwa),
            "Cycling Vocabulary": build_approved_sessions(25, "Cycling Vocabulary", cycling),
            "English Discussion Practice": build_approved_sessions(31, "English Discussion Practice", cycling),
            "Speaking Fluency": build_approved_sessions(37, "Speaking Fluency", fluency),
            "Conversation Confidence": build_approved_sessions(43, "Conversation Confidence", fluency),
            "Reading Vocabulary": build_approved_sessions(49, "Reading Vocabulary", reading),
            "Environmental English": build_approved_sessions(55, "Environmental English", environment),
        }

        selected_module = st.selectbox(
            "Choose an English learning area:",
            options=list(approved_english_library.keys()),
            key="english_learning_module_selector",
        )
        selected_session = st.selectbox(
            "Choose an approved lesson:",
            options=list(approved_english_library[selected_module].keys()),
            key="english_learning_session_selector",
        )
        lesson = approved_english_library[selected_module][selected_session]

        # A changed query parameter is an attempt to select a video outside this
        # English-only library. It is rejected before any player is rendered.
        requested_video_id = st.query_params.get("video", lesson["video_id"])
        if requested_video_id != lesson["video_id"]:
            st.error(
                "You cannot access this video because this is the English Agent. "
                "Only approved English-topic videos are available."
            )
        else:
            video_id = lesson["video_id"]
            watch_url = f"https://www.youtube.com/watch?v={video_id}"

            try:
                response = requests.get(
                    f"https://www.youtube.com/oembed?url={watch_url}&format=json",
                    timeout=6,
                )
                metadata = response.json() if response.status_code == 200 else {}
                video_title = metadata.get("title", "").lower()
                author_name = metadata.get("author_name", "").lower()
                is_english_source = lesson["approved_source"] in author_name
                is_related_to_topic = any(
                    term in video_title for term in lesson["topic_terms"]
                )

                if not (is_english_source and is_related_to_topic):
                    st.error(
                        "You cannot access this video because this is the English Agent. "
                        "Only approved English-topic videos are available."
                    )
                else:
                    embed_url = (
                        f"https://www.youtube-nocookie.com/embed/{video_id}"
                        f"?start={lesson['start_seconds']}&rel=0&modestbranding=1&disablekb=1"
                    )
                    st.markdown(f"### Now Playing: {selected_session}")
                    st.caption(f"English topic: {selected_module}")
                    components.iframe(embed_url, height=360, scrolling=False)
            except (requests.RequestException, ValueError):
                st.error(
                    "You cannot access this video because this is the English Agent. "
                    "Only approved English-topic videos are available."
                )

    elif app_mode == "📬 Submit Custom Prompts":
        st.title("Send a Question to the Admin")

        admin_email = "vihan220@gmail.com"
        current_email = st.session_state.user_email.strip().lower()
        is_admin = current_email == admin_email

        if supabase_client is None:
            st.error("Question prompt storage is not configured. Please contact the administrator.")
        elif is_admin:
            st.subheader("Admin Review")

            try:
                submissions = (
                    supabase_client.table("custom_prompt_submissions")
                    .select("*")
                    .order("created_at", desc=True)
                    .execute()
                    .data
                )
            except Exception:
                submissions = None

            if submissions is None:
                st.error("The question prompt review table is not ready yet.")
            elif not submissions:
                st.info("No learner question prompts are waiting for review.")
            else:
                for item in submissions:
                    submission_id = item["id"]
                    status = item.get("status", "pending")
                    with st.container(border=True):
                        st.markdown(
                            f"**{item.get('topic', 'English question')} - "
                            f"{item.get('difficulty', 'General')}**"
                        )
                        st.caption(
                            f"From {item.get('learner_email', 'Learner')} | "
                            f"Status: {status.title()}"
                        )
                        st.write(item.get("question", ""))

                        if status == "pending":
                            with st.form(f"admin_review_{submission_id}"):
                                personal_answer = st.text_area(
                                    "Your personal answer or message",
                                    key=f"admin_answer_{submission_id}",
                                    height=120,
                                )
                                approve_column, reject_column = st.columns(2)
                                with approve_column:
                                    approve = st.form_submit_button(
                                        "Approve and send answer",
                                        type="primary",
                                    )
                                with reject_column:
                                    reject = st.form_submit_button("Reject")

                            if approve:
                                if not personal_answer.strip():
                                    st.error("Write your personal answer before approving.")
                                else:
                                    supabase_client.table("custom_prompt_submissions").update(
                                        {
                                            "status": "approved",
                                            "admin_answer": personal_answer.strip(),
                                            "reviewed_at": datetime.utcnow().isoformat(),
                                        }
                                    ).eq("id", submission_id).execute()
                                    st.rerun()

                            if reject:
                                rejection_message = (
                                    personal_answer.strip()
                                    or "Your question prompt was rejected. Please send it again."
                                )
                                supabase_client.table("custom_prompt_submissions").update(
                                    {
                                        "status": "rejected",
                                        "admin_answer": rejection_message,
                                        "reviewed_at": datetime.utcnow().isoformat(),
                                    }
                                ).eq("id", submission_id).execute()
                                st.rerun()
                        elif status == "approved":
                            st.success("Approved and answered")
                            st.write(item.get("admin_answer", ""))
                        else:
                            st.error("Rejected")
                            st.write(item.get("admin_answer", ""))

        else:
            st.caption("Your question is private. Only the administrator can review it.")
            with st.form("learner_question_prompt_form", clear_on_submit=True):
                prompt_topic = st.selectbox(
                    "English topic",
                    [
                        "Grammar",
                        "Pronunciation",
                        "Vocabulary",
                        "Reading",
                        "Writing",
                        "Speaking",
                        "Listening",
                        "Business English",
                        "Interview Practice",
                    ],
                )
                prompt_level = st.selectbox(
                    "Difficulty level",
                    ["Beginner", "Intermediate", "Advanced"],
                )
                question = st.text_area(
                    "Your question prompt",
                    placeholder="Example: Please explain when I should use 'has' and 'have'.",
                    height=140,
                )
                send_question = st.form_submit_button("Send to admin", type="primary")

            if send_question:
                if not question.strip():
                    st.error("Write your question before sending it.")
                else:
                    try:
                        supabase_client.table("custom_prompt_submissions").insert(
                            {
                                "learner_email": current_email,
                                "topic": prompt_topic,
                                "difficulty": prompt_level,
                                "question": question.strip(),
                                "status": "pending",
                            }
                        ).execute()
                        st.success("Your question was sent to the admin for review.")
                    except Exception:
                        st.error("Your question could not be sent. Please try again later.")

            st.markdown("---")
            st.subheader("My Question Updates")
            if st.button("Check for new answers", key="refresh_question_updates"):
                st.rerun()

            try:
                my_submissions = (
                    supabase_client.table("custom_prompt_submissions")
                    .select("*")
                    .eq("learner_email", current_email)
                    .order("created_at", desc=True)
                    .execute()
                    .data
                )
            except Exception:
                my_submissions = []

            if not my_submissions:
                st.info("You have not sent any question prompts yet.")
            else:
                for item in my_submissions:
                    status = item.get("status", "pending")
                    with st.container(border=True):
                        st.write(item.get("question", ""))
                        if status == "pending":
                            st.info("Your question is waiting for admin review.")
                        elif status == "approved":
                            st.success("Your question was approved. Admin answer:")
                            st.write(item.get("admin_answer", ""))
                        else:
                            st.error(
                                item.get(
                                    "admin_answer",
                                    "Your question prompt was rejected. Please send it again.",
                                )
                            )
