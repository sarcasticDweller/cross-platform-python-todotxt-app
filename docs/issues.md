# Issues Tracker (AI-reference)

This file exists for the `/review-issues` skill (see `.claude/skills/review-issues/SKILL.md`). It's not a feature backlog — that's `docs/progress.md` — this is a running log of concrete defects found in existing code *and docs*, meant to survive between chat sessions so an AI review can diff "what we knew about" against "what's actually true now." Inaccurate documentation counts as a real issue, not a footnote: docs that confidently state something false are worse than no docs, and get tracked with the same rigor as code bugs.

Each entry keeps a stable ID so it can be referenced/updated across reviews. Don't renumber existing IDs when adding new ones.

## Open

<<<<<<< HEAD
### ISSUE-031: Building for more than one Android arch in `buildozer.spec`'s `android.archs` reliably breaks the build — python-for-android reuses one shared scratch venv across archs without clearing it, corrupting pip on the second arch
=======
### ISSUE-028: Building for more than one Android arch in `buildozer.spec`'s `android.archs` reliably breaks the build — python-for-android reuses one shared scratch venv across archs without clearing it, corrupting pip on the second arch
- **Status:** open
- **Kind:** bug (upstream, in python-for-android — not fixable from this repo)
- **Location:** `buildozer.spec`'s `android.archs` setting; root cause is `pythonforandroid/build.py`'s `run_pymodules_install()` (`shprint(host_python, '-m', 'venv', 'venv')` at the top of the function, no `--clear`, path not arch-qualified)
- **Noted:** 2026-08-05
- **Details:** With `android.archs = arm64-v8a, armeabi-v7a`, `compile_android.sh` compiles Kivy/SDL2/pyjnius from source successfully for *both* archs, then crashes in the final pure-Python-deps install stage for the second arch with `ImportError: cannot import name 'BuildDependencyInstallError' from 'pip._internal.exceptions'`. Root cause, confirmed by reading the checked-out p4a source (`.buildozer/android/platform/python-for-android`, tracking unpinned `master`/`release-2026.05.09`) and its `git log -p` history: `run_pymodules_install()` runs `python -m venv venv` in `ctx.build_dir`, a path shared across all archs in a single build (not arch-qualified), with no `--clear`. For the first arch this creates the venv fresh and `pip install -U pip` cleanly upgrades pip (seen: 25.3 → 26.2, whatever's newest on PyPI at build time — pip itself isn't pinned anywhere in this repo or by p4a). For the second arch, rerunning `python -m venv venv` on the already-upgraded venv re-invokes `ensurepip`, which reseeds its bundled (older) pip's files into site-packages without cleanly removing files/bytecode that only exist in the newer version — leaving a self-inconsistent pip install that crashes on next invocation. This venv-reuse code itself is old (essentially unchanged since 2020/2021), so it's not a recent p4a regression; the trigger is timing-dependent on whatever pip version happens to resolve as "latest" on PyPI when `pip install -U pip` runs, which is why this may not reproduce identically on every machine/every day.
- **Direction (not prescriptive):** can't be fixed by editing p4a directly (it's downloaded fresh into `.buildozer/`, untracked, not part of this repo). Current workaround, applied on branch `drop-armeabi-v7a-support`: dropped `android.archs` to `arm64-v8a` only, sidestepping the bug since there's only one arch stage. A fix that keeps 32-bit (`armeabi-v7a`) support would need something like a Buildozer `p4a.hook` that force-clears `ctx.build_dir`'s shared `venv` directory before each arch's pymodules-install stage.

### ISSUE-027: `TaskWidget.on_completed()` always stamps `completion_date`, even when un-completing a task — and `create_task()` has no guard stopping `completion_date` from being set without `is_completed=True` or without a `creation_date`, so the value is silently swallowed on save
>>>>>>> main
- **Status:** open
- **GitHub:** https://github.com/sarcasticDweller/cross-platform-python-todotxt-app/issues/4
- **Kind:** bug (upstream, in python-for-android — not fixable from this repo)
- **Location:** `buildozer.spec`'s `android.archs` setting; root cause is `pythonforandroid/build.py`'s `run_pymodules_install()` (`shprint(host_python, '-m', 'venv', 'venv')` at the top of the function, no `--clear`, path not arch-qualified)
- **Noted:** 2026-08-05
- **Details:** With `android.archs = arm64-v8a, armeabi-v7a`, `compile_android.sh` compiles Kivy/SDL2/pyjnius from source successfully for *both* archs, then crashes in the final pure-Python-deps install stage for the second arch with `ImportError: cannot import name 'BuildDependencyInstallError' from 'pip._internal.exceptions'`. Root cause, confirmed by reading the checked-out p4a source (`.buildozer/android/platform/python-for-android`, tracking unpinned `master`/`release-2026.05.09`) and its `git log -p` history: `run_pymodules_install()` runs `python -m venv venv` in `ctx.build_dir`, a path shared across all archs in a single build (not arch-qualified), with no `--clear`. For the first arch this creates the venv fresh and `pip install -U pip` cleanly upgrades pip (seen: 25.3 → 26.2, whatever's newest on PyPI at build time — pip itself isn't pinned anywhere in this repo or by p4a). For the second arch, rerunning `python -m venv venv` on the already-upgraded venv re-invokes `ensurepip`, which reseeds its bundled (older) pip's files into site-packages without cleanly removing files/bytecode that only exist in the newer version — leaving a self-inconsistent pip install that crashes on next invocation. This venv-reuse code itself is old (essentially unchanged since 2020/2021), so it's not a recent p4a regression; the trigger is timing-dependent on whatever pip version happens to resolve as "latest" on PyPI when `pip install -U pip` runs, which is why this may not reproduce identically on every machine/every day.
- **Direction (not prescriptive):** can't be fixed by editing p4a directly (it's downloaded fresh into `.buildozer/`, untracked, not part of this repo). Current workaround, applied on branch `drop-armeabi-v7a-support`: dropped `android.archs` to `arm64-v8a` only, sidestepping the bug since there's only one arch stage. A fix that keeps 32-bit (`armeabi-v7a`) support would need something like a Buildozer `p4a.hook` that force-clears `ctx.build_dir`'s shared `venv` directory before each arch's pymodules-install stage.

### ISSUE-032: `LalondeApp.on_start()` unconditionally calls `launch_folder_picker()`, which raises `NotImplementedError` on every non-Android platform — the app cannot start on Linux/macOS on a fresh settings file
- **Status:** open
- **GitHub:** https://github.com/sarcasticDweller/cross-platform-python-todotxt-app/issues/5
- **Kind:** bug
- **Location:** `src/lalonde/main.py:38-40` (`on_start()`); root cause in `src/lalonde/file_loading_api/file_loading_api.py:16-22` (`launch_folder_picker`'s `match` statement)
- **Noted:** 2026-08-10
- **Details:** `on_start()` calls `launch_folder_picker(platform, self.on_folder_picked)` whenever `self.settings["user_data_dir"]` is falsy. `DEFAULT_SETTINGS["user_data_dir"]` in `settings.py` defaults to `""`, and nothing in `main.py`'s `on_folder_picked()` ever calls `Settings.save_settings()` (that method exists but is never invoked anywhere in the codebase — confirmed by repo-wide grep), so `user_data_dir` never actually persists across runs either way. `launch_folder_picker`'s `match platform_name` only handles `"android"`; every other case (including `"linux"`, `"macosx"`) falls to `case _: raise NotImplementedError(...)`. Confirmed by direct repro: running `uv run python src/lalonde/main.py` on this Linux dev machine reaches `on_start()` (past `build()`, so screen/widget construction succeeds) and then crashes immediately with `NotImplementedError: The only supported platform is Android.` This contradicts `CLAUDE.md`'s stated cross-platform goal and its own documented `uv run python src/lalonde/main.py` command for running the app locally.
- **Direction (not prescriptive):** give `launch_folder_picker` (or its caller) a non-Android path — e.g. a desktop file-chooser dialog, or a dev-only default folder — instead of unconditionally raising; and separately, `Settings.save_settings()` looks like it needs to actually be called somewhere for `user_data_dir` to persist at all, Android or not.

### ISSUE-028: `EditTaskScreen` reads/writes `project_tags`/`context_tags` as plain strings, but `TaskData` types them as `list[str]` — editing and saving any task now silently strips all of its existing project/context tags
- **Status:** open
- **GitHub:** https://github.com/sarcasticDweller/cross-platform-python-todotxt-app/issues/3
- **Kind:** bug
- **Location:** `src/lalonde/gui/edit_task.py`, `EditTaskScreen._set_fields()` (`safe_string(task_data.project_tags)`/`safe_string(task_data.context_tags)`) and `EditTaskScreen.on_save()` (`project_tags=self.project_tags.split(" ")`, `context_tags=self.context_tags.split(" ")`)
- **Noted:** 2026-08-02 (re-verified and updated 2026-08-10 — underlying code has changed shape since original write-up)
- **Details:** `TaskData.project_tags`/`context_tags` (`src/lalonde/tasks_api/task.py`) are `list[str]`. The originally-reported call sites have changed (`self.ids.project_tags`/`self.ids.context_tags` no longer exist — `edit_task.kv` currently has no project/context tag widgets at all; `_create_mode()`/`_edit_mode()` only ever add a `DescriptionField` and a `due` `DateField`), and `on_save()` now does `.split(" ")` instead of passing a raw string straight through, so the original "shreds into one-character tags" failure mode no longer reproduces that way. But the root cause is still present and now causes silent, unconditional data loss: `_set_fields()` still passes the list straight into `safe_string()`, whose `isinstance(arg, str)` check fails for a list and returns `""`, blanking the `project_tags`/`context_tags` `StringProperty`s every time the edit screen opens on an existing task — and since nothing in the current UI re-populates them, `on_save()` then rebuilds `TaskData` from those blanked strings. Confirmed by direct repro: constructing `TaskData(description="foo", project_tags=["home"], context_tags=["errand"])`, running it through `_set_fields()`'s and `on_save()`'s logic exactly as written, and serializing the result gives `'foo'` — both tags are gone, with no user interaction needed beyond opening and saving the edit screen. Separately (latent, since there's currently no UI path to trigger it): if a project/context tag field is ever wired back up and a user types the tag with its natural todo.txt `+`/`@` prefix (e.g. `"+home"`), `on_save()`'s `.split(" ")` list flows straight into `create_task()`'s `task.add_project(tag)`/`task.add_context(tag)` without stripping the prefix, and `pytodotxt.Task.add_project("+home")` serializes to a doubled `++home` — confirmed by direct repro against `pytodotxt` directly.
- **Direction (not prescriptive):** decide on a text-entry convention for a list-typed field (e.g. space- or comma-separated, with or without the `+`/`@` prefix) and convert explicitly in both directions — join the list into text in `_set_fields()`, split (and strip any prefix) back into a list in `on_save()` — instead of passing the raw type through `safe_string()`. This also blocks re-adding project/context tag widgets to the edit form without reintroducing data loss.

### ISSUE-024: `scripts/compile_android.sh` fails to compile on GitHub Codespaces, cause not yet diagnosed
- **Status:** open
- **Kind:** bug
- **Location:** `scripts/compile_android.sh`
- **Noted:** 2026-07-30
- **Details:** User reports the script does not successfully compile when run in a GitHub Codespace. Error output not yet captured/attached — pending follow-up.
- **Direction (not prescriptive):** capture the actual failure output from a Codespace run and add it here before investigating further.

## Resolved

### ISSUE-037: `CLAUDE.md`'s pytodotxt-gotchas section still pointed at ISSUE-015 as if it were open
- **Status:** resolved
- **Resolved:** 2026-08-10
- **Kind:** doc-drift
- **Note:** The `creation_date`/`completion_date` bullet under "pytodotxt gotchas worth knowing" said passing a `str` "crashes on serialization (currently tracked as ISSUE-015, see below)." ISSUE-015 was actually resolved on 2026-07-30 — `create_task()` now raises an explicit `TypeError` immediately instead of crashing three calls deep in serialization. The bullet now reads "`create_task()` guards both with an explicit `TypeError` rather than letting a `str` crash deep inside serialization (see resolved ISSUE-015)."

### ISSUE-036: `CLAUDE.md`'s Architecture → `gui/` paragraph described a version of the GUI layer that no longer exists
- **Status:** resolved
- **Resolved:** 2026-08-10
- **Kind:** doc-drift
- **Note:** The paragraph claimed `learning_kivy.py` was still the real entry point (`main.py` importing `LalondeApp` from it) and that GUI widgets called `create_task()` directly via a `CreateTask.on_save()` example. Confirmed by reading current `src/lalonde/main.py` and `src/lalonde/gui/*.py`: `learning_kivy.py` and `form_create_task.kv` no longer exist (only a stray `.pyc` remnant of the former); `main.py` defines `LalondeApp` itself and builds a `ScreenManager` of `MainScreen`/`EditTaskScreen`/`FallbackScreen`; there is no `CreateTask` class — `EditTaskScreen.on_save()` goes through `TaskData`/`data_to_task()` and `TaskManager.add_task()`/`update_task()`, never calling `create_task()` directly. Rewrote the paragraph to match current file names and call flow.

### ISSUE-035: `CLAUDE.md`'s "Known unpinned as of 2026-08-05" list still claims `pillow` floats transitively, but it's now pinned exactly in `pyproject.toml`
- **Status:** resolved
- **Resolved:** 2026-08-10
- **Kind:** doc-drift
- **Note:** Confirmed `pyproject.toml`'s `[dependency-groups] dev` list has `"pillow==9.5.0"` — an exact pin. Removed the stale `pillow` bullet from the "Known unpinned" list in `CLAUDE.md` (kept the still-accurate `pip`/`pytest`/`pytest-cov` floating-range bullet, with a parenthetical noting `pillow` is now pinned) and bumped the "as of" date to 2026-08-10.

### ISSUE-034: `CLAUDE.md`'s "Tracking known defects" section gives the wrong path for the issues tracker file
- **Status:** resolved
- **Resolved:** 2026-08-10
- **Kind:** doc-drift
- **Note:** `CLAUDE.md` said "`.claude/skills/review-issues/issues.md` is a hand-maintained defect log" — that path doesn't exist (`.claude/skills/review-issues/` contains only `SKILL.md`). Changed to `docs/issues.md`, matching this file's own self-description and `SKILL.md`'s references (already corrected under ISSUE-020).

### ISSUE-033: `CLAUDE.md` repeatedly cited a `docs/Notes/` directory and eight files inside it that have never existed anywhere in this repo's git history
- **Status:** resolved
- **Resolved:** 2026-08-10
- **Kind:** doc-drift
- **Note:** Confirmed by `find`/`ls` that no `docs/Notes/` directory exists on disk (tracked or untracked), and by `git log --all --diff-filter=A` for each of the eight filenames (`design_questions.md`, `progress.md`, `uv_instead_of_requirements.md`, `buildozer.md`, `pytodotxt.md`, `todotxt_spec.md`, `pytest.md`, `ruff.md`) that none were ever added on any branch. Stripped all eight dead references from `CLAUDE.md` (Project, Commands ×2, Architecture, pytodotxt gotchas, Testing conventions sections), keeping the substantive guidance text each one was attached to. The "Project" paragraph's `docs/Notes/progress.md` reference was replaced with a pointer to `docs/todo.txt`, the closest currently-real equivalent (a short informal pending-work list); the "Tracking known defects" section's backlog pointer was updated the same way.

### ISSUE-030: Any `MDFloatingActionButton` embedded via `MDBottomAppBar`/`MDTopAppBar(type="bottom")` crashes the app on startup with `ValueError: x1 must be greater than or equal to x0`
- **Status:** resolved
- **Resolved:** 2026-08-10
- **Kind:** bug
- **Note:** `src/lalonde/gui/main_screen.kv` no longer embeds the floating action button inside an `MDBottomAppBar`/`MDTopAppBar(type="bottom")` at all — it's now a plain `MDTopAppBar` (default `type="top"`, no floating button shown) plus a standalone `MDFloatingActionButton` in a separate `FloatLayout`, positioned via `pos_hint`. Both the top bar's (unused) `action_button` and the standalone FAB now set `elevation = 0` via `on_kv_post`. Confirmed by reading `kivymd/uix/behaviors/elevation.py:992` (`if self._elevation > 0:` gates the entire shadow-drawing block, including the `__draw_shadow__`/`PIL.ImageDraw.rectangle` call that previously crashed) — `elevation = 0` means `_elevation` stays `0` and that whole code path never runs. Confirmed live: `uv run python src/lalonde/main.py` now builds both screens' widget trees without the `ValueError` (it does hit a *different*, unrelated crash afterward — see new ISSUE-032).

### ISSUE-029: `edit_task.kv`'s `on_text` handlers for the `creation_date` and `project_tags` `TextInput`s both write to `root.completion_date` instead of their own field, so typing in either box overwrites the completion_date box's text live
- **Status:** resolved
- **Resolved:** 2026-08-02
- **Kind:** bug
- **Note:** Both copy-pasted lines in `src/lalonde/gui/edit_task.kv` now reference their own field — line 65 reads `on_text: root.creation_date = self.text` and line 73 reads `on_text: root.project_tags = self.text` — matching the `text: root.<field>` / `on_text: root.<field> = self.text` pattern used by every other field in the form. Confirmed by re-reading the file: all nine `on_text` lines now each reference a distinct root property with no duplicates.

### ISSUE-027: `TaskWidget.on_completed()` always stamps `completion_date`, even when un-completing a task — and `create_task()` has no guard stopping `completion_date` from being set without `is_completed=True` or without a `creation_date`, so the value is silently swallowed on save
- **Status:** resolved
- **Resolved:** 2026-08-02
- **Kind:** bug
- **Note:** `on_completed()` in `src/lalonde/gui/tasks_view.py` now reads `if value and self.task_data.creation_date: self.task_data.completion_date = today()` — it no longer stamps `completion_date` on un-completing (the `if value` guard), and no longer attempts to set it when there's no `creation_date` to pair it with (the `and self.task_data.creation_date` guard), matching the "Direction" this issue suggested. Confirmed by direct repro: simulating `on_completed(value=True)` against a `TaskData` with no `creation_date` now serializes to `'x foo'` with no dropped/attempted `completion_date`; simulating `on_completed(value=False)` against a previously-completed task with both dates set leaves `completion_date` unset in the serialized output (`pytodotxt` only emits it when `is_completed` is `True`), so nothing stale leaks through either.

### ISSUE-019: `create_task`'s `due` param is `datetime.date`-only (now enforced with a `TypeError` guard), but the GUI's only call site still passes a plain string, so saving a task with a due date still crashes
- **Status:** resolved
- **Resolved:** 2026-08-01
- **Kind:** bug
- **Note:** `CreateTask.on_save()` in `learning_kivy.py:37` now reads `due=datetime.date.fromisoformat(self.ids.due.text) if self.ids.due.text else None` — a real `datetime.date` (or `None`) now reaches `create_task()`'s strict `due` parameter instead of a raw string. Confirmed by direct repro simulating the call site logic: constructing a task the same way `on_save()` does, with `due_text = "2026-08-01"` parsed via `datetime.date.fromisoformat`, now serializes cleanly (`'2026-08-01 foo due:2026-08-01'`) instead of raising.

### ISSUE-026: `CLAUDE.md` claimed every public `TaskManager` method except `refresh()` is decorated with `@auto_refresh`, but six public methods weren't
- **Status:** resolved
- **Resolved:** 2026-07-30
- **Kind:** doc-drift
- **Note:** Corrected the Architecture → `tasks_api/` paragraph in `CLAUDE.md` to say only `__repr__` and the mutating methods (`add_task`, `update_task`, `delete_task`) carry `@auto_refresh`, and that `find_task()`, `__contains__`, and the other dunder accessors run without refreshing first — matching the actual code in `src/lalonde/tasks_api/task_manager.py`.

### ISSUE-025: `docs/Notes/buildozer.md`'s "Compiling" section gave a broken shell command that didn't match the real `scripts/compile_android.sh`
- **Status:** resolved
- **Resolved:** 2026-07-30
- **Kind:** doc-drift
- **Note:** Fixed the typo'd `JAVA_HOME` path in `docs/Notes/buildozer.md:13` (`temurin-uv-17-jdk-amd64` → `temurin-17-jdk-amd64`), so it now matches `scripts/compile_android.sh` and `CLAUDE.md`'s documented command. (The `uv run` prefix was already present in the actual file — this issue's original write-up mistakenly described it as missing.)

### ISSUE-022: `create_task()` accepts two input combinations that the default (pedantic) serializer can never persist — `priority` on a completed task, and `completion_date` without `creation_date` — silently losing the data on the very first save/reparse, independent of ISSUE-021's tag-reparse trigger
- **Status:** resolved (won't fix)
- **Resolved:** 2026-08-01
- **Kind:** bug
- **Note:** Reclassified, not fixed: user confirmed `create_task()` is meant to stay lossy — it validates that inputs will *parse*, not that they'll be *preserved* on write, consistent with its docstring and with the ISSUE-023 precedent. No guards will be added for these two combinations; data-integrity validation for them is the caller's responsibility. (The 2026-08-01 reopening of this issue, which found the previously-claimed guards didn't exist in the code, stands as the accurate technical history — this entry now closes it as an intentional design decision rather than a pending fix.)

### ISSUE-021: `create_task()` sets `priority`/`completion_date`/`creation_date` before adding project/context tags or `due`/`rec` attributes — but `pytodotxt`'s `add_project`/`add_context`/`add_attribute` force a reparse that silently drops priority/completion_date set earlier in the same call
- **Status:** resolved (won't fix)
- **Resolved:** 2026-08-01
- **Kind:** bug
- **Note:** Reclassified, not fixed: same call as ISSUE-022 — `create_task()` stays intentionally lossy, so the reordering fix this issue's "Direction" suggested won't be made. Caller is responsible for not relying on `priority` surviving alongside `is_completed=True` and project/context tags.

### ISSUE-023: `create_task()` allowed one un-persistable completed-task combination — `creation_date` set on a completed task without a `completion_date` — silently losing the creation date on save/reparse
- **Status:** resolved (won't fix)
- **Resolved:** 2026-07-30
- **Kind:** bug
- **Note:** Reclassified, not fixed: the user judged this combination as acceptable/expected behavior rather than a defect worth guarding against — the same "lossy by design" call later extended to ISSUE-021 and ISSUE-022. No code change made.

### ISSUE-015: `create_task`'s `creation_date`/`completion_date` params take `datetime.date` now, but nothing parses a `str` before assigning, so passing a date as a string still crashes on serialization
- **Status:** resolved
- **Resolved:** 2026-07-30
- **Kind:** bug
- **Note:** `create_task()` now explicitly guards both parameters — `if not isinstance(creation_date, datetime.date): raise TypeError(...)` and the same for `completion_date` — rejecting a `str` outright with a clear error instead of letting it crash three calls deep inside `pytodotxt`'s serializer. Confirmed by direct repro: `create_task(description="foo", creation_date="2026-01-01")` now raises `TypeError: creation_date must be a datetime.date, got str` immediately, and `create_task(description="foo", creation_date=datetime.date(2026, 1, 1))` serializes cleanly via `str(task)`. Tests updated to match (`tests/test_tasks.py::test_create_task_creation_date_rejects_str`, `test_create_task_creation_date_accepts_date_and_serializes`, `test_create_task_completion_date_rejects_str`) — the old test asserting a `str` "does not crash" was removed since that was never the intended contract.

### ISSUE-020: `.claude/skills/review-issues/SKILL.md` gives self-contradictory locations for the issues tracker file after an in-progress, uncommitted move to `docs/issues.md`
- **Status:** resolved
- **Resolved:** 2026-07-30
- **Kind:** doc-drift
- **Note:** All five path references in `SKILL.md` (frontmatter `description`, intro paragraph, "Scope reminder", Step 1, Step 4) now consistently say `docs/issues.md`, including the `.docs` → `docs` typo fix. Confirmed by re-reading the current file. Note the underlying file move itself is still uncommitted (`git status` still shows the old path as deleted and `docs/issues.md` as untracked) — that's a separate housekeeping step, not a doc-accuracy issue.

### ISSUE-017: `CreateTask.on_save` in `learning_kivy.py` always crashes — passes `recurrance=` but `create_task` takes `rec`
- **Status:** resolved
- **Resolved:** 2026-07-30
- **Kind:** bug
- **Note:** The call site now reads `rec=self.ids.recurrance.text` (`src/lalonde/gui/learning_kivy.py:33`) — the `ids.recurrance` widget name is unchanged, only the keyword argument was fixed. Confirmed by reading the current call site; the mismatch that caused `TypeError: create_task() got an unexpected keyword argument 'recurrance'` is gone. (Note: the same call site now has a *different* problem — see newly-opened ISSUE-019 — but that's an unrelated regression from a separate, still-in-progress typing change, not a recurrence of this issue.)

### ISSUE-018: `docs/Notes/buildozer.md` claims `tasks_api.py` was moved to `src/lalonde/tasks_api/tasks_api.py` — that file no longer exists
- **Status:** resolved
- **Resolved:** 2026-07-30
- **Kind:** doc-drift
- **Note:** Line 7 now reads "...although since then that file has been split into multiple files serving discrete purposes" — it no longer asserts the stale `tasks_api.py` filename as current fact, just as historical context for the original move. Confirmed by re-reading `docs/Notes/buildozer.md`.

### ISSUE-013: 4 tests in `test_TaskManager.py` now fail — stale `xfail(strict=True)` markers on already-fixed bugs
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** The four `xfail(strict=True)` markers are gone from `tests/test_TaskManager.py` — `test_TaskManager_update_task_persists_to_disk`, `test_TaskManager_delete_task_persists_to_disk`, `test_TaskManager_iter_yields_tasks_in_order`, and `test_TaskManager_repr_returns_a_string` are now plain passing tests. Confirmed by direct repro: `uv run pytest tests/` reports `46 passed, 1 xfailed` (the one remaining xfail is the legitimate, still-open ISSUE-015 marker) with no `XPASS(strict)` failures.

### ISSUE-016: `task_to_dict`'s `due`/`rec` values are single-element lists, not plain strings
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** The conversion function (renamed `task_to_data()`, now returning a `TaskData` dataclass instead of a `dict`) unwraps the list: `due=task.attributes.get("due", [None])[0]` / `rec=task.attributes.get("rec", [None])[0]`. Confirmed by direct repro: `task_to_data(create_task(description="water plants", due="2026-08-01", rec="+1w"))` now has `.due == '2026-08-01'` and `.rec == '+1w'` (plain strings, not lists), so `task_to_data()` → `data_to_task()` round-trips correctly for tasks with `due`/`rec` set.

### ISSUE-014: `dict_to_task` sets `is_completed` to `None` instead of `False` when the key is absent from the input dict
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** The dict-based API was replaced with a `TaskData` dataclass (see ISSUE-016 note) whose `is_completed` field itself defaults to `False` at the type level, so the renamed `data_to_task()` can no longer receive a missing/`None` value for it the way `dict.get("is_completed")` could. Confirmed by direct repro: `data_to_task(TaskData(description="x")).is_completed` is `False`.

### ISSUE-010: `task_manager.py` fails to import at all — `ModuleNotFoundError: No module named 'task'`
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** `task_manager.py` line 4 now reads `from tasks_api.task import compare_tasks_for_equality` — a package-qualified import that matches how the rest of the project resolves this module. Confirmed by direct repro: `uv run pytest tests/` now collects and runs both test modules with no `ModuleNotFoundError`.

### ISSUE-011: `create_task` is not importable from `tasks_api.task_manager`
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** Both remaining call sites were updated to import `create_task` directly from `tasks_api.task` instead of expecting it through `tasks_api.task_manager`: `src/lalonde/gui/learning_kivy.py` now has separate `from tasks_api.task_manager import TaskManager` and `from tasks_api.task import create_task` lines, and `tests/test_TaskManager.py` does the same. Confirmed by direct repro: both modules now import cleanly.

### ISSUE-006: `TaskManager.__iter__` causes infinite recursion
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** `__iter__` (now in `src/lalonde/tasks_api/task_manager.py`) returns `iter(self.todo.tasks)` instead of `iter(self)`. Confirmed by direct repro: iterating a `TaskManager` with tasks now yields task descriptions in order with no `RecursionError`. (The `xfail(strict=True)` test for this in `tests/test_TaskManager.py` can't currently run because `task_manager.py` fails to import at all — see ISSUE-010 — so once that's fixed, this xfail marker will need removing or it'll XPASS-fail the suite.)

### ISSUE-007: `TaskManager.__repr__` returns a list, not a string
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** `__repr__` now returns `repr(self.todo.tasks)` instead of the raw list. Confirmed by direct repro: `repr(manager)` now returns an actual `str` (e.g. `"[Task('buy milk'), Task('walk dog')]"`) instead of raising `TypeError`. Same caveat as ISSUE-006 re: the now-stale `xfail(strict=True)` test.

### ISSUE-008: `TaskManager.update_task` doesn't persist changes to disk
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** `update_task` now calls `self.todo.save()` right after `self[index] = new_task`. Confirmed by direct repro: after `update_task(old, new)`, reopening a fresh `TaskManager` on the same path shows `new` and not `old`. Same xfail-test caveat as above.

### ISSUE-009: `TaskManager.delete_task` doesn't persist changes to disk
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** `delete_task` now calls `self.todo.save()` right after `del self[index]`. Confirmed by direct repro: after `delete_task(task)`, reopening a fresh `TaskManager` on the same path no longer shows the deleted task. Same xfail-test caveat as above.

### ISSUE-012: `task_to_dict` raises `KeyError` for any task missing a `due` or `rec` attribute
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** `task_to_dict()` now uses `task.attributes.get("due", None)` / `task.attributes.get("rec", None)` instead of indexing the dict directly. Confirmed by direct repro: `task_to_dict(create_task(description="water plants"))` (no `due`, no `rec`) now returns cleanly with both fields as `None` instead of raising `KeyError`.

### ISSUE-005: `create_task`'s recurrence attribute doesn't match the todo.txt `rec:` convention
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** `create_task` (in `src/lalonde/tasks_api/task.py`) now calls `task.add_attribute("rec", recurrance)` — the attribute key on the wire is `rec`, matching `docs/todotxt_spec.md` and what `task_to_dict()` reads back.

### ISSUE-001: `TaskManager.update_task` raises `AttributeError`
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** Superseded by a rewrite of `update_task`, which now goes through `find_task()` + `self[index] = new_task` (using `__setitem__`, which correctly operates on `self.todo.tasks`) instead of calling `.index()` directly on the `TodoTxt` wrapper. Confirmed by direct repro: `update_task(existing_task, new_task)` no longer raises and returns `True`/updates in-memory as expected. (The in-place update still isn't saved to disk — that's now tracked separately as ISSUE-008.)

### ISSUE-002: `TaskManager.delete_task` raises `AttributeError`
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** Same rewrite as ISSUE-001 — `delete_task` now goes through `find_task()` + `del self[index]` (using `__delitem__`, which operates on `self.todo.tasks`) instead of calling `.pop()` directly on the `TodoTxt` wrapper. Confirmed by direct repro: `delete_task(existing_task)` no longer raises and returns `True`/removes it in-memory as expected. (Still not saved to disk — tracked separately as ISSUE-009.)

### ISSUE-003: `docs/buildozer.md` states a false import-path warning
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** doc-drift
- **Note:** The doc now states (line 7) "My solution was to move it under `src/lalonde/tasks_api/tasks_api.py`," which matches the actual current location. The old warning is kept as quoted context for *why* the move happened rather than as a live claim about the present layout, so the doc as a whole no longer asserts anything false.

### ISSUE-004: `test_TaskManager_tasks_is_list` currently fails
- **Status:** resolved
- **Resolved:** 2026-07-29
- **Kind:** bug
- **Note:** Superseded — the test suite was rewritten (`tests/test_tasks_api.py` now only covers `create_task`/`compare_tasks_for_equality`; persistence behavior moved to `tests/test_TaskManager.py`). Neither `test_TaskManager_tasks_is_list` nor the `get_tasks()`/`@auto_refresh` method it exercised exist anymore (confirmed via repo-wide grep and reading current `tasks_api.py`), so the original failure mode is moot.

_(earlier entries resolved only once the actual fix, or actual doc correction, is confirmed in the code/docs, not when the underlying cause becomes moot)_
