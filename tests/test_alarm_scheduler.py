import pytest

from alarms.scheduler import get_next_alarm, get_tasks_with_alarm_at_time
from datetime_helper import get_datetime
from tasks.manager import TaskManager
from tasks.task import create_task

# The scheduler only ever compares alarms against a caller-supplied `now`, so every
# test pins both to fixed literals -- no clock mocking, same convention as test_tasks.py.
NOW = get_datetime(2026, 8, 21, 12, 0, 0)

PAST = get_datetime(2026, 8, 21, 9, 0, 0)
SOON = get_datetime(2026, 8, 21, 14, 0, 0)
LATER = get_datetime(2026, 8, 21, 18, 0, 0)


@pytest.fixture
def manager(tmp_path):
    todo_file = tmp_path / "todo.txt"
    todo_file.touch()
    return TaskManager(str(todo_file))


def add(manager, description, **kwargs):
    """Adds a task to the manager and hands it back, so tests read as one line per task."""
    task = create_task(description, **kwargs)
    manager.add_task(task)
    return task


# get_next_alarm

def test_get_next_alarm_returns_none_when_there_are_no_tasks(manager):
    assert get_next_alarm(manager, NOW) is None

def test_get_next_alarm_returns_none_when_no_task_has_an_alarm(manager):
    add(manager, "no alarm here")
    assert get_next_alarm(manager, NOW) is None

def test_get_next_alarm_returns_the_only_future_alarm(manager):
    add(manager, "soon", alarm=SOON)
    assert get_next_alarm(manager, NOW) == SOON

def test_get_next_alarm_returns_the_earliest_of_several(manager):
    add(manager, "later", alarm=LATER)
    add(manager, "soon", alarm=SOON)
    assert get_next_alarm(manager, NOW) == SOON

def test_get_next_alarm_ignores_alarms_in_the_past(manager):
    add(manager, "past", alarm=PAST)
    add(manager, "soon", alarm=SOON)
    assert get_next_alarm(manager, NOW) == SOON

def test_get_next_alarm_returns_none_when_every_alarm_is_past(manager):
    add(manager, "past", alarm=PAST)
    assert get_next_alarm(manager, NOW) is None

def test_get_next_alarm_excludes_an_alarm_exactly_at_now(manager):
    # Strictly-future: the service passes its own wake time as `now`, so an alarm
    # equal to `now` is the one that just fired. Including it would re-register the
    # same alarm forever.
    add(manager, "right now", alarm=NOW)
    add(manager, "later", alarm=LATER)
    assert get_next_alarm(manager, NOW) == LATER

def test_get_next_alarm_ignores_completed_tasks(manager):
    add(manager, "done", is_completed=True, alarm=SOON)
    add(manager, "later", alarm=LATER)
    assert get_next_alarm(manager, NOW) == LATER

def test_get_next_alarm_returns_none_when_every_alarmed_task_is_completed(manager):
    add(manager, "done", is_completed=True, alarm=SOON)
    assert get_next_alarm(manager, NOW) is None

def test_get_next_alarm_survives_a_mix_of_alarmed_and_unalarmed_tasks(manager):
    # The normal state of a todo.txt: most tasks have no alarm at all.
    add(manager, "plain one")
    add(manager, "later", alarm=LATER)
    add(manager, "plain two")
    add(manager, "soon", alarm=SOON)
    add(manager, "plain three")
    assert get_next_alarm(manager, NOW) == SOON


# get_tasks_with_alarm_at_time

def test_get_tasks_with_alarm_at_time_returns_empty_when_nothing_matches(manager):
    add(manager, "later", alarm=LATER)
    assert get_tasks_with_alarm_at_time(manager, SOON) == []

def test_get_tasks_with_alarm_at_time_returns_the_matching_task(manager):
    add(manager, "soon", alarm=SOON)
    add(manager, "later", alarm=LATER)
    found = get_tasks_with_alarm_at_time(manager, SOON)
    assert [task.bare_description() for task in found] == ["soon"]

def test_get_tasks_with_alarm_at_time_returns_every_task_sharing_that_time(manager):
    # Two tasks can share an alarm; returning only one would silently drop a reminder.
    add(manager, "first", alarm=SOON)
    add(manager, "second", alarm=SOON)
    found = get_tasks_with_alarm_at_time(manager, SOON)
    assert [task.bare_description() for task in found] == ["first", "second"]

def test_get_tasks_with_alarm_at_time_ignores_completed_tasks(manager):
    add(manager, "done", is_completed=True, alarm=SOON)
    add(manager, "pending", alarm=SOON)
    found = get_tasks_with_alarm_at_time(manager, SOON)
    assert [task.bare_description() for task in found] == ["pending"]

def test_get_tasks_with_alarm_at_time_ignores_tasks_without_an_alarm(manager):
    add(manager, "no alarm here")
    assert get_tasks_with_alarm_at_time(manager, SOON) == []


# the handoff between the two, which is what phase D actually relies on

def test_next_alarm_feeds_tasks_with_alarm_at_time(manager):
    # get_next_alarm's return value becomes the PendingIntent payload, and the alarm
    # service passes it straight back to get_tasks_with_alarm_at_time. If these two
    # ever disagree about what counts as an alarm, the service wakes to an empty list.
    add(manager, "done", is_completed=True, alarm=PAST)
    add(manager, "plain")
    add(manager, "first", alarm=SOON)
    add(manager, "second", alarm=SOON)
    add(manager, "later", alarm=LATER)

    next_alarm = get_next_alarm(manager, NOW)
    found = get_tasks_with_alarm_at_time(manager, next_alarm)

    assert next_alarm == SOON
    assert [task.bare_description() for task in found] == ["first", "second"]

def test_alarm_survives_the_round_trip_through_disk(manager):
    # The service reads a file the app wrote, in a different process, so the alarm has
    # to come back off disk identically or the == match in get_tasks_with_alarm_at_time
    # silently finds nothing.
    add(manager, "soon", alarm=SOON)
    manager.refresh()
    assert get_next_alarm(manager, NOW) == SOON
