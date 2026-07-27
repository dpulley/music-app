"""Tests for tag reading.

mutagen is mocked for the tagged cases (building real tagged files would mean
committing binary media), and the project's generated WAV fixture covers the
untagged path for real - which is the common case, not an edge case.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.database.metadata import (
    TrackMetadata,
    format_duration,
    read_metadata,
)

MUTAGEN_FILE = "src.database.metadata.mutagen.File"


def fake_audio(tags=None, length=185.0):
    audio = MagicMock()
    audio.tags = tags
    audio.info.length = length
    return audio


# -- duration formatting -------------------------------------------------


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "0:00"),
        (5, "0:05"),
        (65, "1:05"),
        (185.4, "3:05"),
        (3600, "1:00:00"),
        (3725, "1:02:05"),
        (None, "0:00"),
        (-10, "0:00"),
    ],
)
def test_duration_formatting(seconds, expected):
    assert format_duration(seconds) == expected


# -- tagged files --------------------------------------------------------


def test_reads_full_tags():
    tags = {"title": ["Blue Monday"], "artist": ["New Order"], "album": ["Power"]}

    with patch(MUTAGEN_FILE, return_value=fake_audio(tags)):
        meta = read_metadata(Path("music/track.mp3"))

    assert meta.title == "Blue Monday"
    assert meta.artist == "New Order"
    assert meta.album == "Power"
    assert meta.duration == 185.0


def test_falls_back_through_artist_keys():
    tags = {"title": ["Song"], "albumartist": ["Various"]}

    with patch(MUTAGEN_FILE, return_value=fake_audio(tags)):
        meta = read_metadata(Path("music/track.mp3"))

    assert meta.artist == "Various"


def test_empty_tag_values_fall_back_to_filename():
    tags = {"title": [""], "artist": []}

    with patch(MUTAGEN_FILE, return_value=fake_audio(tags)):
        meta = read_metadata(Path("music/quiet_song.mp3"))

    assert meta.title == "quiet_song"
    assert meta.artist == ""


def test_scalar_tag_values_are_accepted():
    """Not every mutagen backend hands back lists."""
    with patch(MUTAGEN_FILE, return_value=fake_audio({"title": "Plain String"})):
        meta = read_metadata(Path("music/track.flac"))

    assert meta.title == "Plain String"


# -- untagged and broken files -------------------------------------------


def test_untagged_file_uses_filename_and_keeps_duration():
    with patch(MUTAGEN_FILE, return_value=fake_audio(tags=None, length=2.0)):
        meta = read_metadata(Path("assets/test_tone.wav"))

    assert meta.title == "test_tone"
    assert meta.artist == ""
    assert meta.album == ""
    assert meta.duration == 2.0


def test_unreadable_file_falls_back_instead_of_raising():
    with patch(MUTAGEN_FILE, side_effect=Exception("corrupt header")):
        meta = read_metadata(Path("music/broken.mp3"))

    assert meta.title == "broken"
    assert meta.duration == 0.0


def test_unrecognised_file_falls_back():
    """mutagen returns None for a file it cannot identify."""
    with patch(MUTAGEN_FILE, return_value=None):
        meta = read_metadata(Path("music/mystery.ogg"))

    assert meta.title == "mystery"


def test_missing_duration_reports_zero_not_none():
    audio = fake_audio(tags=None)
    audio.info.length = None

    with patch(MUTAGEN_FILE, return_value=audio):
        meta = read_metadata(Path("music/track.mp3"))

    assert meta.duration == 0.0


# -- description ---------------------------------------------------------


def test_description_combines_artist_and_title():
    meta = TrackMetadata(path=Path("x.mp3"), title="Song", artist="Band")

    assert meta.description == "Band - Song"


def test_description_of_untagged_track_is_title_alone():
    meta = TrackMetadata(path=Path("x.mp3"), title="just_a_file")

    assert meta.description == "just_a_file"
    assert "-" not in meta.description


def test_duration_text_uses_minutes_and_seconds():
    meta = TrackMetadata(path=Path("x.mp3"), title="Song", duration=185.0)

    assert meta.duration_text == "3:05"


# -- the real fixture ----------------------------------------------------


def test_reads_the_real_generated_fixture(test_tone):
    """End-to-end against a real file with genuinely no tags."""
    meta = read_metadata(test_tone)

    assert meta.title == "test_tone"
    assert meta.artist == ""
    assert meta.duration == pytest.approx(2.0, abs=0.1)
    assert meta.description == "test_tone"
