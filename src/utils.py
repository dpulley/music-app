"""Shared helpers for locating and validating audio files.

The supported-extension list lives here rather than in ``audio_player`` because
the directory scanner (next roadmap item) needs the same list to decide what to
pick up when walking a folder. One constant, so the two can't drift apart.
"""

from pathlib import Path

SUPPORTED_EXTENSIONS = frozenset({".mp3", ".wav", ".flac", ".ogg"})


def validate_music_path(path):
    """Return ``path`` as a :class:`~pathlib.Path` if it is a playable file.

    Validating up front means a missing or unsupported file surfaces as a clear
    Python exception instead of an opaque miniaudio error from the C layer.

    Args:
        path: Path to an audio file, as ``str`` or ``Path``.

    Returns:
        The validated path as a ``Path``.

    Raises:
        FileNotFoundError: The path does not exist, or is not a file.
        ValueError: The file's extension is not in ``SUPPORTED_EXTENSIONS``.
    """
    candidate = Path(path)

    # is_file() is False for both missing paths and directories, which is
    # exactly the distinction we want to collapse here.
    if not candidate.is_file():
        raise FileNotFoundError(f"Audio file not found: {candidate}")

    if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"Unsupported audio format '{candidate.suffix}': {candidate}. "
            f"Supported formats: {supported}"
        )

    return candidate
