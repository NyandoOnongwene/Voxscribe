import React, { useState, useEffect, useRef } from 'react';
import { useParams, useLocation } from 'react-router-dom';

// --- Type Definitions ---
interface Participant {
    name: string;
    avatar: string;
    status: 'speaking' | 'muted';
}

interface Message {
    speaker: string;
    original_text: string;
    language: string;
    translated_text: string;
    timestamp: string;
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

const MutedMicIcon = ({ className = "h-5 w-5 mr-2" }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5 9V5a3 3 0 013-3v0a3 3 0 013 3v4m-6 0v4a3 3 0 003 3h1m-4-7a3 3 0 01-3 3v0a3 3 0 013-3m-3 3h6M12 9v6m3-3h3" />
    </svg>
);

const EndSessionIcon = () => (
     <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
);

const RefreshCwIcon = ({ className }: { className: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 11A8.1 8.1 0 004.5 9M4 5v4h4m-4 4a8.1 8.1 0 0015.5 2 8.1 8.1 0 00-15.5-2" />
    </svg>
);

// --- Mock Data ---
const mockParticipants: Participant[] = [
    { name: 'User A', avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80', status: 'speaking' },
    { name: 'User B', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80', status: 'muted' },
];

const mockMessages: Message[] = [
    { speaker: 'User A', original_text: 'Bonjour tout le monde', language: 'fr', translated_text: 'Hello everyone', timestamp: '2025-06-14T14:32:10Z' },
    { speaker: 'User B', original_text: 'Hola, gracias por invitarme', language: 'es', translated_text: 'Hi, thanks for having me', timestamp: '2025-06-14T14:32:15Z' },
    { speaker: 'User A', original_text: 'Commençons par le premier point à l\'ordre du jour.', language: 'fr', translated_text: 'Let\'s start with the first agenda item.', timestamp: '2025-06-14T14:32:20Z' },
];

const TranscriptMessage = ({ message }: { message: Message }) => {
    const [showOriginal, setShowOriginal] = useState(false);
    const userColor = message.speaker === 'User A' ? 'text-blue-400' : 'text-purple-400';

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
    const location = useLocation();
    const [participants] = useState<Participant[]>(mockParticipants);
    const [messages, setMessages] = useState<Message[]>(mockMessages);
    const [micOn, setMicOn] = useState(false);
    const [translateTo, setTranslateTo] = useState('en');

    const streamRef = useRef<MediaStream | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const audioProcessorRef = useRef<ScriptProcessorNode | null>(null);

    const toggleMic = async () => {
        if (micOn) {
            // Turn microphone off
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
            setMicOn(false);
        } else {
            // Turn microphone on
            try {
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
                    const wavBlob = bufferToWav(downsampled);
                    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                        wsRef.current.send(wavBlob);
                    }
                };
                
                source.connect(processor);
                processor.connect(audioContext.destination);
                audioProcessorRef.current = processor;

                setMicOn(true);
            } catch (error) {
                console.error("Error accessing microphone:", error);
            }
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

    useEffect(() => {
        // Connect to WebSocket server
        // Replace with your actual WebSocket server URL
        wsRef.current = new WebSocket(`ws://localhost:8000/ws/${roomId}`);

        wsRef.current.onopen = () => {
            console.log('WebSocket connected');
        };

        wsRef.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            // Assuming the server sends messages in the format of our Message interface
            setMessages(prevMessages => [...prevMessages, message]);
        };

        wsRef.current.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        wsRef.current.onclose = () => {
            console.log('WebSocket disconnected');
        };

        // Cleanup on component unmount
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
                audioContextRef.current.close();
            }
        };
    }, [roomId]);

  return (
    <div className="bg-gray-900 text-white min-h-screen font-sans">
      <header className="border-b border-gray-800">
        <nav className="container mx-auto px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.2526 7.43934L14.5053 12L19.9449 10.7474L14.5053 12L19.9449 13.2526L14.5053 12L13.2526 16.5607L12 22L10.7474 16.5607L9.49473 12L4.05507 13.2526L9.49473 12L4.05507 10.7474L9.49473 12L10.7474 7.43934L12 2Z" fill="white"/>
            </svg>
            <h1 className="text-xl font-bold">ConvoRoom</h1>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 rounded-full hover:bg-gray-800">
              <HelpCircleIcon />
            </button>
            <img className="h-9 w-9 rounded-full object-cover" src="https://images.unsplash.com/photo-1511367461989-f85a21fda167?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="Current User" />
          </div>
        </nav>
      </header>

      <main className="container mx-auto px-8 py-10">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold">Live Convo Room</h2>
          <p className="text-gray-400 mt-2">Real-time speech-to-text and multilingual translation</p>
        </div>

        <div className="space-y-8">
          <section>
            <h3 className="text-xl font-semibold mb-4 text-gray-300">Participants</h3>
            <div className="bg-gray-800 rounded-xl p-6 flex items-center space-x-8">
                {participants.map(p => (
                    <div key={p.name} className="flex items-center space-x-4">
                        <div className="relative">
                            <img className={`h-14 w-14 rounded-full object-cover ${p.status === 'speaking' ? 'ring-2 ring-green-500' : ''}`} src={p.avatar} alt={p.name} />
                            {p.status === 'speaking' && (
                                <div className="absolute bottom-0 right-0 bg-green-500 rounded-full p-1">
                                    <MicIcon className="h-2 w-2 text-white" />
                                </div>
                            )}
                        </div>
                        <div>
                            <p className="font-semibold">{p.name}</p>
                            <p className={`text-sm ${p.status === 'speaking' ? 'text-green-400' : 'text-gray-400'}`}>{p.status === 'speaking' ? 'Speaking...' : 'Muted'}</p>
                        </div>
                    </div>
                ))}
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
                    {messages.map((msg, i) => <TranscriptMessage key={i} message={msg} />)}
                    <p className="text-gray-500 italic mt-4">Transcript will appear here as the conversation progresses...</p>
                </div>
              </div>
            </section>
            <section>
              <h3 className="text-xl font-semibold mb-4 text-gray-300">Translation Settings</h3>
              <div className="bg-gray-800 rounded-xl p-6 h-64 flex flex-col justify-start">
                <label htmlFor="language" className="text-sm font-medium text-gray-400">Translate my view to:</label>
                <select 
                    id="language"
                    value={translateTo}
                    onChange={(e) => setTranslateTo(e.target.value)}
                    className="w-full bg-gray-700 border-gray-600 rounded-md p-2 mt-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
                <div className="mt-4 text-sm text-gray-400 flex items-center">
                    <RefreshCwIcon className="w-4 h-4 mr-2"/>
                    <p>Your transcript view is set to <span className="font-bold">{translateTo.charAt(0).toUpperCase() + translateTo.slice(1)}</span>.</p>
                </div>
              </div>
            </section>
          </div>
          
          <section>
            <h3 className="text-xl font-semibold mb-4 text-gray-300">Controls</h3>
            <div className="bg-gray-800 rounded-xl p-6 flex justify-center items-center space-x-4">
                <button 
                    onClick={toggleMic}
                    className={`${micOn ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'} text-white font-bold py-2 px-5 rounded-lg flex items-center justify-center w-32`}
                >
                    {micOn ? <MicIcon /> : <MutedMicIcon />}
                    {micOn ? 'Mic On' : 'Mic Off'}
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-5 rounded-lg flex items-center justify-center">
                    <EndSessionIcon />
                    End Session
                </button>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default ConvoRoom; 