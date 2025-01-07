import sys
import unittest
import time
import sounddevice as sd
import queue
from src.stt.stt_engine import STTEngine
import json


class TestSTTEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up shared resources for all tests."""
        model_path = "models/vosk-model-small-en-us-0.15"
        try:
            cls.stt_engine = STTEngine(model_path)
            cls.audio_queue = queue.Queue()
            print("STT Engine initialized successfully.")
        except Exception as e:
            cls.stt_engine = None
            raise RuntimeError(f"Failed to initialize STT Engine: {e}")

    @classmethod
    def tearDownClass(cls):
        """Clean up shared resources."""
        cls.stt_engine = None
        print("STT Engine resources cleaned up.")

    def check_audio_permissions(self):
        """Check if the audio device can be accessed."""
        try:
            devices = sd.query_devices()
            default_device = sd.default.device[0]
            if default_device is not None:
                print(f"Default input device: {devices[default_device]}")
            else:
                self.fail("No default input device found.")
        except Exception as e:
            self.fail(f"Unable to query audio devices. Error: {e}")

        try:
            # Test if the default audio input can be opened
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1):
                print("Microphone permission check passed.")
        except Exception as e:
            self.fail(f"Microphone access denied or unavailable. Error: {e}")

    def run_audio_stream(self, duration=10):
        """Run the audio stream and transcribe for a specified duration."""
        transcription = []

        def callback(indata, frames, time, status):
            """Audio callback function."""
            if status:
                print(f"Audio Status: {status}", file=sys.stderr)
            self.audio_queue.put(bytes(indata))

            try:
                if not self.audio_queue.empty():
                    data = self.audio_queue.get(timeout=1)
                    if self.stt_engine and self.stt_engine.recognizer.AcceptWaveform(data):
                        result = json.loads(self.stt_engine.recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            transcription.append(text)
                            print(f"Recognized Text: {text}")
            except queue.Empty:
                print("Audio queue timeout: No audio data received.")
            except Exception as e:
                print(f"Error in callback: {e}", file=sys.stderr)

        print(f"Recording for {duration} seconds. Please speak into the microphone.")
        start_time = time.time()

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                                   channels=1, callback=callback):
                while time.time() - start_time < duration:
                    pass  # Keep running until the specified duration ends
        except Exception as e:
            self.fail(f"Failed during audio stream setup or transcription: {e}")

        return transcription

    def test_microphone_access(self):
        """Test if the microphone is accessible."""
        self.check_audio_permissions()

    def test_live_transcription(self):
        """Test live audio transcription for 10 seconds."""
        if self.stt_engine is None:
            self.fail("STT Engine is not initialized.")

        self.check_audio_permissions()

        transcription = self.run_audio_stream(duration=10)
        if not transcription:
            self.fail("No transcription was captured.")
        else:
            print(f"Transcription captured: {transcription}")


if __name__ == "__main__":
    unittest.main()
