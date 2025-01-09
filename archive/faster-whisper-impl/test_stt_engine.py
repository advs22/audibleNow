# import unittest
# import time
# import numpy as np
# import sounddevice as sd
# from stt_engine import STTEngine


# class TestSTTEngine(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         """Set up the shared STT Engine instance."""
#         try:
#             cls.stt_engine = STTEngine(model_path= "models/faster-whisper-small.en", device= "cpu", compute_type= "int8")
#             print("STT Engine initialized successfully.")
#         except Exception as e:
#             cls.stt_engine = None
#             raise RuntimeError(f"Failed to initialize STT Engine: {e}")

#     @classmethod
#     def tearDownClass(cls):
#         """Clean up the STT Engine instance."""
#         cls.stt_engine = None
#         print("STT Engine resources cleaned up.")

#     def test_live_transcription(self):
#         """Test live audio transcription for 10 seconds."""
#         self.assertIsNotNone(self.stt_engine, "STT Engine is not initialized.")
#         if self.stt_engine is None:
#             self.fail("STT Engine is not initialized.")

#         # Reset the audio buffer
#         self.stt_engine.audio_buffer = np.empty((0,), dtype=np.float32)

#         print("Listening for 10 seconds. Please speak into the microphone.")
#         start_time = time.time()

#         try:
#             with sd.InputStream(
#                 samplerate=self.stt_engine.samplerate,
#                 channels=1,
#                 dtype="float32",
#                 callback=self.stt_engine.audio_callback,
#             ):
#                 while time.time() - start_time < 10:
#                     # Collect audio data from the queue
#                     if not self.stt_engine.audio_queue.empty():
#                         data = self.stt_engine.audio_queue.get()
#                         self.stt_engine.audio_buffer = np.append(
#                             self.stt_engine.audio_buffer, data.flatten()
#                         )

#             # Final transcription processing
#             print("Finished listening, processing transcription.")
#             self.stt_engine.transcribe_audio()

#         except Exception as e:
#             self.fail(f"Error during live transcription test: {e}")

#         # Validate audio buffer and transcription results
#         self.assertGreater(
#             len(self.stt_engine.audio_buffer),
#             0,
#             "Audio buffer is empty after listening.",
#         )

#         print("Transcription test passed.")


# if __name__ == "__main__":
#     unittest.main()
