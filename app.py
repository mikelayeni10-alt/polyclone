import streamlit as st
import google.generativeai as genai
import base64

# --- 1. CONFIG ---
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# --- 2. STATE ---
if "my_bots" not in st.session_state:
    st.session_state.my_bots = []
if "current_chat_bot" not in st.session_state:
    st.session_state.current_chat_bot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "open_creator" not in st.session_state:
    st.session_state.open_creator = False

# --- 3. PAGE ---
st.set_page_config("PolyClone", layout="centered")

st.markdown("""
<style>
.stApp {
    background: #0f0c29;
    color: white;
}
header, footer { visibility: hidden; }

/* CHAT BUBBLES */
[data-testid="stChatMessage"] {
    border-radius: 15px;
    border: 1px solid #9d50bb;
    background-color: rgba(255,255,255,0.15);
    backdrop-filter: blur(6px);
}

/* FLOATING PLUS BUTTON */
#fab {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 58px;
    height: 58px;
    border-radius: 50%;
    background: white;
    color: black;
    font-size: 36px;
    border: none;
    cursor: pointer;
    z-index: 9999;
    box-shadow: 0 6px 20px rgba(0,0,0,0.6);
}
</style>

<button id="fab">+</button>

<script>
const fab = document.getElementById("fab");
fab.onclick = () => {
    window.parent.postMessage({ type: "OPEN_CREATOR" }, "*");
};
</script>
""", unsafe_allow_html=True)

# --- 4. MESSAGE BRIDGE ---
if st.session_state.get("_streamlit_message") == "OPEN_CREATOR":
    st.session_state.open_creator = True
    st.session_state["_streamlit_message"] = None

# --- 5. CREATOR DIALOG ---
@st.dialog("🎨 New Character")
def create_character():
    name = st.text_input("Name")
    image = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])
    persona = st.text_area("Persona / Instructions")

    if st.button("Save & Launch ✨", use_container_width=True):
        if name and image and persona:
            st.session_state.my_bots.append({
                "name": name,
                "persona": persona,
                "pic": image.getvalue()
            })
            st.session_state.open_creator = False
            st.rerun()
        else:
            st.error("Fill everything.")

if st.session_state.open_creator:
    create_character()

# --- 6. CHAT VIEW ---
if st.session_state.current_chat_bot:
    bot = st.session_state.current_chat_bot

    if bot.get("pic"):
        bg = base64.b64encode(bot["pic"]).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image:
            linear-gradient(rgba(15,12,41,.9), rgba(15,12,41,.9)),
            url("data:image/png;base64,{bg}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

    if st.button("⬅ Back"):
        st.session_state.current_chat_bot = None
        st.session_state.messages = []
        st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Say something..."):
        st.session_state.messages.append({"role":"user","content":prompt})

        history = [
            {"role": "user" if x["role"]=="user" else "model", "parts":[x["content"]]}
            for x in st.session_state.messages[:-1]
        ]

        chat = model.start_chat(history=history)
        res = chat.send_message(
            f"(System: You are {bot['name']}. Persona: {bot['persona']}) {prompt}"
        )

        st.session_state.messages.append({"role":"assistant","content":res.text})
        st.rerun()

# --- 7. MENU ---
else:
    st.title("🤖 PolyClone")

    for i, b in enumerate(st.session_state.my_bots):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1,3,1])
            with c1: st.image(b["pic"], width=50)
            with c2:
                st.write(f"**{b['name']}**")
                if st.button("Chat", key=f"chat{i}"):
                    st.session_state.current_chat_bot = b
                    st.rerun()
            with c3:
                if st.button("🗑", key=f"del{i}"):
                    st.session_state.my_bots.pop(i)
                    st.rerun()
