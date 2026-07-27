## Context

`AudioPlayer` (from `add-audio-playback-core`) plays one file given a valid
path. This change adds the layer that produces those paths and keeps them in
an order the user can navigate. The GUI in Phase 3 will sit on top of exactly
these two objects, so the shape they take now determines how much the GUI has
to reimplement later — the main design pressure here.

## Goals / Non-Goals

**Goals:**
- Find playable files under a directory without duplicating the supported-
  format list.
- An ordered, addressable collection with a current-track cursor that both a
  CLI and a GUI can drive.
- A CLI good enough to actually use the app by hand.

**Non-Goals:**
- No metadata reading (artist/album/title) — that's `add-seek-metadata-search`.
  Tracks are identified by filename for now.
- No persistence: playlists live in memory for the session. A saved-playlist
  store would need a format decision that nothing yet requires.
- No search/filter — also Phase 4.
- No GUI.

## Decisions

- **`scan_directory` returns a sorted list of `Path`, not a generator.**
  Callers (a CLI numbering tracks, a GUI populating a sidebar) all need
  random access and a count immediately, so a generator would just get
  `list()`-ed at every call site. Sorting makes the numbering stable between
  runs, which matters when the user is choosing "track 4" from a printed list.
- **Scan errors are skipped, not raised.** A single unreadable directory
  (permissions, a broken symlink) shouldn't fail an otherwise good scan of a
  large library. `os.walk`'s `onerror` is left at its default of silently
  skipping, and unreadable entries simply don't appear.
- **`Playlist` owns the cursor; `AudioPlayer` stays stateless about ordering.**
  The player knows about one file at a time by design. Putting "which track is
  current" in the playlist keeps that boundary clean and means the GUI's
  next/previous buttons are one call, not bookkeeping in the view layer.
- **`next()`/`previous()` clamp at the ends and return `None` rather than
  wrapping or raising.** Wrapping surprises a user at the end of an album;
  raising forces every caller to wrap navigation in try/except. Returning
  `None` lets a caller decide (a CLI prints "end of playlist", a future
  repeat-mode toggle can wrap explicitly).
- **The CLI is a small REPL, not one-shot flags.** Playback is stateful — you
  play, then pause, then seek — so a one-shot `--play track.mp3` would exit
  before the sound finished. A prompt loop that accepts `play N`, `pause`,
  `resume`, `stop`, `list`, `quit` matches how the thing is actually used.

## Risks / Trade-offs

- [Risk] Scanning a very large library synchronously blocks the CLI at
  startup. → Mitigation: acceptable at this size; if it bites, the GUI phase
  will need a background scan anyway and can move it to a thread then. Noted
  rather than pre-optimized.
- [Risk] A file with a supported extension may still fail to decode (corrupt
  file, mislabeled extension). → Mitigation: `AudioPlayer.load()` surfaces the
  backend error; the CLI catches it per-track and keeps the session alive
  instead of crashing out of the loop.
- [Trade-off] Identifying tracks by filename reads poorly for files named
  `01.mp3`. Accepted deliberately: fixing it means metadata, which is a
  separate roadmap item with its own dependency (`mutagen`).

## Migration Plan

N/A — additive, no existing behavior changes.
