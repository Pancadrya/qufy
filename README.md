# Qufy 🤖💬 - Your Personal PDF Chatbot

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

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
- **Containerization**: Docker & Docker Compose

---

## ⚙️ Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Make sure you have the following installed on your system:

- **Python 3.8+** and **Git**
- **Ollama**: You must have the [Ollama](https://ollama.com/) desktop application installed and running.
- **Docker**: (Optional, for containerized setup) [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Once Ollama is running, pull the necessary models by running these commands in your terminal:

```bash
ollama pull granite3.3:2b
ollama pull nomic-embed-text
```

### Installation (Local)

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

## 🏃‍♀️ Usage (Local)

1.  **Start the Ollama Server**: Ensure the Ollama application is running in the background.
2.  **Run the Streamlit App**:
    ```bash
    streamlit run app.py
    ```
3.  **Open in Browser**: Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

---

## 🐳 Docker Usage

Using Docker is the recommended way to run this application as it creates a consistent and isolated environment.

### Why use Docker?

- **Consistency**: Avoids "it works on my machine" issues by packaging the app and its dependencies together.
- **Isolation**: The app's Python libraries won't conflict with other projects on your system.
- **Simplified Deployment**: Makes it easy to run the application anywhere Docker is installed.

### Recommended Method: Using Docker Compose

This is the easiest way to get started with Docker.

1.  **Create Files**: Make sure you have both a `Dockerfile` and a `docker-compose.yml` file in your project's root directory.

    **`Dockerfile`**

    ```Dockerfile
    FROM python:3.9-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8501
    ENV STREAMLIT_SERVER_PORT 8501
    ENV STREAMLIT_SERVER_ADDRESS 0.0.0.0
    CMD ["streamlit", "run", "app.py"]
    ```

    **`docker-compose.yml`**

    ```yaml
    version: "3.8"
    services:
      qufy-app:
        build: .
        container_name: qufy_app_container
        ports:
          - "8501:8501"
        volumes:
          - ./chat_sessions:/app/chat_sessions
    ```

2.  **Configure Ollama**: Ensure your Ollama server is configured to accept requests from Docker by setting `OLLAMA_HOST=0.0.0.0` before starting it. The application is already configured to connect to `http://host.docker.internal:11434`.

3.  **Build and Run**: Use this command whenever you change your code (`app.py`, `requirements.txt`, etc.). It will rebuild the image and start the container.

    ```bash
    docker-compose up --build
    ```

    To simply restart the application without rebuilding, you can use `docker-compose up`.

4.  **Stop the Application**: Press `Ctrl + C` in the terminal where it's running. To remove the container, you can run `docker-compose down`.

You can now access the application at `http://localhost:8501`.

---

## 📁 Project Structure

```
/
├── app.py                  # Main Streamlit application script
├── chat_sessions/          # Directory for storing user chats (ignored by Git)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Instructions for building the Docker image
├── docker-compose.yml      # Configuration for Docker Compose
├── .gitignore              # Files and folders to be ignored by Git
└── README.md               # You are here!
```

---

_This project is provided for educational and personal use. No official license is specified._
