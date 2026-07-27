"""Tests for the GUI entry point.

The window is injected as a factory, so these exercise argument handling and
the scan-to-window handoff without ever constructing a real toolkit object.
"""

from unittest.mock import MagicMock

from src.ui.__main__ import main


def run_main(argv, **kwargs):
    output = []
    factory = kwargs.pop("window_factory", MagicMock())
    exit_code = main(argv, write=output.append, window_factory=factory, **kwargs)
    return exit_code, "\n".join(output), factory


def test_invalid_directory_reports_and_exits_nonzero(tmp_path):
    exit_code, output, factory = run_main([str(tmp_path / "nope")])

    assert exit_code == 1
    assert "Error" in output
    factory.assert_not_called()


def test_file_path_is_rejected_like_the_cli(tmp_path):
    track = tmp_path / "song.mp3"
    track.write_bytes(b"")

    exit_code, _, factory = run_main([str(track)])

    assert exit_code == 1
    factory.assert_not_called()


def test_empty_directory_still_opens_the_window(tmp_path):
    """A GUI user expects a window; exiting to a prompt reads as a crash."""
    exit_code, output, factory = run_main([str(tmp_path)])

    assert exit_code == 0
    assert "No playable audio files found" in output
    factory.assert_called_once_with(tracks=[])
    factory.return_value.mainloop.assert_called_once()


def test_found_tracks_are_handed_to_the_window(tmp_path):
    (tmp_path / "one.mp3").write_bytes(b"")
    (tmp_path / "two.wav").write_bytes(b"")

    exit_code, _, factory = run_main([str(tmp_path)])

    assert exit_code == 0
    tracks = factory.call_args.kwargs["tracks"]
    assert [path.name for path in tracks] == ["one.mp3", "two.wav"]
    factory.return_value.mainloop.assert_called_once()


def test_no_recursive_flag_limits_the_scan(tmp_path):
    (tmp_path / "top.mp3").write_bytes(b"")
    nested = tmp_path / "album"
    nested.mkdir()
    (nested / "deep.mp3").write_bytes(b"")

    _, _, factory = run_main([str(tmp_path), "--no-recursive"])

    tracks = factory.call_args.kwargs["tracks"]
    assert [path.name for path in tracks] == ["top.mp3"]


def test_recursive_is_the_default(tmp_path):
    (tmp_path / "top.mp3").write_bytes(b"")
    nested = tmp_path / "album"
    nested.mkdir()
    (nested / "deep.mp3").write_bytes(b"")

    _, _, factory = run_main([str(tmp_path)])

    tracks = factory.call_args.kwargs["tracks"]
    assert len(tracks) == 2
