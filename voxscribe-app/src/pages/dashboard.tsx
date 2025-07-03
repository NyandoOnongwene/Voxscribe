import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';

interface Room {
  room_id: string;
  name: string;
  description?: string;
  created_at: string;
  joined_at: string;
  message_count: number;
  last_activity?: string;
  preferred_language: string;
  translate_to_language: string;
}

interface User {
  id: number;
  name: string;
  email: string;
  profession?: string;
  main_language: string;
}

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [createRoomData, setCreateRoomData] = useState({
    name: '',
    description: ''
  });
  const [joinRoomData, setJoinRoomData] = useState({
    room_id: '',
    preferred_language: 'en',
    translate_to_language: 'en'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'fr', name: 'French' },
  ];

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = localStorage.getItem('user');
      if (!userData) {
        navigate('/login');
        return;
      }

      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      
      // Load user's rooms
      await loadUserRooms(parsedUser.id);
    } catch (error) {
      console.error('Error loading user data:', error);
      navigate('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserRooms = async (userId: number) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/users/${userId}/rooms`);
      if (response.ok) {
        const data = await response.json();
        setRooms(data.rooms || []);
      }
    } catch (error) {
      console.error('Error loading rooms:', error);
    }
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setError('');
    setSuccess('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/rooms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: createRoomData.name,
          description: createRoomData.description,
          creator_id: user.id
        }),
      });

      if (response.ok) {
        const roomData = await response.json();
        setSuccess('Room created successfully!');
        setShowCreateModal(false);
        setCreateRoomData({ name: '', description: '' });
        
        // Reload rooms list
        await loadUserRooms(user.id);
        
        // Navigate to the new room
        navigate(`/room/${roomData.room_id}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create room');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleJoinRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setError('');
    setSuccess('');

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/rooms/${joinRoomData.room_id}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          preferred_language: joinRoomData.preferred_language,
          translate_to_language: joinRoomData.translate_to_language
        }),
      });

      if (response.ok) {
        setSuccess('Successfully joined room!');
        setShowJoinModal(false);
        const currentRoomId = joinRoomData.room_id;
        setJoinRoomData({ room_id: '', preferred_language: 'en', translate_to_language: 'en' });
        
        // Reload rooms and navigate to joined room
        await loadUserRooms(user.id);
        navigate(`/room/${currentRoomId}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to join room');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleRoomClick = (roomId: string) => {
    navigate(`/room/${roomId}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    navigate('/login');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getLanguageName = (code: string) => {
    return languages.find(lang => lang.code === code)?.name || code;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 dark:bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Voxscribe</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-gray-700 dark:text-gray-300">Welcome, {user?.name}</span>
              <ThemeToggle />
              <button
                onClick={handleLogout}
                className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success/Error Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 rounded-md">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 border border-green-400 dark:border-green-600 text-green-700 dark:text-green-300 rounded-md">
            {success}
          </div>
        )}

        {/* Dashboard Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h2>
          <p className="text-gray-600 dark:text-gray-400">Manage your conversation rooms and view transcription history</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Create New Room</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">Start a new conversation room for real-time transcription</p>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Create Room
            </button>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Join Existing Room</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">Join a conversation room using a room ID</p>
              </div>
              <button
                onClick={() => setShowJoinModal(true)}
                className="bg-green-600 dark:bg-green-700 hover:bg-green-700 dark:hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Join Room
            </button>
            </div>
          </div>
        </div>

        {/* Room History */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Your Conversation Rooms</h3>
          </div>
          
          {rooms.length === 0 ? (
            <div className="p-12 text-center">
              <svg className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p className="text-gray-500 dark:text-gray-400 text-lg font-medium mb-2">No conversation rooms yet</p>
              <p className="text-gray-400 dark:text-gray-500 text-sm mb-6">Create your first room or join an existing one to get started</p>
              <div className="space-x-4">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Create Room
                </button>
                <button
                  onClick={() => setShowJoinModal(true)}
                  className="bg-gray-600 dark:bg-gray-700 hover:bg-gray-700 dark:hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Join Room
                </button>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {rooms.map((room) => (
                <div
                  key={room.room_id}
                  onClick={() => handleRoomClick(room.room_id)}
                  className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mr-3">{room.name}</h4>
                        <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          {room.room_id}
                        </span>
                      </div>
                      {room.description && (
                        <p className="text-gray-600 dark:text-gray-400 mt-1">{room.description}</p>
                      )}
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                        <span>Joined: {formatDate(room.joined_at)}</span>
                        <span>•</span>
                        <span>{room.message_count} messages</span>
                        {room.last_activity && (
                          <>
                            <span>•</span>
                            <span>Last activity: {formatDate(room.last_activity)}</span>
                          </>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 mt-1 text-xs text-gray-400 dark:text-gray-500">
                        <span>Language: {getLanguageName(room.translate_to_language)}</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <svg className="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create Room Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create New Room</h3>
            <form onSubmit={handleCreateRoom}>
              <div className="mb-4">
                <label htmlFor="roomName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Room Name *
                </label>
                <input
                  id="roomName"
                  type="text"
                  value={createRoomData.name}
                  onChange={(e) => setCreateRoomData({ ...createRoomData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400"
                  placeholder="Enter room name"
                  required
                />
              </div>
              <div className="mb-6">
                <label htmlFor="roomDescription" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  id="roomDescription"
                  value={createRoomData.description}
                  onChange={(e) => setCreateRoomData({ ...createRoomData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400"
                  placeholder="Enter room description"
                  rows={3}
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
                >
                  Create Room
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Room Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Join Room</h3>
            <form onSubmit={handleJoinRoom}>
              <div className="mb-4">
                <label htmlFor="roomId" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Room ID *
                </label>
                <input
                  id="roomId"
                  type="text"
                  value={joinRoomData.room_id}
                  onChange={(e) => setJoinRoomData({ ...joinRoomData, room_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400"
                  placeholder="Enter room ID"
                  required
                />
              </div>
              <div className="mb-4">
                <label htmlFor="translateTo" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Translate to Language *
                </label>
                <select
                  id="translateTo"
                  value={joinRoomData.translate_to_language}
                  onChange={(e) => setJoinRoomData({ ...joinRoomData, translate_to_language: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400"
                  required
                >
                  {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowJoinModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-green-600 dark:bg-green-700 text-white rounded-lg hover:bg-green-700 dark:hover:bg-green-600 transition-colors"
                >
                  Join Room
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;