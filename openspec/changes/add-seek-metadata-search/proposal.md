## Why

The player works but stays dumb about what it's playing: tracks are
filenames, there's no way to jump to the chorus, and finding one song in a
large folder means scrolling. This is `initial_plan.md` Phase 4, the last
roadmap item — and the one the stack was chosen for. `just-playback` was
picked over `pygame.mixer` precisely because it exposes real `seek()` and
`curr_pos`, and the controller/window split exists so seek logic could be
tested before any slider was wired to it.

## What Changes

- Add `src/database/metadata.py`: `read_metadata(path)` returning title,
  artist, album, and duration via mutagen, falling back to the filename stem
  when a file carries no tags. Bare WAVs return `tags = None` from mutagen,
  so the absent-tag path is the normal case, not an edge case.
- Extend `PlayerController` with position reporting (`position`,
  `duration`, `progress_fraction`, `position_text`) and `seek_fraction()`
  for a draggable progress bar, plus `metadata_for()` so the UI can label
  tracks properly.
- Extend `PlayerController` with `search(query)` / `clear_search()` that
  filter the visible track list by title, artist, album, or filename while
  leaving the underlying library and current playback untouched.
- Extend `MusicAppWindow` with a progress bar the user can drag to seek, a
  search entry above the sidebar, a richer now-playing display using
  metadata, and a periodic refresh driven by Tk's `after()`.
- Tests for all of it, keeping the suite free of audio-device and display
  requirements.

## Capabilities

### New Capabilities
- `track-metadata`: reading title/artist/album/duration from audio files,
  with sensible fallbacks when tags are missing.
- `library-search`: filtering the visible library by a text query.

### Modified Capabilities
- `gui-player`: the window gains a seekable progress bar, a search field,
  and a metadata-based now-playing display.

## Impact

- Affected code: new `src/database/metadata.py`; extended
  `src/ui/controller.py` and `src/ui/app.py`. `src/audio_player/` and
  `src/database/library.py` are unchanged.
- `mutagen` is already in `requirements.txt` and installed; no new
  dependency.
- Position polling runs on Tk's `after()`, never a background thread — Tk
  isn't thread-safe, and this is where that temptation shows up.
- The CLI is untouched and keeps working; metadata and search are GUI-side
  for now.
