import pytest
from unittest.mock import patch
from stt.stt_engine import TranscriptionEngine
from stt.utils import (
    check_model_exists,
    fetch_youtube_transcript,
    initialize_stt_engine,
    transcribe_from_media,
    transcribe_from_microphone,
    transcribe_from_youtube,
)


@pytest.mark.parametrize(
    "model_path, exists, is_dir, expected",
    [
        ("models/vosk-model-en-us-0.22-lgraph", True, True, True),
        ("models/nonexistent-model", False, False, False),
    ],
)
def test_check_model_exists(model_path, exists, is_dir, expected):
    with patch("os.path.exists", return_value=exists), patch(
        "os.path.isdir", return_value=is_dir
    ):
        result = check_model_exists(model_path)
        print(f"Check model exists for {model_path}: {result}")
        assert result == expected


def test_initialize_stt_engine_success():
    model_path = "models/vosk-model-en-us-0.22-lgraph"
    if not check_model_exists(model_path):
        pytest.skip(f"Model path {model_path} does not exist.")
    engine = initialize_stt_engine(model_path)
    print(f"Initialized STT engine with model path {model_path}")
    assert isinstance(engine, TranscriptionEngine)


def test_initialize_stt_engine_file_not_found():
    model_path = "models/nonexistent-model"
    with pytest.raises(RuntimeError):
        initialize_stt_engine(model_path)
    print(f"RuntimeError raised for model path {model_path}")


@pytest.mark.microphone
def test_transcribe_from_microphone():
    model_path = "models/vosk-model-en-us-0.22-lgraph"
    if not check_model_exists(model_path):
        pytest.skip(f"Model path {model_path} does not exist.")

    engine = initialize_stt_engine(model_path)

    with patch("builtins.print") as mock_print:
        transcribe_from_microphone(
            engine, on_transcription=lambda text: mock_print(f"Transcribed: {text}")
        )
        mock_print.assert_called()
    print("Transcription from microphone test completed.")


@pytest.mark.youtube
def test_transcribe_from_youtube():
    model_path = "models/vosk-model-en-us-0.22-lgraph"
    if not check_model_exists(model_path):
        pytest.skip(f"Model path {model_path} does not exist.")

    engine = initialize_stt_engine(model_path)
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    with patch("builtins.print") as mock_print:
        transcribe_from_youtube(
            engine,
            youtube_url,
            on_transcription=lambda text: mock_print(f"Transcribed: {text}"),
        )
        mock_print.assert_called()
    print("Transcription from YouTube test completed.")


@pytest.mark.youtube
def test_fetch_youtube_transcript():
    engine = initialize_stt_engine("models/vosk-model-en-us-0.22-lgraph")
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    with patch("builtins.print") as mock_print:
        fetch_youtube_transcript(engine, youtube_url)
        # This assumes fetch_youtube_transcript prints the transcriptions through on_transcription callback
        mock_print.assert_called()
    print("Fetch YouTube transcript test completed.")


@pytest.mark.media
def test_transcribe_from_media():
    model_path = "models/vosk-model-en-us-0.22-lgraph"
    if not check_model_exists(model_path):
        pytest.skip(f"Model path {model_path} does not exist.")

    engine = initialize_stt_engine(model_path)
    media_file_path = "path/to/media/file"

    with patch("builtins.print") as mock_print:
        transcribe_from_media(
            engine,
            media_file_path,
            on_transcription=lambda text: mock_print(f"Transcribed: {text}"),
        )
        mock_print.assert_called()
    print("Transcription from media test completed.")


if __name__ == "__main__":
    pytest.main()