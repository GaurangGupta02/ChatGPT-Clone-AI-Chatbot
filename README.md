# ChatGPT-Clone-AI-Chatbot
# 🤖 AI Hub App — Chat + Vision (LLaVA)

This project is a **Streamlit-based AI assistant** that combines **text-based chat** and **image understanding (OCR)** using the **LLaVA (Large Language and Vision Assistant)** model through **Ollama**.

It allows users to:
- Chat with an AI model locally via Ollama.
- Upload an image to extract text using the model’s vision capabilities.
- Maintain chat history with session management.
- Interact via a modern, responsive chat interface.

---

## 🌟 Features

- 🧠 **AI Chat Interface** — Interact with the LLaVA model directly from the browser.
- 🖼️ **Image Text Extraction (OCR)** — Upload images and automatically extract visible text.
- 💬 **Chat History** — View and manage previous conversations.
- 🛑 **Stop Generation** — Interrupt model responses in real time.
- ⚙️ **Custom UI Design** — Enhanced with CSS for a clean, modern look.
- 🚀 **Streamed Responses** — See answers generated in real-time.

---

## 🧩 Tech Stack

| Component | Description |
|------------|-------------|
| **Frontend/UI** | [Streamlit](https://streamlit.io) |
| **Backend Model** | [Ollama](https://ollama.ai) running **LLaVA** |
| **Language** | Python 3.9+ |
| **Libraries Used** | `streamlit`, `requests`, `json`, `base64`, `re`, `datetime`, `time` |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/GaurangGupta02/ChatGPT-Clone-AI-Chatbot.git
cd ai-hub-app
```

### 2. Install Dependencies
Make sure you have **Python 3.9+** installed.

```bash
pip install streamlit requests
```

### 3. Install and Run Ollama
You need to have **Ollama** installed and the **LLaVA model** available locally.

#### Install Ollama
Visit [Ollama’s official website](https://ollama.ai) to install.

#### Pull the LLaVA Model
```bash
ollama pull llava
```

#### Run Ollama Server
```bash
ollama serve
```

This starts Ollama’s local API at `http://localhost:11434`.

---

## ▶️ Run the App

Once Ollama is running, start the Streamlit app:

```bash
streamlit run ai_hub_app.py
```

Then open the link shown in the terminal (usually `http://localhost:8501`).

---

## 🧠 How It Works

1. **Chat Interface**  
   - Enter text in the chat input box.  
   - The app sends your prompt to Ollama’s LLaVA model using its API.  
   - Responses are streamed and displayed live.

2. **Image Upload (OCR)**  
   - Upload a `.jpg` or `.png` image.  
   - The app sends the base64-encoded image to LLaVA with an OCR prompt.  
   - Extracted text appears as a chat message, ready for further conversation.

3. **Chat History**  
   - Conversations are stored using Streamlit’s session state.  
   - You can start new chats or clear all history from the sidebar.

## 🧑‍💻 Author

**Gaurang Gupta**  
💼 GitHub:https://gith📧 Email: *(optional)*  

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use and modify it.

---

> ⚡ *“Chat with your AI and let it see the world — powered by LLaVA and Streamlit.”*
