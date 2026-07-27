## 1. Path validation utility

- [x] 1.1 Create `src/utils.py` with a `SUPPORTED_EXTENSIONS` constant (`.mp3`, `.wav`, `.flac`, `.ogg`) and `validate_music_path(path)` that raises `FileNotFoundError` for missing paths / non-files and `ValueError` for unsupported extensions, returning a normalized `Path` on success
- [x] 1.2 Add `tests/test_utils.py` covering: valid file passes, missing path raises `FileNotFoundError`, directory raises `FileNotFoundError`, unsupported extension raises `ValueError`, extension matching is case-insensitive

## 2. Test tone fixture

- [x] 2.1 Add `tests/conftest.py` with a session-scoped fixture that generates `assets/test_tone.wav` (stdlib `wave`/`struct`, 2s 440Hz sine, 16-bit mono 44.1kHz) if missing, and exposes its path to tests
- [x] 2.2 Add `assets/test_tone.wav` to `.gitignore` so the generated fixture is not committed as a binary

## 3. AudioPlayer wrapper

- [x] 3.1 Create `src/audio_player/player.py` with an `AudioPlayer` class composing `just_playback.Playback`, with `load(path)` that calls `validate_music_path` before handing the path to the engine
- [x] 3.2 Implement transport controls `play()`, `pause()`, `resume()`, `stop()` as passthroughs to the underlying engine
- [x] 3.3 Implement `seek(seconds)` (validating range against `duration`) and `set_volume(level)` (validating 0.0-1.0)
- [x] 3.4 Implement read-only passthrough properties `curr_pos`, `duration`, `playing`, `paused`, `volume` that return safe zero/falsy defaults when no file is loaded
- [x] 3.5 Export `AudioPlayer` from `src/audio_player/__init__.py`

## 4. AudioPlayer tests

- [x] 4.1 Add `tests/audio_player/__init__.py` and `tests/audio_player/test_player.py` with `unittest.mock.patch` on the `Playback` name as imported in `src.audio_player.player` (never the real engine)
- [x] 4.2 Cover load behavior: valid file loads, missing path raises before the engine is touched, unsupported extension raises before the engine is touched
- [x] 4.3 Cover transport controls: each of play/pause/resume/stop invokes the corresponding engine method exactly once, and state properties reflect the mock
- [x] 4.4 Cover seek/volume: valid values pass through to the engine; out-of-range values raise `ValueError` without calling the engine
- [x] 4.5 Cover the no-file-loaded state: `playing`/`paused` are falsy and `curr_pos`/`duration` are 0.0 with no exception raised

## 5. Verify

- [x] 5.1 Run `venv\Scripts\python.exe -m pytest` and confirm the full suite passes with no audio device required
- [x] 5.2 Run the real-playback smoke test from the `run-music-app` skill against `assets/test_tone.wav` (confirm `curr_pos` advances and `seek()` repositions) and record the observed values
