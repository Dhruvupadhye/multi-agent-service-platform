import os
from faster_whisper import WhisperModel
from app.utils.logger import logger

class VoiceHelper:
    def __init__(self):
        # We use the 'tiny' or 'base' model to ensure it runs fast and cost-efficiently on a CPU
        model_size = "base"
        logger.info(f"Loading local Whisper NLP model ({model_size}) for voice-to-text...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe_audio(self, file_path: str) -> str:
        logger.info(f"Transcribing audio file: {file_path}")
        # Transcribe the audio file
        segments, info = self.model.transcribe(file_path, beam_size=5)
        
        transcript = "".join([segment.text for segment in segments])
        return transcript.strip()

voice_helper = VoiceHelper()