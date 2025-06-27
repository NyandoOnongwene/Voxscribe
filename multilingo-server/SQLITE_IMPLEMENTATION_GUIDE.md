# SQLite Implementation Guide for Voxscribe

## Overview

This document explains the SQLite database implementation in the Voxscribe real-time transcription application, including architectural decisions, optimizations, and implementation details.

## Architecture Overview

### Technology Stack
- **Database Engine**: SQLite 3.x
- **ORM Framework**: SQLAlchemy 2.0+
- **Python Framework**: FastAPI
- **Connection Pool**: SQLAlchemy StaticPool
- **Authentication**: bcrypt password hashing

### Why SQLite?

**Advantages for Voxscribe:**
1. **Zero Configuration**: No separate database server required
2. **ACID Compliance**: Reliable transactions for transcription data
3. **Cross-Platform**: Works identically on Windows, macOS, and Linux
4. **Lightweight**: Perfect for development and small to medium deployments
5. **File-Based**: Easy backup, migration, and version control
6. **SQL Standard**: Full SQL support with proper foreign key constraints

**Trade-offs:**
- Single writer limitation (acceptable for transcription workload)
- Limited concurrent write performance
- No built-in replication (can use external tools)

## Database Design Patterns

### 1. Entity-Relationship Model

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Users    │    │ UserRoomParticip │    │ConversationRooms│
│             │───┼│                  │┼───│                 │
│ - id (PK)   │    │ - user_id (FK)   │    │ - id (PK)       │
│ - email (UK)│    │ - room_id (FK)   │    │ - room_id (UK)  │
│ - password  │    │ - languages      │    │ - created_by    │
└─────────────┘    └──────────────────┘    └─────────────────┘
       │                                           │
       │                                           │
   ┌───▼────────┐                              ┌───▼─────────┐
   │Transcriptio│                              │  Messages   │
   │            │                              │             │
   │ - id (PK)  │──┐                          │ - id (PK)   │
   │ - user_id  │  │                          │ - user_id   │
   │ - room_id  │  │                          │ - room_id   │
   │ - text     │  │                          │ - transcript│
   └────────────┘  │                          └─────────────┘
                   │
              ┌────▼────────┐
              │Translations │
              │             │
              │ - id (PK)   │
              │ - trans_id  │
              │ - language  │
              │ - text      │
              └─────────────┘
```

### 2. Service Layer Pattern

The implementation uses a **Service Layer Pattern** to separate business logic from data access:

```python
# Service Layer (Business Logic)
class UserService:
    @staticmethod
    def create_user(db: Session, user_data: CreateUserRequest) -> User:
        # Business logic: validation, password hashing
        # Data access: SQLAlchemy operations

# Data Access Layer (ORM Models)  
class User(Base):
    __tablename__ = "users"
    # Table definition and relationships

# API Layer (FastAPI endpoints)
@app.post("/api/users/register")
async def register_user(user_data: CreateUserRequest, db: Session = Depends(get_db)):
    # HTTP handling, delegating to service layer
```

## SQLAlchemy Implementation Details

### 1. Database Configuration

```python
# db.py
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voxscribe.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Allow multiple threads
    poolclass=StaticPool,                       # Single connection pool
    echo=False                                  # Set True for SQL logging
)

# Enable foreign key constraints (SQLite specific)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if 'sqlite' in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

**Key Configurations:**
- **`check_same_thread=False`**: Allows FastAPI's thread pool to use the connection
- **`StaticPool`**: Maintains a single connection for SQLite (optimal for file-based DB)
- **Foreign key constraints**: Enabled via PRAGMA for data integrity
- **Echo parameter**: Controls SQL query logging for debugging

### 2. Model Definitions

```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    # Primary key with auto-increment
    id = Column(Integer, primary_key=True, index=True)
    
    # Unique constraint with index for fast lookups
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Automatic timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships with lazy loading
    conversation_rooms = relationship(
        "ConversationRoom", 
        secondary=user_room_association, 
        back_populates="participants"
    )
```

### 3. Real-time Transcription Flow

```python
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """Real-time transcription with database persistence"""
    db = next(get_db())  # Get database session
    
    try:
        while True:
            # 1. Receive audio data
            audio_data = await websocket.receive_bytes()
            
            # 2. Transcribe with Whisper
            transcription_result = whisper_engine.transcribe(audio_data)
            
            # 3. Save transcription (Transaction)
            db_transcription = TranscriptionService.create_transcription(
                db=db, user_id=int(user_id), room_id=room_id,
                original_text=transcription_result["text"],
                detected_language=transcription_result["language"]
            )
            
            # 4. Create translations and messages
            participants = RoomService.get_room_participants(db, room_id)
            for participant in participants:
                # Translate and save to database
                # Broadcast to participants
    finally:
        db.close()  # Ensure connection cleanup
```

## Performance Optimizations

### 1. Query Optimization

**Eager Loading for Related Data:**
```python
def get_room_transcriptions(db: Session, room_id: str, limit: int = 50):
    """Optimized query with eager loading"""
    return db.query(Transcription)\
        .filter(Transcription.room_id == room.id)\
        .options(joinedload(Transcription.translations))\  # Avoid N+1 queries
        .order_by(Transcription.timestamp.desc())\
        .limit(limit)\
        .all()
```

### 2. SQLite-Specific Optimizations

**PRAGMA Settings:**
```python
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")        # Data integrity
    cursor.execute("PRAGMA journal_mode=WAL")       # Write-Ahead Logging
    cursor.execute("PRAGMA synchronous=NORMAL")     # Performance vs safety
    cursor.execute("PRAGMA cache_size=1000")        # Memory cache
    cursor.close()
```

## Security Implementation

### 1. Password Security

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
```

### 2. SQL Injection Prevention

SQLAlchemy ORM automatically prevents SQL injection through parameterized queries:

```python
# Safe - SQLAlchemy handles parameterization
user = db.query(User).filter(User.email == email).first()

# Safe - Using SQLAlchemy text() with parameters
from sqlalchemy import text
result = db.execute(
    text("SELECT * FROM users WHERE email = :email"), 
    {"email": email}
)
```

## Database Schema Features

### 1. Foreign Key Relationships

- **One-to-Many**: User → Transcriptions, Room → Messages
- **Many-to-Many**: Users ↔ Rooms (with language preferences)
- **Cascading Deletes**: Remove dependent data when parent is deleted

### 2. Indexing Strategy

- **Primary Keys**: Automatic clustering indexes
- **Foreign Keys**: Automatic indexes for joins
- **Unique Constraints**: Email addresses, room IDs
- **Composite Keys**: User-room participation table

### 3. Data Integrity

- **NOT NULL constraints**: Required fields enforced
- **Foreign key constraints**: Referential integrity
- **Unique constraints**: Prevent duplicate data
- **Check constraints**: Can be added for data validation

## Transaction Management

### Auto-commit Pattern (Used in services):
```python
def create_transcription(db: Session, ...):
    db_transcription = Transcription(...)
    db.add(db_transcription)
    db.commit()                    # Immediate commit
    db.refresh(db_transcription)   # Refresh with generated ID
    return db_transcription
```

### Manual Transaction Pattern (For complex operations):
```python
def complex_operation(db: Session, ...):
    try:
        # Multiple operations
        user = create_user(...)
        room = create_room(...)
        add_participant(...)
        
        db.commit()  # Commit all or nothing
    except Exception as e:
        db.rollback()  # Rollback on error
        raise e
```

## Error Handling

```python
def create_user(db: Session, user_data: CreateUserRequest) -> User:
    try:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        db_user = User(...)
        db.add(db_user)
        db.commit()
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database constraint violation: {e}")
    except Exception as e:
        db.rollback()
        raise e
```

## Backup and Migration

### Backup Strategy:
```bash
# Create backup
sqlite3 voxscribe.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore from backup  
sqlite3 voxscribe.db ".restore backup_file.db"
```

### Migration Example:
```python
def migrate_v1_to_v2():
    """Example migration script"""
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR(50)"))
        conn.execute(text("UPDATE users SET timezone = 'UTC' WHERE timezone IS NULL"))
        conn.commit()
```

## Production Considerations

1. **Database Location**: Use absolute paths in production
2. **Backup Strategy**: Automated daily backups
3. **Monitoring**: Track database size and query performance
4. **Connection Pooling**: Configure appropriate pool sizes
5. **WAL Mode**: Enable Write-Ahead Logging for better concurrency
6. **PostgreSQL Migration**: Consider when scaling beyond SQLite limits

## Conclusion

The SQLite implementation provides a robust foundation with:
- **ACID compliance** for data reliability
- **Optimized performance** with proper indexing
- **Security measures** including password hashing
- **Clean architecture** with service layer separation
- **Easy deployment** with minimal dependencies

This design scales effectively for real-time transcription workloads while maintaining data integrity and performance. 