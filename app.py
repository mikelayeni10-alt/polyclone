import streamlit as st
import google.generativeai as genai
import base64

# --- 1. CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyDeyyPqwixP9TyuVXZ3Ay8lhEZwCGGWQAg"
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-1.5-flash" 
model = genai.GenerativeModel(MODEL_NAME)

# --- 2. INITIALIZE MEMORY ---
if "my_bots" not in st.session_state:
    st.session_state.my_bots = []
if "current_chat_bot" not in st.session_state:
    st.session_state.current_chat_bot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Home"

# --- 3. PAGE SETUP & PREMIUM MOBILE STYLE ---
st.set_page_config(page_title="PolyClone", layout="wide", initial_sidebar_state="collapsed") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Global smooth feel */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #08080a;
        font-family: 'Inter', sans-serif;
        color: #f1f1f1;
    }
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}

    /* Top Search Bar Refinement */
    .search-container {
        position: sticky;
        top: 0;
        background: rgba(8, 8, 10, 0.8);
        backdrop-filter: blur(15px);
        padding: 20px 15px;
        z-index: 1000;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    div[data-testid="stTextInput"] input {
        background-color: #161618 !important;
        color: white !important;
        border-radius: 14px !important;
        border: 1px solid #28282b !important;
        padding: 12px !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #9d50bb !important;
        box-shadow: 0 0 10px rgba(157, 80, 187, 0.2) !important;
    }

    /* Premium Character Cards */
    .char-card {
        background: #121214;
        border-radius: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.05);
        overflow: hidden;
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .char-card:hover {
        transform: scale(1.02);
        border-color: rgba(157, 80, 187, 0.5);
    }
    
    .stImage > img {
        height: 240px;
        width: 100%;
        object-fit: cover;
        transition: filter 0.3s ease;
    }

    /* High-End Bottom Nav Bar */
    .nav-bar {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 85px;
        background: rgba(18, 18, 20, 0.95);
        backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex !important;
        justify-content: space-around !important;
        align-items: center !important;
        z-index: 100000;
        padding-bottom: 15px; /* Mobile safe area padding */
    }
    
    /* Nav Button Overrides */
    .stButton button {
        background: transparent !important;
        border: none !important;
        color: #888888 !important;
        font-weight: 600 !important;
        transition: color 0.3s ease;
    }
    .stButton button:hover, .stButton button:active {
        color: #ffffff !important;
    }

    /* Premium FAB (Center Button) */
    .fab-button button {
        background: #ffffff !important;
        color: #000000 !important;
        border-radius: 50% !important;
        width: 58px !important;
        height: 58px !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transform: translateY(-10px); /* Lift it above the nav bar line */
    }

    /* Hide default scrollbar for cleaner app feel */
    ::-webkit-scrollbar { width: 0px; background: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. POPUP FOR CREATION ---
@st.dialog("✨ Create Character")
def create_character():
    name = st.text_input("Name", placeholder="Character name...")
    user_pic = st.file_uploader("Upload Profile Image", type=['png', 'jpg', 'jpeg'])
    pers = st.text_area("Persona", placeholder="How do they act? (e.g., 'A witty AI assistant', 'A mysterious traveler')")
    
    if st.button("Initialize ✨", use_container_width=True):
        if name and pers and user_pic:
            st.session_state.my_bots.append({
                "name": name, "persona": pers, "pic": user_pic.getvalue()
            })
            st.success("Character Created!")
            st.rerun()
        else:
            st.error("Please fill all fields.")

# --- 5. APP LOGIC ---

# 1. CHAT INTERFACE
if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot
    st.markdown(f"### 💬 {bot['name']}")
    if st.button("⬅ Back to Home"):
        st.session_state.current_chat_bot = None
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Write something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat_session =
