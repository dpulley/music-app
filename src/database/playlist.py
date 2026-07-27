"""An ordered collection of tracks with a current-track cursor.

The cursor lives here rather than in ``AudioPlayer`` (which knows about one
file at a time by design) or in the UI layer. That keeps "which track is
current" in one place, so a CLI's ``next`` command and a GUI's skip button
are each a single call rather than duplicated bookkeeping.
"""


class Playlist:
    """An ordered list of track paths plus a cursor into it.

    Navigation clamps at both ends and returns ``None`` rather than wrapping
    or raising: wrapping surprises someone at the end of an album, and raising
    would force every caller to wrap next/previous in try/except. Returning
    ``None`` lets the caller decide what "past the end" means - print a
    message now, honor a repeat-mode toggle later.
    """

    def __init__(self, tracks=()):
        self._tracks = list(tracks)
        self._index = 0 if self._tracks else None

    # -- collection protocol ---------------------------------------------

    def __len__(self):
        return len(self._tracks)

    def __iter__(self):
        return iter(self._tracks)

    def __getitem__(self, index):
        return self._tracks[index]

    def __repr__(self):
        return f"Playlist({len(self._tracks)} tracks, current={self.current})"

    # -- cursor ----------------------------------------------------------

    @property
    def tracks(self):
        """A copy of the track list, so callers can't mutate our ordering."""
        return list(self._tracks)

    @property
    def index(self):
        """Position of the current track, or ``None`` when empty."""
        return self._index

    @property
    def current(self):
        """The current track, or ``None`` when the playlist is empty."""
        if self._index is None:
            return None
        return self._tracks[self._index]

    def next(self):
        """Advance to the following track and return it.

        Returns ``None`` (leaving the cursor put) if the last track is already
        current, or if the playlist is empty.
        """
        if self._index is None or self._index >= len(self._tracks) - 1:
            return None

        self._index += 1
        return self.current

    def previous(self):
        """Step back to the preceding track and return it.

        Returns ``None`` (leaving the cursor put) if the first track is already
        current, or if the playlist is empty.
        """
        if self._index is None or self._index <= 0:
            return None

        self._index -= 1
        return self.current

    def select(self, index):
        """Make the track at ``index`` current and return it.

        Negative indices are rejected rather than interpreted Python-style:
        callers are translating a user's "play track 3", where a negative
        number is a bug, not a request for the third-from-last track.

        Raises:
            IndexError: ``index`` is outside the playlist. The cursor is
                left unchanged.
        """
        if not self._tracks:
            raise IndexError("Cannot select from an empty playlist")

        if index < 0 or index >= len(self._tracks):
            raise IndexError(
                f"Track index {index} is outside the playlist "
                f"(0-{len(self._tracks) - 1})"
            )

        self._index = index
        return self.current
