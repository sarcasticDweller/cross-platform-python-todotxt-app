import datetime

import pytest
from tasks_api.task import (
    TaskData,
    compare_tasks_for_equality,
    create_task,
    data_to_task,
    task_to_data,
)

FILE_PATH = "tmp_todo.txt"

# create_task

def test_create_task_no_artifacts():
    # in an iteration of `create_task`, new tasks would have an `@` even when the input was blank. lets assure that doesnt happen.
    task = create_task(description="foo", project_tags=[""], context_tags=[""])
    assert task.description == "foo" # there would be more to `description` in a more complicated task, but we want to make sure that in a simple one there's nothing.

def test_create_task_adds_project_tags():
    task = create_task(description="foo", project_tags=["home", "work"])
    assert task.projects == ["home", "work"]

def test_create_task_adds_context_tags():
    task = create_task(description="foo", context_tags=["phone"])
    assert task.contexts == ["phone"]

def test_create_task_sets_due_attribute():
    task = create_task(description="foo", due=datetime.date(2026, 8, 1))
    assert task.attributes.get("due") == ["2026-08-01"]

def test_create_task_due_rejects_str():
    with pytest.raises(TypeError):
        create_task(description="foo", due="2026-08-01")

def test_create_task_sets_rec_attribute():
    task = create_task(description="foo", rec="+1w")
    assert task.attributes.get("rec") == ["+1w"]

def test_create_task_sets_priority():
    task = create_task(description="foo", priority="A")
    assert task.priority == "A"

def test_create_task_is_completed_defaults_to_false():
    task = create_task(description="foo")
    assert task.is_completed is False

def test_create_task_is_completed_true_when_set():
    task = create_task(description="foo", is_completed=True)
    assert task.is_completed is True

def test_create_task_completion_date_without_is_completed_raises():
    with pytest.raises(TypeError):
        create_task(description="foo", completion_date="2026-01-01")

def test_create_task_completion_date_with_is_completed_sets_it():
    task = create_task(
        description="foo",
        is_completed=True,
        creation_date=datetime.date(2026, 1, 1),
        completion_date=datetime.date(2026, 1, 2),
    )
    assert task.completion_date == datetime.date(2026, 1, 2)

def test_create_task_completion_date_rejects_str():
    with pytest.raises(TypeError):
        create_task(
            description="foo",
            is_completed=True,
            creation_date=datetime.date(2026, 1, 1),
            completion_date="2026-01-02",
        )

def test_create_task_creation_date_rejects_str():
    with pytest.raises(TypeError):
        create_task(description="foo", creation_date="2026-01-01")

def test_create_task_creation_date_accepts_date_and_serializes():
    task = create_task(description="foo", creation_date=datetime.date(2026, 1, 1))
    str(task)


# task_to_data

def test_task_to_data_bare_task():
    task = create_task(description="foo")
    assert task_to_data(task) == TaskData(
        description="foo",
        is_completed=False,
        priority=None,
        completion_date=None,
        creation_date=None,
        project_tags=[],
        context_tags=[],
        due=None,
        rec=None,
    )

def test_task_to_data_full_task_incomplete_with_priority():
    # priority isn't valid on a completed task (see ISSUE-022), so this covers the incomplete case
    task = create_task(
        description="foo",
        priority="B",
        project_tags=["home"],
        context_tags=["errand"],
    )
    data = task_to_data(task)
    assert data.description == "foo"
    assert data.priority == "B"
    assert data.project_tags == ["home"]
    assert data.context_tags == ["errand"]
    assert data.is_completed is False

def test_task_to_data_full_task_completed_with_dates():
    # deliberately leaves out due/rec -- see test_task_to_data_due_is_plain_string_when_set, ISSUE-016
    # deliberately leaves out priority -- not valid on a completed task, see ISSUE-022
    task = create_task(
        description="foo",
        project_tags=["home"],
        context_tags=["errand"],
        is_completed=True,
        creation_date=datetime.date(2026, 1, 1),
        completion_date=datetime.date(2026, 1, 2),
    )
    data = task_to_data(task)
    assert data.description == "foo"
    assert data.project_tags == ["home"]
    assert data.context_tags == ["errand"]
    assert data.is_completed is True
    assert data.creation_date == datetime.date(2026, 1, 1)
    assert data.completion_date == datetime.date(2026, 1, 2)

def test_task_to_data_due_and_rec_default_to_none():
    task = create_task(description="foo")
    data = task_to_data(task)
    assert data.due is None
    assert data.rec is None

def test_task_to_data_due_is_date_when_set():
    task = create_task(description="foo", due=datetime.date(2026, 8, 1))
    assert task_to_data(task).due == datetime.date(2026, 8, 1)

def test_task_to_data_mutating_project_tags_does_not_affect_original_task():
    task = create_task(description="foo", project_tags=["home"])
    data = task_to_data(task)
    data.project_tags.append("work")
    assert task.projects == ["home"]

def test_task_to_data_mutating_context_tags_does_not_affect_original_task():
    task = create_task(description="foo", context_tags=["phone"])
    data = task_to_data(task)
    data.context_tags.append("errand")
    assert task.contexts == ["phone"]

def test_task_to_data_reassigning_description_does_not_affect_original_task():
    task = create_task(description="foo")
    data = task_to_data(task)
    data.description = "bar"
    assert task.bare_description() == "foo"


# data_to_task

def test_data_to_task_round_trip_bare_task():
    original = create_task(description="foo")
    round_tripped = data_to_task(task_to_data(original))
    assert compare_tasks_for_equality(original, round_tripped)

def test_data_to_task_round_trip_with_project_and_context_tags():
    original = create_task(description="foo", project_tags=["home"], context_tags=["errand"], priority="A")
    round_tripped = data_to_task(task_to_data(original))
    assert compare_tasks_for_equality(original, round_tripped)

def test_data_to_task_round_trip_with_due_and_rec():
    original = create_task(description="foo", due=datetime.date(2026, 8, 1), rec="+1w")
    round_tripped = data_to_task(task_to_data(original))
    assert compare_tasks_for_equality(original, round_tripped)

def test_data_to_task_missing_is_completed_defaults_to_false():
    task = data_to_task(TaskData(description="foo"))
    assert task.is_completed is False

def test_data_to_task_mutating_source_data_after_conversion_does_not_affect_task():
    data = TaskData(description="foo", project_tags=["home"])
    task = data_to_task(data)
    data.project_tags.append("work")
    assert task.projects == ["home"]


# compare_tasks_for_equality

def test_compare_tasks_for_equality_a_equals_a():
    a = create_task("dingus")
    assert compare_tasks_for_equality(a)

def test_compare_tasks_for_equality_a_equals_b():
    a = create_task("dingus")
    b = create_task("dingus")
    assert compare_tasks_for_equality(a, b)

def test_compare_tasks_for_equality_a_notequal_b():
    a = create_task("wingus")
    b = create_task("dingus")
    assert not compare_tasks_for_equality(a, b)

def test_compare_tasks_for_equality_multiple_tasks():
    a = create_task("dingus")
    b = create_task("dingus")
    c = create_task("dingus")
    assert compare_tasks_for_equality(a, b, c)
