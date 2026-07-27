---
name: python-test-loop
description: Conventions for writing and running pytest tests in music-app (github.com/dpulley/music-app) - invoking the project venv correctly, mocking just_playback.Playback so no test needs real audio hardware, and generating the deterministic assets/test_tone.wav fixture. Use whenever adding or running tests in music-app, or whenever a test would otherwise touch real audio playback, an audio device, or a downloaded music file.
compatibility: Requires the music-app venv (venv\Scripts\python.exe) with pytest installed.
---

# python-test-loop

This project's hard rule (see `CLAUDE.md`): **unit tests must never require a
real audio device to pass.** Playback hardware isn't reliably present
(headless boxes, CI, an unattended `/next-increment` loop running overnight)
and it's slow and flaky compared to a mock. This skill is how that rule gets
followed in practice.

## Running tests

Always the venv interpreter, never a bare `python`:

```
venv\Scripts\python.exe -m pytest
```

Add `-k <expr>` or a path to scope to what you're working on;
`-v` when you need to see individual test names, not just a pass count.

## Mocking Playback

Everywhere `src/audio_player` calls into `just_playback.Playback`, tests
patch that class rather than exercising real playback:

```python
from unittest.mock import MagicMock, patch

def test_play_starts_playback():
    with patch("src.audio_player.player.Playback") as MockPlayback:
        instance = MockPlayback.return_value
        instance.curr_pos = 0.0
        instance.duration = 3.5

        from src.audio_player.player import AudioPlayer
        ap = AudioPlayer()
        ap.load("assets/test_tone.wav")
        ap.play()

        instance.play.assert_called_once()
```

Patch at the point of use (`src.audio_player.player.Playback`, i.e. wherever
your module does `from just_playback import Playback`), not
`just_playback.Playback` directly — otherwise the patch won't take effect if
the module already imported the name.

Assert on *behavior* (which methods got called, with what args, and how your
wrapper's own state/properties respond) rather than trying to assert
anything about real audio output — that's exactly what the mock removes from
the picture.

## Generating assets/test_tone.wav

The one file tests are allowed to touch on disk for "real" is a short,
deterministically-generated sine wave — not a downloaded or committed music
file (keeps the repo free of binary audio assets and copyright concerns).
Generate it with the stdlib `wave` + `struct` modules, no extra dependency:

```python
import wave, struct, math

def generate_test_tone(path="assets/test_tone.wav", seconds=2, freq=440, rate=44100):
    n_samples = int(seconds * rate)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)  # 16-bit
        f.setframerate(rate)
        for i in range(n_samples):
            sample = int(32767 * 0.3 * math.sin(2 * math.pi * freq * i / rate))
            f.writeframesraw(struct.pack("<h", sample))
```

Call this once (a `conftest.py` session-scoped fixture, or a small setup
script) rather than regenerating it inside every test — it's deterministic,
so there's no benefit to redoing the work, only wasted time.

This file is also what `run-music-app`'s real-playback smoke test loads —
it's the one shared fixture that bridges "tests use a mock" and "does this
actually play."
