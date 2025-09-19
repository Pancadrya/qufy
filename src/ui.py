# src/ui.py
import streamlit as st
from . import auth
from . import database

def display_login_register():
    st.title("Selamat Datang di Qufy 🤖")
    st.info("Silakan login untuk melanjutkan atau buat akun baru jika Anda belum terdaftar.")
    
    login_tab, register_tab = st.tabs(["Login", "Registrasi"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                db = database.SessionLocal()
                if auth.login_user(db, username, password):
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
                db.close()

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Registrasi")
            if submitted:
                if not new_username or not new_password:
                    st.error("Username dan password tidak boleh kosong.")
                else:
                    db = database.SessionLocal()
                    success, message = auth.register_user(db, new_username, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                    db.close()

def display_sidebar(user_id):
    with st.sidebar:
        st.header(f"Selamat Datang, {st.session_state['username']}!")
        
        if st.button("➕ Buat Chat Baru"):
            st.session_state.active_chat_id = None
            st.rerun()

        st.markdown("---")
        
        db = database.SessionLocal()
        chat_sessions = database.get_chats_for_user(db, user_id)
        db.close()
        
        if not chat_sessions:
            st.caption("Anda belum memiliki riwayat chat. Mulai dengan membuat chat baru!")
        else:
            for chat in chat_sessions:
                col1, col2 = st.columns([0.8, 0.2])
                full_name = chat.file_name
                truncated_name = (full_name[:22] + '...') if len(full_name) > 25 else full_name
                
                with col1:
                    if st.button(truncated_name, key=chat.id, help=full_name, use_container_width=True):
                        st.session_state.active_chat_id = chat.id
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{chat.id}", help="Hapus chat ini"):
                        db = database.SessionLocal()
                        database.delete_chat(db, chat.id)
                        db.close()
                        if st.session_state.active_chat_id == chat.id:
                            st.session_state.active_chat_id = None
                        st.rerun()
        
        st.markdown("---")
        if st.button("Logout"):
            auth.logout_user()
            st.rerun()