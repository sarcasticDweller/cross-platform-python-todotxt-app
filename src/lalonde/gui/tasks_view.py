from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from datetime_helper.datetime_helper import today
from tasks_api.task import data_to_task, task_to_data

Builder.load_file(str(Path(__file__).with_name("tasks_view.kv")))

class TaskWidget(ButtonBehavior, BoxLayout):
    # This class might want to expose some data that can be used to filter and sort it.

    description = StringProperty("")
    is_completed = BooleanProperty(False)
    task_manager = ObjectProperty(None) # TaskManager
    task_data = ObjectProperty(None)    # TaskData

    def on_kv_post(self, base_widget):
        self.ids.is_completed.bind(active=self.on_completed)

    def on_completed(self, instance, value):
        old_task = data_to_task(self.task_data)
        self.task_data.is_completed = value
        if value and self.task_data.creation_date:
            self.task_data.completion_date = today()

        self.task_manager.update_task(old_task, data_to_task(self.task_data))

    def on_edit(self):
        """Pass self.task_data through to the edit screen to pre-populate fields with it."""
        manager = App.get_running_app().root
        manager.get_screen("edit_task_screen").open_in_mode("edit", self.task_data)

class TaskList(BoxLayout):
    task_manager = ObjectProperty(None)

    def refresh(self) -> None:
        container = self.ids.tasks_container
        container.clear_widgets()
        for task in self.task_manager:
            container.add_widget(TaskWidget(
                task_data=task_to_data(task),
                task_manager=self.task_manager
            ))

    def on_task_manager(self, instance, value) -> None:
        self.refresh()
