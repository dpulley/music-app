"""Presentation-independent player logic.

This module deliberately imports no GUI library. Everything the window does
in response to a click lives here, so "does Next advance the playlist" is a
plain unit test rather than something only a human staring at a screen can
confirm. The window (``src/ui/app.py``) stays a thin layer that forwards
events here and renders what these properties return.
"""

from src.audio_player import AudioPlayer
from src.database.metadata import format_duration, read_metadata
from src.database.playlist import Playlist

NOTHING_LOADED = "No track loaded"
EMPTY_LIBRARY = "No tracks found"


class PlayerController:
    """Drives an :class:`AudioPlayer` over a :class:`Playlist` for a UI."""

    def __init__(self, tracks=(), player=None):
        self._playlist = Playlist(tracks)
        self._player = player if player is not None else AudioPlayer()
        self._loaded_track = None
        self._error = None
        self._query = ""
        self._metadata = {}

    # -- library ---------------------------------------------------------

    @property
    def tracks(self):
        """The whole track list, for populating a sidebar."""
        return self._playlist.tracks

    @property
    def is_empty(self):
        return len(self._playlist) == 0

    @property
    def selected_index(self):
        """Which track the user has highlighted, or ``None`` when empty."""
        return self._playlist.index

    @property
    def selected_track(self):
        return self._playlist.current

    def select(self, index):
        """Highlight a track.

        Selection is deliberately separate from playback: browsing the library
        shouldn't interrupt what's currently playing.
        """
        return self._playlist.select(index)

    # -- metadata --------------------------------------------------------

    def metadata_for(self, track):
        """Tags for ``track``, read lazily and remembered for this session.

        Lazy rather than eager so opening a large folder doesn't stall on
        reading every file's tags up front.
        """
        if track not in self._metadata:
            self._metadata[track] = read_metadata(track)
        return self._metadata[track]

    def describe(self, track):
        """The label to show for a track: "Artist - Title", else the title."""
        return self.metadata_for(track).description

    # -- search ----------------------------------------------------------

    @property
    def query(self):
        return self._query

    def search(self, query):
        """Filter the visible list. Playback and the cursor are untouched.

        Filtering a *view* rather than rebuilding the playlist is what keeps
        typing in the search box from stopping the music or losing your place
        in an album.
        """
        self._query = (query or "").strip()
        return self.visible_tracks

    def clear_search(self):
        self._query = ""
        return self.visible_tracks

    @property
    def visible_tracks(self):
        """Tracks matching the current query, in playlist order."""
        if not self._query:
            return self._playlist.tracks

        needle = self._query.lower()
        return [
            track
            for track in self._playlist.tracks
            if self._matches(track, needle)
        ]

    def visible_indices(self):
        """Playlist indices of the visible tracks, so a filtered sidebar row
        can still select the right underlying track."""
        visible = set(self.visible_tracks)
        return [
            index
            for index, track in enumerate(self._playlist.tracks)
            if track in visible
        ]

    def _matches(self, track, needle):
        meta = self.metadata_for(track)
        haystack = (
            meta.title,
            meta.artist,
            meta.album,
            track.name,
        )
        return any(needle in field.lower() for field in haystack if field)

    # -- transport -------------------------------------------------------

    def play_selected(self):
        """Load and play the highlighted track."""
        track = self._playlist.current
        if track is None:
            return None
        return self._play(track)

    def toggle_pause(self):
        """Pause if playing, resume if paused, start if nothing is going.

        One control rather than separate pause/resume buttons, so the window
        doesn't have to track which state it's in.
        """
        if self._loaded_track is None:
            return self.play_selected()

        if self._player.paused:
            self._player.resume()
        elif self._player.playing:
            self._player.pause()
        else:
            # Loaded but stopped (or played to the end) - start it again.
            self._player.play()

        return self._loaded_track

    def stop(self):
        if self._loaded_track is None:
            return None
        self._player.stop()
        return self._loaded_track

    def next_track(self):
        """Advance and play. At the end, leave the current track alone."""
        track = self._playlist.next()
        if track is None:
            return None
        return self._play(track)

    def previous_track(self):
        """Step back and play. At the start, leave the current track alone."""
        track = self._playlist.previous()
        if track is None:
            return None
        return self._play(track)

    # -- position and seeking --------------------------------------------

    @property
    def position(self):
        """Elapsed seconds in the loaded track, 0.0 when nothing is loaded."""
        if self._loaded_track is None:
            return 0.0
        return float(self._player.curr_pos)

    @property
    def duration(self):
        """Length of the loaded track in seconds, 0.0 when nothing is loaded."""
        if self._loaded_track is None:
            return 0.0
        return float(self._player.duration)

    @property
    def progress_fraction(self):
        """How far through the track we are, as 0.0-1.0.

        Zero-length or unloaded tracks report 0.0 rather than dividing by
        zero, so a slider bound to this never has to special-case anything.
        """
        duration = self.duration
        if duration <= 0:
            return 0.0
        return min(max(self.position / duration, 0.0), 1.0)

    @property
    def position_text(self):
        """Elapsed / total, e.g. "1:05 / 3:20"."""
        return f"{format_duration(self.position)} / {format_duration(self.duration)}"

    def seek_fraction(self, fraction):
        """Move playback to ``fraction`` (0.0-1.0) through the track.

        The UI works in fractions because that's what a slider naturally
        reports; converting to seconds needs the duration, which only the
        controller knows. Out-of-range values are clamped rather than
        rejected - a slider can overshoot by a pixel and that shouldn't be an
        error.
        """
        if self._loaded_track is None:
            return None

        duration = self.duration
        if duration <= 0:
            return None

        clamped = min(max(float(fraction), 0.0), 1.0)
        seconds = clamped * duration
        self._player.seek(seconds)
        return seconds

    # -- display ---------------------------------------------------------

    @property
    def now_playing(self):
        """One line describing what the user should see above the controls."""
        if self._error is not None:
            return self._error

        if self.is_empty:
            return EMPTY_LIBRARY

        if self._loaded_track is None:
            return NOTHING_LOADED

        if self._player.paused:
            state = "Paused"
        elif self._player.playing:
            state = "Playing"
        else:
            state = "Stopped"

        return f"{state}: {self.describe(self._loaded_track)}"

    # -- internals -------------------------------------------------------

    def _play(self, track):
        try:
            self._player.load(track)
            self._player.play()
        except Exception as exc:  # noqa: BLE001
            # Broad by design, same reasoning as the CLI: a corrupt or
            # mislabeled file must not take the window down. The backend can
            # raise anything from OSError to a miniaudio-specific error.
            self._loaded_track = None
            self._error = f"Could not play {track.name}: {exc}"
            return None

        self._loaded_track = track
        self._error = None
        return track
