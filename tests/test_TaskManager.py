import pytest
from tasks_api.task import create_task
from tasks_api.task_manager import TaskManager


@pytest.fixture
def manager(tmp_path):
    todo_file = tmp_path / "todo.txt"
    todo_file.touch()
    return TaskManager(str(todo_file))


# __init__ / refresh

def test_TaskManager_init_loads_existing_empty_file(manager):
    assert manager.todo.tasks == []

def test_TaskManager_init_nonexistent_file_raises(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        TaskManager(str(missing))

def test_TaskManager_refresh_picks_up_external_changes(manager):
    with open(manager.path_to_todo, "a") as f:
        f.write("external task\n")
    manager.refresh()
    assert any(t.description == "external task" for t in manager.todo.tasks)


# add_task

def test_TaskManager_add_task_appears_in_manager(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    assert task in manager

def test_TaskManager_add_task_persists_to_disk(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    reopened = TaskManager(manager.path_to_todo)
    assert task in reopened


# find_task

def test_TaskManager_find_task_returns_index_when_present(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    assert manager.find_task(task) == 0

def test_TaskManager_find_task_returns_none_when_absent(manager):
    task = create_task("buy milk")
    assert manager.find_task(task) is None


# __contains__

def test_TaskManager_contains_true_when_present(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    assert task in manager

def test_TaskManager_contains_false_when_absent(manager):
    task = create_task("buy milk")
    assert task not in manager


# __getitem__ / __setitem__ / __delitem__

def test_TaskManager_getitem_returns_task_at_index(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    assert manager[0].description == "buy milk"

def test_TaskManager_setitem_overwrites_task_at_index(manager):
    old_task = create_task("buy milk")
    manager.add_task(old_task)
    new_task = create_task("buy oat milk")
    manager[0] = new_task
    assert manager[0].description == "buy oat milk"

def test_TaskManager_delitem_removes_task_at_index(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    del manager[0]
    assert task not in manager


# update_task

def test_TaskManager_update_task_replaces_in_memory_when_present(manager):
    old_task = create_task("buy milk")
    manager.add_task(old_task)
    new_task = create_task("buy oat milk")
    assert manager.update_task(old_task, new_task) is True
    assert new_task in manager
    assert old_task not in manager

def test_TaskManager_update_task_returns_false_when_absent(manager):
    old_task = create_task("buy milk")
    new_task = create_task("buy oat milk")
    assert manager.update_task(old_task, new_task) is False

def test_TaskManager_update_task_persists_to_disk(manager):
    old_task = create_task("buy milk")
    manager.add_task(old_task)
    new_task = create_task("buy oat milk")
    manager.update_task(old_task, new_task)
    reopened = TaskManager(manager.path_to_todo)
    assert new_task in reopened
    assert old_task not in reopened


# delete_task

def test_TaskManager_delete_task_removes_in_memory_when_present(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    assert manager.delete_task(task) is True
    assert task not in manager

def test_TaskManager_delete_task_returns_false_when_absent(manager):
    task = create_task("buy milk")
    assert manager.delete_task(task) is False

def test_TaskManager_delete_task_persists_to_disk(manager):
    task = create_task("buy milk")
    manager.add_task(task)
    manager.delete_task(task)
    reopened = TaskManager(manager.path_to_todo)
    assert task not in reopened


# __iter__

def test_TaskManager_iter_yields_tasks_in_order(manager):
    first = create_task("buy milk")
    second = create_task("walk dog")
    manager.add_task(first)
    manager.add_task(second)
    assert [t.description for t in manager] == ["buy milk", "walk dog"]


# __repr__

def test_TaskManager_repr_returns_a_string(manager):
    manager.add_task(create_task("buy milk"))
    assert isinstance(repr(manager), str)
