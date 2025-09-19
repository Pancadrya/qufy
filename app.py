# app.py
import streamlit as st
import tempfile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.llms import Ollama

# Impor modul dari folder src
from src import ui, auth, database
from src.models import Base

# --- Konfigurasi Awal ---
st.set_page_config(page_title="Qufy", page_icon="🤖", layout="wide")

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

# --- Alur Aplikasi Utama ---
def main():
    # Periksa apakah pengguna sudah login
    if not st.session_state.get('logged_in'):
        ui.display_login_register()
    else:
        # Jika sudah login, tampilkan UI utama
        user_id = st.session_state.get('user_id')
        ui.display_sidebar(user_id)
        
        st.title("🤖 Qufy: Chat dengan Dokumen Anda")

        # Tentukan halaman mana yang akan ditampilkan (chat baru atau chat aktif)
        if st.session_state.get('active_chat_id') is None:
            display_new_chat_page(user_id)
        else:
            display_active_chat_window()

# app.py

# Ganti seluruh fungsi display_new_chat_page dengan ini:
def display_new_chat_page(user_id):
    """Menampilkan halaman untuk mengunggah PDF dan membuat chat baru."""
    st.info("Silakan unggah dokumen PDF untuk memulai sesi chat baru.")
    uploaded_file = st.file_uploader("Pilih file PDF", type="pdf", label_visibility="collapsed")

    if uploaded_file:
        if st.button(f"Proses '{uploaded_file.name}'"):
            with st.spinner("Menganalisis dokumen... Ini bisa memakan waktu beberapa menit."):
                
                # --- Awal blok interaksi database ---
                db = database.SessionLocal()
                try:
                    # Proses PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                        tmpfile.write(uploaded_file.getvalue())
                        loader = PyPDFLoader(tmpfile.name)
                        docs = loader.load()
                    
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                    chunks = text_splitter.split_documents(docs)
                    chunk_texts = [chunk.page_content for chunk in chunks]
                    
                    # Buat embeddings
                    embeddings_client = get_embeddings_client()
                    chunk_embeddings = embeddings_client.embed_documents(chunk_texts)
                    
                    chunks_with_embeddings = [
                        {"text": text, "embedding": embedding}
                        for text, embedding in zip(chunk_texts, chunk_embeddings)
                    ]
                    
                    # Simpan ke database
                    new_chat = database.add_new_chat(db, user_id, uploaded_file.name)
                    # Ambil ID SEKARANG, selagi sesi masih terbuka
                    new_chat_id = new_chat.id
                    database.add_document_chunks(db, new_chat_id, chunks_with_embeddings)

                finally:
                    # Pastikan sesi selalu ditutup, bahkan jika ada error
                    db.close()
                # --- Akhir blok interaksi database ---

                # Gunakan ID yang sudah kita simpan dengan aman
                st.session_state.active_chat_id = new_chat_id
                st.success("Dokumen berhasil diproses! Anda bisa mulai bertanya.")
                st.rerun()

def display_active_chat_window():
    """Menampilkan jendela chat untuk sesi yang sedang aktif."""
    chat_id = st.session_state.active_chat_id
    db = database.SessionLocal()
    
    # Ambil riwayat pesan
    messages = database.get_messages_for_chat(db, chat_id)
    for msg in messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    # Terima input pengguna
    if prompt := st.chat_input("Tanyakan sesuatu tentang dokumen..."):
        # Tambahkan pesan pengguna ke UI dan DB
        with st.chat_message("user"):
            st.markdown(prompt)
        database.add_message(db, chat_id, "user", prompt)

        # Logika RAG (Retrieval-Augmented Generation)
        with st.chat_message("assistant"):
            with st.spinner("AI sedang berpikir..."):
                embeddings_client = get_embeddings_client()
                llm = get_llm_client()

                # 1. Buat embedding untuk pertanyaan pengguna
                query_embedding = embeddings_client.embed_query(prompt)

                # 2. Cari potongan teks yang relevan di DB
                similar_chunks = database.find_similar_chunks(db, chat_id, query_embedding)
                context = "\n\n".join([chunk.chunk_text for chunk in similar_chunks])

                # 3. Buat prompt gabungan (konteks + pertanyaan)
                full_prompt = f"Berdasarkan konteks berikut:\n\n{context}\n\nJawab pertanyaan ini: {prompt}"

                # 4. Kirim ke LLM untuk mendapatkan jawaban
                response = llm.invoke(full_prompt)
                
                st.markdown(response)
                # Tambahkan respons AI ke DB
                database.add_message(db, chat_id, "assistant", response)
    
    db.close()


if __name__ == "__main__":
    main()