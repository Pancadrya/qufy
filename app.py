import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
import tempfile
import os

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(
    page_title="Qufy 💬",
    page_icon="🤖",
    layout="wide"
)

# --- Judul Aplikasi ---
st.markdown("<h1 style='text-align: center;'>Qufy 🤖💬</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Selamat datang di Qufy! Buat chat baru untuk mengunggah dokumen PDF dan mulai bertanya.</p>", unsafe_allow_html=True)


# --- Fungsi Inti Aplikasi (Tidak Berubah) ---
@st.cache_resource(show_spinner="Membuat embedding untuk dokumen...")
def create_vector_store_from_pdf(uploaded_file):
    """
    Fungsi untuk membaca PDF, memecah teks, membuat embedding, 
    dan menyimpannya di FAISS vector store.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
        chunks = text_splitter.split_documents(documents)
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text:latest", 
            base_url="http://host.docker.internal:11434"
        )
        vector_store = FAISS.from_documents(chunks, embeddings)
        return vector_store
    finally:
        os.remove(tmp_file_path)

# --- MODIFIKASI: Inisialisasi Session State yang Baru ---
# 'chats' akan menyimpan semua sesi percakapan.
# Setiap chat adalah dictionary yang berisi: file_name, messages, dan vector_store.
# 'active_chat_index' melacak chat mana yang sedang aktif ditampilkan.
if "chats" not in st.session_state:
    st.session_state.chats = []
if "active_chat_index" not in st.session_state:
    st.session_state.active_chat_index = None

# --- MODIFIKASI: Logika Sidebar untuk Riwayat Chat ---
with st.sidebar:
    st.header("Riwayat Chat")
    
    # Tombol untuk membuat chat room baru
    if st.button("➕ Buat Chat Baru", use_container_width=True):
        st.session_state.active_chat_index = None
        st.rerun() # Memaksa Streamlit untuk menjalankan ulang skrip dari atas

    st.divider()

    # Menampilkan daftar chat yang sudah ada
    if not st.session_state.chats:
        st.caption("Belum ada riwayat chat.")
    else:
        for i, chat in enumerate(st.session_state.chats):
            # Gunakan nama file sebagai label tombol untuk setiap chat
            if st.button(chat["file_name"], key=f"chat_{i}", use_container_width=True):
                st.session_state.active_chat_index = i
                st.rerun()

st.divider()

# --- MODIFIKASI: Tampilan Utama Aplikasi (Bergantung pada state) ---

# Tampilan 1: Layar untuk membuat chat baru jika tidak ada chat yang aktif
if st.session_state.active_chat_index is None:
    st.info("Silakan unggah dokumen PDF untuk memulai percakapan baru.")
    
    uploaded_file = st.file_uploader(
        "Unggah file PDF Anda di sini", 
        type="pdf", 
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Proses file yang diunggah
        vector_store = create_vector_store_from_pdf(uploaded_file)
        
        # Buat entri chat baru
        new_chat = {
            "file_name": uploaded_file.name,
            "vector_store": vector_store,
            "messages": [] # Riwayat pesan dimulai kosong
        }
        
        # Tambahkan ke daftar chats dan set sebagai chat aktif
        st.session_state.chats.append(new_chat)
        st.session_state.active_chat_index = len(st.session_state.chats) - 1
        st.success(f"Dokumen '{uploaded_file.name}' berhasil diproses!")
        st.rerun()

# Tampilan 2: Antarmuka chat jika ada chat yang aktif
else:
    # Ambil data chat yang sedang aktif
    active_chat = st.session_state.chats[st.session_state.active_chat_index]
    
    st.subheader(f"Anda sedang bertanya tentang: `{active_chat['file_name']}`")

    # Menampilkan chat history yang sudah ada untuk chat ini
    for message in active_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Dapatkan input dari pengguna
    if prompt := st.chat_input(f"Tanyakan sesuatu tentang {active_chat['file_name']}..."):
        # Tampilkan pesan pengguna dan simpan ke history chat aktif
        st.chat_message("user").markdown(prompt)
        active_chat["messages"].append({"role": "user", "content": prompt})

        with st.spinner("AI sedang berpikir... 🤔"):
            # Siapkan model LLM dan retriever dari vector store yang sesuai
            llm = Ollama(
                model="granite3.3:2b",
                base_url="http://host.docker.internal:11434"
            )
            retriever = active_chat["vector_store"].as_retriever()
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever
            )
            
            # Dapatkan jawaban dari AI
            response = qa_chain.invoke(prompt)
            
            # Tampilkan jawaban AI dan simpan ke history chat aktif
            with st.chat_message("assistant"):
                st.markdown(response['result'])
            active_chat["messages"].append({"role": "assistant", "content": response['result']})