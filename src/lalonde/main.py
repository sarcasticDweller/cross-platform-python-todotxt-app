from pathlib import Path

from kivy.app import platform
from kivy.clock import mainthread
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from file_loading_api.file_loading_api import (
    ensure_file_exists,
)
from file_loading_api.settings import Settings
from gui.edit_task import EditTaskScreen
from gui.fallback_screen import FallbackScreen
from gui.file_manager import FolderSelectionScreen
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
        manager.add_widget(FolderSelectionScreen(on_folder_picked=self.on_folder_picked)) # spaghetification

        return manager

    def set_app_theme(self):
        self.theme_cls.theme_style = self.settings["theme_style"]
        self.theme_cls.material_style = self.settings["material_style"]

    def on_start(self):
        if self.settings["user_data_dir"]:
            self.on_folder_picked(self.settings["user_data_dir"])
        else:
            self.launch_folder_picker()

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
        self.root.current = "main_screen"
        self.root.get_screen("main_screen")

    def launch_folder_picker(self):
        def case_pc():
            self.root.current = "folder_select_screen"
            self.root.get_screen("folder_select_screen").file_manager_open(self.on_folder_picked)

        match platform:
            case "android":
                from file_loading_api.android import launch_android_folder_picker
                launch_android_folder_picker(self.on_folder_picked)
            case "linux":
                case_pc()
            case "macosx":
                case_pc()
            case _ as unsupported_platform:
                raise NotImplementedError(f"Attempted to launch folder picker on unsupported platform: {unsupported_platform}")

class UnsupportedStorageVolumeError(ValueError): pass

if __name__ == "__main__":
    LalondeApp().run()
