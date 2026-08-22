# Android alarms: plan, progress, and handoff

Working notes for the `android-alarms` branch. Written for a fresh Claude Code
instance picking this up mid-stream. Companion to the phase plan at
`~/.claude/plans/so-i-ve-implemented-the-lucky-scott.md` (same content, more
prose); this file is the one that gets updated as work lands.

**Last updated:** 2026-08-21, mid phase B.

## Working mode (read this first)

Per `CLAUDE.md`, this is a learning project and the user writes the source.
Claude's role is instructor: explain the concept, point at the relevant code,
show illustrative snippets in chat — do **not** write source files unless asked
directly. Files under `tests/` are the standing exception.

Agreed exceptions so far: Claude wrote `alarms/android_alarm.py` (pyjnius/Java
bridging is boilerplate, not something the user is here to learn) and both test
files. The user has explicitly said they want to write the phase E Java receiver
and p4a hook themselves, with explanation.

The user has also asked twice not to be nagged about test breakage — fix it when
asked, don't keep raising it.

## The goal

A **high-importance notification that arrives on time, every time.** Explicitly
*not* a full-screen ringing alarm UI.

That's also the only option policy-wise: `USE_FULL_SCREEN_INTENT` (API 34+) and
`USE_EXACT_ALARM` (33+) are both restricted by Play policy to apps whose *core
function* is alarms or calendars. A to-do app declaring either gets rejected on
review. The workaround is a notification channel whose audio uses `USAGE_ALARM`,
which routes to the alarm volume stream — audible on vibrate, survives most Do
Not Disturb configs, no restricted permission needed.

## Decisions already made — don't relitigate these

- **Android-only, no desktop stub.** Desktop gets zero alarm behavior, not even a
  logged no-op.
- **A separate `alarm:` attribute, not an extension of `due:`.** `due:` stays a
  plain date so other todo.txt tools keep parsing the file. Unknown `key:value`
  pairs pass through untouched in every todo.txt implementation.
- **Naive local wall-clock time.** `alarm:YYYY-MM-DDTHH:MM:SS`, parsed with bare
  `fromisoformat`. A timezone offset in the string parses into an aware datetime
  the rest of the system doesn't expect. Known, accepted gap — the user has
  explicitly deferred it ("data validation is not the objective").
- **One OS alarm registered at a time**, the earliest still in the future. Android
  rate-limits `setExactAndAllowWhileIdle` to once per nine minutes per app while
  dozing, so registering everything up front risks late/out-of-order delivery.
- **The alarm targets a p4a service, not a broadcast receiver.** `services =` in
  `buildozer.spec` generates a real manifest-declared `<service>`; that's what
  lets phases A–D need no Java at all.
- **The service never writes to todo.txt** (through phase D). Keeps the
  cross-process write race and the pytodotxt bug below out of scope.

## Phase status

| Phase | What it delivers | Status |
|---|---|---|
| 0 | `Settings` takes a `Path`; `package.domain` | **done** (domain still `org.test`) |
| A | `alarms/scheduler.py`, pure Python selection logic | **done**, 18 tests green |
| B | Notification posts from Python, app in foreground | **code done, unverified on device** |
| C | p4a service, started by hand | not started |
| D | AlarmManager — fires with app killed, dies on reboot | not started |
| E | Java receiver + manifest hook — survives reboot | not started |

### Where we left off

Phase B's code is written and wired. The user changed `android.ndk_api` 24 → 26,
which invalidated p4a's native build cache (it keys on arch + NDK API level), so
**a full from-source rebuild of every native recipe was in progress** —
python3, kivy, pillow, openssl, sqlite3, libffi, freetype, png, jpeg, pyjnius.
The old `arm64-v8a__ndk_target_24` trees are still on disk alongside the new
`__ndk_target_26` ones. Subsequent builds are incremental again.

**Nothing in phase B has been tested on a physical device yet.** The user does
have a device available. Ask before running any `adb` command against it.

On-device checklist for phase B, in this order:

1. Fresh install → `POST_NOTIFICATIONS` dialog appears on first launch. No dialog
   means it didn't reach the manifest (`aapt dump permissions bin/*.apk`).
2. Ribbon bell button → notification appears.
3. Ringer on vibrate → still audible (proves `USAGE_ALARM` took).
4. Alarm volume slider changes it; notification slider doesn't.

If 2 fails silently, suspect the permission — `notify()` without
`POST_NOTIFICATIONS` on API 33+ is a **silent no-op**, no exception, nothing in
logcat. If 3/4 fail after an earlier build already created the channel, **fully
uninstall** rather than rebuilding over the top: a channel's importance, sound,
and vibration are frozen at first creation and later code changes are ignored.
That's what the `_v1` suffix in the channel id exists to escape.

## What exists now

### `src/lalonde/alarms/` (new package)

- **`scheduler.py`** — pure Python, no Android imports, 100% test coverage.
  - `get_next_alarm(task_manager, now) -> datetime | None` — earliest **strictly
    future** alarm. `>` not `>=` is load-bearing: the service passes its own wake
    time as `now`, so `>=` would re-register the alarm it just fired, forever.
  - `get_tasks_with_alarm_at_time(task_manager, datetime_stamp) -> list[Task]` —
    every non-completed task at exactly that timestamp. Plural matters: two tasks
    can share an alarm.
  - Both skip completed tasks. They must agree on what counts as an alarm — when
    they disagreed during development, the effect was a dead wake-up *and* a
    broken re-arm chain, not just a stale notification.
- **`android_alarm.py`** — pyjnius, Android-only, imports crash on desktop by
  design. `create_notification_channel()` (idempotent, safe every start) and
  `post_notification(title, text)`. Requires **minapi ≥ 26**:
  `NotificationChannel` and the two-arg `Notification.Builder` are both API 26.
- **`__init__.py`** — re-exports the scheduler; guards `android_alarm` behind
  `try/except ModuleNotFoundError`, same pattern as `files/__init__.py`.

⚠️ That guard protects `import alarms` only. `from alarms.android_alarm import x`
reaches past the package straight at the submodule and **will** raise on desktop.
The real protection is an `if platform == "android"` check at each call site.

### Changed outside the package

- `files/settings.py` — `Settings.__init__` now takes a `Path`, not an `MDApp`.
  **This was a prerequisite, not a tidy-up:** the phase C alarm service runs a
  bare interpreter with no `App` instance and could not otherwise find todo.txt.
  The settings key `user_data_dir` was also renamed to `todo_dir` to stop it
  colliding with Kivy's own `user_data_dir`.
- `datetime_helper/` — `today()` split into `today_date()` / `today_datetime()`.
- `tasks/__init__.py` — now re-exports `Task` from pytodotxt, so consumers like
  `scheduler.py` don't import pytodotxt directly.
- `main.py` — `on_start` calls `set_up_notifications()` (platform-guarded,
  requests `POST_NOTIFICATIONS`, creates the channel).
- `gui/main_screen.py` + `.kv` — **temporary** bell button in the top app bar's
  `right_action_items`, calling `on_test_notification()`. Delete both at the end
  of phase B.
- `buildozer.spec` — `android.api = 33`, `minapi = 26`, `ndk_api = 26`,
  `POST_NOTIFICATIONS` added.
- `tests/test_settings.py` rewritten for the new signature;
  `tests/test_alarm_scheduler.py` added. Suite: 81 passing.

**Why `android.api = 33` and not 34:** API 34 enforces
`MissingForegroundServiceTypeException` and wants a `<property>` element *inside*
`<service>` for `specialUse` — unachievable until the phase E manifest hook
exists. Staying at 33 keeps phase C hook-free. Bumping to 34 is a deliberate
later task.

⚠️ **Corollary, learned the hard way:** at `compileSdk 33` you cannot declare
`foregroundServiceType=specialUse` either — that value was added in API 34, so
it's absent from the attribute enum in the API 33 `android.jar` and resource
linking fails with `AAPT: error: 'specialUse' is incompatible with attribute
foregroundServiceType`. The `services =` line therefore ends at `:foreground`
with no type, which is fine because the type isn't enforced below 34. Moving to
API 34 means adding *both* `:foregroundServiceType=specialUse` and the
`<property>` subtype element — i.e. it depends on the phase E hook.

## Known-good facts, verified against this repo's own p4a checkout

These were checked in `.buildozer/`, not assumed from docs or tutorials.

- **`Service{Name}.getDefaultIntent(ctx, icon, title, text, arg)` is public
  static** — `bootstraps/common/build/templates/Service.tmpl.java`. Phase D should
  use it to build the alarm's Intent rather than hand-rolling the nine
  `androidPrivate`/`pythonHome`/`pythonPath`/`serviceEntrypoint`/… extras.
  Then `PendingIntent.getForegroundService(...)`.
- **The service entrypoint path is resolved relative to the app root.**
  `bootstraps/common/build/jni/application/src/start.c` does `chdir(ANDROID_ARGUMENT)`
  (= `getFilesDir()/app`) then `fopen`s the entrypoint relatively. So
  `alarms/service.py` and `./alarm_service.py` both work. It also **requires an
  extension** — it aborts on a filename with no dot.
- **`PythonService.mService` is a public static field** and `PythonService extends
  Service extends ContextWrapper extends Context`, so it *is* a Context.
  `PythonService.java:35`. This is how the service process gets its files dir —
  note Kivy's own `App.user_data_dir` getter uses `PythonActivity.mActivity` and
  **does not use the app name on Android** (`kivy/app.py:852-857`), so the service
  can reach the identical path with no app instance.
- **`before_apk_assemble` is the last hook before gradle**, and it fires after the
  manifest template has been rendered, with cwd set to the dist dir —
  `toolchain.py:1040-1048`. So the manifest to patch in phase E is
  `./src/main/AndroidManifest.xml`.
- **`Permission.POST_NOTIFICATIONS` exists** in this p4a version
  (`recipes/android/src/android/permissions.py:260`).

- **Notification id 1 is taken by the service itself.** The generated
  `ServiceAlarm.getServiceId()` returns `1`, and `PythonService.java:175` does
  `startForeground(getServiceId(), notification)` for its own "Background
  Service" notification. Calling `notify(1, ...)` from the service *replaces*
  that one, and Android cancels it when the service stops — so the alarm
  notification vanishes milliseconds after being posted. `notify()` returns
  cleanly and logcat shows nothing wrong. `NOTIFICATION_ID` is therefore 1001.
  If more p4a services are ever added their ids increment from 1, so keep app
  notification ids well clear of that range.

## Open items

- **`package.domain` is still `org.test`.** Phase D hardcodes
  `org.<domain>.lalonde.ServiceAlarm` in Python; phase E puts the same string in
  Java and in a manifest patch. Pick the real one before it lands in three places.
- **`main_screen.py:on_test_notification` is missing a `return`** after its
  `platform != "android"` print, so it falls through to the Android import and
  crashes on desktop anyway.
- **ISSUE-028** (`project_tags`/`context_tags` are `StringProperty` but `TaskData`
  types them `list[str]`) lives in the same `EditTaskScreen` methods the alarm
  fields were added to. Editing any task strips its tags — relevant because alarm
  testing means repeatedly round-tripping tasks through that screen.
- **`docs/todo.txt`** still says dates should stop being `StringProperty` in
  `edit_task.py`; the alarm work added two more (`alarm_date`, `alarm_time`).

## Deferred deliberately

- Snooze/dismiss notification action buttons — needs extra PendingIntents and a
  file-write path. After "it fires once" works.
- A `setAlarmClock` hard-escalation tier (Doze-exempt, claims the system's "next
  alarm" slot) as an opt-in per task.
- API 34.
- **Writing todo.txt from the service.** Two problems land together the moment
  anything snooze-shaped needs it: the service is a different OS process from the
  app, so there's a real read-modify-write race; and **pytodotxt 3.1.0 drops the
  completion date** from any completed task that has a completion date but no
  creation date (`x 2026-08-01 finished thing`) on re-serialization. A save
  rewrites the whole file, so that silently corrupts *unrelated* tasks. Wants a
  workaround or upstream report first.
- Timezone-aware `alarm:` values.
