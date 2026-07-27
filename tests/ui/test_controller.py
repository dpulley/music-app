"""Tests for the GUI-free player logic.

PlayerController imports no GUI library, so all of this runs with neither a
display nor an audio device - the AudioPlayer is a mock throughout.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.ui.controller import EMPTY_LIBRARY, NOTHING_LOADED, PlayerController

TRACKS = [Path("music/one.mp3"), Path("music/two.wav"), Path("music/three.flac")]


@pytest.fixture
def player():
    """A player mock that starts idle, like a freshly constructed one."""
    mock = MagicMock()
    mock.playing = False
    mock.paused = False
    return mock


@pytest.fixture
def controller(player):
    return PlayerController(TRACKS, player=player)


# -- library and selection -----------------------------------------------


def test_starts_on_the_first_track(controller):
    assert controller.tracks == TRACKS
    assert controller.selected_index == 0
    assert controller.selected_track == TRACKS[0]


def test_selection_does_not_start_playback(controller, player):
    controller.select(2)

    assert controller.selected_track == TRACKS[2]
    player.load.assert_not_called()
    player.play.assert_not_called()


def test_selection_does_not_interrupt_current_playback(controller, player):
    controller.play_selected()
    player.reset_mock()

    controller.select(2)

    player.stop.assert_not_called()
    player.pause.assert_not_called()


def test_empty_library_reports_empty(player):
    controller = PlayerController([], player=player)

    assert controller.is_empty
    assert controller.tracks == []
    assert controller.selected_index is None
    assert controller.now_playing == EMPTY_LIBRARY


# -- play ----------------------------------------------------------------


def test_play_selected_loads_and_starts(controller, player):
    played = controller.play_selected()

    player.load.assert_called_once_with(TRACKS[0])
    player.play.assert_called_once()
    assert played == TRACKS[0]


def test_play_selected_on_empty_library_does_nothing(player):
    controller = PlayerController([], player=player)

    assert controller.play_selected() is None
    player.load.assert_not_called()


# -- pause toggle --------------------------------------------------------


def test_toggle_pauses_while_playing(controller, player):
    controller.play_selected()
    player.playing = True

    controller.toggle_pause()

    player.pause.assert_called_once()


def test_toggle_resumes_while_paused(controller, player):
    controller.play_selected()
    player.paused = True

    controller.toggle_pause()

    player.resume.assert_called_once()


def test_toggle_replays_a_stopped_track(controller, player):
    controller.play_selected()
    player.playing = False
    player.paused = False
    player.reset_mock()

    controller.toggle_pause()

    player.play.assert_called_once()


def test_toggle_before_anything_loaded_starts_the_selection(controller, player):
    controller.toggle_pause()

    player.load.assert_called_once_with(TRACKS[0])
    player.play.assert_called_once()


# -- stop ----------------------------------------------------------------


def test_stop_halts_playback(controller, player):
    controller.play_selected()

    controller.stop()

    player.stop.assert_called_once()


def test_stop_before_anything_loaded_does_nothing(controller, player):
    assert controller.stop() is None
    player.stop.assert_not_called()


# -- next / previous -----------------------------------------------------


def test_next_advances_and_plays(controller, player):
    controller.play_selected()
    player.reset_mock()

    played = controller.next_track()

    assert played == TRACKS[1]
    player.load.assert_called_once_with(TRACKS[1])
    player.play.assert_called_once()


def test_next_at_the_end_leaves_playback_alone(controller, player):
    controller.select(2)
    controller.play_selected()
    player.reset_mock()

    assert controller.next_track() is None
    player.load.assert_not_called()
    player.stop.assert_not_called()


def test_previous_steps_back_and_plays(controller, player):
    controller.select(2)
    controller.play_selected()
    player.reset_mock()

    played = controller.previous_track()

    assert played == TRACKS[1]
    player.load.assert_called_once_with(TRACKS[1])


def test_previous_at_the_start_leaves_playback_alone(controller, player):
    controller.play_selected()
    player.reset_mock()

    assert controller.previous_track() is None
    player.load.assert_not_called()


# -- now playing ---------------------------------------------------------


def test_now_playing_before_anything_loaded(controller):
    assert controller.now_playing == NOTHING_LOADED


def test_now_playing_while_playing(controller, player):
    controller.play_selected()
    player.playing = True

    assert controller.now_playing == "Playing: one.mp3"


def test_now_playing_while_paused(controller, player):
    controller.play_selected()
    player.paused = True

    assert controller.now_playing == "Paused: one.mp3"


def test_now_playing_when_stopped(controller, player):
    controller.play_selected()
    player.playing = False
    player.paused = False

    assert controller.now_playing == "Stopped: one.mp3"


# -- failures ------------------------------------------------------------


def test_unplayable_track_is_reported_not_raised(controller, player):
    player.load.side_effect = OSError("corrupt file")

    assert controller.play_selected() is None
    assert "Could not play one.mp3" in controller.now_playing
    assert "corrupt file" in controller.now_playing


def test_error_clears_after_a_successful_play(controller, player):
    player.load.side_effect = OSError("corrupt file")
    controller.play_selected()

    player.load.side_effect = None
    controller.select(1)
    controller.play_selected()
    player.playing = True

    assert controller.now_playing == "Playing: two.wav"
