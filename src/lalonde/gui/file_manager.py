from pathlib import Path

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager

Builder.load_file(str(Path(__file__).with_name("file_manager.kv")))

class FolderSelectionScreen(Screen):
    """Code mostly ripped from the example code for KivyMD"""
    on_folder_picked = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Window.bind(on_keyboard=self.events)
        #self.theme_cls.material_style = "M3"
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

        # Spike to force elevation to zero. See `docs/kivy_elevation_shadow_crash.md`
        for widget in self.file_manager.walk():
            if hasattr(widget, "elevation"):
                widget.elevation = 0
        self.file_manager.ids.toolbar.action_button.elevation = 0

    def file_manager_open(self, on_folder_picked):
        self.on_folder_picked = on_folder_picked
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        toast(path)
        self.on_folder_picked(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    """
    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True
    """
