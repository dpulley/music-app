"""Reading track tags.

Read-only on purpose: nothing here writes tags, so a bug in the player can't
damage someone's library.

The guiding rule is that metadata never fails loudly. Real libraries are full
of files with no tags, half-filled tags, and formats mutagen only partly
understands - the project's own `assets/test_tone.wav` has ``tags = None``.
A player that refuses to list a song because its ID3 frame is malformed is
worse than one that shows a filename, so every failure path here degrades to
the filename.
"""

from dataclasses import dataclass
from pathlib import Path

import mutagen

# mutagen's easy interface exposes these as lists of strings.
_TITLE_KEYS = ("title",)
_ARTIST_KEYS = ("artist", "albumartist", "performer")
_ALBUM_KEYS = ("album",)


def format_duration(seconds):
    """Render seconds as M:SS (or H:MM:SS past an hour)."""
    total = max(int(seconds or 0), 0)
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


@dataclass(frozen=True)
class TrackMetadata:
    """What we know about a track, with filename-derived fallbacks."""

    path: Path
    title: str
    artist: str = ""
    album: str = ""
    duration: float = 0.0

    @property
    def description(self):
        """One-line label: "Artist - Title", or just the title when untagged."""
        if self.artist:
            return f"{self.artist} - {self.title}"
        return self.title

    @property
    def duration_text(self):
        return format_duration(self.duration)


def read_metadata(path):
    """Read tags from ``path``, falling back to the filename.

    Never raises for tag-related problems: an unreadable or untagged file
    yields filename-based metadata instead.
    """
    audio_path = Path(path)
    fallback = TrackMetadata(path=audio_path, title=audio_path.stem)

    try:
        audio = mutagen.File(audio_path, easy=True)
    except Exception:  # noqa: BLE001
        # Broad by design: mutagen raises a family of format-specific errors
        # for corrupt files, and every one of them means the same thing here.
        return fallback

    if audio is None:
        # mutagen returns None for a file it can't identify at all.
        return fallback

    duration = _read_duration(audio)
    tags = audio.tags

    if not tags:
        # The common case for bare WAVs: no tags, but the stream info (and so
        # the duration) is still perfectly good.
        return TrackMetadata(
            path=audio_path, title=audio_path.stem, duration=duration
        )

    return TrackMetadata(
        path=audio_path,
        title=_first(tags, _TITLE_KEYS) or audio_path.stem,
        artist=_first(tags, _ARTIST_KEYS),
        album=_first(tags, _ALBUM_KEYS),
        duration=duration,
    )


def _read_duration(audio):
    try:
        return float(audio.info.length)
    except (AttributeError, TypeError, ValueError):
        # Some formats report no usable length; 0.0 keeps callers doing
        # arithmetic rather than None-checking.
        return 0.0


def _first(tags, keys):
    """First non-empty value among ``keys``, flattened from mutagen's lists."""
    for key in keys:
        try:
            value = tags.get(key)
        except Exception:  # noqa: BLE001
            continue

        if not value:
            continue

        if isinstance(value, (list, tuple)):
            value = value[0] if value else ""

        text = str(value).strip()
        if text:
            return text

    return ""
