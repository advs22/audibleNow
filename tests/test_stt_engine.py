import pytest
import sounddevice as sd
from src.stt.stt_engine import STTEngine


class TestSTTEngine:
    @pytest.fixture(scope="class")
    def stt_engine(self):
        """Fixture to initialize the STT Engine."""
        model_path = "models/vosk-model-small-en-us-0.15"
        try:
            return STTEngine(model_path)
        except FileNotFoundError as e:
            pytest.fail(f"Model file not found: {e}")
        except Exception as e:
            pytest.fail(f"Failed to initialize STT Engine: {e}")

    def test_microphone_access(self):
        """Test microphone access."""
        try:
            with sd.RawInputStream(
                samplerate=16000, blocksize=8000, dtype="int16", channels=1
            ):
                pass
        except sd.PortAudioError as e:
            pytest.fail(f"Microphone access error: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error during microphone access check: {e}")

    def test_live_transcription(self, stt_engine):
        """Integration test for live transcription using the STT engine."""
        transcription = []

        def on_transcription_result(text):
            """Callback function to store recognized text."""
            if text:
                print(text)
                transcription.append(text)

        try:
            # Start listening for 15 seconds using the STT engine.
            print("Listening... Speak into the microphone.")
            stt_engine.listen_and_transcribe(
                duration=30, on_transcription=on_transcription_result
            )
        except Exception as e:
            pytest.fail(f"Unexpected error during live transcription: {e}")

        # Assert that transcription occurred
        assert transcription, "No transcription captured during live transcription."

        # Print all captured transcription results
        print("\nFinal Transcription Results:", transcription)
