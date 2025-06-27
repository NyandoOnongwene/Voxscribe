from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
from passlib.context import CryptContext

from models import (
    User, ConversationRoom, Transcription, Translation, 
    Message, AudioFile, user_room_association,
    CreateUserRequest, CreateRoomRequest, JoinRoomRequest
)
from db import get_db_session

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_user(db: Session, user_data: CreateUserRequest) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        hashed_password = UserService.get_password_hash(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            profession=user_data.profession,
            password_hash=hashed_password,
            main_language=user_data.main_language
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not UserService.verify_password(password, user.password_hash):
            return None
        return user

class RoomService:
    @staticmethod
    def create_room(db: Session, room_data: CreateRoomRequest, creator_id: int) -> ConversationRoom:
        """Create a new conversation room"""
        # Generate unique room_id
        import uuid
        room_id = str(uuid.uuid4())[:8]
        
        db_room = ConversationRoom(
            room_id=room_id,
            name=room_data.name,
            description=room_data.description,
            created_by=creator_id
        )
        
        db.add(db_room)
        db.commit()
        db.refresh(db_room)
        
        # Add creator as participant
        RoomService.add_participant(db, db_room.id, creator_id, "en", "en")
        
        return db_room
    
    @staticmethod
    def get_room_by_id(db: Session, room_id: str) -> Optional[ConversationRoom]:
        """Get room by external room_id"""
        return db.query(ConversationRoom).filter(ConversationRoom.room_id == room_id).first()
    
    @staticmethod
    def add_participant(db: Session, room_id: int, user_id: int, 
                       preferred_language: str = "en", translate_to_language: str = "en") -> bool:
        """Add a participant to a room"""
        # Check if user is already a participant
        existing = db.execute(
            user_room_association.select().where(
                and_(
                    user_room_association.c.user_id == user_id,
                    user_room_association.c.room_id == room_id
                )
            )
        ).first()
        
        if existing:
            return False
        
        # Add participant
        db.execute(
            user_room_association.insert().values(
                user_id=user_id,
                room_id=room_id,
                preferred_language=preferred_language,
                translate_to_language=translate_to_language
            )
        )
        db.commit()
        return True
    
    @staticmethod
    def get_room_participants(db: Session, room_id: str) -> List[Dict[str, Any]]:
        """Get all participants in a room with their language preferences"""
        room = RoomService.get_room_by_id(db, room_id)
        if not room:
            return []
        
        participants = db.execute(
            user_room_association.select().where(
                user_room_association.c.room_id == room.id
            )
        ).fetchall()
        
        result = []
        for participant in participants:
            user = db.query(User).filter(User.id == participant.user_id).first()
            if user:
                result.append({
                    'user': user,
                    'preferred_language': participant.preferred_language,
                    'translate_to_language': participant.translate_to_language,
                    'joined_at': participant.joined_at
                })
        
        return result

class TranscriptionService:
    @staticmethod
    def create_transcription(db: Session, user_id: int, room_id: str, 
                           original_text: str, detected_language: str,
                           confidence_score: Optional[str] = None,
                           audio_duration: Optional[str] = None) -> Transcription:
        """Create a new transcription"""
        room = RoomService.get_room_by_id(db, room_id)
        if not room:
            raise ValueError("Room not found")
        
        db_transcription = Transcription(
            user_id=user_id,
            room_id=room.id,
            original_text=original_text,
            detected_language=detected_language,
            confidence_score=confidence_score,
            audio_duration=audio_duration
        )
        
        db.add(db_transcription)
        db.commit()
        db.refresh(db_transcription)
        return db_transcription
    
    @staticmethod
    def add_translation(db: Session, transcription_id: int, target_language: str,
                       translated_text: str, translation_service: Optional[str] = None) -> Translation:
        """Add a translation to a transcription"""
        db_translation = Translation(
            transcription_id=transcription_id,
            target_language=target_language,
            translated_text=translated_text,
            translation_service=translation_service
        )
        
        db.add(db_translation)
        db.commit()
        db.refresh(db_translation)
        return db_translation
    
    @staticmethod
    def get_room_transcriptions(db: Session, room_id: str, limit: int = 50) -> List[Transcription]:
        """Get recent transcriptions for a room"""
        room = RoomService.get_room_by_id(db, room_id)
        if not room:
            return []
        
        return db.query(Transcription)\
            .filter(Transcription.room_id == room.id)\
            .options(joinedload(Transcription.translations))\
            .order_by(Transcription.timestamp.desc())\
            .limit(limit)\
            .all()

class MessageService:
    @staticmethod
    def create_message(db: Session, user_id: int, room_id: str, speaker_name: str,
                      original_text: str, original_language: str,
                      translated_text: Optional[str] = None,
                      target_language: Optional[str] = None,
                      transcription_id: Optional[int] = None,
                      message_type: str = "transcription") -> Message:
        """Create a new message"""
        room = RoomService.get_room_by_id(db, room_id)
        if not room:
            raise ValueError("Room not found")
        
        db_message = Message(
            user_id=user_id,
            room_id=room.id,
            transcription_id=transcription_id,
            speaker_name=speaker_name,
            original_text=original_text,
            original_language=original_language,
            translated_text=translated_text,
            target_language=target_language,
            message_type=message_type
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    @staticmethod
    def get_room_messages(db: Session, room_id: str, limit: int = 100) -> List[Message]:
        """Get recent messages for a room"""
        room = RoomService.get_room_by_id(db, room_id)
        if not room:
            return []
        
        return db.query(Message)\
            .filter(Message.room_id == room.id)\
            .order_by(Message.timestamp.desc())\
            .limit(limit)\
            .all()

# Helper function to get all services
def get_services():
    return {
        'user': UserService,
        'room': RoomService,
        'transcription': TranscriptionService,
        'message': MessageService
    } 