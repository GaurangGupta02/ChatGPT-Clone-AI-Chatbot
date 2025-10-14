# ai_hub_app.py
import streamlit as st
import json
from datetime import datetime
import requests
import base64
import time
import re

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Chat + Vision (LLaVA)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CUSTOM CSS -----------------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #10a37f;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e5e5e5;
        padding: 10px 20px;
    }
    .chat-input-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }
    .upload-btn {
        background-color: #f5f5f5;
        border: 2px solid #e0e0e0;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 24px;
        text-align: center;
        line-height: 35px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    .upload-btn:hover {
        background-color: #e0e0e0;
        transform: scale(1.05);
    }
    .stop-btn {
        flex-shrink: 0;
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

OLLAMA_URL = "http://localhost:11434/api/generate"

# ----------------- STREAM RESPONSE (TEXT) -----------------
def stream_response(prompt, model="llava"):
    """Stream chat response from Ollama model."""
    try:
        url = OLLAMA_URL
        payload = {"model": model, "prompt": prompt, "stream": True}
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        full_response = ""
        placeholder = st.empty()
        last_update = time.time()

        for line in response.iter_lines(decode_unicode=True):
            if st.session_state.get("stop_generation", False):
                break
            if not line:
                continue
            try:
                data = json.loads(line)
                chunk = data.get("response", "")
                full_response += chunk
                if time.time() - last_update > 0.1:
                    placeholder.markdown(full_response)
                    last_update = time.time()
            except json.JSONDecodeError:
                pass

        placeholder.markdown(full_response)
        return full_response.strip() or "⚠️ No response from Ollama."
    except Exception as e:
        return f"⚠️ Error connecting to Ollama: {e}"

# ----------------- OCR FUNCTION -----------------
def extract_text_from_image_ollama(uploaded_file, model="llava"):
    """Use Ollama vision model to extract text from an image."""
    try:
        image_bytes = uploaded_file.getvalue()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "model": model,
            "prompt": (
                "You are an OCR assistant. Carefully read all visible text in this image "
                "and return ONLY the extracted text. Do not describe the image."
            ),
            "images": [image_b64],
            "stream": False
        }
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()

        try:
            data = r.json()
            return data.get("response", "").strip() or "⚠️ No text found in image."
        except json.JSONDecodeError:
            match = re.search(r'"response":"(.*?)"', r.text)
            if match:
                return match.group(1).replace("\\n", "\n").strip()
            return "⚠️ Could not parse OCR response."
    except Exception as e:
        return f"⚠️ Error: {e}"

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = 0
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llava"
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False
if "pending_response" not in st.session_state:
    st.session_state.pending_response = None

# ----------------- SIDEBAR -----------------
st.sidebar.title("⚙️ Settings")
st.sidebar.success(f"✅ Active Model: {st.session_state.selected_model}")

st.sidebar.markdown("---")
st.sidebar.title("💬 Chat History")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    if st.session_state.messages:
        chat_title = st.session_state.messages[0]["content"][:30]
        st.session_state.chat_history.append({
            "id": st.session_state.current_chat_id,
            "title": chat_title,
            "messages": st.session_state.messages.copy(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    st.session_state.messages = []
    st.session_state.current_chat_id += 1
    st.rerun()

if st.sidebar.button("🗑 Clear All History", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.messages = []
    st.session_state.pending_response = None
    st.rerun()

if st.session_state.chat_history:
    st.sidebar.subheader("Previous Chats")
    for chat in reversed(st.session_state.chat_history[-10:]):
        if st.sidebar.button(f"💬 {chat['title']}", key=f"chat_{chat['id']}", use_container_width=True):
            st.session_state.messages = chat["messages"].copy()
            st.session_state.pending_response = None
            st.rerun()

# ----------------- MAIN CHAT -----------------
st.markdown('<h1 class="main-header">ChatGPT-Clone</h1>', unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------- FILE UPLOADER ABOVE INPUT -----------------
st.markdown("<br>", unsafe_allow_html=True)
uploaded_image = st.file_uploader("📁 Upload an image (JPG, PNG)", type=["jpg", "jpeg", "png"], label_visibility="visible")

if uploaded_image is not None:
    with st.spinner("Extracting text using LLaVA Vision model..."):
        ocr_text = extract_text_from_image_ollama(uploaded_image, model=st.session_state.selected_model)
    st.success("✅ Text extracted successfully!")
    st.session_state.messages.append({"role": "user", "content": ocr_text})
    st.session_state.pending_response = None
    st.rerun()

# ----------------- CHAT INPUT + STOP BUTTON -----------------
col_input, col_stop = st.columns([9, 1])

with col_input:
    prompt = st.chat_input("Message your AI...")

with col_stop:
    stop_clicked = st.button("🛑", key="stop_btn", help="Stop generation", type="secondary")

if stop_clicked:
    st.session_state.stop_generation = True

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.stop_generation = False
    st.session_state.pending_response = None
    st.rerun()

# ----------------- HANDLE AI RESPONSE -----------------
if st.session_state.pending_response is None and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        with st.spinner(f"Thinking with {st.session_state.selected_model}..."):
            result = stream_response(user_prompt, model=st.session_state.selected_model)

        st.session_state.pending_response = result
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Chatbot powered by Ollama (LLaVA) • Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
