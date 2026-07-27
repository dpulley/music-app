## 1. Track metadata

- [x] 1.1 Create `src/database/metadata.py` with a `TrackMetadata` record (path, title, artist, album, duration) and `read_metadata(path)` using mutagen, falling back to the filename stem for title and empty strings for artist/album when tags are missing or unreadable, and 0.0 duration when unknown
- [x] 1.2 Add a `description` giving "Artist - Title" when both exist and the title alone otherwise, plus a `duration_text` in M:SS
- [x] 1.3 Add `tests/database/test_metadata.py` covering fully tagged files (mocked mutagen), the untagged real WAV fixture, a mutagen exception, missing duration, and both description forms

## 2. Controller: position, seek, search

- [x] 2.1 Extend `PlayerController` with `position`, `duration`, `progress_fraction`, and `position_text` (elapsed / total in M:SS), all safe when nothing is loaded
- [x] 2.2 Add `seek_fraction(fraction)` converting a 0.0-1.0 slider position to seconds against the current duration, ignoring the call when nothing is loaded and clamping out-of-range fractions
- [x] 2.3 Add `search(query)` / `clear_search()` and a `visible_tracks` view filtered case-insensitively on title, artist, album, and filename, leaving the playlist, the current track, and playback untouched
- [x] 2.4 Add `metadata_for(track)` and use metadata in `now_playing` so the display names tagged tracks properly
- [x] 2.5 Extend `tests/ui/test_controller.py` covering position/progress/seek arithmetic, seek clamping, seek with nothing loaded, search matching on each field, case-insensitivity, no-match, clearing, and that searching does not disturb playback

## 3. Window: progress bar, search box, metadata labels

- [x] 3.1 Add a `CTkSlider` progress control plus elapsed/total time label to the main panel, wired to `seek_fraction` on release
- [x] 3.2 Suppress position-driven updates while the user is dragging the slider, and apply the seek on release
- [x] 3.3 Add a `CTkEntry` search box above the sidebar that refilters the track list as the user types, rebuilding the sidebar from `visible_tracks`
- [x] 3.4 Label sidebar rows and the now-playing display with metadata descriptions rather than raw filenames
- [x] 3.5 Start a periodic refresh using `root.after()` at a module-level interval constant, never a background thread
- [x] 3.6 Extend `tests/ui/test_app.py` for the slider wiring, drag suppression, search box refiltering, metadata labelling, and that the periodic refresh is scheduled via `after`

## 4. Verify

- [x] 4.1 Run `venv\Scripts\python.exe -m pytest` and confirm the whole suite passes with no audio device and no display required
- [x] 4.2 Run a real-toolkit construction check (real customtkinter, no mainloop) confirming the new controls build and lay out without a Tcl error
- [x] 4.3 Run a real-playback seek check against `assets/test_tone.wav` confirming `seek_fraction` moves the actual playback position, and record the observed values
