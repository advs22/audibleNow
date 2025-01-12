import ffmpeg
import sounddevice as sd
import queue
import json
import threading
import time
from vosk import Model, KaldiRecognizer
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


class AudioSource:
    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError


class MicrophoneSource(AudioSource):
    def __init__(self, samplerate, blocksize, audio_queue):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.audio_queue = audio_queue

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio Status: {status}")
        try:
            self.audio_queue.put_nowait(bytes(indata))
        except queue.Full:
            print("Audio queue is full. Dropping audio frame.")

    def start(self):
        self.stream = sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype="int16",
            channels=1,
            callback=self.audio_callback
        )
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.stream.close()

    def read(self):
        return self.audio_queue.get(timeout=1)


class YouTubeSource(AudioSource):
    def __init__(self, youtube_url, samplerate, blocksize, audio_queue):
        self.youtube_url = youtube_url
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.audio_queue = audio_queue

    def start(self):
        yt = YouTube(self.youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream is None:
            raise ValueError("No audio stream found for the provided YouTube URL.")
        self.audio_file_path = audio_stream.download(filename='temp_audio')
        self.process = (
            ffmpeg.input(self.audio_file_path)
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar=self.samplerate)
            .run_async(pipe_stdout=True)
        )

    def stop(self):
        self.process.terminate()

    def read(self):
        return self.process.stdout.read(self.blocksize)


class MediaSource(AudioSource):
    def __init__(self, media_file_path, samplerate, blocksize, audio_queue):
        self.media_file_path = media_file_path
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.audio_queue = audio_queue

    def start(self):
        self.process = (
            ffmpeg.input(self.media_file_path)
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar=self.samplerate)
            .run_async(pipe_stdout=True)
        )

    def stop(self):
        self.process.terminate()

    def read(self):
        return self.process.stdout.read(self.blocksize)


class TranscriptionEngine:
    def __init__(self, model_path, samplerate=16000, blocksize=8000, queue_size=50):
        if not model_path:
            raise ValueError("Model path is required.")

        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, samplerate)
        self.audio_queue = queue.Queue(maxsize=queue_size)
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.stop_event = threading.Event()

    def process_audio(self, on_transcription):
        while not self.stop_event.is_set():
            try:
                data = self.audio_queue.get(timeout=1)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    recognized_text = result.get("text", "")
                    if on_transcription and recognized_text:
                        on_transcription(recognized_text)
            except queue.Empty:
                continue
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON result: {e}")
            except Exception as e:
                print(f"Unexpected error in process_audio: {e}")

    def transcribe(self, source: AudioSource, duration=None, on_transcription=None):
        print("Starting real-time transcription...")
        stop_time = time.time() + duration if duration else None
        self.stop_event.clear()

        processing_thread = threading.Thread(
            target=self.process_audio, args=(on_transcription,), daemon=True
        )
        processing_thread.start()

        try:
            source.start()
            while not self.stop_event.is_set():
                if stop_time and time.time() >= stop_time:
                    print("Stopping transcription after duration timeout.")
                    break
                data = source.read()
                if data:
                    self.audio_queue.put_nowait(data)
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            source.stop()
            self.stop_event.set()
            processing_thread.join()
            print("Transcription stopped and resources released.")

    def fetch_youtube_transcript(self, youtube_url, on_transcription=None):
        print("Fetching YouTube transcript...")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(youtube_url.split('v=')[1])
            for entry in transcript:
                if on_transcription:
                    on_transcription(entry['text'])
        except Exception as e:
            print(f"Error fetching YouTube transcript: {e}")

    def shutdown(self):
        print("Shutting down TranscriptionEngine...")
        self.stop_event.set()


# Example usage:
# if __name__ == "__main__":
#     model_path = "path/to/vosk/model"
#     engine = TranscriptionEngine(model_path)

#     def on_transcription(text):
#         print(f"Transcribed: {text}")

#     # Microphone transcription
#     mic_source = MicrophoneSource(samplerate=16000, blocksize=8000, audio_queue=engine.audio_queue)
#     engine.transcribe(mic_source, duration=30, on_transcription=on_transcription)

#     # YouTube real-time transcription using audio stream
#     youtube_source = YouTubeSource(youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", samplerate=16000, blocksize=8000, audio_queue=engine.audio_queue)
#     engine.transcribe(youtube_source, duration=60, on_transcription=on_transcription)

#     # Fetch YouTube transcript using youtube-transcript-api
#     engine.fetch_youtube_transcript(youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", on_transcription=on_transcription)

#     # Media transcription
#     media_source = MediaSource(media_file_path="path/to/media/file", samplerate=16000, blocksize=8000, audio_queue=engine.audio_queue)
#     engine.transcribe(media_source, duration=60, on_transcription=on_transcription)