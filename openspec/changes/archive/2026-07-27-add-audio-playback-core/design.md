## Context

First code in the repo. No existing architecture to fit into — this design
sets the pattern later phases (CLI, GUI, metadata) will follow. The one
constraint that matters: `just-playback` was chosen specifically for its
real `seek()`/`curr_pos`/`duration` (needed by Phase 4's progress bar), so
the wrapper must expose those, not just play/pause/stop.

## Goals / Non-Goals

**Goals:**
- A playback engine usable from a CLI (next change) and later a GUI,
  without either caller touching `just_playback` directly.
- Fully testable without an audio device.
- A single, reusable path-validation utility so "is this a playable file"
  logic isn't duplicated by the directory scanner in the next change.

**Non-Goals:**
- No playlist/queue logic yet (that's `add-library-scan-and-cli`).
- No metadata reading yet (that's `add-seek-metadata-search`).
- No CLI or GUI surface in this change — `AudioPlayer` is a library class
  only, exercised solely by tests (and manually via the `run-music-app`
  skill's smoke test).

## Decisions

- **Thin wrapper, not a subclass.** `AudioPlayer` composes a
  `just_playback.Playback` instance rather than subclassing it. Rationale:
  subclassing a third-party class ties us to its exact constructor/internals;
  composition keeps the swap-out cost low if the playback library ever
  changes, and gives a natural seam for mocking in tests (patch the
  `Playback` name where `AudioPlayer` imports it).
- **`load(path)` validates via `src/utils.validate_music_path` before
  touching `just_playback`.** Rationale: fail fast with a clear Python
  exception (`FileNotFoundError`/`ValueError`) instead of letting an
  unsupported or missing file surface as an opaque miniaudio error deep in
  the C layer.
- **State is read from `just_playback` properties, not tracked separately
  in `AudioPlayer`.** `curr_pos`, `duration`, `playing`, `paused` are thin
  passthroughs. Rationale: avoids two sources of truth drifting apart;
  `just_playback` already tracks this correctly.
- **Supported extensions list lives in `src/utils.py`, not
  `audio_player`.** Rationale: the next change's directory scanner needs the
  same list to decide what to include when walking a folder — one shared
  constant, not two copies that can drift.
- **The `Playback` instance is constructed lazily on the first successful
  `load()`, not in `AudioPlayer.__init__`.** Discovered while reading the
  library source: `Playback.__init__` raises `MiniaudioError('No playback
  device is available!!')` when the machine has no output device. Eager
  construction would therefore make `AudioPlayer()` unusable in headless
  contexts even for pure state queries. Lazy construction also gives the
  "nothing loaded yet" defaults for free.
- **The wrapper normalizes `curr_pos`'s `-1` sentinel to `0.0`.**
  `just_playback` returns `-1` when no file is loaded. Callers — the Phase 4
  progress bar above all — shouldn't have to know about that; a position is
  either a real position or zero.
- **`seek()` and `set_volume()` raise on out-of-range input rather than
  clamping.** `just_playback` silently clamps both. Rationale: a caller
  computing a seek position from a UI drag has a bug if it produces a
  negative or past-the-end value, and silently landing at the track edge
  hides it. Alternative considered (matching the library's clamping) was
  rejected for that reason.

## Risks / Trade-offs

- [Risk] `just_playback` wheels only cover CPython 3.10-3.13 on Windows,
  no sdist → upgrading the venv's Python later could break installs.
  → Mitigation: pin Python 3.13 in `CLAUDE.md` (already done); revisit if
  a future `just-playback` release adds 3.14 wheels.
- [Risk] Tests that mock `Playback` can't catch real miniaudio/driver
  failures (e.g. no output device on a given machine).
  → Mitigation: the `run-music-app` skill's real-playback smoke test exists
  specifically to cover this gap manually; not part of the automated suite
  by design (per the project's no-audio-device-required test policy).

## Migration Plan

N/A — net-new code, nothing to migrate.
