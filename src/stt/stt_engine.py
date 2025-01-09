import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import threading
import time


class STTEngine:
    def __init__(self, model_path: str, samplerate=16000, blocksize=4096):
        """Initialize the STT Engine."""
        if not model_path:
            raise ValueError("Model path is required.")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, samplerate)
        self.audio_queue = queue.Queue(maxsize=10)
        self.samplerate = samplerate
        self.blocksize = blocksize

    def audio_callback(self, indata, frames, time, status):
        """Callback to capture audio."""
        if status:
            print(f"Audio Status: {status}")
        try:
            self.audio_queue.put_nowait(bytes(indata))
        except queue.Full:
            print("Audio queue is full. Dropping audio frame.")

    def process_audio(self, on_transcription):
        """Process audio data from the queue."""
        while True:
            try:
                data = self.audio_queue.get(timeout=1)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    recognized_text = result.get("text", "")
                    if on_transcription:
                        on_transcription(recognized_text)
            except queue.Empty:
                continue  # No data in queue
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON result: {e}")

    def listen_and_transcribe(self, duration=None, on_transcription=None):
        """Listen and transcribe audio in real-time."""
        print("Listening... Press Ctrl+C to stop.")
        stop_time = time.time() + duration if duration else None
        processing_thread = threading.Thread(
            target=self.process_audio, args=(on_transcription,), daemon=True
        )
        processing_thread.start()

        try:
            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                dtype="int16",
                channels=1,
                callback=self.audio_callback,
            ):
                while True:
                    if stop_time and time.time() >= stop_time:
                        print("Stopped listening after duration timeout.")
                        break
        except sd.PortAudioError as e:
            print(f"Audio stream error: {e}")
        except KeyboardInterrupt:
            print("\nExiting transcription...")
        except Exception as e:
            print(f"Unexpected error: {e}")
