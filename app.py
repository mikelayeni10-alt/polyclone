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
st.set_page_config(page_title="PolyClone", layout="wide") # Changed to wide for grid view

st.markdown("""
    <style>
    /* Main Theme */
    .stApp { background-color: #0a0a0b; color: #ffffff; }
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}

    /* Sticky Header & Search Bar */
    .search-container {
        position: sticky;
        top: 0;
        background-color: #0a0a0b;
        padding: 10px 0px;
        z-index: 99;
    }
    
    div[data-testid="stTextInput"] input {
        background-color: #1c1c1e;
        color: white;
        border-radius: 20px;
        border: 1px solid #3a3a3c;
        padding-left: 15px;
    }

    /* Character Card Styling */
    .char-card {
        background-color: #1c1c1e;
        border-radius: 12px;
        padding: 0px;
        margin-bottom: 20px;
        border: 1px solid #2c2c2e;
        overflow: hidden;
        transition: transform 0.2s;
    }
    .char-card:hover {
        transform: translateY(-5px);
        border-color: #9d50bb;
    }
    
    /* Image sizing for the grid */
    .stImage > img {
        border-radius: 12px 12px 0px 0px;
        object-fit: cover;
        height: 200px;
        width: 100%;
    }

    /* Floating Button (Centered Bottom) */
    .bottom-button-container {
        position: fixed !important;
        bottom: 20px !important;
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
        width: 55px !important;
        height: 55px !important;
        font-size: 30px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.8) !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. POPUP FOR CREATION ---
@st.dialog("🎨 Create New Character")
def create_character():
    name = st.text_input("Character Name")
    user_pic = st.file_uploader("Upload Avatar", type=['png', 'jpg', 'jpeg'])
    pers = st.text_area("Persona/Description", placeholder="How should they talk?")
    
    if st.button("Create ✨", use_container_width=True):
        if name and pers and user_pic:
            st.session_state.my_bots.append({
                "name": name, "persona": pers, "pic": user_pic.getvalue()
            })
            st.rerun()
        else:
            st.error("Please provide a name, image, and persona.")

# --- 5. APP LOGIC ---

# CHAT SCREEN
if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot
    # (Chat logic remains the same for functionality)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("Back"):
            st.session_state.current_chat_bot = None
            st.session_state.messages = []
            st.rerun()
    with c2: st.subheader(bot['name'])
    
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

# HOME SCREEN (The Hub)
else:
    # 1. SEARCH HEADER
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="🔍 Search Characters...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. BANNER & TABS
    st.title("For You")
    tabs = st.segmented_control("Categories", ["All", "Anime", "Realistic", "Horror", "OC"], default="All")
    st.divider()

    # 3. CHARACTER GRID
    filtered_bots = [b for b in st.session_state.my_bots if search_query.lower() in b['name'].lower()]

    if not filtered_bots:
        st.info("No characters found. Use the + button to create your first one!")
    else:
        # Create 2 columns for a mobile-friendly grid
        cols = st.columns(2) 
        for i, bot in enumerate(filtered_bots):
            with cols[i % 2]:
                st.markdown('<div class="char-card">', unsafe_allow_html=True)
                st.image(bot['pic'], use_container_width=True)
                st.markdown(f"<div style='padding:10px;'><b>{bot['name']}</b></div>", unsafe_allow_html=True)
                if st.button(f"Chat with {bot['name']}", key=f"btn_{i}", use_container_width=True):
                    st.session_state.current_chat_bot = bot
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # 4. CENTERED FLOATING ACTION BUTTON
    st.markdown('<div class="bottom-button-container">', unsafe_allow_html=True)
    if st.button("＋", key="fab_main"):
        create_character()
    st.markdown('</div>', unsafe_allow_html=True)
