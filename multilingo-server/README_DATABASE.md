# Voxscribe Database Implementation

## Overview

This document provides instructions for setting up and using the SQLite database for the Voxscribe real-time transcription and translation application.

## Quick Start

### 1. Initialize the Database

```bash
# Navigate to the server directory
cd multilingo-server

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py
```

When prompted, choose 'y' to create sample data for testing.

### 2. Verify Installation

```bash
# Verify database structure and data
python verify_db.py
```

This will show you all tables, sample users, rooms, and participants.

### 3. Start the Server

```bash
# Start the FastAPI server
python main.py

# Or use uvicorn with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Database Schema

The database includes the following tables:

- **users** - User accounts and profiles
- **conversation_rooms** - Chat rooms for transcription sessions  
- **user_room_participants** - Many-to-many relationship with language preferences
- **transcriptions** - Audio transcription results from Whisper
- **translations** - Translated versions of transcriptions
- **messages** - Formatted messages for the chat UI
- **audio_files** - Metadata for uploaded audio files

For detailed schema documentation, see [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md).

## API Endpoints

### User Management
- `POST /api/users/register` - Register a new user
- `GET /api/users/{user_id}` - Get user details

### Room Management  
- `POST /api/rooms` - Create a conversation room
- `GET /api/rooms/{room_id}` - Get room details
- `POST /api/rooms/{room_id}/join` - Join a room
- `GET /api/rooms/{room_id}/participants` - Get room participants

### Messages & Transcriptions
- `GET /api/rooms/{room_id}/messages` - Get room messages
- `GET /api/rooms/{room_id}/transcriptions` - Get room transcriptions

### WebSocket
- `WS /ws/{room_id}/{user_id}` - Real-time audio transcription

### Admin (Development)
- `POST /api/admin/init-db` - Initialize database
- `POST /api/admin/reset-db` - Reset database

## Sample Data

The initialization script creates three sample users:

1. **Alice Johnson** (alice@example.com) - English, Software Engineer
2. **Bob García** (bob@example.com) - Spanish, Product Manager  
3. **Claire Dubois** (claire@example.com) - French, Designer

And three conversation rooms:
- Team Standup
- Client Meeting
- Project Discussion

## Database Files

- `voxscribe.db` - Main SQLite database file
- `db.py` - Database configuration and connection
- `models.py` - SQLAlchemy models and Pydantic schemas
- `db_services.py` - Database service functions
- `init_db.py` - Database initialization script
- `verify_db.py` - Database verification script

## API Usage Examples

### Register a User

```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com", 
    "password": "secure_password",
    "profession": "Developer",
    "main_language": "en"
  }'
```

### Create a Room

```bash
curl -X POST "http://localhost:8000/api/rooms?creator_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Meeting",
    "description": "A test meeting room"
  }'
```

### Join a Room

```bash
curl -X POST "http://localhost:8000/api/rooms/{room_id}/join?user_id=2" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_language": "es",
    "translate_to_language": "en"
  }'
```

## Real-time Transcription Flow

1. **Connect**: Client connects to WebSocket endpoint with room and user ID
2. **Audio**: Client sends audio chunks as binary data
3. **Transcribe**: Server uses Whisper to transcribe audio
4. **Translate**: Server translates text for each participant's target language
5. **Store**: Transcriptions, translations, and messages saved to database
6. **Broadcast**: Formatted messages sent to all room participants

## Development

### Database Reset

⚠️ **Warning**: This will delete all data!

```bash
python -c "from db import DatabaseManager; DatabaseManager.reset_db()"
```

Or via API:
```bash
curl -X POST "http://localhost:8000/api/admin/reset-db"
```

### Environment Variables

```bash
# Custom database location
export DATABASE_URL="sqlite:///./custom_voxscribe.db"

# For production, consider PostgreSQL:
# export DATABASE_URL="postgresql://user:password@localhost/voxscribe"
```

### Backup Database

```bash
# Create backup
sqlite3 voxscribe.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore from backup  
sqlite3 voxscribe.db ".restore backup_file.db"
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

2. **Database connection failed**: Check that you're in the correct directory and have write permissions

3. **Foreign key errors**: SQLite foreign key constraints are enabled - ensure referenced records exist

4. **Port already in use**: Change the port in `main.py` or kill the existing process

### Debugging

Enable SQL query logging:
```python
# In db.py, change:
echo=False  # to echo=True
```

Check database tables directly:
```bash
sqlite3 voxscribe.db
.tables
.schema users
SELECT * FROM users;
.quit
```

## Production Considerations

1. **Database**: Consider PostgreSQL for production
2. **Authentication**: Implement proper JWT-based authentication
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Monitoring**: Set up logging and monitoring
5. **Backups**: Implement automated backup strategy
6. **Security**: Use HTTPS and validate all inputs

## Support

For questions or issues:
1. Check the [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for detailed schema information
2. Run `python verify_db.py` to check database state
3. Review the FastAPI automatic documentation at `http://localhost:8000/docs` 