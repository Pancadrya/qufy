# app.py
import streamlit as st
import tempfile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.llms import Ollama

# Import modules from src folder
from src import ui, auth, database
from src.models import Base

# --- Initial Configuration ---
st.set_page_config(page_title="Qufy | Questioning your file, hehe", page_icon="🤖", layout="wide")

OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_LLM = "granite3.3:2b"
OLLAMA_HOST = database.os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:11434"

@st.cache_resource
def get_embeddings_client():
    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)

@st.cache_resource
def get_llm_client():
    return Ollama(model=OLLAMA_LLM, base_url=OLLAMA_BASE_URL)

# --- Main Application Flow ---
def main():
    # Check if the user is already logged in
    if not st.session_state.get('logged_in'):
        ui.display_login_register()
    else:
        # If logged in, show the main UI
        user_id = st.session_state.get('user_id')
        ui.display_sidebar(user_id)
        
        st.title("🤖 Qufy: Chat with Your Documents")

        # Determine which page to display (new chat or active chat)
        if st.session_state.get('active_chat_id') is None:
            display_new_chat_page(user_id)
        else:
            display_active_chat_window()

# Replace the entire display_new_chat_page function with this:
def display_new_chat_page(user_id):
    """Display the page for uploading a PDF and creating a new chat."""
    st.info("Please upload a PDF document to start a new chat session.")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", label_visibility="collapsed")

    if uploaded_file:
        if st.button(f"Process '{uploaded_file.name}'"):
            with st.spinner("Analyzing the document... This may take a few minutes."):
                
                # --- Begin database interaction block ---
                db = database.SessionLocal()
                try:
                    # Process the PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                        tmpfile.write(uploaded_file.getvalue())
                        loader = PyPDFLoader(tmpfile.name)
                        docs = loader.load()
                    
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                    chunks = text_splitter.split_documents(docs)
                    chunk_texts = [chunk.page_content for chunk in chunks]
                    
                    # Create embeddings
                    embeddings_client = get_embeddings_client()
                    chunk_embeddings = embeddings_client.embed_documents(chunk_texts)
                    
                    chunks_with_embeddings = [
                        {"text": text, "embedding": embedding}
                        for text, embedding in zip(chunk_texts, chunk_embeddings)
                    ]
                    
                    # Save to database
                    new_chat = database.add_new_chat(db, user_id, uploaded_file.name)
                    # Capture the ID now while the session is still open
                    new_chat_id = new_chat.id
                    database.add_document_chunks(db, new_chat_id, chunks_with_embeddings)

                finally:
                    # Ensure session is always closed, even if an error occurs
                    db.close()
                # --- End database interaction block ---

                # Use the ID we safely stored
                st.session_state.active_chat_id = new_chat_id
                st.success("Document successfully processed! You can now start asking questions.")
                st.rerun()

def display_active_chat_window():
    """Display the chat window for the active session."""
    chat_id = st.session_state.active_chat_id
    db = database.SessionLocal()

    chat = db.query(database.Chat).filter_by(id=chat_id).first()
    if chat and chat.file_name:  # make sure filename column exists
        st.markdown(
            f"""
            <div style="
                padding: 12px;
                background-color: #1a1c23;
                border-radius: 10px; 
                border-left: 6px solid #ffbd45;
                margin-bottom: 20px;
            ">
                <p style="
                    color: #ffffff;  
                    font-family: 'Segoe UI', 'Roboto', sans-serif; 
                    margin: 0;
                    font-size: 1.1em;
                ">
                    You are asking about: <strong>{chat.file_name}</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Retrieve message history from DB
    messages = database.get_messages_for_chat(db, chat_id)
    for msg in messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    # Receive user input
    if prompt := st.chat_input("Ask something about the document..."):
        # Add the user message to the UI and DB
        with st.chat_message("user"):
            st.markdown(prompt)
        database.add_message(db, chat_id, "user", prompt)

        # Assistant bubble with placeholder
        with st.chat_message("assistant"):
            placeholder = st.empty()
            with placeholder.container():
                with st.spinner("AI is thinking..."):
                    embeddings_client = get_embeddings_client()
                    llm = get_llm_client()

                    # 1. Create embedding for the user’s question
                    query_embedding = embeddings_client.embed_query(prompt)

                    # 2. Find relevant text chunks in DB
                    similar_chunks = database.find_similar_chunks(db, chat_id, query_embedding)
                    context = "\n\n".join([chunk.chunk_text for chunk in similar_chunks])

                    # 3. Combine context + question
                    full_prompt = f"Based on this context:\n\n{context}\n\nAnswer this question: {prompt}"

                    # 4. Get response from LLM
                    response = llm.invoke(full_prompt)

            # Replace placeholder with final response
            placeholder.markdown(response)

            # Save assistant’s response to DB
            database.add_message(db, chat_id, "assistant", response)
    
    db.close()


if __name__ == "__main__":
    main()
