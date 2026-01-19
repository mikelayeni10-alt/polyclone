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

# --- 3. PAGE SETUP & STYLE ---
st.set_page_config(page_title="PolyClone", layout="wide") 

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0b; color: #ffffff; }
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}

    /* Sticky Search Header */
    .search-container {
        position: sticky;
        top: 0;
        background-color: #0a0a0b;
        padding: 15px 0px;
        z-index: 99;
    }
    
    div[data-testid="stTextInput"] input {
        background-color: #1c1c1e;
        color: white;
        border-radius: 20px;
        border: 1px solid #3a3a3c;
    }

    /* Character Card Grid */
    .char-card {
        background-color: #1c1c1e;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #2c2c2e;
        overflow: hidden;
        transition: 0.3s;
    }
    .char-card:hover { border-color: #9d50bb; }
    
    .stImage > img {
        border-radius: 12px 12px 0px 0px;
        object-fit: cover;
        height: 220px;
        width: 100%;
    }

    /* BOTTOM NAVIGATION BAR */
    .nav-wrapper {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background-color: #1c1c1e;
        border-top: 1px solid #2c2c2e;
        display: flex !important;
        justify-content: space-around !important;
        align-items: center !important;
        padding: 10px 0px !important;
        z-index: 1000000 !important;
    }
    
    /* Style for Nav Buttons */
    .stButton button { width: 100% !important; border: none !important; background: transparent !important; color: white !important; }
    
    /* Specific Plus Button Styling */
    .plus-btn button {
        background-color: white !important;
        color: black !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 28px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. POPUP FOR CREATION ---
@st.dialog("🎨 New Character")
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
        else:
            st.error("Missing info!")

# --- 5. APP LOGIC ---

# 1. CHAT INTERFACE (When a bot is selected)
if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot
    if st.button("⬅ Back"):
        st.session_state.current_chat_bot = None
        st.session_state.messages = []
        st.rerun()
    
    st.subheader(f"Chat with {bot['name']}")
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

# 2. MAIN VIEWS (Home or Chats list)
else:
    # Top Search
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="🔍 Search characters...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.active_tab == "Home":
        st.title("For You")
        st.divider()
        # This acts as the "Discover" feed
        filtered_bots = [b for b in st.session_state.my_bots if search_query.lower() in b['name'].lower()]
        
        if not filtered_bots:
            st.info("No characters found. Create one to get started!")
        else:
            cols = st.columns(2) 
            for i, bot in enumerate(filtered_bots):
                with cols[i % 2]:
                    st.markdown('<div class="char-card">', unsafe_allow_html=True)
                    st.image(bot['pic'], use_container_width=True)
                    st.markdown(f"<div style='padding:12px;'><b>{bot['name']}</b></div>", unsafe_allow_html=True)
                    if st.button(f"Chat", key=f"btn_{i}", use_container_width=True):
                        st.session_state.current_chat_bot = bot
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.active_tab == "Chats":
        st.title("My Chats")
        st.divider()
        # List view for existing characters you've talked to
        if not st.session_state.my_bots:
            st.info("No active chats yet.")
        else:
            for i, bot in enumerate(st.session_state.my_bots):
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    with c1: st.image(bot['pic'], width=60)
                    with c2:
                        st.write(f"**{bot['name']}**")
                        if st.button("Open Chat", key=f"open_{i}"):
                            st.session_state.current_chat_bot = bot
                            st.rerun()

    # 3. BOTTOM NAV BAR
    st.markdown('<div class="nav-wrapper">', unsafe_allow_html=True)
    nb_col1, nb_col2, nb_col3 = st.columns(3)
    
    with nb_col1:
        if st.button("🏠 Home"):
            st.session_state.active_tab = "Home"
            st.rerun()
    
    with nb_col2:
        st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
        if st.button("＋", key="nav_create"):
            create_character()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with nb_col3:
        if st.button("💬 Chats"):
            st.session_state.active_tab = "Chats"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
