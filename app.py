import streamlit as st
import google.generativeai as genai
import base64

# --- 1. CONFIGURATION ---
# Note: Keep your API key private in a real production environment!
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
st.set_page_config(page_title="PolyClone", layout="centered")

st.markdown("""
    <style>
    .stApp { background: #0f0c29; color: white; }
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    /* Chat bubble styling */
    [data-testid="stChatMessage"] {
        border-radius: 15px; 
        border: 1px solid #9d50bb;
        background-color: rgba(255, 255, 255, 0.15);
        # backdrop-filter: blur(5px);
        margin-bottom: 10px;
    }

    /* FIXED CENTER BOTTOM FAB CONTAINER */
    .fab-wrapper {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999;
    }

    /* Style the actual Streamlit button inside the FAB wrapper */
    div.stButton > button {
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        background-color: white !important;
        color: black !important;
        border: 2px solid #9d50bb !important;
        font-size: 30px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
        transition: transform 0.2s;
    }
    
    div.stButton > button:hover {
        transform: scale(1.1);
        background-color: #f0f0f0 !important;
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
                "name": name, 
                "persona": pers, 
                "pic": user_pic.getvalue()
            })
            st.rerun()
        else:
            st.error("Fill in all fields and upload an image!")

# --- 5. APP LOGIC ---

# CHAT SCREEN
if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot
    
    # Background logic
    if bot.get('pic'):
        bin_str = base64.b64encode(bot['pic']).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(15, 12, 41, 0.85), rgba(15, 12, 41, 0.85)), url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("⬅️"):
            st.session_state.current_chat_bot = None
            st.session_state.messages = []
            st.rerun()
    with c2:
        st.write(f"### {bot['name']}")
    with c3:
        if st.button("🧹"):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        msg_avatar = bot.get('pic') if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=msg_avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Chat with {bot['name']}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar=bot.get('pic')):
            try:
                history = []
                for m in st.session_state.messages[:-1]: 
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                chat_session = model.start_chat(history=history)
                full_prompt = f"(System: You are {bot['name']}. Persona: {bot['persona']}) {prompt}"
                response = chat_session.send_message(full_prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

# MENU SCREEN
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
                with col_img:
                    st.image(b['pic'], width=50)
