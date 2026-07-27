## Why

`AudioPlayer` can play a file, but nothing can find one yet — the only way
to reach it is to hand-write a path in Python. This is `initial_plan.md`
Phase 2: let the user point at a folder of music, see what's in it, and pick
something to play. It's also what makes the app testable by a human for the
first time, and the GUI in Phase 3 needs exactly this data layer underneath
it.

## What Changes

- Add `src/database/library.py`: `scan_directory(path, recursive=True)`
  walking a folder and returning the audio files it finds, filtered by the
  existing `SUPPORTED_EXTENSIONS` from `src/utils.py` (no second copy of
  that list). Unreadable subdirectories are skipped rather than aborting the
  whole scan — a permission error on one folder shouldn't cost the user
  their entire library.
- Add `src/database/playlist.py`: a `Playlist` model holding an ordered list
  of tracks with a current-index cursor, and `next()`/`previous()`/
  `current`/`select(index)` navigation. Phase 3's sidebar and Phase 4's
  search both need an addressable ordered collection; putting the cursor
  here keeps that logic out of the GUI.
- Add `src/cli.py`: a command-line entry point that scans a directory,
  numbers the tracks it finds, and plays a chosen one through
  `AudioPlayer`, with basic transport commands while playing.
- Tests for all three, mocking `AudioPlayer`/`Playback` so the suite still
  needs no audio device, and using `tmp_path` trees for scan tests.

## Capabilities

### New Capabilities
- `music-library`: discovering playable audio files under a directory and
  holding them as an ordered, navigable playlist.
- `cli-player`: a command-line surface for listing discovered tracks,
  selecting one, and controlling playback.

### Modified Capabilities
(none — `audio-playback` is consumed as-is; no requirement of it changes)

## Impact

- Affected code: new `src/database/library.py`, `src/database/playlist.py`,
  `src/cli.py`, plus tests. `src/utils.py` gains no new behavior but its
  `SUPPORTED_EXTENSIONS` becomes shared, as designed in the previous change.
- No new dependencies — stdlib `pathlib`/`argparse` plus the existing
  `AudioPlayer`.
- `src/audio_player/` is unchanged: the module boundary holds, with the CLI
  depending on the player and never the reverse.
