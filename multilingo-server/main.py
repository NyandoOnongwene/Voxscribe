from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
from datetime import datetime
from typing import List

from websocket_manager import manager
from whisper_engine import whisper_engine
from translator import text_translator
from utils import convert_audio_to_wav
from db import get_db, DatabaseManager, create_tables
from db_services import UserService, RoomService, TranscriptionService, MessageService
from models import (
    User, ConversationRoom, Message, Transcription,
    UserResponse, ConversationRoomResponse, MessageResponse, TranscriptionResponse,
    CreateUserRequest, CreateRoomRequest, JoinRoomRequest, user_room_association
)

app = FastAPI(title="Voxscribe API", description="Real-time transcription and translation service")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    DatabaseManager.check_connection()
    DatabaseManager.init_db()
    print("🚀 Voxscribe server started successfully!")

@app.get("/")
async def get():
    return HTMLResponse("<h1>Voxscribe Server is running! 🎙️</h1>")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "voxscribe-api"}

# Authentication Endpoints
@app.post("/api/auth/signup", response_model=dict)
async def signup_user(user_data: CreateUserRequest, db: Session = Depends(get_db)):
    """Sign up a new user"""
    try:
        user = UserService.create_user(db, user_data)
        # In a real app, you'd generate a proper JWT token here
        return {
            "message": "User created successfully",
            "user": UserResponse.from_orm(user).dict(),
            "token": f"dummy_token_for_{user.id}"  # Replace with real JWT
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login", response_model=dict)
async def login_user(login_data: dict, db: Session = Depends(get_db)):
    """Login user with email and password"""
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )
    
    user = UserService.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Invalid email or password"
        )
    
    # In a real app, you'd generate a proper JWT token here
    return {
        "message": "Login successful",
        "user": UserResponse.from_orm(user).dict(),
        "token": f"dummy_token_for_{user.id}"  # Replace with real JWT
    }

# User Management Endpoints  
@app.post("/api/users/register", response_model=UserResponse)
async def register_user(user_data: CreateUserRequest, db: Session = Depends(get_db)):
    """Register a new user (alternative endpoint)"""
    try:
        user = UserService.create_user(db, user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)

@app.get("/api/users/{user_id}/rooms")
async def get_user_rooms(user_id: int, db: Session = Depends(get_db)):
    """Get all rooms where user is a participant"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all rooms where user is a participant
    user_rooms = db.execute(
        user_room_association.select().where(
            user_room_association.c.user_id == user_id
        )
    ).fetchall()
    
    rooms_data = []
    for room_participation in user_rooms:
        room = db.query(ConversationRoom).filter(
            ConversationRoom.id == room_participation.room_id
        ).first()
        
        if room:
            # Get recent messages count
            message_count = db.query(Message).filter(Message.room_id == room.id).count()
            
            # Get last activity
            last_message = db.query(Message).filter(
                Message.room_id == room.id
            ).order_by(Message.timestamp.desc()).first()
            
            rooms_data.append({
                "room_id": room.room_id,
                "name": room.name,
                "description": room.description,
                "created_at": room.created_at.isoformat() + "Z",
                "joined_at": room_participation.joined_at.isoformat() + "Z",
                "message_count": message_count,
                "last_activity": last_message.timestamp.isoformat() + "Z" if last_message else None,
                "preferred_language": room_participation.preferred_language,
                "translate_to_language": room_participation.translate_to_language
            })
    
    return {"rooms": rooms_data}

# Room Management Endpoints
@app.post("/api/rooms")
async def create_room(request_data: dict, db: Session = Depends(get_db)):
    """Create a new conversation room"""
    try:
        # Extract room data and creator_id from request
        room_data = CreateRoomRequest(
            name=request_data.get("name"),
            description=request_data.get("description", "")
        )
        creator_id = request_data.get("creator_id")
        
        if not creator_id:
            raise HTTPException(status_code=400, detail="creator_id is required")
        
        # Verify user exists
        user = UserService.get_user_by_id(db, creator_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create room
        room = RoomService.create_room(db, room_data, creator_id)
        
        return {
            "room_id": room.room_id,
            "name": room.name,
            "description": room.description,
            "created_at": room.created_at.isoformat() + "Z",
            "created_by": room.created_by
        }
        
    except Exception as e:
        print(f"Error creating room: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/{room_id}", response_model=ConversationRoomResponse)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    """Get room details"""
    room = RoomService.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return ConversationRoomResponse.from_orm(room)

@app.get("/api/rooms/{room_id}/details")
async def get_room_details(room_id: str, db: Session = Depends(get_db)):
    """Get detailed room information"""
    room = RoomService.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Get participant count
    participants = RoomService.get_room_participants(db, room_id)
    participant_count = len(participants)
    
    # Get message count
    message_count = db.query(Message).filter(Message.room_id == room.id).count()
    
    return {
        "room_id": room.room_id,
        "name": room.name,
        "description": room.description,
        "created_at": room.created_at.isoformat() + "Z",
        "participant_count": participant_count,
        "message_count": message_count,
        "created_by": room.created_by
    }

@app.post("/api/rooms/{room_id}/join")
async def join_room(room_id: str, request_data: dict, db: Session = Depends(get_db)):
    """Join a conversation room"""
    try:
        user_id = request_data.get("user_id")
        preferred_language = request_data.get("preferred_language", "en")
        translate_to_language = request_data.get("translate_to_language", "fr")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        room = RoomService.get_room_by_id(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = RoomService.add_participant(
            db, room.id, user_id, 
            preferred_language, 
            translate_to_language
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="User already in room")
        
        return {
            "message": "Successfully joined room",
            "room_id": room.room_id,
            "user_id": user_id
        }
        
    except Exception as e:
        print(f"Error joining room: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/{room_id}/participants")
async def get_room_participants(room_id: str, db: Session = Depends(get_db)):
    """Get all participants in a room"""
    participants = RoomService.get_room_participants(db, room_id)
    return {"participants": participants}

# Message and Transcription Endpoints
@app.get("/api/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_room_messages(room_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Get messages for a room"""
    messages = MessageService.get_room_messages(db, room_id, limit)
    return [MessageResponse.from_orm(msg) for msg in messages]

@app.get("/api/rooms/{room_id}/transcriptions", response_model=List[TranscriptionResponse])
async def get_room_transcriptions(room_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get transcriptions for a room"""
    transcriptions = TranscriptionService.get_room_transcriptions(db, room_id, limit)
    return [TranscriptionResponse.from_orm(trans) for trans in transcriptions]

# WebSocket endpoint for real-time transcription
@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time audio transcription and translation"""
    await manager.connect(websocket, room_id, int(user_id))
    print(f"User {user_id} connected to room {room_id}")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Verify user and room exist
        user = UserService.get_user_by_id(db, int(user_id))
        room = RoomService.get_room_by_id(db, room_id)
        
        if not user or not room:
            await websocket.close(code=4004, reason="User or room not found")
            return
        
        # Get room participants and their language preferences
        participants = RoomService.get_room_participants(db, room_id)
        
        # Send current participants list to the newly connected user
        current_participants = []
        for participant in participants:
            current_participants.append({
                "user_id": participant['user'].id,
                "user_name": participant['user'].name,
                "language": participant['preferred_language'],
                "is_online": True,
                "is_creator": participant['user'].id == room.created_by
            })
        
        # Send current participants to the new user
        await websocket.send_text(json.dumps({
            "type": "participants_list",
            "participants": current_participants,
            "room_creator_id": room.created_by
        }))
        
        # Send recent messages to the new user (filtered by their language preferences)
        user_lang_pref = None
        for participant in participants:
            if participant['user'].id == int(user_id):
                user_lang_pref = participant['translate_to_language']
                break
        
        recent_messages = MessageService.get_room_messages(db, room_id, limit=20)
        for msg in reversed(recent_messages):  # Show oldest first
            # Only send messages that match user's language preference
            if user_lang_pref and msg.target_language == user_lang_pref:
                message_data = {
                    "type": "transcription",
                    "message_id": msg.id,
                    "speaker_name": msg.speaker_name,
                    "speaker_id": msg.user_id,
                    "original_text": msg.original_text,
                    "original_language": msg.original_language,
                    "translated_text": msg.translated_text or msg.original_text,
                    "target_language": msg.target_language or msg.original_language,
                    "timestamp": msg.timestamp.isoformat() + "Z",
                    "transcription_id": msg.transcription_id
                }
                await websocket.send_text(json.dumps(message_data))
        
        # Broadcast participant joined to others
        await manager.broadcast(json.dumps({
            "type": "participant_joined",
            "user_id": int(user_id),
            "user_name": user.name,
            "language": user.main_language,
            "is_creator": int(user_id) == room.created_by
        }), room_id)
        
        while True:
            # Receive data from WebSocket
            try:
                # Try to receive different types of data
                raw_data = await websocket.receive()
                
                # Check for disconnect
                if raw_data.get("type") == "websocket.disconnect":
                    print(f"WebSocket disconnect received for user {user_id}")
                    break
                
                # Handle text messages (control messages)
                if raw_data.get("type") == "websocket.receive" and "text" in raw_data:
                    try:
                        message = json.loads(raw_data["text"])
                        
                        # Handle different message types
                        if message.get("type") == "join":
                            # Refresh participants list when someone joins
                            participants = RoomService.get_room_participants(db, room_id)
                            await manager.broadcast(json.dumps({
                                "type": "participant_joined",
                                "user_id": message["user_id"],
                                "user_name": message["user_name"],
                                "language": message["language"]
                            }), room_id)
                            continue
                            
                        elif message.get("type") == "end_session":
                            # Only room creator can end session for everyone
                            if room.created_by == int(user_id):
                                print(f"Room creator {user_id} ending session for room {room_id}")
                                
                                # Broadcast session ended message first
                                await manager.broadcast(json.dumps({
                                    "type": "session_ended",
                                    "ended_by": user.name,
                                    "message": "Session ended by room creator"
                                }), room_id)
                                
                                # Close the entire room
                                await manager.close_room(room_id, "Session ended by creator")
                                return
                            else:
                                await websocket.send_text(json.dumps({
                                    "type": "error",
                                    "message": "Only the room creator can end the session"
                                }))
                                continue
                            
                        elif message.get("type") == "leave":
                            await manager.broadcast(json.dumps({
                                "type": "participant_left",
                                "user_id": message["user_id"]
                            }), room_id)
                            break  # Exit the loop when user leaves
                            
                        elif message.get("type") == "speaking_status":
                            await manager.broadcast(json.dumps({
                                "type": "speaking_status",
                                "user_id": message["user_id"],
                                "is_speaking": message["is_speaking"]
                            }), room_id)
                            continue
                            
                        elif message.get("type") == "language_change":
                            # Handle language preference change
                            print(f"User {user_id} changed language preference")
                            # Refresh participants to get updated language preferences
                            participants = RoomService.get_room_participants(db, room_id)
                            continue
                            
                    except json.JSONDecodeError:
                        print("Invalid JSON received")
                        continue
                
                # Handle binary data (audio)
                elif raw_data.get("type") == "websocket.receive" and "bytes" in raw_data:
                    data = raw_data["bytes"]
                    
                    # 1. Convert audio chunk to WAV
                    audio_array = convert_audio_to_wav(data)
                    
                    # 2. Transcribe using Whisper with speaker's main language
                    # Use the speaker's main language as the target transcription language
                    speaker_main_language = user.main_language
                    transcription_result = whisper_engine.transcribe(audio_array, language=speaker_main_language)
                    original_text = transcription_result["text"]
                    
                    if not original_text.strip():
                        continue

                    print(f"Transcription to {speaker_main_language}: {original_text}")
                    
                    # 3. Save transcription to database (using speaker's main language)
                    db_transcription = TranscriptionService.create_transcription(
                        db=db,
                        user_id=int(user_id),
                        room_id=room_id,
                        original_text=original_text,
                        detected_language=speaker_main_language,  # Use speaker's main language
                        confidence_score=str(transcription_result.get("confidence", ""))
                    )
                    
                    # 4. Create translations from speaker's language to other participants' preferred languages
                    translations = {}
                    target_languages = set()
                    
                    # Get unique target languages from other participants (not the speaker)
                    for participant in participants:
                        # Skip the speaker themselves
                        if participant['user'].id == int(user_id):
                            continue
                            
                        target_lang = participant['translate_to_language']
                        if target_lang != speaker_main_language and target_lang not in target_languages:
                            target_languages.add(target_lang)
                            
                            try:
                                translated_text = text_translator.translate(
                                    original_text, speaker_main_language, target_lang
                                )
                                
                                # Save translation to database
                                TranscriptionService.add_translation(
                                    db=db,
                                    transcription_id=db_transcription.id,
                                    target_language=target_lang,
                                    translated_text=translated_text,
                                    translation_service="deep-translator"
                                )
                                
                                translations[target_lang] = translated_text
                                print(f"Translated to {target_lang}: {translated_text}")
                                
                            except Exception as e:
                                print(f"Translation error for {target_lang}: {e}")
                                translations[target_lang] = original_text
                    
                    # 5. Send targeted messages to each participant based on their language preference
                    for participant in participants:
                        participant_user = participant['user']
                        target_lang = participant['translate_to_language']
                        
                        # Determine what message to show this participant
                        if participant_user.id == int(user_id):
                            # For the speaker: show original text in their main language
                            display_text = original_text
                            display_language = speaker_main_language
                        else:
                            # For other participants: show translation to their preferred language
                            if target_lang == speaker_main_language:
                                # Same language as speaker, show original
                                display_text = original_text
                                display_language = speaker_main_language
                            else:
                                # Show translation to participant's preferred language
                                display_text = translations.get(target_lang, original_text)
                                display_language = target_lang
                        
                        # Save message to database for this participant
                        db_message = MessageService.create_message(
                            db=db,
                            user_id=int(user_id),
                            room_id=room_id,
                            speaker_name=user.name,
                            original_text=original_text,
                            original_language=speaker_main_language,
                            translated_text=display_text if display_language != speaker_main_language else None,
                            target_language=display_language,
                            transcription_id=db_transcription.id
                        )
                        
                        # Send targeted message to this specific participant
                        participant_message = {
                            "type": "transcription",
                            "message_id": db_message.id,
                            "speaker_name": user.name,
                            "speaker_id": int(user_id),
                            "original_text": original_text,
                            "original_language": speaker_main_language,
                            "translated_text": display_text,
                            "target_language": display_language,
                            "timestamp": db_message.timestamp.isoformat() + "Z",
                            "transcription_id": db_transcription.id
                        }
                        
                        # Send to specific participant
                        await manager.send_to_user(json.dumps(participant_message), room_id, participant_user.id)
                
                else:
                    continue
                    
            except Exception as audio_error:
                print(f"Error processing audio/message: {audio_error}")
                continue

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, int(user_id))
        print(f"User {user_id} disconnected from room {room_id}")
        
        # Broadcast participant left
        try:
            await manager.broadcast(json.dumps({
                "type": "participant_left",
                "user_id": int(user_id)
            }), room_id)
        except:
            pass
            
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
        manager.disconnect(websocket, room_id, int(user_id))
        
        # Broadcast participant left on error
        try:
            await manager.broadcast(json.dumps({
                "type": "participant_left",
                "user_id": int(user_id)
            }), room_id)
        except:
            pass
            
    finally:
        db.close()

# Database management endpoints (for development)
@app.post("/api/admin/init-db")
async def init_database():
    """Initialize/reset the database (development only)"""
    DatabaseManager.init_db()
    return {"message": "Database initialized successfully"}

@app.post("/api/admin/reset-db")
async def reset_database():
    """Reset the database (development only)"""
    DatabaseManager.reset_db()
    return {"message": "Database reset successfully"}

@app.get("/api/admin/room-stats")
async def get_room_stats():
    """Get statistics about active rooms and connections"""
    active_rooms = manager.get_active_rooms()
    room_stats = {}
    
    for room_id in active_rooms:
        participant_count = manager.get_room_participant_count(room_id)
        room_stats[room_id] = {
            "participant_count": participant_count,
            "is_active": participant_count > 0
        }
    
    return {
        "active_rooms": len(active_rooms),
        "room_details": room_stats,
        "total_connections": sum(manager.get_room_participant_count(room_id) for room_id in active_rooms)
    }

@app.get("/api/admin/evaluation-metrics")
async def get_evaluation_metrics():
    """Get latest model evaluation metrics"""
    try:
        from evaluation import VoxScribeEvaluator
        import json
        from pathlib import Path
        
        results_dir = Path("evaluation_results")
        if not results_dir.exists():
            return {"error": "No evaluation results available. Run evaluation first."}
        
        # Find latest metric files
        stt_metrics_files = list(results_dir.glob("stt_metrics_*.json"))
        translation_metrics_files = list(results_dir.glob("translation_metrics_*.json"))
        
        response = {
            "evaluation_available": len(stt_metrics_files) > 0 or len(translation_metrics_files) > 0,
            "last_evaluation": None,
            "speech_to_text": {},
            "translation": {},
            "overall_score": None
        }
        
        # Get latest STT metrics
        if stt_metrics_files:
            latest_stt = max(stt_metrics_files, key=lambda p: p.stat().st_mtime)
            with open(latest_stt) as f:
                stt_data = json.load(f)
            response["speech_to_text"] = stt_data
            response["last_evaluation"] = latest_stt.stem.split("_")[-2] + "_" + latest_stt.stem.split("_")[-1]
        
        # Get latest translation metrics
        if translation_metrics_files:
            latest_translation = max(translation_metrics_files, key=lambda p: p.stat().st_mtime)
            with open(latest_translation) as f:
                translation_data = json.load(f)
            response["translation"] = translation_data
        
        # Calculate overall score if both are available
        if response["speech_to_text"] and response["translation"]:
            stt_score = (response["speech_to_text"].get('f1_score', 0) + 
                        (1 - response["speech_to_text"].get('word_error_rate', 1))) / 2
            translation_score = (response["translation"].get('bleu_score', 0) + 
                               response["translation"].get('f1_score', 0)) / 2
            response["overall_score"] = (stt_score + translation_score) / 2
            
            # Add performance assessment
            if response["overall_score"] > 0.8:
                response["performance_assessment"] = "Excellent"
            elif response["overall_score"] > 0.6:
                response["performance_assessment"] = "Good"
            elif response["overall_score"] > 0.4:
                response["performance_assessment"] = "Fair"
            else:
                response["performance_assessment"] = "Poor"
        
        return response
        
    except Exception as e:
        return {"error": f"Failed to get evaluation metrics: {str(e)}"}

@app.post("/api/admin/run-evaluation")
async def run_evaluation():
    """Run model evaluation and return results"""
    try:
        from evaluation import create_sample_evaluation
        
        # Run evaluation in background
        stt_metrics, translation_metrics = create_sample_evaluation()
        
        # Calculate overall score
        stt_score = (stt_metrics.get('f1_score', 0) + (1 - stt_metrics.get('word_error_rate', 1))) / 2
        translation_score = (translation_metrics.get('bleu_score', 0) + translation_metrics.get('f1_score', 0)) / 2
        overall_score = (stt_score + translation_score) / 2
        
        return {
            "message": "Evaluation completed successfully",
            "speech_to_text": stt_metrics,
            "translation": translation_metrics,
            "overall_score": overall_score,
            "performance_assessment": (
                "Excellent" if overall_score > 0.8 else
                "Good" if overall_score > 0.6 else
                "Fair" if overall_score > 0.4 else
                "Poor"
            )
        }
        
    except Exception as e:
        return {"error": f"Failed to run evaluation: {str(e)}"}

@app.post("/api/admin/cleanup-empty-rooms")
async def cleanup_empty_rooms():
    """Manually trigger cleanup of empty rooms"""
    active_rooms = manager.get_active_rooms()
    cleaned_rooms = []
    
    for room_id in active_rooms.copy():  # Use copy to avoid modification during iteration
        participant_count = manager.get_room_participant_count(room_id)
        if participant_count == 0:
            await manager.close_room(room_id, "Manual cleanup - no participants")
            cleaned_rooms.append(room_id)
    
    return {
        "cleaned_rooms": cleaned_rooms,
        "message": f"Cleaned up {len(cleaned_rooms)} empty rooms"
    }

@app.post("/api/admin/create-sample-data")
async def create_sample_data(db: Session = Depends(get_db)):
    """Create sample users and rooms for testing"""
    try:
        # Create sample users
        sample_users = [
            CreateUserRequest(
                name="Alice Johnson",
                email="alice@example.com",
                profession="Teacher",
                password="password123",
                main_language="en"
            ),
            CreateUserRequest(
                name="Pierre Dubois",
                email="pierre@example.com", 
                profession="Engineer",
                password="password123",
                main_language="fr"
            ),
            CreateUserRequest(
                name="Sarah Wilson",
                email="sarah@example.com",
                profession="Doctor",
                password="password123", 
                main_language="en"
            )
        ]
        
        created_users = []
        for user_data in sample_users:
            try:
                user = UserService.create_user(db, user_data)
                created_users.append(user)
            except ValueError:
                # User already exists, get existing user
                user = UserService.get_user_by_email(db, user_data.email)
                if user:
                    created_users.append(user)
        
        # Create sample rooms
        sample_rooms = [
            CreateRoomRequest(
                name="Team Meeting",
                description="Weekly team sync in English and French"
            ),
            CreateRoomRequest(
                name="Project Discussion",
                description="Bilingual project planning session"
            )
        ]
        
        created_rooms = []
        for i, room_data in enumerate(sample_rooms):
            if created_users:
                room = RoomService.create_room(db, room_data, created_users[i % len(created_users)].id)
                created_rooms.append(room)
                
                # Add other users as participants
                for j, user in enumerate(created_users):
                    if j != i % len(created_users):  # Don't add creator again
                        RoomService.add_participant(
                            db, room.id, user.id,
                            user.main_language,
                            "fr" if user.main_language == "en" else "en"
                        )
        
        return {
            "message": "Sample data created successfully",
            "users": len(created_users),
            "rooms": len(created_rooms),
            "room_ids": [room.room_id for room in created_rooms]
        }
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 