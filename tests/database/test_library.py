"""Tests for directory scanning.

These build real file trees under ``tmp_path``. The files are empty - the
scanner only inspects names and extensions, never decodes audio - so no audio
device or real media is involved.
"""

import pytest

from src.database.library import scan_directory


def make_files(directory, *names):
    """Create empty files (and any parent dirs) and return their paths."""
    created = []
    for name in names:
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"")
        created.append(path)
    return created


def test_finds_every_supported_format(tmp_path):
    expected = make_files(
        tmp_path, "a.mp3", "b.wav", "c.flac", "d.ogg"
    )

    assert scan_directory(tmp_path) == sorted(expected)


def test_excludes_non_audio_files(tmp_path):
    make_files(tmp_path, "notes.txt", "cover.jpg", "booklet.pdf", "song.mp3")

    found = scan_directory(tmp_path)

    assert [path.name for path in found] == ["song.mp3"]


def test_extension_matching_is_case_insensitive(tmp_path):
    make_files(tmp_path, "LOUD.MP3", "Quiet.Wav")

    assert len(scan_directory(tmp_path)) == 2


def test_descends_into_subdirectories_by_default(tmp_path):
    make_files(tmp_path, "top.mp3", "album/deep.mp3", "album/disc2/deeper.flac")

    found = scan_directory(tmp_path)

    assert [path.name for path in found] == ["deep.mp3", "deeper.flac", "top.mp3"]


def test_recursion_can_be_disabled(tmp_path):
    make_files(tmp_path, "top.mp3", "album/deep.mp3")

    found = scan_directory(tmp_path, recursive=False)

    assert [path.name for path in found] == ["top.mp3"]


def test_results_are_stably_sorted(tmp_path):
    make_files(tmp_path, "z.mp3", "a.mp3", "m/b.mp3")

    first = scan_directory(tmp_path)
    second = scan_directory(tmp_path)

    assert first == second == sorted(first)


def test_directory_without_audio_returns_empty_list(tmp_path):
    make_files(tmp_path, "readme.txt")

    assert scan_directory(tmp_path) == []


def test_empty_directory_returns_empty_list(tmp_path):
    assert scan_directory(tmp_path) == []


def test_missing_path_raises_not_a_directory(tmp_path):
    with pytest.raises(NotADirectoryError):
        scan_directory(tmp_path / "no_such_folder")


def test_file_path_raises_not_a_directory(tmp_path):
    (single_file,) = make_files(tmp_path, "track.mp3")

    with pytest.raises(NotADirectoryError):
        scan_directory(single_file)


def test_scan_accepts_path_given_as_string(tmp_path):
    make_files(tmp_path, "song.wav")

    assert len(scan_directory(str(tmp_path))) == 1


def test_generated_test_tone_is_discoverable(test_tone):
    """The real generated fixture should be found by a scan of assets/."""
    found = scan_directory(test_tone.parent, recursive=False)

    assert test_tone in found
