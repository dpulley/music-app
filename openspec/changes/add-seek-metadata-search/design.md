## Context

Final roadmap item. Three features land together because they share one
surface: the progress bar, the search box, and the metadata labels all live
in the window built in Phase 3, and all three need the controller to grow.
The controller/window split from Phase 3 is what makes this testable — seek
arithmetic and search filtering are plain functions of state, verifiable with
no display.

## Goals / Non-Goals

**Goals:**
- Jump to any point in a track by dragging a bar.
- See real track names (artist/title) instead of filenames where tags exist.
- Filter a library down to what you're looking for.

**Non-Goals:**
- No tag *writing* — read-only, so a bug can't corrupt someone's library.
- No album art, no fuzzy search, no search history.
- No metadata caching layer. Reading tags is fast enough at this scale and a
  cache is a correctness liability (stale entries after a file changes) for
  a speed problem nobody has yet.
- The CLI does not gain search or metadata in this change.

## Decisions

- **Metadata failures degrade to the filename, never raise.** A library of
  real music contains files with no tags, broken tags, and formats mutagen
  half-understands. `read_metadata` catches those and falls back to the
  filename stem as the title. Rationale: a music player that refuses to list
  a file because its ID3 frame is malformed is worse than one that shows a
  filename. Confirmed against the project's own fixture — a bare WAV returns
  `tags = None` from mutagen, so this path runs constantly, not rarely.
- **Duration comes from mutagen's `info.length`, not the playback engine.**
  It's available before a track is loaded, so the sidebar can show durations
  without touching the audio device. `AudioPlayer.duration` remains the
  source of truth for the *currently loaded* track.
- **Seeking is expressed as a fraction (0.0-1.0), not seconds, at the UI
  boundary.** A slider naturally reports a fraction of its travel; converting
  to seconds is the controller's job, since only it knows the duration. This
  keeps the window free of arithmetic and makes the conversion unit-testable.
- **Search filters a *view*, never the underlying playlist.** `Playlist` keeps
  every track and the current-track cursor; the controller exposes
  `visible_tracks` plus a mapping back to real indices. Rationale: typing in
  the search box must not stop the music or lose your place in the album,
  which is exactly what rebuilding the playlist would do.
- **Position updates use `root.after()` on a fixed interval, not a thread.**
  Tk is not thread-safe; touching widgets from a worker is the classic source
  of intermittent, unreproducible crashes. The refresh interval is a module
  constant so it can be tuned without hunting through the window code.
- **The progress bar is a `CTkSlider`, not a `CTkProgressBar`.** A progress
  bar can only display; the requirement is to *seek*, which needs a control
  the user can grab.

## Risks / Trade-offs

- [Risk] Polling `curr_pos` several times a second while the user drags the
  slider fights the drag, snapping the handle back. → Mitigation: suppress
  position-driven updates while a drag is in progress, and apply the seek on
  release.
- [Risk] Reading tags for every file makes opening a large folder slow.
  → Mitigation: metadata is read lazily per track rather than eagerly for the
  whole library; noted as the first thing to revisit if a big library drags.
- [Trade-off] Substring matching is crude next to fuzzy search. Accepted:
  it's predictable, needs no dependency, and is what most users expect from a
  filter box.

## Migration Plan

N/A — additive. Existing playback, CLI, and window behavior are unchanged.
