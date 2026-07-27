"""Tests for the Playlist cursor model.

Pure in-memory logic - no files, no audio, no mocks needed. Tracks are
represented by plain strings here since Playlist never inspects them.
"""

import pytest

from src.database.playlist import Playlist

TRACKS = ["one.mp3", "two.mp3", "three.mp3"]


@pytest.fixture
def playlist():
    return Playlist(TRACKS)


# -- construction --------------------------------------------------------


def test_new_playlist_starts_on_the_first_track(playlist):
    assert playlist.current == "one.mp3"
    assert playlist.index == 0
    assert len(playlist) == 3


def test_playlist_is_iterable_and_indexable(playlist):
    assert list(playlist) == TRACKS
    assert playlist[1] == "two.mp3"


def test_tracks_property_does_not_expose_internal_list(playlist):
    playlist.tracks.append("sneaky.mp3")

    assert len(playlist) == 3


def test_accepts_any_iterable_of_tracks():
    assert len(Playlist(iter(TRACKS))) == 3


# -- forward navigation --------------------------------------------------


def test_next_advances_and_returns_the_new_track(playlist):
    assert playlist.next() == "two.mp3"
    assert playlist.current == "two.mp3"


def test_next_walks_the_whole_playlist(playlist):
    assert [playlist.next() for _ in range(2)] == ["two.mp3", "three.mp3"]


def test_next_clamps_at_the_end(playlist):
    playlist.select(2)

    assert playlist.next() is None
    assert playlist.current == "three.mp3"


# -- backward navigation -------------------------------------------------


def test_previous_steps_back_and_returns_the_new_track(playlist):
    playlist.select(2)

    assert playlist.previous() == "two.mp3"
    assert playlist.current == "two.mp3"


def test_previous_clamps_at_the_start(playlist):
    assert playlist.previous() is None
    assert playlist.current == "one.mp3"


# -- select --------------------------------------------------------------


def test_select_moves_the_cursor(playlist):
    assert playlist.select(2) == "three.mp3"
    assert playlist.index == 2


@pytest.mark.parametrize("index", [3, 99, -1])
def test_select_out_of_range_raises_and_leaves_cursor_alone(playlist, index):
    playlist.select(1)

    with pytest.raises(IndexError):
        playlist.select(index)

    assert playlist.current == "two.mp3"


# -- empty playlist ------------------------------------------------------


def test_empty_playlist_has_no_current_track():
    empty = Playlist()

    assert empty.current is None
    assert empty.index is None
    assert len(empty) == 0


def test_empty_playlist_navigation_returns_none_without_raising():
    empty = Playlist()

    assert empty.next() is None
    assert empty.previous() is None


def test_selecting_from_empty_playlist_raises():
    with pytest.raises(IndexError):
        Playlist().select(0)


# -- integration with the scanner ----------------------------------------


def test_playlist_holds_scanned_paths(test_tone):
    from src.database.library import scan_directory

    found = scan_directory(test_tone.parent, recursive=False)
    playlist = Playlist(found)

    assert playlist.current == found[0]
