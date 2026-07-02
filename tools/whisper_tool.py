import os
import logging
from typing import Dict, Any, List
from tools.registry import BaseActionSyncTool, tool_registry
from config.settings import settings

logger = logging.getLogger("actionsync.tools.whisper")

class WhisperTool(BaseActionSyncTool):
    def __init__(self):
        super().__init__(
            name="WhisperTool",
            description="Transcribes audio files into timestamped segments using OpenAI Whisper."
        )
        self.model = None

    def initialize(self) -> None:
        """Loads the Whisper model into memory, utilizing GPU if available."""
        try:
            from faster_whisper import WhisperModel
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            logger.info(f"Hardware Check: PyTorch CUDA Available = {torch.cuda.is_available()}")
            if device == "cuda":
                logger.info(f"Target GPU Name: {torch.cuda.get_device_name(0)}")
            logger.info(f"Loading faster-whisper model '{settings.WHISPER_MODEL_NAME}' on device '{device}' with compute_type '{compute_type}'...")
            self.model = WhisperModel(settings.WHISPER_MODEL_NAME, device=device, compute_type=compute_type)
            self.initialized = True
            logger.info(f"faster-whisper model loaded successfully on device: {device}")
        except ImportError:
            logger.error("faster-whisper package not installed. Running in mock mode.")
            self.initialized = True  # Proceed in fallback/mock mode
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise e

    def execute(self, audio_path: str) -> Dict[str, Any]:
        """Transcribes the audio file at audio_path.
        
        Returns:
            Dict containing:
            - text: Consolidated raw transcript
            - segments: List of Dicts with text, start_time, end_time, and speaker
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing audio: {audio_path}")

        # Fallback/mock mode if model was not successfully loaded
        if self.model is None:
            logger.warning("Whisper model not loaded. Returning mock transcription.")
            return self._generate_mock_transcription(audio_path)

        try:
            # Run transcription using faster-whisper (beam_size=5 is standard)
            segments_generator, info = self.model.transcribe(audio_path, beam_size=5)
            
            # Realize the generator to perform transcription
            raw_segments = list(segments_generator)
            
            segments = []
            text_parts = []
            
            for seg in raw_segments:
                cleaned_text = seg.text.strip()
                if cleaned_text:
                    text_parts.append(cleaned_text)
                    segments.append({
                        "speaker": "Speaker 1",  # Mono speaker default
                        "text": cleaned_text,
                        "start_time": float(seg.start),
                        "end_time": float(seg.end)
                    })

            return {
                "text": " ".join(text_parts),
                "segments": segments
            }
        except Exception as e:
            logger.error(f"faster-whisper transcription failed: {e}")
            raise e

    def validate(self, output: Any) -> bool:
        if not isinstance(output, dict):
            return False
        if "text" not in output or "segments" not in output:
            return False
        if not isinstance(output["segments"], list):
            return False
        return True

    def _generate_mock_transcription(self, audio_path: str) -> Dict[str, Any]:
        """Mock fallback for environments where whisper model load fails."""
        # Simple test transcription
        filename = os.path.basename(audio_path)
        mock_text = (
            "Welcome to the ActionSync AI kick-off meeting. Today we are planning the roadmap for "
            "the next quarter. John, you will be responsible for completing the API database schema by next Tuesday. "
            "Sarah, please coordinate with John to align the frontend interfaces. We have a major risk of "
            "delayed deployment if the database credentials are not set up by our hosting team. "
            "Let's make sure we meet again next Thursday to review progress."
        )
        segments = [
            {"speaker": "Speaker 1", "text": "Welcome to the ActionSync AI kick-off meeting.", "start_time": 0.0, "end_time": 4.5},
            {"speaker": "Speaker 1", "text": "Today we are planning the roadmap for the next quarter.", "start_time": 4.5, "end_time": 8.0},
            {"speaker": "Speaker 1", "text": "John, you will be responsible for completing the API database schema by next Tuesday.", "start_time": 8.0, "end_time": 14.5},
            {"speaker": "Speaker 1", "text": "Sarah, please coordinate with John to align the frontend interfaces.", "start_time": 14.5, "end_time": 20.0},
            {"speaker": "Speaker 1", "text": "We have a major risk of delayed deployment if the database credentials are not set up by our hosting team.", "start_time": 20.0, "end_time": 28.5},
            {"speaker": "Speaker 1", "text": "Let's make sure we meet again next Thursday to review progress.", "start_time": 28.5, "end_time": 35.0}
        ]
        return {
            "text": mock_text,
            "segments": segments
        }

# Register the tool
tool_registry.register(WhisperTool())
