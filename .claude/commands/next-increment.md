---
name: "Next Increment"
description: Do exactly one bounded, testable increment of the music-app roadmap (OpenSpec-driven) and stop. The unit of work /loop repeats to build the project unattended.
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
category: Workflow
---

Do **one bounded increment** of music-app and then stop — don't try to
finish the whole roadmap in one pass. This command is designed to be run
repeatedly and unattended (via `/loop`), so it favors small, verifiable
steps over speed, and it must never need a human to answer a prompt
mid-run. Where the OpenSpec `/opsx:*` skills would use `AskUserQuestion`,
this command makes the deterministic choice itself instead.

The roadmap and full stack context live in `openspec/config.yaml`
(`context:` field) and `CLAUDE.md` — read both if this is your first time
touching this repo in the session.

## Step 1 — Find or create the active change

```bash
openspec list --json
```

- If there's an active (non-archived) change with an incomplete `tasks`
  artifact, use it.
- If there are **zero** active changes, read the `Roadmap` list in
  `openspec/config.yaml`'s `context:` field, find the first item not yet
  present under `openspec/changes/archive/`, and create it directly —
  don't wait for a human prompt:

  ```bash
  openspec new change "<next-roadmap-id>" --description "<one-line from the roadmap>"
  ```

  Then generate its artifacts (proposal, design, tasks) yourself following
  the same loop `.claude/skills/openspec-propose/SKILL.md` describes:
  `openspec status --change "<name>" --json` for the build order, then
  `openspec instructions <artifact-id> --change "<name>" --json` for each
  one, writing to `resolvedOutputPath`. Stop once `tasks` is `done` —
  that's all this step needs; implementation starts next.

  **Branch for the new phase.** Each roadmap item maps to a phase of
  `initial_plan.md`, and each phase gets its own branch so a human reviewing
  later has sane-sized chunks. When you create a new change, also create the
  matching branch off the current one:

  ```bash
  git checkout -b feat/phase-<N>-<short-name>
  ```

  e.g. roadmap item 2 (`add-library-scan-and-cli`) → `feat/phase-2-library-cli`.
  If that branch already exists, switch to it instead of recreating it.
  Check `git status` first and never switch branches with uncommitted work
  in the tree — commit it or stop and report.
- If **every** roadmap item is already archived, the roadmap is complete.
  Report that and stop — do not invent new work.

Announce which change you're working on and why (new vs. continuing).

## Step 2 — Implement 1-3 tasks, not the whole file

```bash
openspec instructions apply --change "<name>" --json
```

Read the `contextFiles` this returns (proposal, specs, design, tasks) before
touching code. Then take the **next 1-3 unchecked tasks** from `tasks.md`,
in order, and implement them:

- Follow the module boundaries and test policy in `CLAUDE.md` (no test may
  require a real audio device — mock `just_playback.Playback`).
- Keep changes scoped to exactly those tasks. Resist the urge to also fix
  or refactor unrelated things you notice — note them in the commit body
  instead if worth remembering, but leave them for a later increment.
- Tick each task's checkbox (`- [ ]` → `- [x]`) in `tasks.md` immediately
  after implementing it, not in a batch at the end.

**If a task is genuinely ambiguous** (ambiguity that would change what code
gets written, not just a minor judgment call): make the most reasonable
interpretation given the proposal/design docs, implement it, and say what
you assumed in the commit message and your summary. Don't stall the loop
waiting for an answer nobody unattended can give.

## Step 3 — Test

```bash
venv\Scripts\python.exe -m pytest
```

- **All green:** continue to Step 4.
- **Any red:** try once to fix it (if the fix is obviously within scope of
  the tasks you just touched). If it's still red after that, **stop here**
  — do not commit broken tests, do not proceed to Step 4. Report which
  tests failed and why, and leave the working tree as-is for a human to
  look at.

## Step 4 — Commit locally (never push)

```bash
git add -A
git commit -m "feat: <summary> [<change-name>]"
```

Conventional commit prefix (`feat:`/`fix:`/`test:`/`chore:`), referencing
the change id, per `CLAUDE.md`. This must land on the current
`feat/phase-N-*` branch — confirm with `git branch --show-current` if
unsure which branch you're on rather than assuming.

**Never**: `git push`, `git reset --hard`, `git clean -f`, force-anything,
or amending a previous commit. If a hook blocks the commit, fix the
reported issue and commit again as a new commit — don't bypass hooks.

## Step 5 — Archive if the change is complete

Re-check:

```bash
openspec status --change "<name>" --json
```

If every artifact is `done` and every task in `tasks.md` is checked:

```bash
openspec archive "<name>" -y
```

`-y` skips the confirmation prompt (there's no human here to confirm) but
still runs validation and spec sync — don't add `--no-validate`. Report the
archive summary. The next `/next-increment` run will pick up the following
roadmap item automatically via Step 1.

If the change isn't fully done yet, just stop — the next iteration
continues it from where this one left off.

## Stop conditions — end the session cleanly here, don't keep iterating

- **Tests red two iterations in a row** (this run and the run before it,
  going by the last commit's test status): stop, report the failure
  clearly, don't attempt a third fix blind.
- **The same task is still unchecked after two attempts**: stop and report
  what's blocking it rather than repeating the same failed approach.
- **Roadmap exhausted**: stop, report completion.
- Anything that would require `git push`, touching `origin`, installing new
  system-level dependencies, or modifying files outside this repo: stop and
  report instead of proceeding — those are outside what this command is
  allowed to do unattended.

## Summary to report at the end of every run

- Which change and which tasks were touched this iteration.
- Test result (pass/fail, and which tests if fail).
- The commit hash and message (or "no commit — tests failed" / "no commit —
  nothing to do").
- Whether a change was archived.
- Which stop condition (if any) ended the run.
