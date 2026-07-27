## Why

The CLI proves the engine works but isn't how anyone actually listens to
music — you can't see your library, and every action is a typed command.
This is `initial_plan.md` Phase 3: a real window with a track list you can
click and buttons you can press. It's also the surface Phase 4's progress
bar and search box attach to, so the layout decided here is what those
extend.

## What Changes

- Add `src/ui/controller.py`: a `PlayerController` holding a `Playlist` and
  an `AudioPlayer` and exposing the operations a UI needs — `play_index`,
  `toggle_pause`, `stop`, `next_track`, `previous_track`, plus a
  `now_playing` description. It imports no GUI library at all, which is what
  makes the behavior testable without a display.
- Add `src/ui/app.py`: a `MusicAppWindow` built on customtkinter — playlist
  sidebar on the left, now-playing display and transport controls
  (play/pause, stop, previous, next) on the right — delegating every action
  to `PlayerController`.
- Add `src/ui/__main__.py` so the GUI launches with
  `python -m src.ui <directory>`, mirroring how the CLI is invoked.
- Tests: full coverage of `PlayerController` with a mocked `AudioPlayer`, and
  window-construction tests with customtkinter mocked, so the suite still
  runs with neither an audio device nor a display.

## Capabilities

### New Capabilities
- `gui-player`: a graphical window presenting the library as a selectable
  track list with transport controls and a now-playing display.

### Modified Capabilities
(none — `audio-playback`, `music-library`, and `cli-player` are all consumed
as-is; the GUI is an additional surface, not a replacement, and the CLI keeps
working)

## Impact

- Affected code: new `src/ui/controller.py`, `src/ui/app.py`,
  `src/ui/__main__.py`, plus tests. Nothing in `src/audio_player/`,
  `src/database/`, or `src/cli.py` changes.
- `customtkinter` is already in `requirements.txt` and installed; no new
  dependency.
- The module boundary from `CLAUDE.md` holds: `src/ui` depends on
  `audio_player` and `database`, and neither depends on `ui`.
- First part of the project that cannot be fully verified without a human
  looking at it — automated tests can prove the wiring, not that the layout
  reads well.
