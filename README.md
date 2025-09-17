# Qufy 🤖💬 - Your Personal PDF Chatbot

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://www.langchain.com/)

Qufy is a Streamlit web application that allows you to upload PDF documents and have interactive conversations about their content. Powered by local language models via Ollama and LangChain, it turns any PDF into a knowledgeable chatbot.

This application features a persistent, multi-chat interface, ensuring your conversations are saved locally and can be resumed at any time.

## 🚀 Demo

_(**Note**: It is highly recommended to replace the image above with a GIF showcasing the app's workflow: uploading a PDF, asking a question, switching between chats, and deleting a chat.)_

---

## ✨ Features

- **📄 PDF Upload & Processing**: Upload any PDF and have its content automatically processed for conversation.
- **💬 Interactive Chat Interface**: A user-friendly chat interface to ask questions and get answers.
- **💾 Persistent Chat Sessions**: All conversations, including the source PDF and message history, are saved locally. You can close the app and resume your chats later.
- **📚 Multi-Document Conversations**: Manage and switch between separate conversations for different documents using the sidebar.
- **🔒 Local & Private**: Runs entirely on your local machine using Ollama. Your documents and conversations never leave your computer.
- **🚀 Efficient & Fast**: Uses the FAISS vector store for fast and relevant context retrieval from your documents.

---

## 🛠️ Tech Stack

- **Framework**: Streamlit
- **LLM Orchestration**: LangChain
- **LLM & Embeddings**: Ollama (with models like `granite3.3` and `nomic-embed-text`)
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **UI/UX**: HTML/JavaScript for auto-scrolling

---

## ⚙️ Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Make sure you have the following installed on your system:

- **Python 3.8+**
- **Git**
- **Ollama**: You must have the [Ollama](https://ollama.com/) desktop application installed and running.

Once Ollama is running, pull the necessary models by running these commands in your terminal:

```bash
ollama pull granite3.3:2b
ollama pull nomic-embed-text
```

### Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/your-username/qufy-app.git](https://github.com/your-username/qufy-app.git)
    cd qufy-app
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🏃‍♀️ Usage

1.  **Start the Ollama Server**: Ensure the Ollama application is running in the background.

2.  **(Optional, for Docker Users)** If you are running this app inside a Docker container and Ollama on your host machine, make sure to configure Ollama to accept requests from other IPs:

    ```bash
    # On macOS/Linux
    export OLLAMA_HOST=0.0.0.0

    # On Windows (Command Prompt)
    set OLLAMA_HOST=0.0.0.0
    ```

    Then restart the Ollama server.

3.  **Run the Streamlit App**:

    ```bash
    streamlit run app.py
    ```

4.  **Open in Browser**: Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`). Upload your first PDF to begin a conversation!

---

## 📁 Project Structure

```
/
├── app.py              # Main Streamlit application script
├── chat_sessions/      # Directory for storing user chats (ignored by Git)
├── requirements.txt    # Python dependencies
├── .gitignore          # Files and folders to be ignored by Git
└── README.md           # You are here!
```

---
