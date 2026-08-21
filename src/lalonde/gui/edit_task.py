import copy
import datetime
from pathlib import Path

from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import OneLineAvatarListItem, OneLineIconListItem, OneLineListItem
from kivymd.uix.pickers import MDDatePicker

from datetime_helper.helper import date_to_str, str_to_date, today
from tasks.task import TaskData, data_to_task

Builder.load_file(str(Path(__file__).with_name("edit_task.kv")))

def safe_string(arg: any) -> str:
    """Returns "" if the arg is not a string, otherwise returns the arg"""
    if isinstance(arg, str):
        return arg
    return ""

class DateField(OneLineIconListItem):
    field_name = StringProperty("")  # Used to setattr in EditTaskScreen
    screen = ObjectProperty(None)
    label_text = StringProperty("")  # Display text
    value_text = StringProperty("")  # the date data... yes we're still encoding it as a string until i refactor it

    def on_screen(self, *args) -> None:
        self._connect()

    def on_field_name(self, *args) -> None:
        self._connect()

    def _connect(self):
        if self.screen and self.field_name:
            self.screen.bind(**{self.field_name: self.setter("value_text")})
            self.value_text = getattr(self.screen, self.field_name)

    def show_date_picker(self, field_name: str) -> None:
        # IMHO this should be in DateField somehow
        picker = MDDatePicker()
        picker.bind(
            on_save=lambda instance, value, date_range: self.screen.on_date_picked(field_name, value),
        )
        picker.open()

class DescriptionField(OneLineListItem):
    screen = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        self.ids.description_input.text = self.screen.description
        self.ids.description_input.bind(
            text=self.on_description_changed
        )

    def on_description_changed(self, instance, value):
        self.screen.description = value

class EditTaskScreen(Screen):

    # --- Data ----------------------------------------------------------------

    task_manager = ObjectProperty(None)
    task_data = ObjectProperty(None)
    mode = OptionProperty("create", options=["create", "edit"])

    # --- Form Field Content --------------------------------------------------

    description = StringProperty("")
    is_completed = BooleanProperty(False)
    priority = StringProperty("")
    completion_date = StringProperty("")
    creation_date = StringProperty("")   # Do not expose in create mode
    project_tags = StringProperty("")
    context_tags = StringProperty("")
    due = StringProperty("")
    rec = StringProperty("")

    # --- Initialization ------------------------------------------------------

    def open(self, mode: str, task_data: TaskData | None = None):
        self.mode = mode
        match self.mode:
            case "create":
                self._open_in_create_mode()
            case "edit":
                self._open_in_edit_mode(task_data)

    def _open_in_create_mode(self):
        # --- Setup Data --------------
        self.task_data = TaskData(description="")
        self._set_fields(self.task_data)
        self.manager.current = self.name

        # --- Build Form --------------
        container = self._get_container()
        self._clear_widgets()
        container.add_widget(DescriptionField(screen=self))
        container.add_widget(DateField(
            screen=self,
            field_name="due",
            label_text="Due Date"
        ))

    def _open_in_edit_mode(self, task_data: TaskData):
        # --- Setup Data --------------
        if not isinstance(task_data, TaskData):
            raise TypeError(f"edit mode requires taskdata to edit, got {task_data.__class__}")
        self.task_data = task_data
        self._set_fields(self.task_data)
        self.manager.current = self.name

        # --- Build Form --------------
        container = self._get_container()
        self._clear_widgets()
        container.add_widget(DescriptionField(screen=self))
        container.add_widget(DateField(
            screen=self,
            field_name="due",
            label_text="Due Date"
        ))

    # --- Save ----------------------------------------------------------------

    def save(self):
        if self.description == "":
            return # or better yet, Toast(text="Nothing to save!")

        match self.mode:
            case "create":
                self._save_in_create_mode()
            case "edit":
                self._save_in_edit_mode()

        self.back()

    def _save_in_create_mode(self):
        self.creation_date = today()
        self.manager.add_task(data_to_task(
            self._create_task_data_from_fields()
        ))

    def _save_in_edit_mode(self):
        old_task_data = copy.deepcopy(self.task_data)
        self.task_data = self._create_task_data_from_fields()
        self.task_manager.update_task(
            data_to_task(old_task_data),
            data_to_task(self.task_data)
        )

    # --- Delete --------------------------------------------------------------

    def delete(self):
        match self.mode:
            case "create":
                self._delete_in_create_mode()
            case "edit":
                self._delete_in_edit_mode()

        self.back()

    def _delete_in_create_mode(self):
        self.back()

    def _delete_in_edit_mode(self):
        del self.task_manager[
            self.task_manager.find_task(
                data_to_task(self.task_data)
            )
        ]
        self.back()

    # --- Helpers -------------------------------------------------------------

    def back(self):
        self._clear_widgets()
        self._clear_fields()
        self.manager.current = "main_screen"

    def _get_container(self):
        return self.ids.edit_task_options_container

    def _clear_widgets(self):
        self._get_container().clear_widgets()

    # --- Field Manipulation ----------

    def on_date_picked(self, field_name: str, value: datetime.date) -> None:
        setattr(self, field_name, date_to_str(value))

    def open_in_mode(self, mode: str, task_data: TaskData | None = None) -> None:
        self.mode = mode
        if mode == "create":
            self._create_mode()
        elif mode == "edit":
            self._edit_mode(task_data)
        else: # this should never fire due to the nature of OptionProperty
            raise ValueError(f"{type(self).__name__} must recieve mode 'edit' or 'create', got: '{mode}'")

    def _create_mode(self):
        self.task_data = TaskData(description="")
        self.manager.current = self.name
        container = self.ids.edit_task_options_container # antipattern, how are you actually supposed to query props?
        container.clear_widgets()
        container.add_widget(DescriptionField(screen=self))
        container.add_widget(DateField(
            screen=self,
            field_name="due",
            label_text="Due Date"
        ))

    def _edit_mode(self, task_data: TaskData):
        self.task_data = task_data
        self.manager.current = self.name


    def on_date_picked(self, field_name: str, value: datetime.date) -> None:
        setattr(self, field_name, date_to_str(value))

    def _set_fields(self, task_data: TaskData | None = None) -> None:
        if task_data == None:
            task_data = TaskData(description="")

        self.description = task_data.description # because a description is a requirement for all tasks, it does not need `safe_string()` insurance
        self.is_completed = task_data.is_completed
        self.priority = safe_string(task_data.priority)
        self.completion_date = date_to_str(task_data.completion_date)
        self.creation_date = date_to_str(task_data.creation_date)
        self.project_tags = safe_string(task_data.project_tags)
        self.context_tags = safe_string(task_data.context_tags)
        self.due = date_to_str(task_data.due)
        self.rec = safe_string(task_data.rec)

    def _clear_fields(self):
        self._set_fields()

    def _create_task_data_from_fields(self) -> TaskData:
        return TaskData(
            description=self.description,
            is_completed=self.is_completed,
            priority=self.priority,
            completion_date=str_to_date(self.completion_date),
            creation_date=str_to_date(self.creation_date),
            project_tags=self.project_tags.split(" "),
            context_tags=self.context_tags.split(" "),
            due=str_to_date(self.due),
            rec=self.rec
        )
