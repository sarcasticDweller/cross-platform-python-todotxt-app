from pathlib import Path

from kivy.app import platform
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from file_loading_api.settings import Settings
from gui.edit_task import EditTaskScreen
from gui.fallback_screen import FallbackScreen
from gui.main_screen import MainScreen
from gui.tasks_view import TaskList  #noqa: F401 - Kivy needs this to be imported
from tasks_api.task_manager import TaskManager


class LalondeApp(MDApp):
    task_manager = ObjectProperty(None)

    def build(self):
        self.theme_cls.theme_style = "Dark" # its 2026, dark mode is "in". but seriously, light mode should come soon. this just works as a stop-gap to make text visible again as this app switches to a MDApp
        self.theme_cls.material_style = "M3"

        manager = ScreenManager()
        manager.add_widget(MainScreen())
        manager.add_widget(EditTaskScreen())
        manager.add_widget(FallbackScreen())

        return manager

    def on_start(self):
        if platform == "android":
            # this is more of a test of jnius than anything. not permanent code.
            from jnius import autoclass
            Build = autoclass("android.os.Build$VERSION")
            Popup(
                title="pyjnius test",
                content=Label(text=f"SDK version: {Build.SDK_INT}"),
                size_hint=(0.8, 0.4)
            ).open()

            # the actual important bit: this loads the todo.txt inside of the Android app's app folder. again, not a permanent structure. this exists as a stopgap for android development until file permissions are figured out
            file_path = Path(self.user_data_dir) / "todo.txt"
            file_path.touch(exist_ok=True)
        else:
            file_path = Path("tmp_todo.txt")

        # just for giggles and to see if this initiates properly
        self.settings = Settings(self)
        self.settings["file_path"] = str(file_path)
        self.settings.save_settings()

        # back to seriousness
        self.task_manager = TaskManager(str(file_path))

if __name__ == "__main__":
    LalondeApp().run()
