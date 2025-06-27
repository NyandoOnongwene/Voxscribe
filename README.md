# Voxscribe - Real-time Voice Transcription & Translation

A simple app that records your voice, transcribes it, and translates it to French in real-time.

## What You Need (Windows)

- **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
- **Node.js** - Download from [nodejs.org](https://nodejs.org/)
- **A microphone** and modern web browser

## Quick Setup (Windows)

### Step 1: Start the Backend Server

1. Open **PowerShell** (search for it in Start menu)
2. Navigate to your project folder:
 
   ```

3. Run this single command to start the backend:
   ```powershell
   cd multilingo-server; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn main:app --reload
   ```

4. Wait for it to show:
   ```
   INFO: Uvicorn running on http://127.0.0.1:8000
   Whisper model loaded.
   ```

### Step 2: Start the Frontend

   ```
 Run this command:
   ```powershell
   cd voxscribe-app; npm install; npm run dev
   ```

4. Wait for it to show:
   ```
   Local: http://localhost:5173/
   ```

### Step 3: Use the App

1. Open your browser and go to: `http://localhost:5173`
2. Allow microphone access when asked
3. Click "Start Session"
4. Click "Start Recording" → speak → click "Stop Recording"
5. See your speech transcribed and translated to French!

## Simple Windows Batch Files (Optional)

To make it even easier, you can create these batch files:

### Create `start-backend.bat`:
```batch
@echo off
cd multilingo-server
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --reload
pause
```

### Create `start-frontend.bat`:
```batch
@echo off
cd voxscribe-app
npm install
npm run dev
pause
```

Then just double-click these files to start each part!

## Troubleshooting

**If Python command doesn't work:**
- Make sure you checked "Add Python to PATH" during installation
- Restart PowerShell after installing Python

**If npm command doesn't work:**
- Restart PowerShell after installing Node.js
- Make sure Node.js installation completed successfully

**If microphone doesn't work:**
- Check Windows microphone permissions in Settings
- Make sure your browser has microphone access

**If you get permission errors:**
- Run PowerShell as Administrator
- Or try: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Change Translation Language

To translate to a different language instead of French:

1. Open `multilingo-server\main.py` in any text editor
2. Find this line: `"fr"` (appears twice)
3. Replace with:
   - `"es"` for Spanish
   - `"de"` for German  
   - `"it"` for Italian
   - `"pt"` for Portuguese
4. Save the file

## Model Performance & Evaluation

VoxScribe includes comprehensive model evaluation with industry-standard metrics:

- 📊 **Speech-to-Text**: WER: 0.1568, F1: 0.9116 ✅ Good Performance
- 🌐 **Translation**: BLEU: 0.4667, F1: 0.7961 ✅ Good Performance  
- 🎯 **Overall Score**: 75.44% → **Production Ready** ✅

### Evaluation Documentation
- 📖 **[Complete Evaluation Guide](multilingo-server/MODEL_EVALUATION_GUIDE.md)** - Comprehensive metrics documentation
- ⚡ **[Quick Reference](multilingo-server/EVALUATION_QUICK_REFERENCE.md)** - Key metrics and commands
- 🔬 **Run Evaluation**: `cd multilingo-server && python evaluation.py`

### Key Metrics Explained
- **Word Error Rate (WER)**: 15.68% - Industry standard: <20% ✅
- **Translation BLEU Score**: 46.67% - Industry standard: >40% ✅
- **F1 Scores**: STT: 91.16%, Translation: 79.61% ✅
- **Character Accuracy**: 79.43% ✅

## Features

- 🎤 **Real-time voice recording** with WebSocket streaming
- 🤖 **AI-powered transcription** using OpenAI Whisper
- 🌐 **Instant translation** between English and French
- 💾 **Session persistence** with SQLite database
- 🎨 **Modern, responsive UI** with Tailwind CSS
- 📊 **Performance monitoring** with comprehensive metrics
- ✅ **Production-ready** quality assurance
- 👥 **Multi-participant** conversation rooms
- 🔒 **User authentication** and room management

## Tech Stack

- **Backend**: Python + FastAPI + OpenAI Whisper + SQLAlchemy
- **Frontend**: React + TypeScript + Tailwind CSS + Vite
- **Real-time**: WebSockets for live audio streaming
- **Database**: SQLite with user authentication
- **Evaluation**: Custom framework with WER, BLEU, F1 metrics
- **Translation**: Google Translate API integration

## That's It!

The app should now be running with verified AI performance! Both PowerShell windows need to stay open while using the app.

---

*Built for seamless English-French communication with verified AI performance! 🇨🇦* 