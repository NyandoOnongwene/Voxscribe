from pydantic import BaseModel, Field
from typing import List, Optional

class User(BaseModel):
    name: str
    email: str
    profession: Optional[str] = None
    password_hash: str  # Storing hashed password
    main_language: str

class Participant(BaseModel):
    user: User
    main_language: str
    translate_to: str

class Message(BaseModel):
    speaker: str
    original_text: str
    language: str
    translated_text: str
    recipient_language: str
    timestamp: str

class ConvoRoom(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    participants: List[Participant] = []
    transcription_chat: List[Message] = [] 