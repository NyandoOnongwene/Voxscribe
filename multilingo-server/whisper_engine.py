import whisper
import numpy as np

class WhisperEngine:
    def __init__(self, model_name="base"):
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded.")

    def transcribe(self, audio_array: np.ndarray, language=None):
        """
        Transcribes audio using the loaded Whisper model.
        
        Args:
            audio_array: The audio data as numpy array
            language: Optional language code (e.g., 'en', 'fr') to force transcription in that language
        """
        if audio_array.size == 0:
            return {"text": "", "language": "unknown"}

        # Prepare transcription options
        transcribe_options = {}
        if language:
            transcribe_options["language"] = language
            print(f"Transcribing with forced language: {language}")
        
        result = self.model.transcribe(audio_array, **transcribe_options)
        
        return {
            "text": result.get("text", ""),
            "language": result.get("language", language or "en"),
            "confidence": getattr(result, 'confidence', None)
        }

# Initialize a single engine for the app
whisper_engine = WhisperEngine() 