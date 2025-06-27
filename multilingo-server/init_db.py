#!/usr/bin/env python3
"""
Database initialization script for Voxscribe
This script creates the database schema and optionally seeds with sample data
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import DatabaseManager, get_db_session
from db_services import UserService, RoomService
from models import CreateUserRequest, CreateRoomRequest

def create_sample_data():
    """Create sample users and rooms for testing"""
    db = get_db_session()
    
    try:
        print("Creating sample data...")
        
        # Create sample users
        sample_users = [
            CreateUserRequest(
                name="Alice Johnson",
                email="alice@example.com", 
                password="password123",
                profession="Software Engineer",
                main_language="en"
            ),
            CreateUserRequest(
                name="Bob García",
                email="bob@example.com",
                password="password123", 
                profession="Product Manager",
                main_language="es"
            ),
            CreateUserRequest(
                name="Claire Dubois",
                email="claire@example.com",
                password="password123",
                profession="Designer", 
                main_language="fr"
            )
        ]
        
        created_users = []
        for user_data in sample_users:
            try:
                user = UserService.create_user(db, user_data)
                created_users.append(user)
                print(f"✅ Created user: {user.name} ({user.email})")
            except ValueError as e:
                print(f"⚠️ User {user_data.email} already exists, skipping...")
                # Get existing user
                user = UserService.get_user_by_email(db, user_data.email)
                if user:
                    created_users.append(user)
        
        # Create sample rooms
        if created_users:
            sample_rooms = [
                CreateRoomRequest(
                    name="Team Standup",
                    description="Daily team standup meeting"
                ),
                CreateRoomRequest(
                    name="Client Meeting",
                    description="Meeting with international clients"
                ),
                CreateRoomRequest(
                    name="Project Discussion",
                    description="Technical project discussion"
                )
            ]
            
            for i, room_data in enumerate(sample_rooms):
                creator = created_users[i % len(created_users)]
                room = RoomService.create_room(db, room_data, creator.id)
                print(f"✅ Created room: {room.name} (ID: {room.room_id})")
                
                # Add other users to the room
                for j, user in enumerate(created_users):
                    if user.id != creator.id:
                        # Set different target languages for demonstration
                        target_languages = ["en", "es", "fr"]
                        target_lang = target_languages[j % len(target_languages)]
                        
                        success = RoomService.add_participant(
                            db, room.id, user.id, 
                            user.main_language, target_lang
                        )
                        if success:
                            print(f"  ✅ Added {user.name} to room (translating to {target_lang})")
        
        print("\n🎉 Sample data created successfully!")
        print("\nSample users created:")
        for user in created_users:
            print(f"  - {user.name} ({user.email}) - Language: {user.main_language}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing Voxscribe Database...")
    print("=" * 50)
    
    # Check database connection
    if not DatabaseManager.check_connection():
        print("❌ Cannot connect to database. Please check your configuration.")
        return
    
    # Initialize database schema
    try:
        DatabaseManager.init_db()
        print("✅ Database schema initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return
    
    # Ask user if they want to create sample data
    print("\n" + "=" * 50)
    create_samples = input("Do you want to create sample data for testing? (y/N): ").lower().strip()
    
    if create_samples in ['y', 'yes']:
        create_sample_data()
    else:
        print("Skipping sample data creation.")
    
    print("\n" + "=" * 50)
    print("🎉 Database initialization complete!")
    print("\nYou can now start the Voxscribe server with:")
    print("  python main.py")
    print("\nOr use uvicorn:")
    print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main() 