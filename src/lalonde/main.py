from pathlib import Path

from kivy.app import platform
from kivy.clock import mainthread
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from files import Settings, ensure_file_exists
from gui import (
    EditTaskScreen,
    FallbackScreen,
    FolderSelectionScreen,
    MainScreen,
)
from tasks import TaskManager


class LalondeApp(MDApp):
    task_manager = ObjectProperty(None)

    def build(self):
        self.settings = Settings(self)
        self.set_app_theme()

        manager = ScreenManager()
        manager.add_widget(MainScreen())
        manager.add_widget(EditTaskScreen())
        manager.add_widget(FallbackScreen())
        #manager.add_widget(FolderSelectionScreen(on_folder_picked=self.on_folder_picked)) # spaghetification
        manager.add_widget(FolderSelectionScreen())

        return manager

    def set_app_theme(self):
        self.theme_cls.theme_style = self.settings["theme_style"]
        self.theme_cls.material_style = self.settings["material_style"]

    def on_start(self):
        if self.settings["user_data_dir"]:
            self.on_folder_picked(self.settings["user_data_dir"])
        else:
            self.launch_folder_picker()

    # --- Folder Selection ----------------------------------------------------

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
        def kivy_folder_picker():
            self.root.current = "folder_select_screen"
            self.root.get_screen("folder_select_screen").open(self.on_folder_picked)

        match platform:
            case "android":
                from files import android
                if android.has_storage_permission():
                    android.launch_folder_picker(self.on_folder_picked)
                else:
                    android.request_storage_permission()
            case "linux":
                kivy_folder_picker()
            case "macosx":
                kivy_folder_picker()
            case _ as unsupported_platform:
                raise NotImplementedError(f"Attempted to launch folder picker on unsupported platform: {unsupported_platform}")


if __name__ == "__main__":
    LalondeApp().run()
