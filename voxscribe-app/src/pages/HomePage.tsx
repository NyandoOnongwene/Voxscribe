import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileDropdown from '../components/ProfileDropdown';
import ThemeToggle from '../components/ThemeToggle';

const HelpCircleIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.546-.994 1.093v.213h-2v-.213c0-1.06.86-1.928 1.944-2.093C15.398 13.382 16 12.646 16 12c0-1.105-.895-2-2-2s-2 .895-2 2h-2z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01" />
    </svg>
);

const ArrowRightIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
    </svg>
);


const HomePage = () => {
    const navigate = useNavigate();
    const [roomId, setRoomId] = useState('');
    const [microphones, setMicrophones] = useState<MediaDeviceInfo[]>([]);
    const [selectedMic, setSelectedMic] = useState('');
    const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
    
    useEffect(() => {
        const getMicrophones = async () => {
            try {
                // Request permission to trigger device enumeration
                await navigator.mediaDevices.getUserMedia({ audio: true });
                const devices = await navigator.mediaDevices.enumerateDevices();
                const audioDevices = devices.filter(device => device.kind === 'audioinput');
                setMicrophones(audioDevices);
                if (audioDevices.length > 0) {
                    setSelectedMic(audioDevices[0].deviceId);
                }
            } catch (err) {
                console.error("Error enumerating microphones:", err);
            }
        };

        getMicrophones();
    }, []);

    const handleStartSession = () => {
        if (roomId) {
            navigate(`/room/${roomId}`, { state: { selectedMic } });
        } else {
            // A random ID for new rooms
            const newRoomId = Math.random().toString(36).substring(7);
            navigate(`/room/${newRoomId}`, { state: { selectedMic } });
        }
    };


    return (
        <div className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen font-sans flex flex-col transition-colors duration-200">
            <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                <nav className="container mx-auto px-8 py-4 flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                         <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L13.2526 7.43934L14.5053 12L19.9449 10.7474L14.5053 12L19.9449 13.2526L14.5053 12L13.2526 16.5607L12 22L10.7474 16.5607L9.49473 12L4.05507 13.2526L9.49473 12L4.05507 10.7474L9.49473 12L10.7474 7.43934L12 2Z" fill="currentColor"/>
                        </svg>
                        <h1 className="text-xl font-bold">Convo</h1>
                    </div>
                     <div className="flex items-center space-x-4">
                        <ThemeToggle />
                        <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                            <HelpCircleIcon />
                        </button>
                        <div className="relative">
                            <button onClick={() => setIsProfileDropdownOpen(prev => !prev)}>
                                <img className="h-9 w-9 rounded-full object-cover" src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="User" />
                            </button>
                            {isProfileDropdownOpen && <ProfileDropdown />}
                        </div>
                    </div>
                </nav>
            </header>

            <main className="flex-grow flex items-center justify-center">
                <div className="bg-white dark:bg-gray-800 p-10 rounded-xl shadow-lg w-full max-w-lg">
                    <h2 className="text-3xl font-bold text-center">Start a conversation</h2>
                    <p className="text-center text-gray-600 dark:text-gray-400 mt-2 mb-8">Create or join a room to begin.</p>
                    
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="roomId" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Room ID</label>
                            <input
                                type="text"
                                id="roomId"
                                value={roomId}
                                onChange={(e) => setRoomId(e.target.value)}
                                placeholder="Enter or create room ID"
                                className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md p-3 text-sm text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>

                         <div>
                            <label htmlFor="microphone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Microphone</label>
                            <select
                                id="microphone"
                                value={selectedMic}
                                onChange={(e) => setSelectedMic(e.target.value)}
                                className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md p-3 text-sm text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                            >
                                {microphones.map(mic => (
                                    <option key={mic.deviceId} value={mic.deviceId}>{mic.label}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Language (Your Speech to Target)</label>
                            <div className="flex items-center space-x-4">
                                <select className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md p-3 text-sm text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500">
                                    <option>English (US)</option>
                                </select>
                                <ArrowRightIcon />
                                <select className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md p-3 text-sm text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500">
                                    <option>Français</option>
                                </select>
                            </div>
                        </div>

                        <button 
                            onClick={handleStartSession}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300"
                        >
                            Start Session
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default HomePage; 