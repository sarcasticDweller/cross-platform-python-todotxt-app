# Issues Tracker (AI-reference)

This file exists for the `/review-issues` skill (see `.claude/skills/review-issues/SKILL.md`). It's not a feature backlog — that's `docs/progress.md` — this is a running log of concrete defects found in existing code *and docs*, meant to survive between chat sessions so an AI review can diff "what we knew about" against "what's actually true now." Inaccurate documentation counts as a real issue, not a footnote: docs that confidently state something false are worse than no docs, and get tracked with the same rigor as code bugs.

Each entry keeps a stable ID so it can be referenced/updated across reviews. Don't renumber existing IDs when adding new ones.

## Open

### ISSUE-027: `TaskWidget.on_completed()` always stamps `completion_date`, even when un-completing a task — and `create_task()` has no guard stopping `completion_date` from being set without `is_completed=True` or without a `creation_date`, so the value is silently swallowed on save
- **Status:** open
- **Kind:** bug
- **Location:** `src/lalonde/gui/tasks_view.py`, `TaskWidget.on_completed()` (`self.task.completion_date = datetime.date.today()` runs unconditionally after toggling `is_completed` either direction); `src/lalonde/tasks_api/task.py`'s `create_task()` (no guard rejects `completion_date` when `is_completed` is `False` or when `creation_date` is `None`)
- **Noted:** 2026-08-01
- **Details:** `on_completed()` flips `self.task.is_completed` and then sets `completion_date` to today regardless of the new value — so un-completing a task also stamps a `completion_date`. Separately, `create_task()` has no validation tying `completion_date` to `is_completed`/`creation_date` — and per ISSUE-021/ISSUE-022 (resolved as won't-fix: `create_task()` is intentionally lossy), that won't change — so neither combination ever raises; the value is just dropped at serialization time. Confirmed by direct repro: `create_task(description="foo", is_completed=True, completion_date=datetime.date(2026, 8, 1))` (no `creation_date`, the realistic shape for completing a task that was never stamped with a creation date) serializes to `'x foo'` — `completion_date` silently vanishes even though `is_completed=True` persists correctly. This is reachable from normal use: checking off any task that lacks a `creation_date` (common for todo.txt lines not created through this app) loses its completion date with no error.
- **Direction (not prescriptive):** since `create_task()` won't gain guards for this, the fix has to live in `on_completed()` — only set `completion_date` when the task is newly completed (not on every toggle), and account for the case where the task has no `creation_date` to begin with.

### ISSUE-024: `scripts/compile_android.sh` fails to compile on GitHub Codespaces, cause not yet diagnosed
- **Status:** open
- **Kind:** bug
- **Location:** `scripts/compile_android.sh`
- **Noted:** 2026-07-30
- **Details:** User reports the script does not successfully compile when run in a GitHub Codespace. Error output not yet captured/attached — pending follow-up.
- **Direction (not prescriptive):** capture the actual failure output from a Codespace run and add it here before investigating further.

## Resolved

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
