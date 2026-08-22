try:
    from alarms import android_alarm  # noqa: F401
    # module crashes on non-android systems
except ModuleNotFoundError:
    pass
from alarms.scheduler import get_next_alarm, get_tasks_with_alarm_at_time

__all__ = [
    "get_next_alarm",
    "get_tasks_with_alarm_at_time"
]
