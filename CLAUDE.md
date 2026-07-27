# music-app

Desktop Python music player. Roadmap and full stack rationale live in
`openspec/config.yaml` (`context:` field) — that's what OpenSpec feeds to
`/opsx:propose` and `/opsx:apply`. This file is for conventions a human or an
unattended loop needs that aren't OpenSpec-specific.

## Running Python in this repo

**Always use the venv interpreter, never bare `python`:**

```
venv\Scripts\python.exe -m pytest
venv\Scripts\python.exe -m pip install -r requirements.txt
```

Bare `python`/`python3` on this machine may resolve to the Microsoft Store
alias stub, not a real interpreter. Only `venv\Scripts\python.exe` is
guaranteed correct.

## Stack (see openspec/config.yaml for the full rationale)

- `just-playback` for playback — chosen over `pygame.mixer` because it has a
  real `seek()` and `curr_pos`/`duration`, which the Phase 4 progress bar needs.
- `mutagen` for tags, `customtkinter` for the GUI, `pytest` for tests.

## Module boundaries

- `src/audio_player/` — playback engine. **Never** imports from `src/ui`.
- `src/ui/` — customtkinter GUI. Depends on `audio_player`, not vice versa.
- `src/database/` — playlist/metadata storage.
- `tests/` mirrors the `src/` layout.

## Test policy

Unit tests **must** mock `just_playback.Playback` (`unittest.mock`) — no test
may require a real audio device to pass. Use `assets/test_tone.wav` (generated
via the stdlib `wave` module, see the `python-test-loop` skill) for anything
that needs a real file on disk.

## Commits

Conventional commits (`feat:`, `fix:`, `test:`, `chore:`). One commit per
OpenSpec task batch, referencing the change id, e.g.
`feat(playback): add Playback wrapper [add-audio-playback-core]`.

## The OpenSpec loop contract

This repo is driven by `/next-increment` (see `.claude/commands/`), which
`/loop` runs repeatedly while unattended. Each iteration does ONE bounded
step — never rushes to finish the whole roadmap in one shot. It:

1. Finds the active change (or proposes the next roadmap item via
   `/opsx:propose` if none is active).
2. Implements 1-3 tasks from that change's `tasks.md`.
3. Runs `venv\Scripts\python.exe -m pytest`.
4. Commits locally on the current `feat/phase-N-*` branch.
5. Archives the change and starts the next roadmap item only once every task
   is done.

**Hard rules for the loop:** never `git push`, never `git reset --hard`,
never force anything. Stop and report (don't keep iterating) if tests are
red two iterations in a row, or the same task is still unticked after two
attempts.
