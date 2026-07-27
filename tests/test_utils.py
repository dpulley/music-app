"""Tests for path validation.

These use ``tmp_path`` files rather than the generated tone because validation
only inspects existence and extension - the bytes never matter here.
"""

import pytest

from src.utils import SUPPORTED_EXTENSIONS, validate_music_path


@pytest.mark.parametrize("extension", sorted(SUPPORTED_EXTENSIONS))
def test_accepts_every_supported_extension(tmp_path, extension):
    audio_file = tmp_path / f"track{extension}"
    audio_file.write_bytes(b"not really audio, but validation doesn't decode")

    assert validate_music_path(audio_file) == audio_file


def test_accepts_path_given_as_string(tmp_path):
    audio_file = tmp_path / "track.wav"
    audio_file.write_bytes(b"")

    assert validate_music_path(str(audio_file)) == audio_file


def test_extension_matching_is_case_insensitive(tmp_path):
    audio_file = tmp_path / "TRACK.MP3"
    audio_file.write_bytes(b"")

    assert validate_music_path(audio_file) == audio_file


def test_missing_path_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_music_path(tmp_path / "does_not_exist.mp3")


def test_directory_raises_file_not_found(tmp_path):
    # A directory named like a track is still not something we can play.
    directory = tmp_path / "album.mp3"
    directory.mkdir()

    with pytest.raises(FileNotFoundError):
        validate_music_path(directory)


def test_unsupported_extension_raises_value_error(tmp_path):
    text_file = tmp_path / "liner_notes.txt"
    text_file.write_text("not audio")

    with pytest.raises(ValueError, match="Unsupported audio format"):
        validate_music_path(text_file)


def test_generated_test_tone_is_valid(test_tone):
    """The shared fixture must itself pass validation, or every other test lies."""
    assert validate_music_path(test_tone) == test_tone
