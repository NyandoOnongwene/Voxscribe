import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ConvoRoom from './pages/ConvoRoom';

// import { useState } from 'react'




function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/room/:id" element={<ConvoRoom />} />
      </Routes>
    </Router>
  );
}

export default App;
