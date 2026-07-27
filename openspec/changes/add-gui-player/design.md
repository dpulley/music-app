## Context

Everything so far is headless-testable because no module needed a screen. The
GUI breaks that: customtkinter needs a display to instantiate widgets, and the
project's test policy (`CLAUDE.md`) says the suite must pass without special
hardware. An unattended loop building this can't look at the window either, so
as much behavior as possible has to be verifiable without one.

## Goals / Non-Goals

**Goals:**
- A usable window: see the library, click a track, control playback.
- Keep the testable logic out of the widget layer, so "does clicking next
  advance the playlist" is a unit test rather than a screenshot.
- Leave obvious room for Phase 4's progress bar and search box.

**Non-Goals:**
- No progress bar or seek control — Phase 4. Position polling is deliberately
  not started here.
- No metadata display (artist/album) — Phase 4; the sidebar shows filenames,
  same as the CLI.
- No theming/settings UI, no playlist persistence, no drag-to-reorder.
- The CLI is not deprecated or changed.

## Decisions

- **Split `PlayerController` (no GUI imports) from `MusicAppWindow` (all the
  widgets).** The controller owns "what should happen", the window owns "what
  it looks like". Rationale: this is the only way to get real test coverage of
  behavior in a headless suite — the controller is plain Python and tests
  drive it directly. It also means Phase 4 can add seek logic to the
  controller with tests, before wiring a slider to it. Alternative considered:
  putting logic in the window and testing with a virtual display (Xvfb-style)
  — rejected as heavy, platform-specific, and still unable to assert on
  anything but pixels.
- **The window is constructed with dependency-injected customtkinter.** Tests
  patch `src.ui.app.ctk`, so window-construction tests verify widget wiring
  (right callbacks bound to right buttons) without a display.
- **Play/pause is one toggle button, not two.** Matches how every music player
  behaves; the controller exposes `toggle_pause()` so the window doesn't track
  which state it's in.
- **Periodic UI updates will use Tk's `after()`, not a background thread.**
  Tk isn't thread-safe — widget calls from another thread are a classic source
  of intermittent crashes. Nothing polls yet in this change, but the decision
  is recorded here because Phase 4's progress bar is where the temptation
  appears.
- **Selecting a track in the sidebar does not auto-play it.** Selection and
  playback are separate actions (click to select, double-click or press Play
  to start), so browsing a library doesn't interrupt what's currently playing.

## Risks / Trade-offs

- [Risk] Mocked-customtkinter tests can pass while the real window fails to
  open (wrong widget name, bad geometry call). → Mitigation: the change isn't
  done until a human launches it once via the `run-music-app` skill; that
  manual check is an explicit task, not an afterthought.
- [Risk] A large library makes the sidebar slow to populate. → Mitigation:
  out of scope at this size; noted for Phase 4, which touches this list again
  for search and can add virtualization if it bites.
- [Trade-off] The controller/window split is more indirection than a small app
  strictly needs. Accepted: it buys headless testability, which the project's
  test policy requires and an unattended build loop depends on.

## Migration Plan

N/A — additive. The CLI entry point is untouched and keeps working.
