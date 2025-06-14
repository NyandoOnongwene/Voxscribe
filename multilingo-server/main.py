from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
from datetime import datetime

from websocket_manager import manager
from whisper_engine import whisper_engine
from translator import text_translator
from utils import convert_audio_to_wav
from models import Message

app = FastAPI()

@app.get("/")
async def get():
    return HTMLResponse("<h1>Multilingo Server is running!</h1>")

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    # This is a simplified connection. In a real app, you'd authenticate the user.
    await manager.connect(websocket, room_id)
    print(f"User {user_id} connected to room {room_id}")
    
    try:
        while True:
            data = await websocket.receive_bytes()
            
            # 1. Convert audio chunk to WAV
            audio_array = convert_audio_to_wav(data)
            
            # 2. Transcribe
            transcription = whisper_engine.transcribe(audio_array)
            original_text = transcription["text"]
            detected_language = transcription["language"]
            
            if not original_text.strip():
                continue

            print(f"Transcription: {original_text} ({detected_language})")

            # In a real implementation, we would get participants' languages from the db
            # For now, let's assume a simple case
            
            # 3. Translate for recipients (dummy example)
            # This part needs to be connected to the ConvoRoom participants' data
            translated_text = text_translator.translate(original_text, detected_language, "es") # translate to Spanish
            
            # 4. Create and broadcast message
            message = Message(
                speaker=user_id,
                original_text=original_text,
                language=detected_language,
                translated_text=translated_text,
                recipient_language="es", # This should be dynamic per participant
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            await manager.broadcast(message.json(), room_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        print(f"User {user_id} disconnected from room {room_id}")
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
        manager.disconnect(websocket, room_id) 