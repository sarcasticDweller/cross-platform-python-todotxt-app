"""Alarm service entrypoint.

Not a module -- p4a executes this as a script in a brand-new Python interpreter,
in its own OS process (`android:process=":service_alarm"`), every time the service
is started. Nothing carries over between invocations, and it MUST exit promptly:
p4a silently drops a start request while a previous invocation's thread is alive.
"""

import os
import sys
import traceback

# p4a pipes stdout to logcat, and Python block-buffers a non-tty pipe. This process
# lives well under a second, so small prints can be swallowed at teardown and never
# reach logcat. Force line buffering before anything else runs.
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:  # noqa: BLE001, S110 - diagnostics only; never let this kill the service
    pass

try:
    # Inside the try on purpose: an ImportError here is exactly the kind of failure
    # that otherwise vanishes.
    from alarms.android_alarm import create_notification_channel, post_notification

    payload = os.environ.get("PYTHON_SERVICE_ARGUMENT", "")
    print(f"[alarm-service] started, payload={payload!r}", flush=True)

    create_notification_channel()
    print("[alarm-service] channel created", flush=True)

    post_notification(title="Lalonde Test Notif", text=f"payload: {payload}")
    print("[alarm-service] notification posted", flush=True)

    print("[alarm-service] done", flush=True)

except Exception:  # noqa: BLE001 - catch-all is the point: this is the only reporting path
    # Without this, an exception escaping the entrypoint leaves nothing in logcat but
    # "Python for android ended." -- indistinguishable from a clean run that did nothing.
    print("[alarm-service] FAILED", flush=True)
    traceback.print_exc(file=sys.stdout)
    sys.stdout.flush()
