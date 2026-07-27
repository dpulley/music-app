"""Tests for the GUI-free player logic.

PlayerController imports no GUI library, so all of this runs with neither a
display nor an audio device - the AudioPlayer is a mock throughout.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.database.metadata import TrackMetadata
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
    """Untagged files fall back to the filename stem, so 'one.mp3' -> 'one'."""
    controller.play_selected()
    player.playing = True

    assert controller.now_playing == "Playing: one"


def test_now_playing_while_paused(controller, player):
    controller.play_selected()
    player.paused = True

    assert controller.now_playing == "Paused: one"


def test_now_playing_when_stopped(controller, player):
    controller.play_selected()
    player.playing = False
    player.paused = False

    assert controller.now_playing == "Stopped: one"


def test_now_playing_uses_tags_when_present(controller, player):
    controller._metadata[TRACKS[0]] = TrackMetadata(
        path=TRACKS[0], title="Blue Monday", artist="New Order"
    )
    controller.play_selected()
    player.playing = True

    assert controller.now_playing == "Playing: New Order - Blue Monday"


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

    assert controller.now_playing == "Playing: two"


# -- position and progress -----------------------------------------------


def test_position_and_duration_are_zero_before_loading(controller):
    assert controller.position == 0.0
    assert controller.duration == 0.0
    assert controller.progress_fraction == 0.0
    assert controller.position_text == "0:00 / 0:00"


def test_position_reports_engine_state(controller, player):
    player.curr_pos = 30.0
    player.duration = 120.0
    controller.play_selected()

    assert controller.position == 30.0
    assert controller.duration == 120.0


def test_progress_fraction_is_position_over_duration(controller, player):
    player.curr_pos = 30.0
    player.duration = 120.0
    controller.play_selected()

    assert controller.progress_fraction == 0.25


def test_progress_fraction_handles_zero_length_track(controller, player):
    """A zero-length track must not divide by zero."""
    player.curr_pos = 0.0
    player.duration = 0.0
    controller.play_selected()

    assert controller.progress_fraction == 0.0


def test_progress_fraction_is_clamped(controller, player):
    player.curr_pos = 500.0
    player.duration = 120.0
    controller.play_selected()

    assert controller.progress_fraction == 1.0


def test_position_text_is_minutes_and_seconds(controller, player):
    player.curr_pos = 65.0
    player.duration = 200.0
    controller.play_selected()

    assert controller.position_text == "1:05 / 3:20"


# -- seeking -------------------------------------------------------------


def test_seek_fraction_converts_to_seconds(controller, player):
    player.duration = 200.0
    controller.play_selected()

    seconds = controller.seek_fraction(0.5)

    assert seconds == 100.0
    player.seek.assert_called_once_with(100.0)


@pytest.mark.parametrize(
    ("fraction", "expected"), [(-0.5, 0.0), (1.5, 200.0), (0.0, 0.0), (1.0, 200.0)]
)
def test_seek_fraction_clamps_out_of_range(controller, player, fraction, expected):
    """A slider can overshoot by a pixel; that shouldn't be an error."""
    player.duration = 200.0
    controller.play_selected()

    assert controller.seek_fraction(fraction) == expected
    player.seek.assert_called_once_with(expected)


def test_seek_before_loading_does_nothing(controller, player):
    assert controller.seek_fraction(0.5) is None
    player.seek.assert_not_called()


def test_seek_on_zero_length_track_does_nothing(controller, player):
    player.duration = 0.0
    controller.play_selected()

    assert controller.seek_fraction(0.5) is None
    player.seek.assert_not_called()


# -- search --------------------------------------------------------------


def tag(controller, track, **kwargs):
    """Give a track known metadata without touching the filesystem."""
    controller._metadata[track] = TrackMetadata(path=track, **kwargs)


def test_all_tracks_visible_without_a_query(controller):
    assert controller.visible_tracks == TRACKS


def test_search_matches_filename(controller):
    assert controller.search("two") == [TRACKS[1]]


def test_search_matches_title(controller):
    tag(controller, TRACKS[0], title="Blue Monday")

    assert controller.search("monday") == [TRACKS[0]]


def test_search_matches_artist(controller):
    tag(controller, TRACKS[1], title="Song", artist="New Order")

    assert controller.search("new order") == [TRACKS[1]]


def test_search_matches_album(controller):
    tag(controller, TRACKS[2], title="Song", album="Power Corruption")

    assert controller.search("corruption") == [TRACKS[2]]


def test_search_is_case_insensitive(controller):
    tag(controller, TRACKS[0], title="Blue Monday")

    assert controller.search("BLUE") == [TRACKS[0]]


def test_search_with_no_matches_returns_empty(controller):
    assert controller.search("zzzznothing") == []


def test_clearing_search_restores_everything(controller):
    controller.search("two")

    assert controller.clear_search() == TRACKS
    assert controller.query == ""


def test_blank_query_is_treated_as_no_filter(controller):
    assert controller.search("   ") == TRACKS


def test_search_does_not_disturb_playback(controller, player):
    controller.play_selected()
    player.playing = True
    player.reset_mock()

    controller.search("zzzznothing")

    player.stop.assert_not_called()
    player.pause.assert_not_called()
    assert controller.selected_track == TRACKS[0]
    assert controller.now_playing.startswith("Playing:")


def test_visible_indices_map_back_to_the_playlist(controller):
    controller.search("three")

    assert controller.visible_indices() == [2]


def test_visible_indices_cover_everything_when_unfiltered(controller):
    assert controller.visible_indices() == [0, 1, 2]


# -- metadata ------------------------------------------------------------


def test_metadata_is_read_once_and_reused(controller):
    with patch("src.ui.controller.read_metadata") as mock_read:
        mock_read.return_value = TrackMetadata(path=TRACKS[0], title="Song")

        controller.metadata_for(TRACKS[0])
        controller.metadata_for(TRACKS[0])

    mock_read.assert_called_once_with(TRACKS[0])


def test_describe_uses_metadata_description(controller):
    tag(controller, TRACKS[0], title="Song", artist="Band")

    assert controller.describe(TRACKS[0]) == "Band - Song"
