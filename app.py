import streamlit as st
import os
import shutil
import json
import uuid
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# --- Konfigurasi Aplikasi ---

# Direktori untuk menyimpan sesi chat
SESSIONS_DIR = Path("chat_sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

# Konfigurasi Model (ubah sesuai kebutuhan)
OLLAMA_BASE_URL = "http://host.docker.internal:11434"
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "granite3.3:2b"

st.set_page_config(
    page_title="Qufy 💬",
    page_icon="🤖",
    layout="wide"
)

# --- Fungsi Inti & Manajemen Sesi ---

def create_vector_store(uploaded_file):
    """
    Membuat vector store dari file PDF yang diunggah.
    Menyimpan file sementara untuk diproses oleh PyPDFLoader.
    """
    temp_dir = Path("./temp_files")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / uploaded_file.name
    
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        loader = PyPDFLoader(str(temp_file_path))
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
        chunks = text_splitter.split_documents(documents)
        
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
        vector_store = FAISS.from_documents(chunks, embeddings)
        
        return vector_store
    finally:
        # Hapus file sementara setelah selesai
        shutil.rmtree(temp_dir)

def save_chat_session(chat_id, file_name, messages, vector_store):
    """Menyimpan seluruh data sesi chat ke disk."""
    session_path = SESSIONS_DIR / chat_id
    session_path.mkdir(exist_ok=True)
    
    # Simpan metadata dan pesan
    with open(session_path / "metadata.json", "w") as f:
        json.dump({"file_name": file_name}, f)
    with open(session_path / "messages.json", "w") as f:
        json.dump(messages, f)
        
    # Simpan vector store
    vector_store.save_local(str(session_path / "faiss_index"))

@st.cache_resource
def load_vector_store(chat_id):
    """Memuat vector store dari disk."""
    session_path = SESSIONS_DIR / chat_id
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
    return FAISS.load_local(str(session_path / "faiss_index"), embeddings, allow_dangerous_deserialization=True)

@st.cache_resource
def get_qa_chain(chat_id):  # <-- INPUT CHANGED
    """Membuat dan meng-cache RAG chain untuk chat_id tertentu."""
    # The function now loads its own vector store
    vector_store = load_vector_store(chat_id) 
    
    llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
    retriever = vector_store.as_retriever()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )

def load_chats_from_disk():
    """Memuat metadata semua chat yang tersimpan di disk."""
    chats = {}
    for session_dir in SESSIONS_DIR.iterdir():
        if session_dir.is_dir():
            metadata_path = session_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    chats[session_dir.name] = metadata
    return chats

# --- Antarmuka Streamlit (UI) ---

def render_sidebar(chats):
    """Menampilkan sidebar dengan riwayat chat dan tombol aksi."""
    with st.sidebar:
        st.header("Riwayat Chat")
        
        if st.button("➕ Buat Chat Baru", use_container_width=True):
            st.session_state.active_chat_id = None
            st.rerun()
            
        st.divider()

        if not chats:
            st.caption("Belum ada riwayat chat.")
        else:
            # --- PERUBAHAN DIMULAI DI SINI ---

            # 1. Tentukan panjang maksimum untuk nama file di sidebar
            MAX_LENGTH = 25 

            sorted_chat_ids = sorted(chats.keys(), reverse=True)
            for chat_id in sorted_chat_ids:
                file_name = chats[chat_id].get("file_name", "Chat Tanpa Nama")
                
                # 2. Buat nama tampilan yang dipotong jika terlalu panjang ✂️
                display_name = (file_name[:MAX_LENGTH - 3] + "...") if len(file_name) > MAX_LENGTH else file_name
                
                # --- PERUBAHAN SELESAI ---

                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    # 3. Gunakan 'display_name' untuk label tombol
                    if st.button(display_name, key=f"chat_{chat_id}", use_container_width=True, help=file_name):
                        st.session_state.active_chat_id = chat_id
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{chat_id}", use_container_width=True, help="Hapus chat ini"):
                        shutil.rmtree(SESSIONS_DIR / chat_id)
                        if st.session_state.get("active_chat_id") == chat_id:
                            st.session_state.active_chat_id = None
                        st.rerun()

def render_new_chat_view():
    """Menampilkan halaman untuk memulai percakapan baru."""
    st.markdown("<h1 style='text-align: center;'>Qufy 🤖💬</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Selamat datang di Qufy! Unggah dokumen PDF untuk memulai percakapan baru.</p>", unsafe_allow_html=True)
    st.info("Silakan unggah dokumen PDF Anda untuk memulai.")

    uploaded_file = st.file_uploader(
        "Pilih file PDF",
        type="pdf",
        label_visibility="collapsed"
    )

    if uploaded_file:
        with st.spinner(f"Memproses '{uploaded_file.name}'... Ini mungkin memakan waktu beberapa saat."):
            try:
                vector_store = create_vector_store(uploaded_file)
                chat_id = str(uuid.uuid4())
                messages = []
                
                # Simpan sesi baru ke disk
                save_chat_session(chat_id, uploaded_file.name, messages, vector_store)
                
                st.session_state.active_chat_id = chat_id
                st.success(f"Dokumen '{uploaded_file.name}' berhasil diproses!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memproses PDF: {e}")
                st.stop()


def render_active_chat_view(chat_id, chats):
    """Menampilkan antarmuka chat untuk sesi yang aktif."""
    st.markdown("<h1 style='text-align: center;'>Qufy 🤖💬</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Selamat datang di Qufy! Unggah dokumen PDF untuk memulai percakapan baru.</p>", unsafe_allow_html=True)
    
    file_name = chats[chat_id]["file_name"]
    st.subheader(f"Anda bertanya tentang: `{file_name}`")

    # Muat pesan dan vector store
    session_path = SESSIONS_DIR / chat_id
    messages_path = session_path / "messages.json"
    with open(messages_path, "r") as f:
        messages = json.load(f)

    # Dapatkan pesan untuk berdasarkan chat_id
    qa_chain = get_qa_chain(chat_id)

    # Tampilkan riwayat chat
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dari pengguna
    if prompt := st.chat_input(f"Tanyakan sesuatu tentang {file_name}..."):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI sedang berpikir... 🤔"):
                try:
                    response = qa_chain.invoke(prompt)
                    result = response.get('result', "Maaf, saya tidak dapat menemukan jawaban.")
                    st.markdown(result)
                    messages.append({"role": "assistant", "content": result})
                    
                    # Simpan pesan baru ke disk
                    with open(messages_path, "w") as f:
                        json.dump(messages, f)
                except Exception as e:
                    error_message = f"Terjadi kesalahan: {e}"
                    st.error(error_message)
                    messages.append({"role": "assistant", "content": error_message})
                    with open(messages_path, "w") as f:
                        json.dump(messages, f)

# --- Main App Logic ---

def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    
    # Muat semua sesi chat yang ada dari disk
    all_chats = load_chats_from_disk()
    
    # Render sidebar
    render_sidebar(all_chats)
    
    # Ambil chat yang sedang aktif dari session state
    active_chat_id = st.session_state.get("active_chat_id")
    
    # Tentukan tampilan mana yang akan dirender
    if active_chat_id is None:
        render_new_chat_view()
    else:
        render_active_chat_view(active_chat_id, all_chats)

if __name__ == "__main__":
    main()