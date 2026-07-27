# Music App

A music player built with Python — library scanning, a CLI, and a
customtkinter GUI with seek, metadata, and search.

## 🚀 Getting Started

1. Clone the repository.
2. Set up the virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

Requires Python 3.10–3.13. `just-playback` ships no source distribution, so a
version outside that range has no wheel to install.

## ▶️ Running

Graphical player:

```
venv\Scripts\python.exe -m src.ui <music-folder>
```

Command-line player:

```
venv\Scripts\python.exe -m src.cli <music-folder>
```

Both scan the folder recursively (`--no-recursive` to stay at the top level)
for `.mp3`, `.wav`, `.flac`, and `.ogg`. The CLI accepts `list`, `play N`,
`pause`, `resume`, `stop`, `help`, and `quit`.

## 🗂️ Directory Structure

- `src/`
    - `audio_player/`: playback engine wrapping `just-playback`. The only
      module that imports it, so the backend could be swapped in one place.
    - `ui/`: `controller.py` holds the player logic and imports no GUI library
      (which is what makes it testable headless); `app.py` is the
      customtkinter window; `__main__.py` is the entry point.
    - `database/`: library scanning, the playlist model, and tag reading.
    - `cli.py`: command-line player.
    - `utils.py`: path validation and the shared supported-format list.
- `tests/`: mirrors `src/`. No test requires an audio device or a display.
- `assets/`: holds the generated `test_tone.wav` fixture (not committed;
  `tests/conftest.py` regenerates it on demand).
- `openspec/`: specifications and the archived change history.

## 🧪 Tests

```
venv\Scripts\python.exe -m pytest
```

Tests mock `just_playback.Playback` and patch `customtkinter`, so the suite
passes on a machine with no sound card and no screen. That also means green
tests don't prove audio actually plays — see the `run-music-app` skill for the
real-hardware smoke checks.

## 📋 Development

Built spec-first with [OpenSpec](https://github.com/Fission-AI/OpenSpec).
`openspec/specs/` is the source of truth for behavior, `openspec/changes/`
holds proposals, and `changes/archive/` records how each phase was built and
why. `openspec/config.yaml` carries the project context and roadmap.

Run `openspec list --specs` to see the current capabilities.
