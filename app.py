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

# --- 3. PAGE SETUP & HIGH-END MOBILE CSS ---
st.set_page_config(page_title="PolyClone", layout="wide", initial_sidebar_state="collapsed") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #08080a;
        font-family: 'Inter', sans-serif;
        color: #f1f1f1;
    }
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}

    /* Sticky Top Search Header */
    .search-container {
        position: sticky;
        top: 0;
        background: rgba(8, 8, 10, 0.9);
        backdrop-filter: blur(20px);
        padding: 15px;
        z-index: 1000;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    div[data-testid="stTextInput"] input {
        background-color: #161618 !important;
        border-radius: 12px !important;
        border: 1px solid #28282b !important;
    }

    /* Modern Character Cards */
    .char-card {
        background: #121214;
        border-radius: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.05);
        overflow: hidden;
    }
    
    .stImage > img {
        height: 220px;
        width: 100%;
        object-fit: cover;
    }

    /* THE NEW MOBILE BOTTOM NAV BAR */
    .nav-bar-container {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 80px;
        background: rgba(18, 18, 20, 0.98);
        backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 100000;
        padding: 0 20px 10px 20px;
    }
    
    /* Plus Button Style */
    .create-fab button {
        background: #ffffff !important;
        color: #000000 !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        font-size: 30px !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;
        transform: translateY(-15px);
        border: none !important;
    }

    /* Tab Buttons Style */
    .tab-btn button {
        background: transparent !important;
        border: none !important;
        color: #888888 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding-top: 10px !important;
    }
    .active-tab button {
        color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
        border-radius: 0 !important;
    }

    /* Remove scrollbars */
    ::-webkit-scrollbar { width: 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. POPUP FOR CREATION ---
@st.dialog("✨ New Character")
def create_character():
    name = st.text_input("Name")
    user_pic = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    pers = st.text_area("Persona")
    
    if st.button("Create ✨", use_container_width=True):
        if name and pers and user_pic:
            st.session_state.my_bots.append({
                "name": name, "persona": pers, "pic": user_pic.getvalue()
            })
            st.rerun()

# --- 5. APP LOGIC ---

if st.session_state.current_chat_bot:
    # --- CHAT VIEW ---
    bot = st.session_state.current_chat_bot
    st.markdown(f"### 💬 {bot['name']}")
    if st.button("⬅ Back"):
        st.session_state.current_chat_bot = None
        st.session_state.messages = []
        st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(f"(You are {bot['name']}. Persona: {bot['persona']}) {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

else:
    # --- HUB VIEW ---
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="🔍 Search characters...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.active_tab == "Home":
        st.title("Discover")
        filtered_bots = [b for b in st.session_state.my_bots if search_query.lower() in b['name'].lower()]
        if not filtered_bots:
            st.info("No characters yet. Tap '+' to create.")
        else:
            cols = st.columns(2) 
            for i, bot in enumerate(filtered_bots):
                with cols[i % 2]:
                    st.markdown('<div class="char-card">', unsafe_allow_html=True)
                    st.image(bot['pic'], use_container_width=True)
                    st.markdown(f"<div style='padding:12px; font-weight:600;'>{bot['name']}</div>", unsafe_allow_html=True)
                    if st.button(f"Chat", key=f"chat_{i}", use_container_width=True):
                        st.session_state.current_chat_bot = bot
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.active_tab == "Chats":
        st.title("My Chats")
        for i, bot in enumerate(st.session_state.my_bots):
            with st.container():
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1: st.image(bot['pic'], width=50)
                with c2: st.markdown(f"**{bot['name']}**")
                with c3:
                    if st.button("Open", key=f"open_{i}"):
                        st.session_state.current_chat_bot = bot
                        st.rerun()
                st.divider()

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

    # --- UPDATED BOTTOM NAV BAR (HOME & CHATS NEXT TO EACH OTHER) ---
    st.markdown('<div class="nav-bar-container">', unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns([1.5, 1.5, 1, 3]) # Adjusting spacing
    
    with n1:
        st.markdown(f'<div class="tab-btn {"active-tab" if st.session_state.active_tab == "Home" else ""}">', unsafe_allow_html=True)
        if st.button("HOME", key="tab_h"):
            st.session_state.active_tab = "Home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with n2:
        st.markdown(f'<div class="tab-btn {"active-tab" if st.session_state.active_tab == "Chats" else ""}">', unsafe_allow_html=True)
        if st.button("CHATS", key="tab_c"):
            st.session_state.active_tab = "Chats"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with n3:
        # Pushes the plus button to the right side
        st.write("")

    with n4:
        st.markdown('<div class="create-fab">', unsafe_allow_html=True)
        if st.button("＋", key="fab_plus"):
            create_character()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
