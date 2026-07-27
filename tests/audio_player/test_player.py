"""Tests for the AudioPlayer wrapper.

Every test here patches ``Playback`` where ``player`` imports it, so nothing in
this file needs a real output device. Patching ``just_playback.Playback``
directly would not work: ``player`` already bound the name at import time.
"""

from unittest.mock import patch

import pytest

from src.audio_player import AudioPlayer

PLAYBACK = "src.audio_player.player.Playback"


@pytest.fixture
def loaded_player(test_tone):
    """An AudioPlayer with a mocked engine and the test tone loaded."""
    with patch(PLAYBACK) as mock_playback_cls:
        engine = mock_playback_cls.return_value
        engine.duration = 2.0
        engine.curr_pos = 0.0
        engine.playing = False
        engine.paused = False
        engine.volume = 1.0

        player = AudioPlayer()
        player.load(test_tone)
        engine.reset_mock()  # drop the load_file call; tests assert on their own calls

        yield player, engine


# -- loading -------------------------------------------------------------


def test_load_hands_validated_path_to_engine(test_tone):
    with patch(PLAYBACK) as mock_playback_cls:
        engine = mock_playback_cls.return_value

        player = AudioPlayer()
        player.load(test_tone)

        engine.load_file.assert_called_once_with(str(test_tone))
        assert player.path == test_tone


def test_load_rejects_missing_path_before_touching_engine(tmp_path):
    with patch(PLAYBACK) as mock_playback_cls:
        player = AudioPlayer()

        with pytest.raises(FileNotFoundError):
            player.load(tmp_path / "nope.mp3")

        mock_playback_cls.assert_not_called()


def test_load_rejects_unsupported_extension_before_touching_engine(tmp_path):
    junk = tmp_path / "cover_art.png"
    junk.write_bytes(b"")

    with patch(PLAYBACK) as mock_playback_cls:
        player = AudioPlayer()

        with pytest.raises(ValueError):
            player.load(junk)

        mock_playback_cls.assert_not_called()


# -- transport -----------------------------------------------------------


@pytest.mark.parametrize("method", ["play", "pause", "resume", "stop"])
def test_transport_controls_delegate_once(loaded_player, method):
    player, engine = loaded_player

    getattr(player, method)()

    getattr(engine, method).assert_called_once_with()


@pytest.mark.parametrize("method", ["play", "pause", "resume", "stop"])
def test_transport_controls_require_a_loaded_file(method):
    player = AudioPlayer()

    with pytest.raises(RuntimeError, match="No audio file loaded"):
        getattr(player, method)()


def test_paused_reflects_engine_state(loaded_player):
    player, engine = loaded_player

    engine.paused = True
    assert player.paused is True

    engine.paused = False
    assert player.paused is False


def test_playing_reflects_engine_state(loaded_player):
    player, engine = loaded_player

    engine.playing = True
    assert player.playing is True

    engine.playing = False
    assert player.playing is False


# -- seek and volume -----------------------------------------------------


@pytest.mark.parametrize("position", [0, 1.25, 2.0])
def test_seek_passes_valid_position_through(loaded_player, position):
    player, engine = loaded_player

    player.seek(position)

    engine.seek.assert_called_once_with(position)


@pytest.mark.parametrize("position", [-0.1, 2.5])
def test_seek_rejects_out_of_range_without_calling_engine(loaded_player, position):
    player, engine = loaded_player

    with pytest.raises(ValueError, match="outside the track"):
        player.seek(position)

    engine.seek.assert_not_called()


def test_curr_pos_reports_engine_position(loaded_player):
    player, engine = loaded_player

    engine.curr_pos = 1.5
    assert player.curr_pos == 1.5


def test_curr_pos_normalises_engine_sentinel(loaded_player):
    """The backend reports -1 for 'nothing loaded'; callers should see 0.0."""
    player, engine = loaded_player

    engine.curr_pos = -1
    assert player.curr_pos == 0.0


@pytest.mark.parametrize("level", [0.0, 0.5, 1.0])
def test_set_volume_passes_valid_level_through(loaded_player, level):
    player, engine = loaded_player

    player.set_volume(level)

    engine.set_volume.assert_called_once_with(level)


@pytest.mark.parametrize("level", [-0.1, 1.1])
def test_set_volume_rejects_out_of_range_without_calling_engine(loaded_player, level):
    player, engine = loaded_player

    with pytest.raises(ValueError, match="outside the range"):
        player.set_volume(level)

    engine.set_volume.assert_not_called()


def test_duration_reports_engine_duration(loaded_player):
    player, engine = loaded_player

    engine.duration = 185.5
    assert player.duration == 185.5


# -- state before anything is loaded -------------------------------------


def test_state_queries_are_safe_before_loading():
    """Constructing an AudioPlayer must not need an audio device or a file."""
    player = AudioPlayer()

    assert player.playing is False
    assert player.paused is False
    assert player.curr_pos == 0.0
    assert player.duration == 0.0
    assert player.path is None


def test_constructing_player_does_not_construct_engine():
    """Engine construction is deferred - it raises when no output device exists."""
    with patch(PLAYBACK) as mock_playback_cls:
        AudioPlayer()

        mock_playback_cls.assert_not_called()
