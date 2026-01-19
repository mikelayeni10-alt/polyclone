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
    .char-card:hover {
        border-color: #9d50bb;
    }
    
    .stImage > img {
        border-radius: 12px 12px 0px 0px;
        object-fit: cover;
        height: 220px;
        width: 100%;
    }

    /* FAB Button */
    .bottom-button-container {
        position: fixed !important;
        bottom: 25px !important;
        left: 0 !important;
        right: 0 !important;
        display: flex !important;
        justify-content: center !important;
        z-index: 1000 !important;
        pointer-events: none !important;
    }
    .bottom-button-container button {
        pointer-events: auto !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        font-size: 32px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.8) !important;
        border: none !important;
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

if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot
    # Simplified chat navigation for clean look
    if st.button("⬅ Back"):
        st.session_state.current_chat_bot = None
        st.session_state.messages = []
        st.rerun()
    
    st.subheader(f"Chatting with {bot['name']}")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Say something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(f"(You are {bot['name']}. Persona: {bot['persona']}) {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

else:
    # 1. TOP SEARCH
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="🔍 Search characters...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. MAIN HUB
    st.title("For You")
    st.divider()

    # 3. CHARACTER GRID (2 per row)
    filtered_bots = [b for b in st.session_state.my_bots if search_query.lower() in b['name'].lower()]

    if not filtered_bots:
        st.info("Your library is empty. Click the button below to add a character!")
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

    # 4. BOTTOM CENTER FAB
    st.markdown('<div class="bottom-button-container">', unsafe_allow_html=True)
    if st.button("＋", key="fab_main"):
        create_character()
    st.markdown('</div>', unsafe_allow_html=True)
