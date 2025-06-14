import whisper
import numpy as np

class WhisperEngine:
    def __init__(self, model_name="base"):
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded.")

    def transcribe(self, audio_array: np.ndarray):
        """
        Transcribes audio using the loaded Whisper model.
        """
        if audio_array.size == 0:
            return {"text": "", "language": "unknown"}

        result = self.model.transcribe(audio_array)
        
        return {
            "text": result.get("text", ""),
            "language": result.get("language", "en")
        }

# Initialize a single engine for the app
whisper_engine = WhisperEngine() 