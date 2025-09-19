# src/auth.py
import bcrypt
import streamlit as st
from . import database

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(db, username, password):
    if database.get_user_by_username(db, username):
        return False, "Username already in use."
    hashed = hash_password(password)
    database.add_user(db, username, hashed.decode('utf-8'))
    return True, "Registration successful! Please log in."

def login_user(db, username, password):
    user = database.get_user_by_username(db, username)
    if user and verify_password(password, user.hashed_password):
        # Set session state after successful login
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user.id
        st.session_state['username'] = user.username
        st.session_state['active_chat_id'] = None  # Reset active chat on login
        return True
    return False

def logout_user():
    # Remove all session-related state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
