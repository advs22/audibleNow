import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

class STTEngine:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()

    def audio_callback(self, indata, frames, time, status):
        """Callback function to capture live audio."""
        if status:
            print(f"Audio Status: {status}")
        self.audio_queue.put(bytes(indata))

    def listen_and_transcribe(self):
        """Listen to live audio and transcribe it."""
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                               channels=1, callback=self.audio_callback):
            print("Listening... Press Ctrl+C to stop.")
            while True:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    print(f"Recognized: {result.get('text', '')}")
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    print(f"Partial: {partial.get('partial', '')}")

if __name__ == "__main__":
    model_path = "models/vosk-model-small-en-us-0.15"
    stt = STTEngine(model_path)
    try:
        stt.listen_and_transcribe()
    except KeyboardInterrupt:
        print("\nExiting...")
