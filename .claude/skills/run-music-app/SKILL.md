---
name: run-music-app
description: Launch and smoke-test the music-app player (github.com/dpulley/music-app) to confirm a change actually works, not just that pytest is green. Use this whenever you've just implemented or modified playback, CLI, or GUI code in music-app and need to see it run, or the user asks to "run the app", "try it", or "does it actually play". Also covers telling a genuine playback bug apart from "no audio output device on this machine".
compatibility: Requires the music-app venv (venv\Scripts\python.exe) with just-playback, mutagen, and customtkinter installed.
---

# Run music-app

Tests mock `just_playback.Playback`, so a green pytest run only proves the
code *calls* the right methods — it never proves audio actually comes out.
This skill closes that gap with a real, unattended smoke test.

## Before running anything

Confirm you're using the project venv, not a bare `python`:

```
venv\Scripts\python.exe --version
```

If that path doesn't exist yet, the venv hasn't been created — stop and set
it up first (`python -m venv venv` at the repo root, then
`venv\Scripts\python.exe -m pip install -r requirements.txt`). Never fall
back to a bare `python`/`python3` on this machine — it may be the Microsoft
Store alias stub, not a real interpreter.

## Smoke-testing playback (CLI/core, Phase 1-2)

1. Make sure `assets/test_tone.wav` exists — a short deterministic sine wave
   used exactly for this purpose. If it's missing, generate it with the
   `python-test-loop` skill (stdlib `wave` module, no network, nothing to
   download).
2. Run a short one-shot script (don't hand-play interactively) that:
   - loads `assets/test_tone.wav` through the real `Playback` class (not the
     mock — this is the one place in the whole project a real call is
     correct),
   - calls `play()`,
   - polls `curr_pos` a few times over ~1 second and asserts it's increasing,
   - calls `seek()` partway through and asserts `curr_pos` jumps accordingly,
   - calls `stop()`.
3. Report what actually happened: which assertions passed, and the observed
   `curr_pos` values — don't just say "it worked."

## Telling a real bug apart from "no audio device"

`just_playback` (via miniaudio) needs a working output device. On a
headless machine, CI runner, or a box with audio disabled, playback calls
can raise or silently no-op even when the code is correct. Before treating a
smoke-test failure as a bug:

- Check the actual exception/error text for device-related wording (e.g.
  "no device", "failed to initialize", "WASAPI"/"DirectSound" errors on
  Windows) vs. a Python traceback pointing at your own code.
- If it looks device-related, say so explicitly and treat pytest (with the
  mock) as the source of truth for that change instead of blocking on the
  smoke test — don't spend time chasing a hardware issue that isn't the
  code's fault.
- If the traceback points into your own `audio_player`/`ui` code, that's a
  real bug — fix it before moving on, regardless of what pytest says.

## Running the GUI (Phase 3+)

Once `src/ui/` exists, launch it non-interactively where possible:

```
venv\Scripts\python.exe -m src.ui.app
```

customtkinter needs a display; on a headless session this will fail the
same way the audio device can fail — apply the same "is this environment or
is this my code" judgment before reporting a failure. When a display is
available, take a screenshot or describe what rendered (playlist sidebar
populated, now-playing text correct, transport buttons enabled/disabled
appropriately) rather than assuming the window opening means success.
