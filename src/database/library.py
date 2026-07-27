"""Discovery of playable audio files on disk.

The supported-format list is imported from :mod:`src.utils` rather than
redefined here, so the scanner and :func:`~src.utils.validate_music_path`
can't disagree about what counts as playable.
"""

import os
from pathlib import Path

from src.utils import SUPPORTED_EXTENSIONS


def scan_directory(path, recursive=True):
    """Return the playable audio files under ``path``, sorted.

    Sorted (rather than in filesystem order) because callers number the
    results for the user to choose from - "track 4" should mean the same
    thing between two runs of the same library.

    Unreadable subdirectories are skipped rather than raising: one folder
    with bad permissions shouldn't cost the user the rest of their library.

    Args:
        path: Directory to scan.
        recursive: Whether to descend into subdirectories.

    Returns:
        A sorted list of ``Path`` objects. Empty if nothing playable is found.

    Raises:
        NotADirectoryError: ``path`` does not exist or is not a directory.
    """
    root = Path(path)

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    if recursive:
        # os.walk swallows per-directory errors by default, which is the
        # skip-and-continue behavior we want.
        tracks = [
            Path(dirpath) / filename
            for dirpath, _dirnames, filenames in os.walk(root)
            for filename in filenames
            if _is_supported(filename)
        ]
    else:
        tracks = [
            entry
            for entry in root.iterdir()
            if entry.is_file() and _is_supported(entry.name)
        ]

    return sorted(tracks)


def _is_supported(filename):
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS
