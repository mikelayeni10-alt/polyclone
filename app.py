import streamlit as st
import google.generativeai as genai
import base64

# --- 1. CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyDeyyPqwixP9TyuVXZ3Ay8lhEZwCGGWQAg"
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-2.5-flash" 
model = genai.GenerativeModel(MODEL_NAME)

# --- 2. INITIALIZE MEMORY ---
if "my_bots" not in st.session_state:
    st.session_state.my_bots = []
if "current_chat_bot" not in st.session_state:
    st.session_state.current_chat_bot = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. PAGE SETUP & STYLE ---
st.set_page_config(page_title="PolyClone", layout="centered")

st.markdown("""
    <style>
    .stApp { background: #0f0c29; color: white; }
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    /* THE FIX: Force the container to the very bottom of the viewport */
    .bottom-button-container {
        position: fixed !important;
        bottom: 20px !important;
        left: 0 !important;
        right: 0 !important;
        display: flex !important;
        justify-content: center !important;
        z-index: 1000000 !important;
        pointer-events: none !important;
    }

    .bottom-button-container button {
        pointer-events: auto !important;
        background-color: white !important;
        color: black !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        font-size: 30px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5) !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding-bottom: 4px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. POPUP FOR CREATION ---
@st.dialog("🎨 New Character")
def create_character():
    name = st.text_input("Name")
    user_pic = st.file_uploader("Upload Image (Required)", type=['png', 'jpg', 'jpeg'])
    pers = st.text_area("Persona / Instructions")
    
    if st.button("Save & Launch ✨", use_container_width=True):
        if name and pers and user_pic:
            st.session_state.my_bots.append({
                "name": name, "persona": pers, "pic": user_pic.getvalue()
            })
            st.rerun()
        else:
            st.error("Fill in all fields!")

# --- 5. APP LOGIC ---

if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot
    if bot.get('pic'):
        bin_str = base64.b64encode(bot['pic']).decode()
        st.markdown(f"<style>.stApp {{background-image: linear-gradient(rgba(15, 12, 41, 0.85), rgba(15, 12, 41, 0.85)), url('data:image/png;base64,{bin_str}'); background-size: cover; background-attachment: fixed;}}</style>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("⬅️"):
            st.session_state.current_chat_bot = None
            st.session_state.messages = []
            st.rerun()
    with c2: st.write(f"### {bot['name']}")
    with c3:
        if st.button("🧹"):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=bot.get('pic') if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Chat with {bot['name']}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        with st.chat_message("assistant", avatar=bot.get('pic')):
            try:
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(f"(System: You are {bot['name']}. Persona: {bot['persona']}) {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e: st.error(f"Error: {e}")

else:
    st.title("🤖 PolyClone")
    menu = st.segmented_control("Navigation", ["Explore", "My Bots"], default="My Bots")
    st.divider()

    if menu == "My Bots":
        if not st.session_state.my_bots:
            st.info("No bots found. Tap the + to create one!")
        for index, b in enumerate(st.session_state.my_bots):
            with st.container(border=True):
                col_img, col_txt, col_del = st.columns([1, 3, 1])
                with col_img: st.image(b['pic'], width=50)
                with col_txt:
                    st.write(f"**{b['name']}**")
                    if st.button(f"Chat", key=f"chat_{index}"):
                        st.session_state.current_chat_bot = b
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{index}"):
                        st.session_state.my_bots.pop(index)
                        st.rerun()
    
    # THE FLOATING BUTTON AT THE VERY BOTTOM GLASS
    st.markdown('<div class="bottom-button-container">', unsafe_allow_html=True)
    if st.button("＋", key="fixed_plus_btn"):
        create_character()
    st.markdown('</div>', unsafe_allow_html=True)
