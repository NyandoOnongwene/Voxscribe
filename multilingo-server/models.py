from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from db import Base

# Association table for many-to-many relationship between users and conversation rooms
user_room_association = Table(
    'user_room_participants',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('room_id', Integer, ForeignKey('conversation_rooms.id'), primary_key=True),
    Column('preferred_language', String(10), nullable=False),
    Column('translate_to_language', String(10), nullable=False),
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)

# SQLAlchemy Models for Database
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    profession = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    main_language = Column(String(10), nullable=False, default='en')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversation_rooms = relationship(
        "ConversationRoom", 
        secondary=user_room_association, 
        back_populates="participants"
    )
    messages = relationship("Message", back_populates="user")
    transcriptions = relationship("Transcription", back_populates="user")

class ConversationRoom(Base):
    __tablename__ = "conversation_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(50), unique=True, index=True, nullable=False)  # External room identifier
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    participants = relationship(
        "User", 
        secondary=user_room_association, 
        back_populates="conversation_rooms"
    )
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")
    transcriptions = relationship("Transcription", back_populates="room", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('conversation_rooms.id'), nullable=False)
    original_text = Column(Text, nullable=False)
    detected_language = Column(String(10), nullable=False)
    confidence_score = Column(String(10), nullable=True)  # Whisper confidence score
    audio_duration = Column(String(20), nullable=True)  # Duration in seconds
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transcriptions")
    room = relationship("ConversationRoom", back_populates="transcriptions")
    translations = relationship("Translation", back_populates="transcription", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="transcription")

class Translation(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(Integer, ForeignKey('transcriptions.id'), nullable=False)
    target_language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    translation_service = Column(String(50), nullable=True)  # e.g., 'google', 'deepl'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transcription = relationship("Transcription", back_populates="translations")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('conversation_rooms.id'), nullable=False)
    transcription_id = Column(Integer, ForeignKey('transcriptions.id'), nullable=True)
    speaker_name = Column(String(100), nullable=False)
    original_text = Column(Text, nullable=False)
    original_language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=True)
    target_language = Column(String(10), nullable=True)
    message_type = Column(String(20), default='transcription')  # 'transcription', 'system', 'manual'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="messages")
    room = relationship("ConversationRoom", back_populates="messages")
    transcription = relationship("Transcription", back_populates="messages")

class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(Integer, ForeignKey('transcriptions.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    duration = Column(String(20), nullable=True)  # Duration in seconds
    format = Column(String(10), nullable=True)  # e.g., 'wav', 'mp3'
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transcription = relationship("Transcription", foreign_keys=[transcription_id])

# Pydantic Models for API Responses
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    profession: Optional[str] = None
    main_language: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    speaker_name: str
    original_text: str
    original_language: str
    translated_text: Optional[str] = None
    target_language: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ConversationRoomResponse(BaseModel):
    id: int
    room_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    participants: List[UserResponse] = []
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class TranscriptionResponse(BaseModel):
    id: int
    original_text: str
    detected_language: str
    confidence_score: Optional[str] = None
    timestamp: datetime
    translations: List[dict] = []

    class Config:
        from_attributes = True

# Request Models
class CreateUserRequest(BaseModel):
    name: str
    email: str
    profession: Optional[str] = None
    password: str
    main_language: str = 'en'

class CreateRoomRequest(BaseModel):
    name: str
    description: Optional[str] = None

class JoinRoomRequest(BaseModel):
    preferred_language: str = 'en'
    translate_to_language: str = 'en' 