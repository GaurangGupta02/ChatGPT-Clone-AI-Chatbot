# ai_hub_app.py
import streamlit as st
import json
from datetime import datetime
import requests
import base64
import time
import re
import subprocess
import sys
from PyPDF2 import PdfReader

# ----------------- AUTO-FIX FOR DOCX IMPORT -----------------
try:
    from docx import Document
except ModuleNotFoundError:
    st.warning("⚠️ Fixing docx import issue automatically...")
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "docx"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    from docx import Document

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Chat + Vision + Docs",
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
    /* Stop button styling */
    .stop-btn {
        flex-shrink: 0;
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold;
    }
    /* --- FILE UPLOADER STYLE CLEANUP --- */
    [data-testid="stFileUploader"] > section {
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] > section > div {
        display: none !important; /* Hides drag-drop text */
    }
    [data-testid="stFileUploader"] label {
        display: none !important; /* Hides label text */
    }
    [data-testid="stFileUploader"] div div div button {
        background-color: #10a37f !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 6px 12px !important;
        font-size: 14px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

OLLAMA_URL = "http://localhost:11434/api/generate"

# ----------------- STREAM RESPONSE -----------------
def stream_response(prompt, context_text="", model="llava"):
    """Stream chat response from Ollama model using optional context."""
    try:
        full_prompt = (
            f"Use the following document context to answer questions accurately:\n\n"
            f"{context_text}\n\n"
            f"User: {prompt}\n\nAssistant:"
        ) if context_text else prompt

        payload = {"model": model, "prompt": full_prompt, "stream": True}
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
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

# ----------------- FILE READING HELPERS -----------------
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text.strip() or ""
    except Exception as e:
        return f"⚠️ Error reading PDF: {e}"

def extract_text_from_docx(uploaded_file):
    try:
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs]).strip()
    except Exception as e:
        return f"⚠️ Error reading DOCX: {e}"

def extract_text_from_txt(uploaded_file):
    try:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"⚠️ Error reading TXT: {e}"

def extract_text_from_image_ollama(uploaded_file, model="llava"):
    """Use Ollama vision model to extract text from image."""
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
            return data.get("response", "").strip()
        except json.JSONDecodeError:
            return "⚠️ Could not parse OCR response."
    except Exception as e:
        return f"⚠️ Error: {e}"

# ----------------- SESSION STATE -----------------
defaults = {
    "messages": [],
    "chat_history": [],
    "current_chat_id": 0,
    "selected_model": "llava",
    "stop_generation": False,
    "pending_response": None,
    "file_context": "",
    "uploaded_files": []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
    st.session_state.file_context = ""
    st.session_state.uploaded_files = []
    st.rerun()

if st.sidebar.button("🗑 Clear All History", use_container_width=True):
    st.session_state.update({
        "chat_history": [],
        "messages": [],
        "pending_response": None,
        "file_context": "",
        "uploaded_files": []
    })
    st.rerun()

if st.session_state.chat_history:
    st.sidebar.subheader("🕘 Previous Chats")
    for chat in reversed(st.session_state.chat_history[-10:]):
        if st.sidebar.button(f"💬 {chat['title']}", key=f"chat_{chat['id']}", use_container_width=True):
            st.session_state.messages = chat["messages"].copy()
            st.session_state.pending_response = None
            st.session_state.file_context = ""
            st.rerun()

# ----------------- MAIN HEADER -----------------
st.markdown('<h1 class="main-header">ChatGPT-Clone 📚 </h1>', unsafe_allow_html=True)

# ----------------- CHAT DISPLAY -----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------- CHAT INPUT ROW -----------------
col_upload, col_input, col_stop = st.columns([1, 8, 1])

# Left: File upload (button only)
with col_upload:
    uploaded_files = st.file_uploader(
        "",
        type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

# Middle: Chat input
with col_input:
    prompt = st.chat_input("Message your AI...")

# Right: Stop button
with col_stop:
    stop_clicked = st.button("🛑", key="stop_btn", help="Stop generation", type="secondary")

# ----------------- FILE EXTRACTION -----------------
if uploaded_files:
    all_texts = []
    with st.spinner("Extracting text from uploaded files..."):
        for file in uploaded_files:
            if file.type == "application/pdf":
                text = extract_text_from_pdf(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text_from_docx(file)
            elif file.type.startswith("text/"):
                text = extract_text_from_txt(file)
            elif file.type.startswith("image/"):
                text = extract_text_from_image_ollama(file)
            else:
                text = "⚠️ Unsupported file format."
            all_texts.append(f"--- FILE: {file.name} ---\n{text}\n")

    st.session_state.file_context = "\n".join(all_texts)
    st.session_state.uploaded_files = [f.name for f in uploaded_files]
    st.toast(f"✅ Loaded {len(uploaded_files)} file(s): " + ", ".join(st.session_state.uploaded_files))

# ----------------- CHAT FUNCTIONALITY -----------------
if stop_clicked:
    st.session_state.stop_generation = True

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.stop_generation = False
    st.session_state.pending_response = None
    st.rerun()

if (
    st.session_state.pending_response is None
    and st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
):
    user_prompt = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner(f"Thinking with {st.session_state.selected_model}..."):
            result = stream_response(
                user_prompt,
                context_text=st.session_state.file_context,
                model=st.session_state.selected_model
            )
        st.session_state.pending_response = result
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Chatbot powered by Ollama (LLaVA) • Compact file upload button 📁 beside chat box 💬
    </div>
    """,
    unsafe_allow_html=True
)
