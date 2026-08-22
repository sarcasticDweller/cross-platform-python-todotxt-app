from pathlib import Path

from kivy.app import platform
from kivy.clock import mainthread
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

import datetime_helper as dh
from alarms import get_next_alarm
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
        self.settings = Settings(Path(self.user_data_dir))
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
        self.set_up_notifications()
        if self.settings["todo_dir"]:
            self.on_folder_picked(self.settings["todo_dir"])
        else:
            self.launch_folder_picker()
    
    # --- Notifications -------------------------------------------------------

    def set_up_notifications(self):
        if platform != "android":
            return
        
        from android.permissions import Permission, request_permissions

        from alarms.android_alarm import create_notification_channel

        request_permissions([Permission.POST_NOTIFICATIONS])
        create_notification_channel()

    def sync_next_alarm(self):
        if platform != "android":
            return
        
        from alarms.android_alarm import cancel_alarm, schedule_alarm

        next_alarm = get_next_alarm(
            self.task_manager,
            dh.today_datetime()
        )
        if next_alarm:
            schedule_alarm(
                when=next_alarm,
                payload=dh.date_to_str(next_alarm)
            )
        else:
            cancel_alarm()
    
    # --- Folder Selection ----------------------------------------------------

    @mainthread
    def on_folder_picked(self, folder_path: Path):
        if not self.settings["todo_dir"]:
            self.settings["todo_dir"] = str(folder_path)
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
        self.sync_next_alarm()

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
