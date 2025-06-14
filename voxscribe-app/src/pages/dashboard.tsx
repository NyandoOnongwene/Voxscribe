// src/components/Dashboard.jsx
import React from 'react';

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-white text-gray-800 px-6 py-10">
      <header className="flex  items-center border-b pb-4 mb-10">
        <h1 className="text-xl font-bold">Voxscribe</h1>
        <nav className="flex items-center gap-6 text-sm font-medium">
          <a href="#" className="hover:text-blue-600">Home</a>
          <a href="#" className="hover:text-blue-600">Convo Rooms</a>
          <a href="#" className="hover:text-blue-600">Transcripts</a>
          <a href="#" className="hover:text-blue-600">Help</a>
          <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
            <img
              src="https://i.pravatar.cc/40?img=65"
              alt="User"
              className="object-cover w-full h-full"
            />
          </div>
        </nav>
      </header>

      <main className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-8">Dashboard</h2>

        {/* Convo Rooms */}
        <section className="mb-12 justify-center items-center">
          <h3 className="text-xl font-semibold mb-4">Convo Rooms</h3>
          <div className="border-2 border-dashed border-gray-300 p-10 rounded-lg text-center">
            <p className="font-semibold text-gray-700 mb-2">No Convo Rooms yet</p>
            <p className="text-sm text-gray-500 mb-6">
              Start a new Convo Room to begin translating conversations in real-time.
            </p>
            <button className="bg-gray-200 hover:bg-gray-300 text-sm font-medium px-4 py-2 rounded">
              New Convo Room
            </button>
          </div>
        </section>

        {/* Transcripts */}
        <section>
          <h3 className="text-xl font-semibold mb-4">Transcripts</h3>
          <div className="border-2 border-dashed border-gray-300 p-10 rounded-lg text-center">
            <p className="font-semibold text-gray-700 mb-2">No Transcripts yet</p>
            <p className="text-sm text-gray-500 mb-6">
              Transcripts of your Convo Rooms will appear here.
            </p>
            <button className="bg-gray-200 hover:bg-gray-300 text-sm font-medium px-4 py-2 rounded">
              View Convo Rooms
            </button>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
