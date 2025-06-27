# Voxscribe Database Schema - Simple Overview

## Core Tables

### 👤 **User**
- **Purpose**: Store user accounts and authentication
- **Key Fields**: `id`, `email`, `password_hash`, `main_language`
- **Relationships**: Creates rooms, makes transcriptions, sends messages

### 🏠 **ConversationRoom** 
- **Purpose**: Chat rooms for transcription sessions
- **Key Fields**: `id`, `room_id`, `name`, `created_by`
- **Relationships**: Has participants, contains transcriptions and messages

### 👥 **UserRoomParticipants**
- **Purpose**: Links users to rooms with language preferences
- **Key Fields**: `user_id`, `room_id`, `preferred_language`, `translate_to_language`
- **Relationships**: Many-to-many bridge between users and rooms

### 🎙️ **Transcription**
- **Purpose**: Store audio transcription results from Whisper AI
- **Key Fields**: `id`, `original_text`, `detected_language`, `confidence_score`
- **Relationships**: Belongs to user and room, has multiple translations

### 🌐 **Translation**
- **Purpose**: Store translated versions of transcriptions
- **Key Fields**: `id`, `target_language`, `translated_text`, `translation_service`
- **Relationships**: Belongs to one transcription

### 💬 **Message**
- **Purpose**: Formatted chat messages for the UI
- **Key Fields**: `id`, `original_text`, `translated_text`, `speaker_name`
- **Relationships**: Links user, room, and transcription data

### 🎵 **AudioFile**
- **Purpose**: Metadata for uploaded audio files
- **Key Fields**: `id`, `file_path`, `file_name`, `file_size`, `format`
- **Relationships**: Belongs to one transcription

## Key Relationships

```
User ←→ Room (many-to-many via UserRoomParticipants)
  ↓
User → Transcription (one-to-many)
  ↓
Transcription → Translation (one-to-many)
  ↓
Transcription → Message (one-to-many)
```

## Data Flow

1. **User joins Room** → Record in `UserRoomParticipants` with language preferences
2. **Audio received** → Create `Transcription` with Whisper AI results  
3. **Text translated** → Create `Translation` for each participant's target language
4. **UI message** → Create `Message` with formatted content for chat display
5. **Audio saved** → Create `AudioFile` record with metadata

## Language Support

- **Input Languages**: User's `preferred_language` (what they speak)
- **Output Languages**: User's `translate_to_language` (what they want to see)
- **Language Codes**: ISO 639-1 format (en, es, fr, de, etc.)

## Key Features

- **Real-time**: WebSocket connection for live transcription
- **Multi-language**: Automatic translation for each participant
- **Persistent**: All transcriptions and translations saved
- **Secure**: bcrypt password hashing, SQL injection protection
- **Scalable**: Optimized queries with proper indexing 