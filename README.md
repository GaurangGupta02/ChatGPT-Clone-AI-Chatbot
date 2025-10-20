# 🤖 ChatGPT-Clone-AI-Chatbot

This project is an advanced **Streamlit-based AI assistant** that unifies **text chat**, **document understanding**, and **image OCR** in a single interface using **LLaVA** through **Ollama**.

It allows users to:

* Chat with a local AI model (via Ollama).
* Upload multiple files (PDF, DOCX, TXT, or Images).
* Extract and use file content as chat context.
* Stream live responses with the ability to stop generation.
* Keep and revisit chat history — all inside the browser.

---

## 🌟 Features

* 💬 **AI Chat Interface** — Interact with LLaVA directly in Streamlit.
* 📁 **Multi-File Upload Support** — Upload PDFs, DOCX, TXT, and image files.
* 🧠 **Document-Aware Responses** — The model uses uploaded document text as context to answer user queries.
* 🖼️ **Image OCR Integration** — Reads visible text from uploaded images using vision capabilities.
* 🔁 **Chat History & Session Management** — View, save, and clear past conversations.
* 🛑 **Stop Generation Button** — Halt model output in real-time.
* 🧰 **Automatic DOCX Fix** — Self-corrects missing `python-docx` dependency if needed.
* ⚙️ **Polished UI** — Modern, responsive design with styled upload buttons and layout.
* ⚡ **Streamed Responses** — Watch AI output generate live as it’s produced.

---

## 🧩 Tech Stack

| Component          | Description                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------------- |
| **Frontend/UI**    | [Streamlit](https://streamlit.io)                                                            |
| **Backend Model**  | [Ollama](https://ollama.ai) running **LLaVA**                                                |
| **Language**       | Python 3.9+                                                                                  |
| **Libraries Used** | `streamlit`, `requests`, `json`, `base64`, `re`, `time`, `datetime`, `PyPDF2`, `python-docx` |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/GaurangGupta02/ChatGPT-Clone-AI-Chatbot.git
cd ChatGPT-Clone-AI-Chatbot
```

### 2. Install Dependencies

Make sure you have **Python 3.9+** installed.

```bash
pip install streamlit requests PyPDF2 python-docx
```

### 3. Install and Run Ollama

Install Ollama from its official website:
👉 [https://ollama.ai](https://ollama.ai)

Pull the **LLaVA** model:

```bash
ollama pull llava
```

Then run Ollama’s local server:

```bash
ollama serve
```

This launches a local API at:
`http://localhost:11434`

---

## ▶️ Run the App

With Ollama running, start the Streamlit app:

```bash
streamlit run ai_hub_app.py
```

You’ll see the app running at:
`http://localhost:8501`

---

## 🧠 How It Works

1. **Chat Interface**

   * Type a message in the chat input.
   * The message is sent to the LLaVA model via Ollama’s API.
   * Responses are streamed back in real-time.

2. **File Upload (Docs + Images)**

   * Upload any combination of `.pdf`, `.docx`, `.txt`, `.jpg`, `.jpeg`, or `.png` files.
   * The app extracts text automatically using PDF/DOCX readers or OCR for images.
   * Extracted content becomes **context** for subsequent chat queries.

3. **Chat History**

   * Session state saves recent conversations.
   * Start a new chat or revisit old ones from the sidebar.
   * Clear all history when needed.

4. **Stop Generation**

   * Instantly stop AI response generation mid-stream via the 🛑 button.

---

## 🧑‍💻 Author

**Gaurang Gupta**
📦 GitHub: [GaurangGupta02](https://github.com/GaurangGupta02)

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

> ⚡ *“Chat with your AI, read your files, and see your world — powered by LLaVA and Streamlit.”*
