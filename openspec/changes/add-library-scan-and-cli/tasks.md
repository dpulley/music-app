## 1. Library scanning

- [x] 1.1 Create `src/database/library.py` with `scan_directory(path, recursive=True)` returning a sorted list of `Path`, filtered by `SUPPORTED_EXTENSIONS` imported from `src/utils.py`, raising `NotADirectoryError` for a non-directory path and skipping unreadable subdirectories
- [x] 1.2 Add `tests/database/__init__.py` and `tests/database/test_library.py` using `tmp_path` trees: mixed audio/non-audio files, nested directories, `recursive=False`, stable sort order, empty directory, non-directory path

## 2. Playlist model

- [ ] 2.1 Create `src/database/playlist.py` with a `Playlist` class holding an ordered track list plus a cursor, exposing `current`, `next()`, `previous()`, `select(index)`, `__len__`, and iteration
- [ ] 2.2 Implement end-of-list behavior: `next()`/`previous()` clamp and return `None` at the ends, `select()` raises `IndexError` out of range leaving the cursor unchanged, and an empty playlist reports `current is None` without raising
- [ ] 2.3 Add `tests/database/test_playlist.py` covering navigation, clamping at both ends, select by index, out-of-range select, and the empty-playlist case

## 3. CLI

- [ ] 3.1 Create `src/cli.py` with an argparse entry point taking a directory argument, scanning it, printing a 1-based numbered track list, and exiting non-zero with a message on an invalid directory or cleanly on an empty one
- [ ] 3.2 Implement the command loop: `list`, `play N`, `pause`, `resume`, `stop`, `quit`, driving an `AudioPlayer`, reporting "no track loaded" for transport commands issued too early, and catching per-track load failures without exiting the loop
- [ ] 3.3 Add `tests/test_cli.py` mocking `AudioPlayer` and driving the command loop with scripted input: play by number, out-of-range number, transport before load, load failure, and quit

## 4. Verify

- [ ] 4.1 Run `venv\Scripts\python.exe -m pytest` and confirm the whole suite passes with no audio device required
- [ ] 4.2 Run the CLI by hand against a directory containing `assets/test_tone.wav` and confirm listing, `play 1`, `pause`, `resume`, `stop`, and `quit` all behave (record observed output)
