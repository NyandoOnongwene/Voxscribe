from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Track which user owns which websocket connection
        self.user_connections: Dict[str, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: int = None):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.user_connections[room_id] = {}
        self.active_connections[room_id].append(websocket)
        if user_id:
            self.user_connections[room_id][user_id] = websocket
        
        print(f"User {user_id} connected to room {room_id}. Room now has {len(self.active_connections[room_id])} participants.")

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: int = None):
        if room_id in self.active_connections:
            try:
                if websocket in self.active_connections[room_id]:
                    self.active_connections[room_id].remove(websocket)
            except ValueError:
                # WebSocket already removed, ignore
                pass
            
            # Remove user-specific connection
            if user_id and room_id in self.user_connections and user_id in self.user_connections[room_id]:
                del self.user_connections[room_id][user_id]
            
            # Check if room is now empty and clean up
            self._cleanup_empty_room(room_id)
            
            remaining_count = len(self.active_connections.get(room_id, []))
            print(f"User {user_id} disconnected from room {room_id}. Room now has {remaining_count} participants.")

    def _cleanup_empty_room(self, room_id: str):
        """Clean up room if it has no active connections"""
        if room_id in self.active_connections:
            if not self.active_connections[room_id]:
                print(f"🔴 Closing empty room {room_id} - no participants remaining")
                del self.active_connections[room_id]
                if room_id in self.user_connections:
                    del self.user_connections[room_id]
                return True
        return False

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Failed to send personal message: {e}")

    async def send_to_user(self, message: str, room_id: str, user_id: int):
        """Send message to a specific user in a room"""
        if room_id in self.user_connections and user_id in self.user_connections[room_id]:
            try:
                await self.user_connections[room_id][user_id].send_text(message)
            except Exception as e:
                print(f"Failed to send message to user {user_id}: {e}")
                # Remove broken connection
                await self._remove_broken_connection(room_id, user_id)

    async def _remove_broken_connection(self, room_id: str, user_id: int):
        """Remove a broken connection and clean up if room becomes empty"""
        if room_id in self.user_connections and user_id in self.user_connections[room_id]:
            broken_websocket = self.user_connections[room_id][user_id]
            del self.user_connections[room_id][user_id]
            
            # Remove from active connections
            if room_id in self.active_connections and broken_websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(broken_websocket)
            
            # Check if room is now empty
            self._cleanup_empty_room(room_id)

    async def broadcast(self, message: str, room_id: str):
        if room_id in self.active_connections:
            disconnected_connections = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Failed to send message to connection: {e}")
                    disconnected_connections.append(connection)
            
            # Remove disconnected connections safely
            for connection in disconnected_connections:
                try:
                    if connection in self.active_connections[room_id]:
                        self.active_connections[room_id].remove(connection)
                        
                        # Also remove from user_connections
                        if room_id in self.user_connections:
                            for user_id, ws in list(self.user_connections[room_id].items()):
                                if ws == connection:
                                    del self.user_connections[room_id][user_id]
                                    break
                except ValueError:
                    # Connection already removed, ignore
                    pass
            
            # Clean up empty room after removing broken connections
            self._cleanup_empty_room(room_id)

    def get_room_participant_count(self, room_id: str) -> int:
        """Get the number of active participants in a room"""
        return len(self.active_connections.get(room_id, []))

    def get_active_rooms(self) -> List[str]:
        """Get list of active room IDs"""
        return list(self.active_connections.keys())

    async def close_room(self, room_id: str, reason: str = "Room closed"):
        """Forcefully close a room and disconnect all participants"""
        if room_id in self.active_connections:
            connections_to_close = self.active_connections[room_id].copy()
            print(f"🔴 Closing room {room_id} with {len(connections_to_close)} participants. Reason: {reason}")
            
            # Close all connections
            for connection in connections_to_close:
                try:
                    await connection.close(code=1000, reason=reason)
                except Exception as e:
                    print(f"Error closing connection: {e}")
            
            # Clean up the room
            self.active_connections[room_id] = []
            if room_id in self.user_connections:
                self.user_connections[room_id] = {}
            
            self._cleanup_empty_room(room_id)

manager = ConnectionManager() 