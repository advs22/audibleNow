import os

def check_model_exists(model_path: str) -> bool:
    """Check if the Vosk model exists in the specified path."""
    return os.path.exists(model_path) and os.path.isdir(model_path)
