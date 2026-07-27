"""Tests for the window layer.

``src.ui.app.ctk`` is patched wholesale, so these construct the window and
exercise its callbacks with no display present. They verify *wiring* - that
each control reaches the right controller method - not appearance, which only
a human looking at the screen can judge (see task 4.2).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ui.app import REFRESH_INTERVAL_MS, TRANSPORT_LABELS, MusicAppWindow

TRACKS = [Path("music/one.mp3"), Path("music/two.wav")]


@pytest.fixture
def controller():
    """A controller stand-in with a populated library."""
    mock = MagicMock()
    mock.is_empty = False
    mock.tracks = TRACKS
    mock.visible_tracks = TRACKS
    mock.visible_indices.return_value = list(range(len(TRACKS)))
    mock.describe.side_effect = lambda track: track.stem
    mock.now_playing = "No track loaded"
    mock.position_text = "0:00 / 0:00"
    mock.progress_fraction = 0.0
    return mock


@pytest.fixture
def empty_controller():
    mock = MagicMock()
    mock.is_empty = True
    mock.tracks = []
    mock.visible_tracks = []
    mock.visible_indices.return_value = []
    mock.now_playing = "No tracks found"
    mock.position_text = "0:00 / 0:00"
    mock.progress_fraction = 0.0
    return mock


@pytest.fixture
def window(controller):
    # A patched ctk hands back the same return_value for every CTkLabel call,
    # which would make the now-playing and position labels the same object and
    # any assertion about one of them meaningless. Give each widget call its
    # own mock so the two labels stay distinguishable.
    with patch("src.ui.app.ctk") as mock_ctk:
        mock_ctk.CTkLabel.side_effect = lambda *args, **kwargs: MagicMock()
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


# -- progress and seeking ------------------------------------------------


def test_progress_reflects_controller_fraction(window, controller):
    controller.progress_fraction = 0.42

    window.refresh()

    window.progress.set.assert_called_with(0.42)


def test_position_label_shows_elapsed_and_total(window, controller):
    controller.position_text = "1:05 / 3:20"

    window.refresh()

    window.position_label.configure.assert_called_with(text="1:05 / 3:20")


def test_releasing_the_handle_seeks_to_that_fraction(window, controller):
    window.progress.get.return_value = 0.75

    window.on_drag_end()

    controller.seek_fraction.assert_called_once_with(0.75)


def test_dragging_does_not_seek_on_every_pixel(window, controller):
    """Seeking per drag event would hammer the engine; release is enough."""
    window.on_drag_start()
    window.on_drag(0.3)
    window.on_drag(0.6)

    controller.seek_fraction.assert_not_called()


def test_refresh_leaves_the_handle_alone_while_dragging(window, controller):
    window.on_drag_start()
    window.progress.set.reset_mock()
    controller.progress_fraction = 0.9

    window.refresh()

    window.progress.set.assert_not_called()


def test_refresh_resumes_updating_after_the_drag_ends(window, controller):
    window.on_drag_start()
    window.on_drag_end()
    window.progress.set.reset_mock()
    controller.progress_fraction = 0.9

    window.refresh()

    window.progress.set.assert_called_with(0.9)


# -- periodic refresh ----------------------------------------------------


def test_refresh_is_scheduled_on_the_tk_loop(window):
    """after(), never a thread - Tk isn't thread-safe."""
    window.root.after.assert_called_with(
        REFRESH_INTERVAL_MS, window._on_tick
    )


def test_each_tick_reschedules_itself(window, controller):
    window.root.after.reset_mock()

    window._on_tick()

    window.root.after.assert_called_once_with(REFRESH_INTERVAL_MS, window._on_tick)


# -- search --------------------------------------------------------------


def test_typing_filters_the_sidebar(window, controller):
    window.search_entry.get.return_value = "blue"
    controller.visible_tracks = [TRACKS[0]]
    controller.visible_indices.return_value = [0]

    window.on_search()

    controller.search.assert_called_once_with("blue")
    assert len(window.track_buttons) == 1


def test_clearing_the_search_restores_every_row(window, controller):
    window.search_entry.get.return_value = "blue"
    controller.visible_tracks = [TRACKS[0]]
    controller.visible_indices.return_value = [0]
    window.on_search()

    window.search_entry.get.return_value = ""
    controller.visible_tracks = TRACKS
    controller.visible_indices.return_value = [0, 1]
    window.on_search()

    assert len(window.track_buttons) == len(TRACKS)


def test_filtered_rows_still_select_the_right_track(controller):
    """Row 0 of a filtered list may be playlist index 1."""
    controller.visible_tracks = [TRACKS[1]]
    controller.visible_indices.return_value = [1]

    with patch("src.ui.app.ctk") as mock_ctk:
        window = MusicAppWindow(controller=controller)

        commands = [
            call.kwargs["command"]
            for call in mock_ctk.CTkButton.call_args_list
            if call.kwargs.get("anchor") == "w"
        ]

    commands[0]()

    controller.select.assert_called_once_with(1)


# -- metadata labels -----------------------------------------------------


def test_sidebar_rows_use_metadata_descriptions(controller):
    controller.describe.side_effect = lambda track: f"Band - {track.stem}"

    with patch("src.ui.app.ctk") as mock_ctk:
        MusicAppWindow(controller=controller)

        labels = [
            call.kwargs["text"]
            for call in mock_ctk.CTkButton.call_args_list
            if call.kwargs.get("anchor") == "w"
        ]

    assert labels == ["Band - one", "Band - two"]
