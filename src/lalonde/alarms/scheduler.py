import datetime

import datetime_helper as dh
from tasks import Task, TaskManager, get_keyval_attrib


def _get_alarm_attribute(task: Task) -> datetime.datetime:
    attrib: str = get_keyval_attrib(task, "alarm")
    return dh.str_to_datetime(attrib)

def get_tasks_with_alarm_at_time(
    task_manager: TaskManager,
    datetime_stamp: datetime.datetime
) -> list[Task]:
    return [
        task for task in task_manager
        if _get_alarm_attribute(task) == datetime_stamp
        and not task.is_completed
    ]

def get_next_alarm(
    task_manager: TaskManager,
    now: datetime.datetime
) -> datetime.datetime | None:
    return min(
        (
            alarm for alarm in [
                _get_alarm_attribute(task) 
                for task in task_manager
                if not task.is_completed
            ] if alarm is not None and alarm > now
        ), 
        default=None
    )