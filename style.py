import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        /* 1. Reset Global Font Family & Canvas Base */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            background-color: #f3f4f6 !important; /* Soft premium off-white base */
        }
        
        /* 2. Unified Background Overhaul */
        .stApp {
            background: radial-gradient(at 0% 0%, #f8fafc 0px, transparent 50%),
                        radial-gradient(at 50% 0%, #eff6ff 0px, transparent 50%),
                        radial-gradient(at 100% 100%, #f1f5f9 0px, transparent 50%) !important;
        }

        /* 3. Dark Mode Ultra-Premium Sidebar Control Pane */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important; /* Deep Slate Midnight */
            border-right: 1px solid #1e293b !important;
            box-shadow: 4px 0px 24px rgba(15, 23, 42, 0.15) !important;
        }
        
        /* Force Sidebar Typography Visibility */
        [data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }
        
        /* Style Sidebar Radio Targets Selectors */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            padding: 10px 14px !important;
            border-radius: 10px !important;
            margin-bottom: 8px !important;
            transition: all 0.25s ease-in-out !important;
        }
        
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            border-color: #3b82f6 !important;
            background: #273549 !important;
        }
        
        /* Active Radio Accent Indicator */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
            border-color: #60a5fa !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }

        /* 4. Main Section Typography Design */
        h1 {
            font-weight: 700 !important;
            color: #0f172a !important;
            letter-spacing: -0.04em !important;
            background: linear-gradient(135deg, #0f172a 30%, #2563eb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px !important;
        }

        /* 5. Fluid Responsive Dashboard Cards */
        .skill-card {
            background: #ffffff !important;
            padding: 24px !important;
            border-radius: 16px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.02), 0 8px 10px -6px rgba(0, 0, 0, 0.02) !important;
            margin-bottom: 16px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .skill-card:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.03) !important;
            border-color: #cbd5e1 !important;
        }
        
        .skill-title {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: #1e293b !important;
            margin-bottom: 8px !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }
        
        .skill-desc {
            font-size: 0
