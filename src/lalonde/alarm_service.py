# """Alarm service entrypoint.
#
# Not a module -- p4a executes this as a script in a brand-new Python interpreter,
# in its own OS process (`android:process=":service_alarm"`), every time the service
# is started. Nothing carries over between invocations, and it MUST exit promptly:
# p4a silently drops a start request while a previous invocation's thread is alive.
# """
#
# import os
# import sys
# import traceback
#
# # p4a pipes stdout to logcat, and Python block-buffers a non-tty pipe. This process lives well under a second, so small prints can be swallowed at teardown and never reach logcat. Force line buffering before anything else runs.
# try:
#     sys.stdout.reconfigure(line_buffering=True)
#     sys.stderr.reconfigure(line_buffering=True)
# except Exception:  # noqa: BLE001, S110 - diagnostics only; never let this kill the service
#     pass
#
# try:
#     # Inside the try on purpose: an ImportError here is exactly the kind of failure
#     # that otherwise vanishes.
#     from alarms.android_alarm import create_notification_channel, post_notification
#
#     payload = os.environ.get("PYTHON_SERVICE_ARGUMENT", "")
#     print(f"[alarm-service] started, payload={payload!r}", flush=True)
#
#     create_notification_channel()
#     print("[alarm-service] channel created", flush=True)
#
#     post_notification(title="Lalonde Test Notif", text=f"payload: {payload}")
#     print("[alarm-service] notification posted", flush=True)
#
#     print("[alarm-service] done", flush=True)
#
# except Exception:  # noqa BLE001: i want a catch-all
#     print("[alarm-service] FAILED", flush=True)
#     traceback.print_exc(file=sys.stdout)
#     sys.stdout.flush()

import os
from pathlib import Path

import datetime_helper as dh
from alarms import get_next_alarm, get_tasks_with_alarm_at_time
from alarms.android_alarm import (
    NOTIFICATION_ID,
    create_notification_channel,
    get_app_files_dir,
    post_notification,
    schedule_alarm,
)
from files import Settings
from tasks import TaskManager

payload = os.environ.get("PYTHON_SERVICE_ARGUMENT", "") # mysterious android payload
alarm_time = dh.str_to_datetime(payload) if payload != "boot" else None
# technically the payload CAN be something that isn't an ISO datetime or "boot", but that's not mission-critical ATM
settings = Settings(get_app_files_dir())
todo_file_path = str(Path(settings["todo_dir"]) / settings["todo_file_name"])
task_manager = TaskManager(todo_file_path)

create_notification_channel()

for i, task in enumerate(
    get_tasks_with_alarm_at_time(task_manager, alarm_time)
):
    post_notification(
        title="Lalonde", 
        text=task.bare_description(),
        notification_id=NOTIFICATION_ID + i
    )

next_alarm = get_next_alarm(
    task_manager,
    dh.today_datetime()
)
if next_alarm:
    schedule_alarm(
        when=next_alarm,
        payload=dh.date_to_str(next_alarm) # close the mysterious android payload loop
    )