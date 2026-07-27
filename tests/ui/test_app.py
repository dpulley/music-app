"""Tests for the window layer.

``src.ui.app.ctk`` is patched wholesale, so these construct the window and
exercise its callbacks with no display present. They verify *wiring* - that
each control reaches the right controller method - not appearance, which only
a human looking at the screen can judge (see task 4.2).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ui.app import TRANSPORT_LABELS, MusicAppWindow

TRACKS = [Path("music/one.mp3"), Path("music/two.wav")]


@pytest.fixture
def controller():
    """A controller stand-in with a populated library."""
    mock = MagicMock()
    mock.is_empty = False
    mock.tracks = TRACKS
    mock.now_playing = "No track loaded"
    return mock


@pytest.fixture
def empty_controller():
    mock = MagicMock()
    mock.is_empty = True
    mock.tracks = []
    mock.now_playing = "No tracks found"
    return mock


@pytest.fixture
def window(controller):
    with patch("src.ui.app.ctk"):
        yield MusicAppWindow(controller=controller)


# -- construction --------------------------------------------------------


def test_window_constructs_without_a_display(controller):
    with patch("src.ui.app.ctk") as mock_ctk:
        MusicAppWindow(controller=controller)

    mock_ctk.CTk.assert_called_once()
    mock_ctk.CTk.return_value.title.assert_called_once()
    mock_ctk.CTk.return_value.geometry.assert_called_once()


def test_sidebar_gets_one_button_per_track(window):
    assert len(window.track_buttons) == len(TRACKS)


def test_transport_has_all_four_controls(window):
    assert set(window.transport_buttons) == {"previous", "play_pause", "stop", "next"}


def test_transport_labels_are_distinct():
    """Four controls that read the same would be unusable."""
    assert len(set(TRANSPORT_LABELS.values())) == 4


# -- control wiring ------------------------------------------------------


def test_play_pause_button_toggles_via_controller(window, controller):
    window.on_play_pause()

    controller.toggle_pause.assert_called_once()


def test_stop_button_stops_via_controller(window, controller):
    window.on_stop()

    controller.stop.assert_called_once()


def test_next_button_advances_via_controller(window, controller):
    window.on_next()

    controller.next_track.assert_called_once()


def test_previous_button_steps_back_via_controller(window, controller):
    window.on_previous()

    controller.previous_track.assert_called_once()


def test_selecting_a_track_selects_but_does_not_play(window, controller):
    window.on_select(1)

    controller.select.assert_called_once_with(1)
    controller.play_selected.assert_not_called()


def test_each_sidebar_button_selects_its_own_index(controller):
    """A late-bound closure would make every row select the last track."""
    with patch("src.ui.app.ctk") as mock_ctk:
        window = MusicAppWindow(controller=controller)

        commands = [
            call.kwargs["command"]
            for call in mock_ctk.CTkButton.call_args_list
            if "command" in call.kwargs and call.kwargs.get("anchor") == "w"
        ]

    assert len(commands) == len(TRACKS)

    for index, command in enumerate(commands):
        controller.select.reset_mock()
        command()
        controller.select.assert_called_once_with(index)


# -- display refresh -----------------------------------------------------


def test_every_action_refreshes_the_now_playing_label(window, controller):
    controller.now_playing = "Playing: one.mp3"

    window.on_play_pause()

    window.now_playing_label.configure.assert_called_with(text="Playing: one.mp3")


def test_refresh_reads_current_controller_state(window, controller):
    controller.now_playing = "Paused: two.wav"

    window.refresh()

    window.now_playing_label.configure.assert_called_with(text="Paused: two.wav")


# -- empty library -------------------------------------------------------


def test_empty_library_shows_message_and_no_track_buttons(empty_controller):
    with patch("src.ui.app.ctk"):
        window = MusicAppWindow(controller=empty_controller)

    assert window.track_buttons == []
    assert hasattr(window, "empty_label")


def test_empty_library_disables_transport(empty_controller):
    with patch("src.ui.app.ctk"):
        window = MusicAppWindow(controller=empty_controller)

    for button in window.transport_buttons.values():
        button.configure.assert_any_call(state="disabled")


def test_populated_library_leaves_transport_enabled(window):
    for button in window.transport_buttons.values():
        for call in button.configure.call_args_list:
            assert call.kwargs.get("state") != "disabled"


# -- lifecycle -----------------------------------------------------------


def test_mainloop_runs_the_toolkit_loop(window):
    window.mainloop()

    window.root.mainloop.assert_called_once()
