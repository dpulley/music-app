"""Playback engine.

``just_playback`` is imported here and nowhere else in the project, so the UI
and CLI layers depend on :class:`AudioPlayer` rather than on the third-party
library directly. If the playback backend is ever swapped out, this is the only
module that changes.
"""

from just_playback import Playback

from src.utils import validate_music_path


class AudioPlayer:
    """Play, pause, seek, and report position for a single audio file.

    The underlying ``Playback`` object is created on the first successful
    :meth:`load` rather than in ``__init__``. Two reasons: constructing it
    raises ``MiniaudioError`` on a machine with no output device (so eager
    construction would make an ``AudioPlayer()`` unusable in headless contexts
    even for state queries), and it gives well-defined "nothing loaded yet"
    defaults for free.
    """

    def __init__(self):
        self._playback = None
        self._path = None

    # -- loading ---------------------------------------------------------

    def load(self, path):
        """Validate ``path`` and load it for playback, replacing any current file.

        Raises:
            FileNotFoundError: The path does not exist or is not a file.
            ValueError: The file's extension is unsupported.
        """
        audio_path = validate_music_path(path)

        if self._playback is None:
            self._playback = Playback()

        self._playback.load_file(str(audio_path))
        self._path = audio_path
        return audio_path

    @property
    def path(self):
        """The currently loaded file, or ``None`` if nothing is loaded."""
        return self._path

    # -- transport -------------------------------------------------------

    def play(self):
        """Play the loaded file from the beginning."""
        self._require_loaded()
        self._playback.play()

    def pause(self):
        """Suspend playback, keeping the current position."""
        self._require_loaded()
        self._playback.pause()

    def resume(self):
        """Continue playback from a paused position."""
        self._require_loaded()
        self._playback.resume()

    def stop(self):
        """Halt playback and reset the position to the start."""
        self._require_loaded()
        self._playback.stop()

    def seek(self, seconds):
        """Move playback to ``seconds`` from the start of the track.

        The backend silently clamps out-of-range values; we raise instead, so a
        caller computing a position from a UI drag finds out it got the maths
        wrong rather than quietly landing at one end of the track.

        Raises:
            ValueError: ``seconds`` is negative or beyond the track duration.
        """
        self._require_loaded()

        if seconds < 0 or seconds > self.duration:
            raise ValueError(
                f"Seek position {seconds}s is outside the track "
                f"(0-{self.duration}s)"
            )

        self._playback.seek(seconds)

    def set_volume(self, level):
        """Set output volume, where 0.0 is silent and 1.0 is full scale.

        Raises:
            ValueError: ``level`` is outside 0.0-1.0.
        """
        self._require_loaded()

        if not 0.0 <= level <= 1.0:
            raise ValueError(f"Volume {level} is outside the range 0.0-1.0")

        self._playback.set_volume(level)

    # -- state -----------------------------------------------------------

    @property
    def playing(self):
        """True while audio is actively playing."""
        if self._playback is None:
            return False
        return bool(self._playback.playing)

    @property
    def paused(self):
        """True while playback is paused."""
        if self._playback is None:
            return False
        return bool(self._playback.paused)

    @property
    def curr_pos(self):
        """Current position in seconds, 0.0 when nothing is loaded.

        The backend reports ``-1`` when no file is loaded; normalising that to
        0.0 here keeps callers (progress bars, especially) from having to know
        about the sentinel.
        """
        if self._playback is None:
            return 0.0
        return max(float(self._playback.curr_pos), 0.0)

    @property
    def duration(self):
        """Length of the loaded track in seconds, 0.0 when nothing is loaded."""
        if self._playback is None:
            return 0.0
        return float(self._playback.duration)

    @property
    def volume(self):
        """Current output volume in the range 0.0-1.0."""
        if self._playback is None:
            return 1.0
        return float(self._playback.volume)

    # -- internals -------------------------------------------------------

    def _require_loaded(self):
        if self._playback is None:
            raise RuntimeError("No audio file loaded - call load() first")
