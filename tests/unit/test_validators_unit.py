from src.utils.validators import is_audio_filename
def test_is_audio_filename():
    assert is_audio_filename("a.wav")
    assert is_audio_filename("b.MP3")
    assert not is_audio_filename("c.txt")
