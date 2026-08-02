import functools

import pytodotxt

from tasks_api.task import compare_tasks_for_equality


def auto_refresh(func):
    """
    Only for internal use with TaskManager (see below).

    Really, this should be done with a watchdog instead of refreshing every cycle. But wtv.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.refresh()
        return func(self, *args, **kwargs)
    return wrapper

class TaskManager:
    """A dirty pytodotxt.todo"""
    todo: pytodotxt.TodoTxt | None = None
    def __init__(self, path_to_todo: str | None = None): # maybe ill want to add an archive later down the line, who knows
        self.path_to_todo = path_to_todo # stow this for `refresh()`
        self.todo = pytodotxt.TodoTxt(self.path_to_todo)
        self.todo.parse()

    def refresh(self) -> None:
        """Reload task manager based on contents of todo file"""
        self.todo = pytodotxt.TodoTxt(self.path_to_todo)
        self.todo.parse()

    @auto_refresh
    def __repr__(self):
        return repr(self.todo.tasks)

    def __iter__(self):
        return iter(self.todo.tasks)

    def __contains__(self, task: pytodotxt.Task) -> bool:
        """We do this wacky check because task objects are ephemeral. What matters is the content."""
        return any(compare_tasks_for_equality(task, t) for t in self.todo.tasks)

    def __getitem__(self, index: int) -> pytodotxt.Task:
        return self.todo.tasks[index]

    def __setitem__(self, index: int, task: pytodotxt.Task) -> None:
        self.todo.tasks[index] = task

    def __delitem__(self, index: int) -> None:
        del self.todo.tasks[index]
        self.todo.save()


    @auto_refresh
    def add_task(self, task: pytodotxt.Task) -> None:    # Crud: Create
        self.todo.add(task)
        self.todo.save() # lets see if this implicitly calls `self.todo.filename`!

    """
    Design consideration:

    `update_task` and `delete_task` both return their sucess as a true/false. What information does that `False` actually transmit? IDK, but I'm sure I'll find out when it bites me.
    """

    def find_task(self, lookup_task: pytodotxt.Task) -> int | None:
        """Returns the index of a task if its present in self, otherwise none"""
        for i, task in enumerate(self.todo.tasks):
            if compare_tasks_for_equality(lookup_task, task):
                return i
        return None

    @auto_refresh
    def update_task(                                     # crUd: Update
        self,
        old_task: pytodotxt.Task,
        new_task: pytodotxt.Task
    ) -> bool:
        """Replaces overwritten values in-line. Note: will not preserve any old values."""
        index = self.find_task(old_task)
        if index is None:
            return False

        self[index] = new_task
        self.todo.save()
        return True

    @auto_refresh
    def delete_task(self, task: pytodotxt.Task) -> bool: # cruD: Destroy
        """If the passed task is present in the manager, it'll delete it"""
        index = self.find_task(task)
        if index is None:
            return False

        del self[index]
        self.todo.save()
        return True
