def is_audio_filename(name: str) -> bool:
    return any(name.lower().endswith(ext) for ext in [".wav",".mp3",".flac",".m4a",".ogg"])
