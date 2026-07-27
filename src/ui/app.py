"""customtkinter window.

Deliberately thin: every button forwards to :class:`PlayerController` and
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
WINDOW_SIZE = "760x480"
SIDEBAR_WIDTH = 260

TRANSPORT_LABELS = {
    "previous": "<< Prev",
    "play_pause": "Play / Pause",
    "stop": "Stop",
    "next": "Next >>",
}


class MusicAppWindow:
    """Main application window: track sidebar, now-playing label, transport."""

    def __init__(self, controller=None, tracks=()):
        self.controller = (
            controller if controller is not None else PlayerController(tracks)
        )

        self.root = ctk.CTk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.track_buttons = []
        self.transport_buttons = {}

        self._build_sidebar()
        self._build_main_panel()
        self.refresh()

    # -- layout ----------------------------------------------------------

    def _build_sidebar(self):
        self.sidebar = ctk.CTkScrollableFrame(
            self.root, width=SIDEBAR_WIDTH, label_text="Library"
        )
        self.sidebar.pack(side="left", fill="y", padx=8, pady=8)

        if self.controller.is_empty:
            self.empty_label = ctk.CTkLabel(
                self.sidebar, text=self.controller.now_playing
            )
            self.empty_label.pack(padx=8, pady=8)
            return

        for index, track in enumerate(self.controller.tracks):
            button = ctk.CTkButton(
                self.sidebar,
                text=track.name,
                anchor="w",
                # Bind the index at definition time; a late-bound closure over
                # the loop variable would make every row select the last track.
                command=lambda index=index: self.on_select(index),
            )
            button.pack(fill="x", padx=4, pady=2)
            self.track_buttons.append(button)

    def _build_main_panel(self):
        self.main_panel = ctk.CTkFrame(self.root)
        self.main_panel.pack(side="right", expand=True, fill="both", padx=8, pady=8)

        self.now_playing_label = ctk.CTkLabel(
            self.main_panel, text=self.controller.now_playing
        )
        self.now_playing_label.pack(pady=(24, 16))

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

    # -- display ---------------------------------------------------------

    def refresh(self):
        """Re-render anything derived from controller state."""
        self.now_playing_label.configure(text=self.controller.now_playing)

    def mainloop(self):
        self.root.mainloop()


def launch(tracks=()):
    """Open the window and run until the user closes it."""
    window = MusicAppWindow(tracks=tracks)
    window.mainloop()
    return window
