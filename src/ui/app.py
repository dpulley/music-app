"""customtkinter window.

Deliberately thin: every control forwards to :class:`PlayerController` and
then refreshes the display. Keeping decisions out of here is what lets the
behavior be tested without a screen - see ``src/ui/controller.py``.

The window *holds* a ``ctk.CTk`` root rather than subclassing it. Subclassing
would bind the real base class at import time, which no amount of patching
could displace - tests would need an actual display just to import this
module. With composition, patching ``src.ui.app.ctk`` swaps the whole toolkit
out and the window constructs fine headless.
"""

import customtkinter as ctk

from src.ui.controller import PlayerController

WINDOW_TITLE = "Music App"
WINDOW_SIZE = "820x520"
SIDEBAR_WIDTH = 280

#: How often the progress display re-reads the player, in milliseconds.
#: A module constant so it can be tuned without hunting through widget code.
REFRESH_INTERVAL_MS = 250

TRANSPORT_LABELS = {
    "previous": "<< Prev",
    "play_pause": "Play / Pause",
    "stop": "Stop",
    "next": "Next >>",
}


class MusicAppWindow:
    """Main window: search + track sidebar, now-playing, progress, transport."""

    def __init__(self, controller=None, tracks=()):
        self.controller = (
            controller if controller is not None else PlayerController(tracks)
        )

        self.root = ctk.CTk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.track_buttons = []
        self.transport_buttons = {}
        self._visible_indices = []

        # True while the user has the progress handle grabbed. Position
        # updates stand down during that, otherwise the periodic refresh
        # yanks the handle back mid-drag.
        self._dragging = False

        self._build_sidebar()
        self._build_main_panel()
        self.refresh()
        self._schedule_refresh()

    # -- layout ----------------------------------------------------------

    def _build_sidebar(self):
        self.sidebar_container = ctk.CTkFrame(self.root, width=SIDEBAR_WIDTH)
        self.sidebar_container.pack(side="left", fill="y", padx=8, pady=8)

        self.search_entry = ctk.CTkEntry(
            self.sidebar_container, placeholder_text="Search library"
        )
        self.search_entry.pack(fill="x", padx=4, pady=(4, 8))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.sidebar = ctk.CTkScrollableFrame(
            self.sidebar_container, width=SIDEBAR_WIDTH, label_text="Library"
        )
        self.sidebar.pack(expand=True, fill="both", padx=4, pady=(0, 4))

        self._populate_sidebar()

    def _populate_sidebar(self):
        """(Re)build the track rows from the controller's visible tracks."""
        for button in self.track_buttons:
            button.destroy()
        self.track_buttons = []

        if self.controller.is_empty:
            self.empty_label = ctk.CTkLabel(
                self.sidebar, text=self.controller.now_playing
            )
            self.empty_label.pack(padx=8, pady=8)
            return

        visible = self.controller.visible_tracks
        self._visible_indices = self.controller.visible_indices()

        for row, track in enumerate(visible):
            playlist_index = self._visible_indices[row]
            button = ctk.CTkButton(
                self.sidebar,
                text=self.controller.describe(track),
                anchor="w",
                # Bind the index at definition time; a late-bound closure over
                # the loop variable would make every row select the last track.
                command=lambda index=playlist_index: self.on_select(index),
            )
            button.pack(fill="x", padx=4, pady=2)
            self.track_buttons.append(button)

    def _build_main_panel(self):
        self.main_panel = ctk.CTkFrame(self.root)
        self.main_panel.pack(side="right", expand=True, fill="both", padx=8, pady=8)

        self.now_playing_label = ctk.CTkLabel(
            self.main_panel, text=self.controller.now_playing
        )
        self.now_playing_label.pack(pady=(24, 12))

        self.progress = ctk.CTkSlider(
            self.main_panel, from_=0, to=1, command=self.on_drag
        )
        self.progress.pack(fill="x", padx=32, pady=(4, 4))
        self.progress.bind("<ButtonPress-1>", self.on_drag_start)
        self.progress.bind("<ButtonRelease-1>", self.on_drag_end)

        self.position_label = ctk.CTkLabel(
            self.main_panel, text=self.controller.position_text
        )
        self.position_label.pack(pady=(0, 16))

        self.transport = ctk.CTkFrame(self.main_panel)
        self.transport.pack(pady=8)

        for name, handler in (
            ("previous", self.on_previous),
            ("play_pause", self.on_play_pause),
            ("stop", self.on_stop),
            ("next", self.on_next),
        ):
            button = ctk.CTkButton(
                self.transport, text=TRANSPORT_LABELS[name], command=handler
            )
            button.pack(side="left", padx=4)
            self.transport_buttons[name] = button

        if self.controller.is_empty:
            # Nothing to control - leave the buttons visible but inert rather
            # than hiding them, so the layout doesn't jump around.
            for button in self.transport_buttons.values():
                button.configure(state="disabled")

    # -- event handlers --------------------------------------------------

    def on_select(self, index):
        self.controller.select(index)
        self.refresh()

    def on_play_pause(self):
        self.controller.toggle_pause()
        self.refresh()

    def on_stop(self):
        self.controller.stop()
        self.refresh()

    def on_next(self):
        self.controller.next_track()
        self.refresh()

    def on_previous(self):
        self.controller.previous_track()
        self.refresh()

    def on_search(self, _event=None):
        self.controller.search(self.search_entry.get())
        self._populate_sidebar()

    # -- progress dragging -----------------------------------------------

    def on_drag_start(self, _event=None):
        self._dragging = True

    def on_drag(self, _value=None):
        """Fires continuously while the handle moves; seeking waits for release
        so we don't spam the engine with a seek per pixel."""
        self._dragging = True

    def on_drag_end(self, _event=None):
        self._dragging = False
        self.controller.seek_fraction(self.progress.get())
        self.refresh()

    # -- display ---------------------------------------------------------

    def refresh(self):
        """Re-render anything derived from controller state."""
        self.now_playing_label.configure(text=self.controller.now_playing)
        self.position_label.configure(text=self.controller.position_text)

        if not self._dragging:
            self.progress.set(self.controller.progress_fraction)

    def _schedule_refresh(self):
        """Tick the display on Tk's own loop.

        `after` rather than a worker thread: Tk isn't thread-safe, and
        touching widgets from another thread is a classic source of
        intermittent, unreproducible crashes.
        """
        self.root.after(REFRESH_INTERVAL_MS, self._on_tick)

    def _on_tick(self):
        self.refresh()
        self._schedule_refresh()

    def mainloop(self):
        self.root.mainloop()


def launch(tracks=()):
    """Open the window and run until the user closes it."""
    window = MusicAppWindow(tracks=tracks)
    window.mainloop()
    return window
