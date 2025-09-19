# src/models.py
import uuid
from sqlalchemy import create_engine, Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    chat = relationship("Chat", back_populates="messages")

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)  # nomic-embed-text has 768 dimensions
    chat = relationship("Chat", back_populates="chunks")
