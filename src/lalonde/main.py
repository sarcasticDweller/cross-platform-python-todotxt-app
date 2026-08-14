from pathlib import Path

from kivy.app import platform
from kivy.clock import mainthread
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from file_loading_api.file_loading_api import (
    ensure_file_exists,
    launch_folder_picker,
)
from file_loading_api.settings import Settings
from gui.edit_task import EditTaskScreen
from gui.fallback_screen import FallbackScreen
from gui.main_screen import MainScreen
from gui.tasks_view import TaskList  #noqa: F401 - Kivy *may* need this to be imported
from tasks_api.task_manager import TaskManager


class LalondeApp(MDApp):
    task_manager = ObjectProperty(None)

    def build(self):
        self.settings = Settings(self)
        self.set_app_theme()

        manager = ScreenManager()
        manager.add_widget(MainScreen())
        manager.add_widget(EditTaskScreen())
        manager.add_widget(FallbackScreen())

        return manager

    def set_app_theme(self):
        self.theme_cls.theme_style = self.settings["theme_style"]
        self.theme_cls.material_style = self.settings["material_style"]

    def on_start(self):
        if self.settings["user_data_dir"]:
            self.on_folder_picked(self.settings["user_data_dir"])
        else:
            launch_folder_picker(platform, self.on_folder_picked)

    @mainthread
    def on_folder_picked(self, folder_path: Path):
        if not self.settings["user_data_dir"]:
            self.settings["user_data_dir"] = str(folder_path)
            self.settings.save_settings() # was this really the source of the bugs?
        self.task_manager = TaskManager(
            str(
                ensure_file_exists(
                    folder_path if isinstance(folder_path, Path) else Path(folder_path), # patchwork
                    self.settings["todo_file_name"]
                )
            )
        )

if __name__ == "__main__":
    LalondeApp().run()
