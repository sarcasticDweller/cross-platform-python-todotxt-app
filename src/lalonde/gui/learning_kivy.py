from pathlib import Path

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform
from kivymd.app import MDApp

from gui.edit_task import EditTaskScreen
from gui.tasks_view import TaskList  #noqa: F401 - Kivy needs this to be imported
from tasks_api.task_manager import TaskManager

Builder.load_file(str(Path(__file__).with_name("main_screen.kv")))
Builder.load_file(str(Path(__file__).with_name("fallback_screen.kv")))

class MainScreen(Screen):
    task_manager = ObjectProperty(None)

    def on_create_task(self):
        if not self.task_manager:
            print("no task manager yet, action failed")
            return
        self.manager.get_screen("edit_task_screen").open_in_mode("create")

    def on_pre_enter(self):
        if not self.task_manager:
            print("no task manager yet, action failed")
            return
        self.ids.task_list.refresh()

class FallbackScreen(Screen):
    pass

class LalondeApp(MDApp):
    task_manager = ObjectProperty(None)

    def build(self):
        self.theme_cls.theme_style = "Dark" # its 2026, dark mode is "in". but seriously, light mode should come soon. this just works as a stop-gap to make text visible again as this app switches to a MDApp
        manager = ScreenManager()
        manager.add_widget(MainScreen())
        manager.add_widget(EditTaskScreen())
        manager.add_widget(FallbackScreen())

        return manager

    def on_start(self):
        if platform == "android":
            from jnius import autoclass
            Build = autoclass("android.os.Build$VERSION")
            Popup(
                title="pyjnius test",
                content=Label(text=f"SDK version: {Build.SDK_INT}"),
                size_hint=(0.8, 0.4)
            ).open()
            file_path = Path(self.user_data_dir) / "todo.txt"
            file_path.touch(exist_ok=True)
        else:
            file_path = Path("tmp_todo.txt")

        self.task_manager = TaskManager(str(file_path))
