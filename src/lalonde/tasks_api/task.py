# Functions explicitly related to tasks.

import datetime
from dataclasses import dataclass, field

import pytodotxt

# pytodotxt doesn't treat `due` as a real date property (since it doesnt even recognize that it exists). for the scope of this project, i want to surface it as a datetime item while encoding it as text (iso format). expect to see extra logic around `due` to this end.

def create_task(
    description: str,
    is_completed: bool = False,
    priority: str | None = None,
    completion_date: datetime.date | None = None,
    creation_date: datetime.date | None = None,
    project_tags: list[str] | None = None,
    context_tags: list[str] | None = None,
    due: datetime.date| None = None,
    rec: str | None = None,
) -> pytodotxt.Task:
    """Helper pytodotxt.Task constructor. Lossy by design: it only checks that its parameters will parse, not that they will be preserved on write. This is by design; data-integrity validation should be done before creating a task object."""
    # lets keep things clean and write things in the same order as the function signature. this tedious file is a pain enough to read as it is

    task = pytodotxt.Task(description)

    task.is_completed = is_completed

    if priority:
        if len(priority) > 1 or not priority.isupper():
            raise ValueError(f"priority expected one upercase letter, got {priority}")
        task.priority = priority

    if completion_date:
        if not isinstance(completion_date, datetime.date):
            raise TypeError(f"completion_date must be a datetime.date, got {type(completion_date).__name__}")
        task.completion_date = completion_date

    if creation_date:
        if not isinstance(creation_date, datetime.date):
            raise TypeError(f"creation_date must be a datetime.date, got {type(creation_date).__name__}")
        task.creation_date = creation_date

    if project_tags:
        for tag in project_tags:
            if not tag:
                continue
            task.add_project(tag)

    if context_tags:
        for tag in context_tags:
            if not tag:
                continue
            task.add_context(tag)

    if due:
        if not isinstance(due, datetime.date):
            # lol, zed claims this code is unreachable.
            raise TypeError(f"due must be a datetime.date, got {type(due).__name__}")
        task.add_attribute("due", due.isoformat())

    if rec:
        task.add_attribute("rec", rec)

    task.parse(str(task))
    return task

@dataclass
class TaskData:
    """Detached, editable copy of a task's fields, for the render/edit layers to play with without touching the real pytodotxt.Task."""
    description: str
    is_completed: bool = False
    priority: str | None = None
    completion_date: datetime.date | None = None
    creation_date: datetime.date | None = None
    project_tags: list[str] = field(default_factory=list)
    context_tags: list[str] = field(default_factory=list)
    due: datetime.date | None = None
    rec: str | None = None

def task_to_data(task: pytodotxt.Task) -> TaskData:
    """Converts a task into a detached TaskData copy of itself."""
    # According to Claude (awful start to any sentence, I know), the values for `due` and `rec` get encoded into a list at some point in pytodotxt's sourcecode. This weird syntax down here ensures that 1. there is always a list with at least one value in it (`None`) and 2. the first value of that list is passed into the respective parameter.
    due_str = task.attributes.get("due", [None])[0]
    rec_str = task.attributes.get("rec", [None])[0]

    return TaskData(
        description=task.bare_description(),
        is_completed=task.is_completed,
        priority=task.priority,
        completion_date=task.completion_date,
        creation_date=task.creation_date,
        project_tags=task.projects,
        context_tags=task.contexts,
        due=datetime.date.fromisoformat(due_str) if due_str else None, # remember that this date is encoded as text in pytodotxt's library
        rec=rec_str
    )

def data_to_task(task_data: TaskData) -> pytodotxt.Task:
    return create_task(
        description=task_data.description,
        is_completed=task_data.is_completed,
        priority=task_data.priority,
        completion_date=task_data.completion_date,
        creation_date=task_data.creation_date,
        project_tags=task_data.project_tags,
        context_tags=task_data.context_tags,
        due=task_data.due,
        rec=task_data.rec,
    )

def compare_tasks_for_equality(first: pytodotxt.Task, *rest: pytodotxt.Task) -> bool:
    """Compares whether 1+ tasks are equal to each other by comparing their strings directly."""
    return all(str(first) == str(task) for task in rest)
