# Voxscribe Database Schema Documentation

## Overview

Voxscribe uses SQLite as its database engine with SQLAlchemy ORM for Python integration. The database stores users, conversation rooms, audio transcriptions, translations, and messages.

## Database Structure

### Core Tables

#### 1. `users`
Stores user account information and preferences.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique user identifier |
| name | VARCHAR(100) | NOT NULL | User's display name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| profession | VARCHAR(100) | NULLABLE | User's profession/title |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| main_language | VARCHAR(10) | NOT NULL, DEFAULT 'en' | User's primary language |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | DATETIME | DEFAULT NOW() | Account creation timestamp |
| updated_at | DATETIME | ON UPDATE NOW() | Last update timestamp |

#### 2. `conversation_rooms`
Stores conversation room details and metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Internal room ID |
| room_id | VARCHAR(50) | UNIQUE, NOT NULL | External room identifier |
| name | VARCHAR(255) | NOT NULL | Room display name |
| description | TEXT | NULLABLE | Room description |
| is_active | BOOLEAN | DEFAULT TRUE | Room status |
| created_by | INTEGER | FOREIGN KEY → users.id | Room creator |
| created_at | DATETIME | DEFAULT NOW() | Creation timestamp |
| updated_at | DATETIME | ON UPDATE NOW() | Last update timestamp |

#### 3. `transcriptions`
Stores audio transcription results from Whisper.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique transcription ID |
| user_id | INTEGER | FOREIGN KEY → users.id | Speaker user |
| room_id | INTEGER | FOREIGN KEY → conversation_rooms.id | Associated room |
| original_text | TEXT | NOT NULL | Transcribed text |
| detected_language | VARCHAR(10) | NOT NULL | Language detected by Whisper |
| confidence_score | VARCHAR(10) | NULLABLE | Whisper confidence score |
| audio_duration | VARCHAR(20) | NULLABLE | Audio duration in seconds |
| timestamp | DATETIME | DEFAULT NOW() | Transcription timestamp |

#### 4. `translations`
Stores translations of transcriptions into different languages.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique translation ID |
| transcription_id | INTEGER | FOREIGN KEY → transcriptions.id | Source transcription |
| target_language | VARCHAR(10) | NOT NULL | Target language code |
| translated_text | TEXT | NOT NULL | Translated text |
| translation_service | VARCHAR(50) | NULLABLE | Translation service used |
| created_at | DATETIME | DEFAULT NOW() | Translation timestamp |

#### 5. `messages`
Stores formatted messages for the conversation UI.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique message ID |
| user_id | INTEGER | FOREIGN KEY → users.id | Message sender |
| room_id | INTEGER | FOREIGN KEY → conversation_rooms.id | Associated room |
| transcription_id | INTEGER | FOREIGN KEY → transcriptions.id | Source transcription |
| speaker_name | VARCHAR(100) | NOT NULL | Speaker display name |
| original_text | TEXT | NOT NULL | Original text |
| original_language | VARCHAR(10) | NOT NULL | Original language |
| translated_text | TEXT | NULLABLE | Translated text (if applicable) |
| target_language | VARCHAR(10) | NULLABLE | Target language (if translated) |
| message_type | VARCHAR(20) | DEFAULT 'transcription' | Message type |
| timestamp | DATETIME | DEFAULT NOW() | Message timestamp |

#### 6. `audio_files` (Optional)
Stores audio file metadata for uploaded files.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique file ID |
| transcription_id | INTEGER | FOREIGN KEY → transcriptions.id | Associated transcription |
| file_path | VARCHAR(500) | NOT NULL | File storage path |
| file_name | VARCHAR(255) | NOT NULL | Original filename |
| file_size | INTEGER | NULLABLE | File size in bytes |
| duration | VARCHAR(20) | NULLABLE | Audio duration |
| format | VARCHAR(10) | NULLABLE | Audio format (wav, mp3, etc.) |
| uploaded_at | DATETIME | DEFAULT NOW() | Upload timestamp |

### Association Tables

#### 7. `user_room_participants`
Many-to-many relationship between users and rooms with language preferences.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | PRIMARY KEY, FOREIGN KEY → users.id | Participant user |
| room_id | INTEGER | PRIMARY KEY, FOREIGN KEY → conversation_rooms.id | Associated room |
| preferred_language | VARCHAR(10) | NOT NULL | User's preferred input language |
| translate_to_language | VARCHAR(10) | NOT NULL | User's target translation language |
| joined_at | DATETIME | DEFAULT NOW() | Join timestamp |

## Relationships

### Entity Relationship Diagram

```
users (1) ←→ (M) user_room_participants (M) ←→ (1) conversation_rooms
users (1) ←→ (M) transcriptions (M) ←→ (1) conversation_rooms
users (1) ←→ (M) messages (M) ←→ (1) conversation_rooms
transcriptions (1) ←→ (M) translations
transcriptions (1) ←→ (M) messages
transcriptions (1) ←→ (M) audio_files
```

### Key Relationships

1. **Users ↔ Rooms**: Many-to-many through `user_room_participants`
2. **Rooms ↔ Transcriptions**: One room can have many transcriptions
3. **Transcriptions ↔ Translations**: One transcription can have multiple translations
4. **Transcriptions ↔ Messages**: One transcription can generate multiple messages (one per participant language)
5. **Users ↔ Messages**: One user can create many messages

## Language Codes

The system uses ISO 639-1 language codes:

| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| fr | French |
| de | German |
| it | Italian |
| pt | Portuguese |
| zh | Chinese |
| ja | Japanese |
| ko | Korean |
| ar | Arabic |

## Usage Examples

### Creating a User
```python
from db_services import UserService
from models import CreateUserRequest

user_data = CreateUserRequest(
    name="John Doe",
    email="john@example.com",
    password="secure_password",
    profession="Developer",
    main_language="en"
)

user = UserService.create_user(db, user_data)
```

### Creating a Room
```python
from db_services import RoomService
from models import CreateRoomRequest

room_data = CreateRoomRequest(
    name="Team Meeting",
    description="Weekly team standup"
)

room = RoomService.create_room(db, room_data, creator_id=1)
```

### Adding Participants
```python
# Add user to room with language preferences
RoomService.add_participant(
    db=db,
    room_id=room.id,
    user_id=2,
    preferred_language="es",  # Speaks Spanish
    translate_to_language="en"  # Wants English translations
)
```

### Storing Transcriptions
```python
from db_services import TranscriptionService

transcription = TranscriptionService.create_transcription(
    db=db,
    user_id=1,
    room_id="abc123",
    original_text="Hello, how are you?",
    detected_language="en",
    confidence_score="0.95"
)

# Add translation
TranscriptionService.add_translation(
    db=db,
    transcription_id=transcription.id,
    target_language="es",
    translated_text="Hola, ¿cómo estás?",
    translation_service="deep-translator"
)
```

## Database Initialization

### Setup Commands

```bash
# Initialize database with tables
python init_db.py

# Or use the API endpoint (development)
curl -X POST http://localhost:8000/api/admin/init-db

# Reset database (WARNING: Deletes all data)
curl -X POST http://localhost:8000/api/admin/reset-db
```

### Environment Variables

```bash
# Optional: Set custom database URL
export DATABASE_URL="sqlite:///./custom_voxscribe.db"

# For production, you might use PostgreSQL:
# export DATABASE_URL="postgresql://user:password@localhost/voxscribe"
```

## Performance Considerations

### Indexes
The schema includes automatic indexes on:
- Primary keys (all tables)
- Foreign keys (all relationships)
- Unique constraints (`users.email`, `conversation_rooms.room_id`)

### Query Optimization
- Use `joinedload()` for related data to avoid N+1 queries
- Limit results for message/transcription lists
- Consider pagination for large datasets

### Maintenance
- Regular VACUUM operations for SQLite
- Monitor database size growth
- Consider archiving old transcriptions/messages

## Security Considerations

1. **Password Security**: Passwords are hashed using bcrypt
2. **SQL Injection**: Protected by SQLAlchemy ORM parameterization
3. **Foreign Key Constraints**: Enabled for data integrity
4. **Access Control**: Implement authentication/authorization at application level

## Migration Strategy

For schema changes:
1. Create new migration script
2. Test on development database
3. Backup production data
4. Apply migration
5. Verify data integrity

## Backup Strategy

### SQLite Backup
```bash
# Create backup
sqlite3 voxscribe.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore from backup
sqlite3 voxscribe.db ".restore backup_file.db"
```

### Automated Backup
Consider implementing scheduled backups for production environments. 