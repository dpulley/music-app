"""Tests for the command-line player.

The loop reads and writes through injected callables, so these drive it with
scripted commands and collect output in a list - no terminal, and no real
AudioPlayer, so nothing here touches an audio device.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.cli import format_track_list, main, run_session
from src.database.playlist import Playlist

TRACKS = [Path("music/one.mp3"), Path("music/two.wav")]


class ScriptedInput:
    """Feeds a fixed list of commands, then raises EOFError like a closed pipe."""

    def __init__(self, *commands):
        self._commands = list(commands)

    def __call__(self, _prompt=""):
        if not self._commands:
            raise EOFError
        return self._commands.pop(0)


@pytest.fixture
def player():
    return MagicMock()


@pytest.fixture
def playlist():
    return Playlist(TRACKS)


def run(playlist, player, *commands):
    """Drive a session with scripted commands, returning the output lines."""
    output = []
    exit_code = run_session(
        playlist, player, read_command=ScriptedInput(*commands), write=output.append
    )
    return exit_code, "\n".join(str(line) for line in output)


# -- listing -------------------------------------------------------------


def test_track_list_is_numbered_from_one(playlist):
    rendered = format_track_list(playlist)

    assert "1. one.mp3" in rendered
    assert "2. two.wav" in rendered


def test_list_command_shows_tracks(playlist, player):
    _, output = run(playlist, player, "list")

    assert "one.mp3" in output and "two.wav" in output


# -- playing -------------------------------------------------------------


def test_play_loads_and_starts_the_chosen_track(playlist, player):
    _, output = run(playlist, player, "play 2")

    player.load.assert_called_once_with(TRACKS[1])
    player.play.assert_called_once()
    assert "Playing: two.wav" in output


def test_play_uses_one_based_numbering(playlist, player):
    run(playlist, player, "play 1")

    player.load.assert_called_once_with(TRACKS[0])


@pytest.mark.parametrize("command", ["play 0", "play 3", "play 99"])
def test_play_out_of_range_reports_and_continues(playlist, player, command):
    exit_code, output = run(playlist, player, command, "list")

    assert "No track" in output
    player.load.assert_not_called()
    assert "one.mp3" in output  # session continued to the list command
    assert exit_code == 0


def test_play_without_a_number_reports_and_continues(playlist, player):
    _, output = run(playlist, player, "play", "list")

    assert "needs a track number" in output
    player.load.assert_not_called()


def test_unplayable_track_reports_and_keeps_session_alive(playlist, player):
    player.load.side_effect = OSError("corrupt file")

    exit_code, output = run(playlist, player, "play 1", "list")

    assert "Could not play one.mp3" in output
    assert "corrupt file" in output
    assert "two.wav" in output  # still listing afterwards
    assert exit_code == 0


# -- transport -----------------------------------------------------------


@pytest.mark.parametrize("command", ["pause", "resume", "stop"])
def test_transport_commands_delegate_to_player(playlist, player, command):
    run(playlist, player, command)

    getattr(player, command).assert_called()


@pytest.mark.parametrize("command", ["pause", "resume", "stop"])
def test_transport_before_loading_reports_and_continues(playlist, player, command):
    player.pause.side_effect = RuntimeError("No audio file loaded")
    player.resume.side_effect = RuntimeError("No audio file loaded")
    player.stop.side_effect = RuntimeError("No audio file loaded")

    exit_code, output = run(playlist, player, command, "list")

    assert "No track loaded" in output
    assert "one.mp3" in output
    assert exit_code == 0


# -- session lifecycle ---------------------------------------------------


def test_quit_stops_playback_and_exits_cleanly(playlist, player):
    exit_code, output = run(playlist, player, "quit")

    player.stop.assert_called()
    assert "Goodbye." in output
    assert exit_code == 0


def test_end_of_input_ends_the_session(playlist, player):
    """A closed pipe should end the session, not raise."""
    exit_code, output = run(playlist, player)

    assert exit_code == 0
    assert "Goodbye." in output


def test_unknown_command_reports_and_continues(playlist, player):
    _, output = run(playlist, player, "boogie", "list")

    assert "Unknown command" in output
    assert "one.mp3" in output


def test_blank_input_is_ignored(playlist, player):
    exit_code, output = run(playlist, player, "", "   ", "quit")

    assert exit_code == 0
    assert "Unknown command" not in output


# -- entry point ---------------------------------------------------------


def test_main_reports_invalid_directory_with_nonzero_exit(tmp_path):
    output = []

    exit_code = main(
        [str(tmp_path / "nope")], write=output.append, read_command=ScriptedInput()
    )

    assert exit_code == 1
    assert "Error" in "\n".join(output)


def test_main_exits_cleanly_when_no_audio_found(tmp_path):
    (tmp_path / "notes.txt").write_text("no music here")
    output = []

    exit_code = main(
        [str(tmp_path)], write=output.append, read_command=ScriptedInput()
    )

    assert exit_code == 0
    assert "No playable audio files found" in "\n".join(output)


def test_main_lists_found_tracks_then_runs_session(tmp_path):
    (tmp_path / "song.mp3").write_bytes(b"")
    output = []

    with patch("src.cli.AudioPlayer") as mock_player_cls:
        exit_code = main(
            [str(tmp_path)],
            write=output.append,
            read_command=ScriptedInput("play 1", "quit"),
        )

    rendered = "\n".join(output)
    assert exit_code == 0
    assert "Found 1 track(s):" in rendered
    assert "song.mp3" in rendered
    mock_player_cls.return_value.play.assert_called_once()
