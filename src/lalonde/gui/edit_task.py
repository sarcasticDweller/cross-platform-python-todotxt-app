import copy
import datetime
from pathlib import Path

from kivy.lang import Builder
from kivy.properties import ObjectProperty, OptionProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.pickers import MDDatePicker

from datetime_helper.datetime_helper import date_to_str, str_to_date
from tasks_api.task import TaskData, data_to_task

Builder.load_file(str(Path(__file__).with_name("edit_task.kv")))




def safe_string(arg: any) -> str:
    """Returns "" if the arg is not a string, otherwise returns the arg"""
    if isinstance(arg, str):
        return arg
    return ""

class EditTaskScreen(Screen):
    task_manager = ObjectProperty(None)
    task_data = ObjectProperty(None)

    mode = OptionProperty("create", options=["create", "edit"])

    # Form Fields
    description = StringProperty("")
    is_completed = StringProperty("")    # its a boolean, but we enter it as text for now
    priority = StringProperty("")
    completion_date = StringProperty("") # its a date, but we enter it as text for now
    creation_date = StringProperty("")   # its a date, ...
    project_tags = StringProperty("")
    context_tags = StringProperty("")
    due = StringProperty("")             # its a date, ...
    rec = StringProperty("")

    def on_pre_enter(self) -> None:
        self.clear()

        if self.mode == "create":
            return

        self._set_fields(self.task_data)

    def open_in_mode(self, mode: str, task_data: TaskData | None = None) -> None:
        self.mode = mode
        if task_data == None:
            task_data = TaskData(description="")
        self.task_data = task_data
        self.manager.current = self.name

    def show_date_picker(self, field_name: str) -> None:
        picker = MDDatePicker()
        picker.bind(
            on_save=lambda instance, value, date_range: self._on_date_picked(field_name, value),
        )
        picker.open()

    def _on_date_picked(self, field_name: str, value: datetime.date) -> None:
        setattr(self, field_name, date_to_str(value))

    def _set_fields(self, task_data: TaskData | None = None) -> None:
        if task_data == None:
            task_data = TaskData(description="")

        self.description= task_data.description # because a description is a requirement for all tasks, it does not need `safe_string()` insurance
        self.is_completed= safe_string(str(task_data.is_completed))
        self.priority = safe_string(task_data.priority)
        self.completion_date = date_to_str(task_data.completion_date)
        self.creation_date = date_to_str(task_data.creation_date)
        self.project_tags = safe_string(task_data.project_tags)
        self.context_tags = safe_string(task_data.context_tags)
        self.due = date_to_str(task_data.due)
        self.rec = safe_string(task_data.rec)

    def on_save(self) -> None:
        description = self.description
        if description == "":
            return

        old_task_data = copy.deepcopy(self.task_data)
        self.task_data = TaskData(
            description=description,
            is_completed=self.is_completed,
            priority=self.priority,
            completion_date=str_to_date(self.completion_date),
            creation_date=str_to_date(self.creation_date),
            project_tags=self.project_tags.split(" "),
            context_tags=self.context_tags.split(" "),
            due=str_to_date(self.due),
            rec=self.rec
        )

        if self.mode == "create":
            self.task_manager.add_task(data_to_task(self.task_data))
        if self.mode == "edit":
            self.task_manager.update_task(
                old_task=data_to_task(old_task_data),
                new_task=data_to_task(self.task_data)
            )
        self.clear()
        self.on_back()

    def on_back(self) -> None:
        self.manager.current = "main_screen"

    def on_delete(self) -> None:
        del self.task_manager[self.task_manager.find_task(data_to_task(self.task_data))]
        self.on_back()

    def clear(self) -> None:
        self._set_fields()

class DateField(BoxLayout):
    field_name = StringProperty("")
    screen = ObjectProperty(None)
    name_text = StringProperty("")

    def on_screen(self, *args) -> None:
        self._connect()

    def on_field_name(self, *args) -> None:
        self._connect()

    def _connect(self):
        if self.screen and self.field_name:
            self.screen.bind(**{self.field_name: self.setter("name_text")})
            self.name_text = getattr(self.screen, self.field_name)
