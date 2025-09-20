# Qufy 🤖💬 - Chat with Your Documents

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

Qufy is an interactive web application that allows you to "talk" to your PDF documents. Upload a file, and start asking questions about its content. The entire Q&A process is powered by a Large Language Model (LLM) running 100% in your local environment via Ollama, ensuring privacy and complete control over your data.

## ✨ Key Features

- **📤 PDF Document Upload:** A simple and intuitive interface to quickly upload and process PDF files.
- **💬 Chat-Based Interaction:** Ask questions in natural language and receive contextual answers extracted directly from the document's content.
- **👥 Multi-User Support:** Features a registration and login system, allowing each user to have their own separate workspace and conversation history.
- **📚 Chat History:** Every chat session is saved, enabling you to return and continue your discussions at any time.
- **🔒 Privacy Guaranteed:** With the AI model running entirely locally via Ollama, none of your data or documents are ever sent to a third-party server.

## 📺 Demo

Check out a quick demo of Qufy in action!

![ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/207aee12-3b16-4fe9-a32a-cb32b2afe73a)

---

## 🏗️ Architecture and Tech Stack

This application is designed with a modern approach that prioritizes privacy, scalability, and ease of deployment.

**Architecture Explained:**

The Streamlit application (frontend & backend) and the PostgreSQL database run within isolated Docker containers. To perform AI inference, the application container communicates directly with the Ollama instance running on the host machine (your laptop). This architecture ensures that document data remains within the container and is not exposed, while the intensive AI processing leverages the host machine's resources (GPU).

**Tech Stack:**

- **Frontend:** **Streamlit**
- **Backend & AI Orchestration:** **Python**, **LangChain**, **langchain-community**
- **Database:** **PostgreSQL** with the **pgvector** extension (for storing embeddings and user data)
- **Infrastructure:** **Docker** & **Docker Compose**
- **Inference Engine (Local):** **Ollama**
- **AI Model (Inference):** `ibm-granite-code:3b`
- **Key Dependencies:** `pypdf`, `faiss-cpu` (used in the initial prototype), `sqlalchemy`, `psycopg2-binary`, `bcrypt`, `python-dotenv`, `streamlit-javascript`.

---

## 🚀 Getting Started

Follow these steps to run Qufy in your local environment.

### Prerequisites

Ensure you have the following installed on your system:

- [Git](https://git-scm.com/)
- [Docker & Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/)
- **A GPU with adequate VRAM** is highly recommended for fast Ollama inference performance.

### Installation Steps

1.  **Clone the Repository**
    Open your terminal and run the following command:

    ```bash
    git clone [https://github.com/YOUR-USERNAME/qufy.git](https://github.com/YOUR-USERNAME/qufy.git)
    ```

2.  **Navigate to the Project Directory**

    ```bash
    cd qufy
    ```

3.  **Download the AI Model via Ollama**
    Make sure the Ollama application is running in the background. Then, pull the required model:

    ```bash
    ollama pull ibm-granite-code:2b
    ```

4.  **Configure the Environment**
    Copy the example configuration file to a new environment file.

    ```bash
    cp .env.example .env
    ```

    Open the `.env` file and adjust the values if necessary.

5.  **Build and Run the Containers**
    Use Docker Compose to build the images and run all services.

    ```bash
    docker-compose up --build -d
    ```

    The `-d` flag will run the containers in detached mode (in the background).

6.  **Access the Application**
    Once the containers are running successfully, open your web browser and navigate to:
    **[http://localhost:8501](http://localhost:8501)**

---

## 📖 The Development Journey

The Qufy project was born from a simple question: how can a useful AI application be built in a short amount of time?

The journey began with a brainstorming session with **Google Gemini** to explore interesting and quickly implementable project ideas. The result was a "Chat with Your Document" application.

**An initial prototype was successfully built in just one day.** This version had the core functionality: uploading a PDF and performing Q&A. To store chat history and embeddings, this prototype used **FAISS**, saving the indexes directly to the local filesystem.

Sensing the prototype's potential, development continued for another **3-4 days** to overcome various challenges and add more advanced features. The main evolutions during this phase included:

- **Database Migration:** Transitioning from file-based storage (FAISS) to a more robust and scalable **PostgreSQL database with pgvector**.
- **Multi-User Functionality:** Implementing a registration and authentication system to manage different users.
- **UI/UX Improvements:** Refining the user interface for a better overall experience.

This story shows how a simple idea can evolve into a more mature and functional application through an iterative process and the adoption of the right technologies.

---

## 🤖 AI Collaboration

This project is a true testament to the power of human-AI collaboration. Various AI models played crucial roles in every stage of development.

- **Development Assistant:**
  A combination of **Google Gemini 2.5 Pro**, **GPT-4o Mini**, and **IBM Granite 3.3 2B** served as coding assistants. They helped write code, debug errors, provide ideas for the application's structure, and even design UI components.

- **Application Inference Engine:**
  The **IBM Granite 3.3 2B** model, run via **Ollama**, became the "brain" behind Qufy's chat functionality. This model is responsible for understanding user questions and finding relevant answers within the documents.

**Reflection:**
This experience confirms that AI is a tremendous accelerator in software development. However, it is not a magic bullet. The process required **prompt engineering skills** to get the desired outputs, **critical validation** to check the correctness of the generated code, and **manual optimization** to ensure the application runs efficiently. AI is a powerful partner, not a replacement for a developer's expertise.
