from stt.stt_engine import (
    MediaSource,
    MicrophoneSource,
    TranscriptionEngine,
    YouTubeSource,
)
import os


def check_model_exists(model_path: str) -> bool:
    """Check if the Vosk model exists in the specified path."""
    return os.path.exists(model_path) and os.path.isdir(model_path)


def initialize_stt_engine(model_path: str):
    """Initialize the STT Engine."""
    model_path = "models/vosk-model-en-us-0.22-lgraph"
    try:
        return TranscriptionEngine(model_path)
    except FileNotFoundError as e:
        raise RuntimeError(f"Model file not found: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize STT Engine: {e}")


# Microphone transcription
def transcribe_from_microphone(engine: TranscriptionEngine, on_transcription=None):
    try:
        mic_source = MicrophoneSource(
            samplerate=16000, blocksize=8000, audio_queue=engine.audio_queue
        )
        engine.transcribe(mic_source, duration=30, on_transcription=on_transcription)
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe from microphone: {e}")


# YouTube real-time transcription using audio stream
def transcribe_from_youtube(
    engine: TranscriptionEngine, youtube_url: str, on_transcription=None
):
    try:
        youtube_source = YouTubeSource(
            youtube_url=youtube_url,
            samplerate=16000,
            blocksize=8000,
            audio_queue=engine.audio_queue,
        )
        engine.transcribe(
            youtube_source, duration=60, on_transcription=on_transcription
        )
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe from YouTube: {e}")


# Fetch YouTube transcript using youtube-transcript-api
def fetch_youtube_transcript(engine: TranscriptionEngine, youtube_url: str):
    try:
        engine.fetch_youtube_transcript(youtube_url)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch YouTube transcript: {e}")


# Media transcription
def transcribe_from_media(
    engine: TranscriptionEngine, media_file_path: str, on_transcription=None
):
    try:
        media_source = MediaSource(
            media_file_path=media_file_path,
            samplerate=16000,
            blocksize=8000,
            audio_queue=engine.audio_queue,
        )
        engine.transcribe(media_source, duration=60, on_transcription=on_transcription)
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe from media: {e}")


# Print transcribed text
def on_transcription(text):
    print(f"Transcribed: {text}")
