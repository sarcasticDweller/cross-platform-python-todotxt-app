from pathlib import Path

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

Builder.load_file(str(Path(__file__).with_name("main_screen.kv")))

class MainScreen(Screen):
    task_manager = ObjectProperty(None)

    def on_create_task(self):
        if not self.task_manager:
            print("no task manager yet, action failed")
            return
        self.manager.get_screen("edit_task_screen").open("create")

    def on_pre_enter(self):
        if not self.task_manager:
            print("no task manager yet, action failed")
            return
        self.ids.task_list.refresh()
    