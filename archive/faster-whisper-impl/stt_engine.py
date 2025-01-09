
# import sounddevice as sd
# import queue
# import numpy as np
# from faster_whisper import WhisperModel

# class STTEngine:
#     def __init__(self, model_path: str, device: str = "cpu", compute_type: str = "int8"):
#         """
#         Initialize faster-whisper model.
#         model_path: Whisper model size ('small', 'base', 'small', 'medium', 'large', 'large-v3').
#         device: Device to use for inference ('cpu', 'cuda', 'auto').
#         compute_type: Compute precision ('int8', 'int8_float16', 'float16', 'float32').
#         """
#         self.model_path = model_path
#         print("Loading faster-whisper model. This may take a while...")
#         self.model = WhisperModel(model_path, device=device, compute_type=compute_type)
#         print("faster-whisper model loaded successfully.")
#         self.audio_queue = queue.Queue()
#         self.samplerate = 16000
#         self.audio_buffer = np.empty((0,), dtype=np.float32)  # Store audio chunks here

#     def audio_callback(self, indata, frames, time, status):
#         """Callback function to capture live audio."""
#         if status:
#             print(f"Audio Status: {status}")
#         self.audio_queue.put(indata.copy())

#     def listen_and_transcribe(self):
#         """Listen to live audio and transcribe it using faster-whisper."""
#         with sd.InputStream(
#             samplerate=self.samplerate,
#             channels=1,
#             dtype="float32",
#             callback=self.audio_callback,
#         ):
#             print("Listening... Press Ctrl+C to stop.")
#             try:
#                 while True:
#                     # Process audio chunks
#                     if not self.audio_queue.empty():
#                         data = self.audio_queue.get()
#                         self.audio_buffer = np.append(self.audio_buffer, data.flatten())

#                         # Transcribe when buffer exceeds ~10 seconds of audio
#                         if len(self.audio_buffer) > self.samplerate * 10:
#                             print("Transcribing...")
#                             self.transcribe_audio()
#                             self.audio_buffer = np.empty(
#                                 (0,), dtype=np.float32
#                             )  # Reset buffer
#             except KeyboardInterrupt:
#                 print("\nExiting...")
#                 if len(self.audio_buffer) > 0:
#                     print("Final transcription for remaining audio:")
#                     self.transcribe_audio()

#     def transcribe_audio(self):
#         """Transcribe the audio buffer using faster-whisper."""
#         # Convert audio buffer to a format usable by faster-whisper
#         audio_data = np.copy(self.audio_buffer)
#         segments, _ = self.model.transcribe(audio_data, beam_size=5)
#         transcription = " ".join(segment.text for segment in segments)
#         print(f"Transcription: {transcription}")


# if __name__ == "__main__":
#     stt = STTEngine(model_path="models/faster-whisper-small.en", device="cpu", compute_type="int8")
#     stt.listen_and_transcribe()
