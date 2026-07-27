## 1. Player controller (no GUI imports)

- [x] 1.1 Create `src/ui/controller.py` with a `PlayerController` wrapping a `Playlist` and an `AudioPlayer`, exposing `tracks`, `selected_index`, `select(index)`, `play_selected()`, `toggle_pause()`, `stop()`, `next_track()`, `previous_track()`, and a `now_playing` string
- [x] 1.2 Implement the state rules: selection never interrupts playback, `toggle_pause` resumes when paused and pauses when playing, next/previous at the ends leave playback untouched, and a failed load is reported through `now_playing` instead of raising
- [x] 1.3 Add `tests/ui/__init__.py` and `tests/ui/test_controller.py` with a mocked `AudioPlayer`, covering selection, play, pause/resume toggle, stop, next/previous including both ends, the empty-library case, and load failure

## 2. Window

- [x] 2.1 Create `src/ui/app.py` with a `MusicAppWindow` building the customtkinter layout: playlist sidebar on the left, now-playing label and transport buttons (previous, play/pause, stop, next) on the right
- [x] 2.2 Wire every button and the list selection to the corresponding `PlayerController` method, and refresh the now-playing label after each action
- [x] 2.3 Handle the empty-library case in the window: show the empty message and disable transport controls
- [x] 2.4 Add `tests/ui/test_app.py` patching `src.ui.app.ctk` to verify the window constructs, binds each control to the right controller method, and disables controls for an empty library — all without a display

## 3. Entry point

- [ ] 3.1 Add `src/ui/__main__.py` so `python -m src.ui <directory>` scans the directory and opens the window, reusing `scan_directory` and reporting an invalid directory the same way the CLI does
- [ ] 3.2 Add entry-point tests covering the invalid-directory and empty-directory paths with the window mocked

## 4. Verify

- [ ] 4.1 Run `venv\Scripts\python.exe -m pytest` and confirm the whole suite passes with no audio device and no display required
- [ ] 4.2 Launch the real window via the `run-music-app` skill against `assets/`, confirm the track list, transport buttons, and now-playing display work, and record what was observed (needs a human at the screen — flag for review rather than assuming)
