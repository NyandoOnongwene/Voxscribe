import { useState, useEffect, useRef } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import ProfileDropdown from '../components/ProfileDropdown';
import ThemeToggle from '../components/ThemeToggle';

// --- Type Definitions ---
interface Participant {
    id: number;
    name: string;
    avatar: string;
    status: 'speaking' | 'muted';
    language: string;
    isOnline: boolean;
}

interface Message {
    id?: number;
    speaker: string;
    speaker_id: number;
    original_text: string;
    language: string;
    translated_text: string;
    target_language: string;
    timestamp: string;
}

interface User {
    id: number;
    name: string;
    email: string;
    main_language: string;
}

// --- Helper Icons ---
const HelpCircleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.546-.994 1.093v.213h-2v-.213c0-1.06.86-1.928 1.944-2.093C15.398 13.382 16 12.646 16 12c0-1.105-.895-2-2-2s-2 .895-2 2h-2z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01" />
  </svg>
);

const DownloadIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
);

const MicIcon = ({ className = "h-5 w-5 mr-2" }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
    </svg>
);

/*
const MutedMicIcon = ({ className = "h-5 w-5 mr-2" }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5 9V5a3 3 0 013-3v0a3 3 0 013 3v4m-6 0v4a3 3 0 003 3h1m-4-7a3 3 0 01-3 3v0a3 3 0 013-3m-3 3h6M12 9v6m3-3h3" />
    </svg>
);
*/

const EndSessionIcon = () => (
     <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
);

const StopIcon = ({ className = "h-5 w-5 mr-2" }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 6h12v12H6z" />
    </svg>
);

/*
const RefreshCwIcon = ({ className }: { className: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 11A8.1 8.1 0 004.5 9M4 5v4h4m-4 4a8.1 8.1 0 0015.5 2 8.1 8.1 0 00-15.5-2" />
    </svg>
);
*/

const TranscriptMessage = ({ message }: { message: Message }) => {
    const [showOriginal, setShowOriginal] = useState(false);
    // Use a consistent color for all speakers for now
    const userColor = 'text-blue-400';

    return (
        <div onMouseEnter={() => setShowOriginal(true)} onMouseLeave={() => setShowOriginal(false)} className="relative">
            <p>
                <span className={`font-bold ${userColor}`}>{message.speaker}:</span>
                <span className="ml-2">{message.translated_text}</span>
            </p>
            {showOriginal && (
                 <div className="text-xs text-gray-400 italic ml-2 absolute bg-gray-700 px-2 py-1 rounded-md -top-7">
                    Original ({message.language}): {message.original_text}
                </div>
            )}
        </div>
    );
};

const ConvoRoom = () => {
    const { id: roomId } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const location = useLocation();

    // States
    const [roomName, setRoomName] = useState<string>('Live Convo Room');
    const [participants, setParticipants] = useState<Participant[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [translateTo, setTranslateTo] = useState<string>('en');
    const [isRecording, setIsRecording] = useState(false);
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState<string | null>(null);
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [isCreator, setIsCreator] = useState(false);
    // const [roomCreatorId, setRoomCreatorId] = useState<number | null>(null);
    const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);

    // Refs for WebSocket and audio
    const wsRef = useRef<WebSocket | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const audioProcessorRef = useRef<ScriptProcessorNode | null>(null);
    const audioChunksRef = useRef<Float32Array[]>([]);

    // Authentication check
    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            const user = JSON.parse(storedUser);
            setCurrentUser(user);
            // Set default translation language based on user's main language
            setTranslateTo(user.main_language === 'en' ? 'en' : 'fr');
        } else {
            navigate('/login');
        }
    }, [navigate]);

    // Room and participant management
    useEffect(() => {
        if (!currentUser || !roomId) return;

        const fetchRoomData = async () => {
            try {
                // Get room details
                const roomResponse = await fetch(`http://127.0.0.1:8001/api/rooms/${roomId}/details`);
                if (roomResponse.ok) {
                    const roomData = await roomResponse.json();
                    setRoomName(roomData.name || 'Live Convo Room');
                }

                // Get room participants
                const participantsResponse = await fetch(`http://127.0.0.1:8001/api/rooms/${roomId}/participants`);
                if (participantsResponse.ok) {
                    const participantsData = await participantsResponse.json();
                    console.log('Participants data:', participantsData);
                    
                    // Check if participants data has the expected structure
                    const participantsList = participantsData.participants || [];
                    setParticipants(participantsList.map((p: any) => ({
                        id: p.user?.id || 0,
                        name: p.user?.name || 'Unknown User',
                        avatar: `https://images.unsplash.com/photo-${1500 + (p.user?.id || 1)}?w=100&h=100&fit=crop&crop=face`,
                        status: 'muted',
                        language: p.preferred_language || 'en',
                        isOnline: false
                    })));
                }

                // Get room messages
                const messagesResponse = await fetch(`http://127.0.0.1:8001/api/rooms/${roomId}/messages`);
                if (messagesResponse.ok) {
                    const messagesData = await messagesResponse.json();
                    console.log('Messages data:', messagesData);
                    
                    // Messages endpoint returns an array directly
                    const messagesList = Array.isArray(messagesData) ? messagesData : [];
                    setMessages(messagesList.map((msg: any) => ({
                        id: msg.id || Math.random(),
                        speaker: msg.speaker_name || 'Unknown',
                        speaker_id: msg.user_id || 0,
                        original_text: msg.original_text || '',
                        language: msg.original_language || 'en',
                        translated_text: msg.translated_text || msg.original_text || '',
                        target_language: msg.target_language || msg.original_language || 'en',
                        timestamp: msg.timestamp || new Date().toISOString()
                    })));
                }
            } catch (error) {
                console.error('Error fetching room data:', error);
                setConnectionError('Failed to load room data');
            }
        };

        fetchRoomData();
    }, [currentUser, roomId]);

    // WebSocket connection for real-time communication
    useEffect(() => {
        if (!currentUser || !roomId) return;

        const connectWebSocket = () => {
            // Use correct port (8001) for backend connection
            const wsUrl = `ws://127.0.0.1:8001/ws/${roomId}/${currentUser.id}`;
            console.log(`Connecting to WebSocket: ${wsUrl}`);
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                console.log(`WebSocket connected for user ${currentUser.name} in room ${roomId}`);
                setIsConnected(true);
                setConnectionError(null);
                
                // Immediately mark current user as online
                setParticipants(prev => prev.map(p => 
                    p.id === currentUser.id ? { ...p, isOnline: true } : p
                ));
                
                // Send join message
                if (wsRef.current) {
                    wsRef.current.send(JSON.stringify({
                        type: 'join',
                        user_id: currentUser.id,
                        user_name: currentUser.name,
                        language: currentUser.main_language
                    }));
                }
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    switch (data.type) {
                        case 'transcription':
                            // Filter messages based on user's translation preference
                            if (data.target_language === translateTo || data.speaker_id === currentUser.id) {
                                const newMessage: Message = {
                                    id: data.message_id,
                                    speaker: data.speaker_name,
                                    speaker_id: data.speaker_id,
                                    original_text: data.original_text,
                                    language: data.original_language,
                                    translated_text: data.translated_text || data.original_text,
                                    target_language: data.target_language,
                                    timestamp: data.timestamp || new Date().toISOString()
                                };
                                
                                setMessages(prev => {
                                    // Avoid duplicates
                                    if (prev.some(msg => msg.id === newMessage.id)) {
                                        return prev;
                                    }
                                    return [...prev, newMessage];
                                });
                            }
                            break;
                            
                        case 'participants_list':
                            // Set the complete participants list when joining
                            console.log('Received participants_list:', data.participants);
                            const participantsList = data.participants.map((p: any) => ({
                                id: p.user_id,
                                name: p.user_name,
                                avatar: `https://images.unsplash.com/photo-${1500 + p.user_id}?w=100&h=100&fit=crop&crop=face`,
                                status: 'muted',
                                language: p.language,
                                isOnline: true  // All participants in the list are considered online
                            }));
                            setParticipants(participantsList);
                            console.log('Updated participants with online status:', participantsList);
                            
                            // Check if current user is the room creator
                            if (data.room_creator_id && currentUser) {
                                // setRoomCreatorId(data.room_creator_id);
                                setIsCreator(currentUser.id === data.room_creator_id);
                            }
                            break;
                            
                        case 'participant_joined':
                            setParticipants(prev => {
                                const existing = prev.find(p => p.id === data.user_id);
                                if (existing) {
                                    return prev.map(p => p.id === data.user_id ? { ...p, isOnline: true } : p);
                                } else {
                                    return [...prev, {
                                        id: data.user_id,
                                        name: data.user_name,
                                        avatar: `https://images.unsplash.com/photo-${1500 + data.user_id}?w=100&h=100&fit=crop&crop=face`,
                                        status: 'muted',
                                        language: data.language,
                                        isOnline: true
                                    }];
                                }
                            });
                            break;
                            
                        case 'participant_left':
                            setParticipants(prev => prev.map(p => 
                                p.id === data.user_id ? { ...p, isOnline: false } : p
                            ));
                            break;
                            
                        case 'speaking_status':
                            setParticipants(prev => prev.map(p => 
                                p.id === data.user_id ? { ...p, status: data.is_speaking ? 'speaking' : 'muted' } : p
                            ));
                            break;
                            
                        case 'session_ended':
                            // Session was ended by the creator, navigate back to dashboard
                            alert(`Session ended by ${data.ended_by}`);
                            navigate('/dashboard');
                            break;
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                setConnectionError('Connection error occurred');
                setIsConnected(false);
            };

            wsRef.current.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                setIsConnected(false);
                
                // Attempt to reconnect after 3 seconds if not manually closed
                if (event.code !== 1000) {
                    setTimeout(() => {
                        if (currentUser && roomId) {
                            connectWebSocket();
                        }
                    }, 3000);
                }
            };
        };

        connectWebSocket();

        // Cleanup on component unmount
        return () => {
            if (wsRef.current) {
                // Send leave message before closing
                if (wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify({
                        type: 'leave',
                        user_id: currentUser.id
                    }));
                }
                wsRef.current.close(1000, 'Component unmounting');
            }
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
                audioContextRef.current.close();
            }
        };
    }, [currentUser, roomId]);

    // Handle translation language changes
    useEffect(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && currentUser) {
            // Notify server about language preference change
            wsRef.current.send(JSON.stringify({
                type: 'language_change',
                user_id: currentUser.id,
                translate_to: translateTo
            }));
            
            // Filter existing messages based on new language preference
            setMessages(prev => prev.filter(msg => 
                msg.target_language === translateTo || msg.speaker_id === currentUser.id
            ));
        }
    }, [translateTo, currentUser]);

    const concatenateFloat32Arrays = (arrays: Float32Array[]): Float32Array => {
        let totalLength = 0;
        for (const arr of arrays) {
            totalLength += arr.length;
        }
        const result = new Float32Array(totalLength);
        let offset = 0;
        for (const arr of arrays) {
            result.set(arr, offset);
            offset += arr.length;
        }
        return result;
    };

    const handleMicClick = async () => {
        if (isRecording) {
            // Stop recording
            setIsRecording(false);
            
            // Update speaking status
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({
                    type: 'speaking_status',
                    user_id: currentUser?.id,
                    is_speaking: false
                }));
            }
            
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
                streamRef.current = null;
            }
            if (audioProcessorRef.current) {
                audioProcessorRef.current.disconnect();
                audioProcessorRef.current = null;
            }
            if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
                audioContextRef.current.close();
            }
    
            if (audioChunksRef.current.length > 0) {
                const completeBuffer = concatenateFloat32Arrays(audioChunksRef.current);
                const wavBlob = bufferToWav(completeBuffer);
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(wavBlob);
                }
            }
            audioChunksRef.current = [];

        } else {
            // Start recording
            try {
                audioChunksRef.current = [];
                const selectedMicId = location.state?.selectedMic;
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: selectedMicId ? { deviceId: { exact: selectedMicId } } : true 
                });
                streamRef.current = stream;
                
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioContextRef.current = audioContext;

                const source = audioContext.createMediaStreamSource(stream);
                const processor = audioContext.createScriptProcessor(4096, 1, 1);

                processor.onaudioprocess = (e) => {
                    const inputData = e.inputBuffer.getChannelData(0);
                    const downsampled = downsampleBuffer(inputData, audioContext.sampleRate, 16000);
                    audioChunksRef.current.push(new Float32Array(downsampled));
                };
                
                source.connect(processor);
                processor.connect(audioContext.destination);
                audioProcessorRef.current = processor;

                setIsRecording(true);
                
                // Update speaking status
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify({
                        type: 'speaking_status',
                        user_id: currentUser?.id,
                        is_speaking: true
                    }));
                }
            } catch (error) {
                console.error("Error accessing microphone:", error);
                setConnectionError("Failed to access microphone");
            }
        }
    };

    const handleEndSession = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            // Send end session message
            wsRef.current.send(JSON.stringify({
                type: 'end_session',
                user_id: currentUser?.id
            }));
        }
    };

    // --- Audio Utility Functions ---
    const downsampleBuffer = (buffer: Float32Array, sampleRate: number, outSampleRate: number) => {
        if (outSampleRate === sampleRate) {
            return buffer;
        }
        const sampleRateRatio = sampleRate / outSampleRate;
        const newLength = Math.round(buffer.length / sampleRateRatio);
        const result = new Float32Array(newLength);
        let offsetResult = 0;
        let offsetBuffer = 0;
        while (offsetResult < result.length) {
            const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
            let accum = 0, count = 0;
            for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
                accum += buffer[i];
                count++;
            }
            result[offsetResult] = accum / count;
            offsetResult++;
            offsetBuffer = nextOffsetBuffer;
        }
        return result;
    };

    const bufferToWav = (buffer: Float32Array) => {
        const numChannels = 1, sampleRate = 16000, bitDepth = 16;
        const numSamples = buffer.length;
        const dataSize = numSamples * numChannels * (bitDepth / 8);
        const bufferSize = 44 + dataSize;
        
        const wavBuffer = new ArrayBuffer(bufferSize);
        const view = new DataView(wavBuffer);

        let offset = 0;
        const writeString = (str: string) => {
            for (let i = 0; i < str.length; i++) {
                view.setUint8(offset++, str.charCodeAt(i));
            }
        };

        writeString('RIFF');
        view.setUint32(offset, 36 + dataSize, true); offset += 4;
        writeString('WAVE');
        writeString('fmt ');
        view.setUint32(offset, 16, true); offset += 4;
        view.setUint16(offset, 1, true); offset += 2;
        view.setUint16(offset, numChannels, true); offset += 2;
        view.setUint32(offset, sampleRate, true); offset += 4;
        view.setUint32(offset, sampleRate * numChannels * (bitDepth / 8), true); offset += 4;
        view.setUint16(offset, numChannels * (bitDepth / 8), true); offset += 2;
        view.setUint16(offset, bitDepth, true); offset += 2;
        writeString('data');
        view.setUint32(offset, dataSize, true); offset += 4;

        for (let i = 0; i < numSamples; i++, offset += 2) {
            const s = Math.max(-1, Math.min(1, buffer[i]));
            view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }

        return new Blob([view], { type: 'audio/wav' });
    };

  return (
    <div className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen font-sans transition-colors duration-200">
      <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <nav className="container mx-auto px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.2526 7.43934L14.5053 12L19.9449 10.7474L14.5053 12L19.9449 13.2526L14.5053 12L13.2526 16.5607L12 22L10.7474 16.5607L9.49473 12L4.05507 13.2526L9.49473 12L4.05507 10.7474L9.49473 12L10.7474 7.43934L12 2Z" fill="currentColor"/>
            </svg>
            <h1 className="text-xl font-bold">ConvoRoom</h1>
          </div>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
              <HelpCircleIcon />
            </button>
            <div className="relative">
                <button onClick={() => setIsProfileDropdownOpen(prev => !prev)}>
                    <img className="h-9 w-9 rounded-full object-cover" src="https://images.unsplash.com/photo-1511367461989-f85a21fda167?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="Current User" />
                </button>
                {isProfileDropdownOpen && <ProfileDropdown />}
            </div>
          </div>
        </nav>
      </header>

      <main className="container mx-auto px-8 py-10">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold">{roomName}</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Real-time speech-to-text and multilingual translation</p>
          <div className="flex items-center justify-center mt-4 space-x-4">
            <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
            {connectionError && (
              <span className="text-red-400 text-sm">{connectionError}</span>
            )}
          </div>
        </div>

        <div className="space-y-8">
          <section>
            <h3 className="text-xl font-semibold mb-4 text-gray-300">Participants</h3>
            <div className="bg-gray-800 rounded-xl p-6">
                {participants.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {participants.map(p => (
                            <div key={p.id} className="flex items-center space-x-4 p-3 bg-gray-700 rounded-lg">
                                <div className="relative">
                                    <img 
                                        className={`h-12 w-12 rounded-full object-cover ${p.status === 'speaking' ? 'ring-2 ring-green-500' : ''} ${p.isOnline ? '' : 'opacity-50'}`} 
                                        src={p.avatar} 
                                        alt={p.name} 
                                    />
                                    {p.status === 'speaking' && p.isOnline && (
                                        <div className="absolute bottom-0 right-0 bg-green-500 rounded-full p-1">
                                            <MicIcon className="h-3 w-3 text-white" />
                                        </div>
                                    )}
                                    {!p.isOnline && (
                                        <div className="absolute bottom-0 right-0 bg-gray-500 rounded-full p-1">
                                            <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                                        </div>
                                    )}
                                </div>
                                <div className="flex-1">
                                    <p className="font-semibold text-sm">{p.name}</p>
                                    <p className="text-xs text-gray-400">
                                        {p.language === 'en' ? 'English' : 'French'}
                                    </p>
                                    <p className={`text-xs ${p.status === 'speaking' && p.isOnline ? 'text-green-400' : 'text-gray-500'}`}>
                                        {p.isOnline 
                                            ? (p.status === 'speaking' ? 'Speaking...' : 'Listening') 
                                            : 'Offline'
                                        }
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <p className="text-gray-400">You appear to be the only one in the room.</p>
                        <p className="text-gray-500 text-sm mt-2">Share the room ID with others to start collaborating!</p>
                        <p className="text-blue-400 font-mono text-lg mt-3">{roomId}</p>
                    </div>
                )}
            </div>
          </section>

          <div className="grid grid-cols-3 gap-8">
            <section className="col-span-2">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-semibold text-gray-300">Real-time Transcript</h3>
                    <button className="bg-gray-700 hover:bg-gray-600 text-sm font-semibold py-1.5 px-3 rounded-lg flex items-center">
                        <DownloadIcon />
                        Download
                    </button>
              </div>
              <div className="bg-gray-800 rounded-xl p-6 h-64">
                <div className="space-y-3 text-sm text-gray-300 h-full overflow-y-auto">
                    {messages.length > 0 ? (
                        messages.map((msg, i) => <TranscriptMessage key={i} message={msg} />)
                    ) : (
                        <p className="text-gray-500 italic mt-4">Transcript will appear here as the conversation progresses...</p>
                    )}
                </div>
              </div>
            </section>
            <section>
              <h3 className="text-xl font-semibold mb-4 text-gray-300">Translation Settings</h3>
              <div className="bg-gray-800 rounded-xl p-6 h-64 flex flex-col justify-start">
                <div className="space-y-4">
                    <div>
                        <label htmlFor="translate-to" className="block text-sm font-medium text-gray-300 mb-2">
                            Translate my view to:
                        </label>
                        <select
                            id="translate-to"
                            value={translateTo}
                            onChange={(e) => setTranslateTo(e.target.value)}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-pink-500"
                        >
                            <option value="en">English</option>
                            <option value="fr">French</option>
                        </select>
                    </div>
                    <div className="text-sm text-gray-400">
                        Your transcript view is set to <span className="text-pink-400 font-medium">
                            {translateTo === 'en' ? 'English' : 'French'}
                        </span>.
                    </div>
                    <div className="mt-4 p-3 bg-gray-700 rounded-lg">
                        <div className="text-sm text-gray-300 mb-2">Room Settings:</div>
                        <div className="text-sm text-gray-400">Room ID: <span className="text-pink-400">{roomId}</span></div>
                        <div className="text-sm text-gray-400">Your Language: <span className="text-green-400">{currentUser?.main_language === 'en' ? 'English' : 'French'}</span></div>
                        {isCreator && <div className="text-sm text-yellow-400 mt-1">👑 Room Creator</div>}
                    </div>
                </div>
              </div>
            </section>
          </div>
          
          <section>
            <h3 className="text-xl font-semibold mb-4 text-gray-300">Controls</h3>
            <div className="bg-gray-800 rounded-xl p-6 flex justify-center items-center space-x-4">
                <button 
                    onClick={handleMicClick}
                    className={`${isRecording ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'} text-white font-bold py-2 px-5 rounded-lg flex items-center justify-center w-48`}
                >
                    {isRecording ? <StopIcon /> : <MicIcon />}
                    {isRecording ? 'Stop Recording' : 'Start Recording'}
                </button>
                {isCreator && (
                    <button 
                        onClick={handleEndSession}
                        className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-5 rounded-lg flex items-center justify-center"
                    >
                        <EndSessionIcon />
                        End Session
                    </button>
                )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default ConvoRoom; 