from pathlib import Path

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

Builder.load_file(str(Path(__file__).with_name("fallback_screen.kv")))

class FallbackScreen(Screen):
    pass
