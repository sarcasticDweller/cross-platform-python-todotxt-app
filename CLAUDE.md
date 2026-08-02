# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Lalonde: a cross-platform (Linux/macOS/Android) todo.txt app written in Python + Kivy, built on `pytodotxt`. Core goals (see `README.md`): stay Google-independent, keep the on-disk `todo.txt` as the single source of truth (read-mostly, so external syncing tools like Syncthing don't get clobbered), and eventually support recurring tasks + Android alarms. The project is in an early, deliberately scrappy phase — `docs/Notes/design_questions.md` and `docs/Notes/progress.md` (a scope checklist, not a schedule) capture the current thinking.

This is also a learning project: the user is using it to learn Python/Kivy hands-on, so Claude's default role here is instructor/tutor, not implementer. Explain concepts, point to relevant code, and show illustrative example snippets in conversation — but let the user write and edit the actual source themselves. Only write or edit files directly when the user explicitly asks for that. Exception: files under `tests/` are fair game to write and edit directly, since writing tests together (rather than only ever describing them) is part of how the tutoring works here.

## Commands

Environment setup (uv-based; see `docs/Notes/ uv_instead_of_requirements.md`):
```bash
./scripts/setup_dev_env.sh   # installs uv, pins Python 3.11.15, uv sync, Buildozer apt deps
source .venv/bin/activate
```

Running tests:
```bash
uv run pytest                          # runs whole suite with coverage (see pyproject.toml addopts)
uv run pytest tests/test_tasks.py::test_create_task_adds_project_tags   # single test
```

Linting:
```bash
uvx ruff check --fix path/to/file      # see docs/Notes/ruff.md — ruff is picky about unused imports
```

Running the app:
```bash
uv run python src/lalonde/main.py
```

Building the Android APK:
```bash
JAVA_HOME=/usr/lib/jvm/temurin-17-jdk-amd64 uv run buildozer android debug   # or scripts/compile_android.sh
```

## Architecture

**Import roots.** `pyproject.toml` sets `pythonpath = ["src/lalonde"]`, so all internal imports are rooted *inside* `lalonde`, not at the package itself — e.g. `from tasks_api.task import create_task`, never `from lalonde.tasks_api...`. `buildozer.spec` sets `source.dir = src/lalonde` for the same reason: Buildozer only bundles what's under that directory, so any module living outside `src/lalonde` won't ship to Android (this bit the project once — see the buildozer note in `docs/Notes/buildozer.md`).

**`tasks_api/` — the data layer** (`task.py` + `task_manager.py`), independent of any GUI code:
- `task.py` wraps `pytodotxt.Task` construction/inspection. `create_task()` is the one constructor path everything else should go through. `TaskData` is a plain dataclass — a detached, mutable copy of a task's fields meant for GUI/edit-layer code to manipulate without touching the live `pytodotxt.Task` (which is otherwise awkward to mutate safely). `task_to_data()`/`data_to_task()` convert between the two; `compare_tasks_for_equality()` compares tasks by their serialized string form since `pytodotxt.Task` objects are ephemeral/non-identity-comparable.
- `task_manager.py`'s `TaskManager` wraps a single `pytodotxt.TodoTxt` file and is the only thing that should touch disk. `@auto_refresh` calls `self.refresh()` (full file re-read) before running — a deliberately blunt stand-in for real file-watching (the docstring flags this: "really, this should be done with a watchdog instead"). Only `__repr__` and the mutating methods (`add_task`, `update_task`, `delete_task`) carry it; `find_task()`, `__contains__`, and the other dunder accessors run without refreshing first. Mutating methods both mutate `self.todo.tasks` and immediately `self.todo.save()`; `find_task()`/`__contains__` locate tasks by `compare_tasks_for_equality()`, not object identity, since a task read back from disk is never the same object as the one that was passed in.

**`gui/`** — Kivy layer. `learning_kivy.py` is currently the app's real entry point despite the name (it's a holdover from initially learning Kivy — `main.py` imports `LalondeApp` from it). Screens are plain Kivy `Screen`/`ScreenManager` with matching `.kv` files (`main_screen.kv`, `form_create_task.kv`) loaded explicitly via `Builder.load_file()` in the same module. GUI widgets talk to `tasks_api` directly (e.g. `CreateTask.on_save()` calls `create_task()`); there's no intermediate view-model layer yet.

**pytodotxt gotchas worth knowing before touching this code** (see `docs/Notes/pytodotxt.md`, `docs/Notes/todotxt_spec.md`):
- `Task.description` includes completion/priority/date markup; use `Task.bare_description()` for just the text.
- Custom `key:value` attributes (`due:`, `rec:`) come back from `task.attributes.get(key)` as a *list*, not a scalar — `task_to_data()`'s `[0]`-indexing exists specifically to unwrap that.
- `creation_date`/`completion_date` on `pytodotxt.Task` are expected to be `datetime.date`, not `str` — passing strings crashes on serialization (currently tracked as ISSUE-015, see below).

## Testing conventions

Tests use `@pytest.mark.xfail(reason="...", strict=True)` as a live bug tracker, not just a skip mechanism — see `docs/Notes/pytest.md` for the full rationale. In short: a known bug gets a test encoding the *correct* behavior, marked `xfail(strict=True)` with a reason referencing the relevant `ISSUE-NNN`. When the bug is fixed, that test starts `XPASS`ing, which — because of `strict=True` — shows up as a hard suite failure. That failure means "pull the now-stale `xfail` marker off," not "something regressed." A normal (non-`xfail`) test going red is a real regression with no such nuance.

## Tracking known defects

`.claude/skills/review-issues/issues.md` is a hand-maintained defect log (open bugs + doc-drift), reconciled against the code via the `review-issues` skill/slash command — it is not a feature backlog (that's `docs/Notes/progress.md`). That skill's own scope note is worth preserving: it only investigates and updates the issues file, and deliberately never edits source as part of running it.
