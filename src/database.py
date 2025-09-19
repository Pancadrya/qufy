# src/database.py
import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base, User, Chat, Message, DocumentChunk

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- User Management ---
def get_user_by_username(db, username):
    return db.query(User).filter(User.username == username).first()

def add_user(db, username, hashed_password):
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Chat Management ---
def get_chats_for_user(db, user_id):
    return db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()

def add_new_chat(db, user_id, file_name):
    new_chat = Chat(user_id=user_id, file_name=file_name)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

def delete_chat(db, chat_id):
    db_chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if db_chat:
        db.delete(db_chat)
        db.commit()

# --- Message Management ---
def get_messages_for_chat(db, chat_id):
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()

def add_message(db, chat_id, role, content):
    new_message = Message(chat_id=chat_id, role=role, content=content)
    db.add(new_message)
    db.commit()

# --- Document Chunk Management ---
def add_document_chunks(db, chat_id, chunks_with_embeddings):
    db_chunks = [
        DocumentChunk(chat_id=chat_id, chunk_text=item['text'], embedding=item['embedding'])
        for item in chunks_with_embeddings
    ]
    db.bulk_save_objects(db_chunks)
    db.commit()

def find_similar_chunks(db, chat_id, query_embedding, k=4):
    # Gunakan operator <-> dari pgvector untuk L2 distance
    # Pastikan chat_id juga difilter untuk isolasi data
    results = db.query(DocumentChunk).filter(DocumentChunk.chat_id == chat_id).order_by(
        DocumentChunk.embedding.l2_distance(query_embedding)
    ).limit(k).all()
    return results