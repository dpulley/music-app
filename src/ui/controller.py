"""Presentation-independent player logic.

This module deliberately imports no GUI library. Everything the window does
in response to a click lives here, so "does Next advance the playlist" is a
plain unit test rather than something only a human staring at a screen can
confirm. The window (``src/ui/app.py``) stays a thin layer that forwards
events here and renders :attr:`PlayerController.now_playing`.
"""

from src.audio_player import AudioPlayer
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

    # -- library ---------------------------------------------------------

    @property
    def tracks(self):
        """The track list, for populating a sidebar."""
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

        return f"{state}: {self._loaded_track.name}"

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
