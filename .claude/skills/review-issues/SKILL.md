---
name: review-issues
description: Review the Lalonde codebase for defects by diffing docs/issues.md against the current state of the code, marking resolved issues and logging newly found ones. Use when the user asks to check the codebase for problems, review for bugs/issues, or reconcile the issues tracker.
---

# Review Issues

This project is in an early "caffeine and spite" phase — no GitHub Issues yet. Instead, `docs/issues.md` is a hand-maintained log of concrete defects, and this skill is how it gets kept in sync with reality. Think of it as an AI-assisted linter pass that catches things `ruff`/`pyright` structurally can't: wrong assumptions about a library's API, logic errors, silently-broken error handling, footguns.

**Scope reminder:** the user writes all the code themselves ([[feedback_conceptual_not_code]] if that memory exists). This skill only investigates and updates `docs/issues.md` — never edit source files as part of this skill, even to "fix while you're in there."

**Don't duplicate `docs/progress.md`.** That file tracks unbuilt features/facets. This skill only cares about defects in code that already exists — not "X isn't implemented yet."

## Steps

1. **Read `docs/issues.md` in full.** Note every entry under "Open" (and skim "Resolved" for context, but don't re-verify those).

2. **Re-verify each open issue against the current code:**
   - Read the referenced file/location. If the surrounding code has changed enough that the line reference is stale, find the equivalent spot.
   - If the issue describes a bug you can cheaply repro (a quick `uv run python3 -c "..."` snippet, similar to how ISSUE-001/002 were originally confirmed by actually calling `TaskManager.update_task`/`delete_task` and observing the `AttributeError`), do that rather than eyeballing it — this file's whole value is that entries are empirically confirmed, not guessed.
   - Decide: still open (unchanged), resolved, or superseded (issue is moot because surrounding code changed shape entirely).
   - For `Kind: doc-drift` entries specifically: resolve only when the doc text itself now says something true. If the underlying code concern the doc was warning about became moot, but the doc still asserts the old (now false) claim, the issue stays **open** — inaccurate documentation is treated as a real, present defect in its own right, not a lesser or self-resolving one.

3. **Scan for new issues.** Focus on `src/lalonde/` (and any other app code, not `.venv`/`.buildozer`/generated files). Prioritize:
   - Places where code assumes a method/attribute exists on a third-party object (like `pytodotxt.TodoTxt`) without checking the library source
   - Silent failure paths (broad `except` blocks, `try/except` that swallow the wrong exception type)
   - Mismatches between what a function's docstring/type hints claim and what it actually does
   - Anything that would break if exercised, not stylistic nitpicks (leave those to `ruff`)

   When something looks wrong, verify it the same way — read the actual library/stdlib source or run a small repro — before logging it. Don't log a suspicion as a confirmed issue.

4. **Update `docs/issues.md`:**
   - Move resolved entries to the "Resolved" section, keeping their original ID, adding a `**Resolved:** <date>` line and a one-line note on what changed.
   - Add new entries under "Open" with the next available `ISSUE-NNN` ID (don't renumber existing ones), following the existing field structure (Status, Kind, Location, Noted, Details, Direction).
   - Leave everything else in the file untouched.

5. **Report to the user in chat, in this order:**
   - One line of counts: newly resolved / still open / newly found this pass.
   - A **BRIEF plain-English action list**: one line per issue currently open (all of them, not just this pass's new ones) — phrased as "what's wrong" in plain terms a non-technical read can act on, not a technical restatement of the doc entry. E.g. "Editing an existing task crashes the app" rather than "`update_task` raises `AttributeError` on `TodoTxt.index`." This is the part meant to double as the user's action list, so keep each line to a single sentence and skip anything that isn't currently open.
   - Don't dump the whole file, full repro steps, or Details/Direction fields back into chat — that detail lives in the doc for when they're ready to act on a specific item.
