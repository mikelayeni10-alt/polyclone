import streamlit as st
import google.generativeai as genai
import base64

# --- 1. SET YOUR API KEY HERE ---
GOOGLE_API_KEY = "AIzaSyDeyyPqwixP9TyuVXZ3Ay8lhEZwCGGWQAg"

# This connects your app to the Google AI Brain
genai.configure(api_key=GOOGLE_API_KEY)

# FIXED: Using the stable model name
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

# Basic styling
st.markdown("""
    <style>
    .stApp { background: #0f0c29; color: white; }
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Chat bubble styling */
    [data-testid="stChatMessage"] {
        border-radius: 20px; 
        border: 1px solid #9d50bb;
        background-color: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---

# CHAT SCREEN
if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot
    
    # DYNAMIC BACKGROUND INJECTION
    if bot.get('pic'):
        bin_str = base64.b64encode(bot['pic']).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(15, 12, 41, 0.8), rgba(15, 12, 41, 0.8)), url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.current_chat_bot = None
            st.session_state.messages = []
            st.rerun()
    with col2:
        st.title(f"{bot['name']}")

    # Display Chat History
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            msg_avatar = bot.get('pic', '🤖')
        else:
            msg_avatar = "👤"
            
        with st.chat_message(message["role"], avatar=msg_avatar):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input(f"Message {bot['name']}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar=bot.get('pic', '🤖')):
            try:
                history = []
                for m in st.session_state.messages[:-1]: 
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                chat_session = model.start_chat(history=history)
                full_prompt = f"(System: You are {bot['name']}. Persona: {bot['persona']}) {prompt}"
                
                response = chat_session.send_message(full_prompt)
                ai_text = response.text
                
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
            except Exception as e:
                st.error(f"Brain Error: {e}")

# MENU SCREEN
else:
    st.title("🤖 PolyClone")
    menu = st.segmented_control("Navigation", ["Explore", "My Bots", "Create"], default="Explore")
    st.divider()

    if menu == "Create":
        st.subheader("🎨 Create a New Character")
        name = st.text_input("Bot Name")
        
        # EMOJI SELECTOR REMOVED - ONLY FILE UPLOADER
        user_pic = st.file_uploader("Upload a Profile Picture / Background", type=['png', 'jpg', 'jpeg'])
        
        pers = st.text_area("Persona")
        
        if st.button("Save & Launch ✨", use_container_width=True):
            if name and pers:
                final_pic = None
                if user_pic:
                    final_pic = user_pic.getvalue()

                st.session_state.my_bots.append({
                    "name": name, 
                    "persona": pers, 
                    "pic": final_pic
                })
                st.balloons()
                st.success(f"{name} is added to your library!")

    elif menu == "My Bots":
        st.subheader("💬 Choose a Bot to Chat")
        if not st.session_state.my_bots:
            st.write("No bots yet. Go to 'Create' to make one!")
        
        for index, b in enumerate(st.session_state.my_bots):
            with st.container(border=True):
                col_a, col_b = st.columns([1, 4])
                with col_a:
                    if b.get('pic'):
                        st.image(b['pic'], width=60)
                    else:
                        st.header("🤖")
                with col_b:
                    st.subheader(b['name'])
                    if st.button(f"Chat with {b['name']}", key=f"btn_{index}"):
                        st.session_state.current_chat_bot = b
                        st.rerun()

    else:
        st.subheader("🔥 Trending Bots")
        st.info("Welcome to the PolyClone Beta. Use the tabs above to start creating your own AI characters!")
