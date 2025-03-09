import time
import RNS

from typing import Union
from kivy.metrics import dp,sp
from kivy.lang.builder import Builder
from kivy.core.clipboard import Clipboard
from kivy.utils import escape_markup
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.pickers import MDColorPicker
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.icon_definitions import md_icons
from kivymd.toast import toast
from kivy.properties import StringProperty, BooleanProperty
from kivy.effects.scroll import ScrollEffect
from kivy.clock import Clock
from sideband.sense import Telemeter
import threading
from datetime import datetime

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import ts_format
    from android.permissions import request_permissions, check_permission
else:
    from .helpers import ts_format

class Voice():
    def __init__(self, app):
        self.app = app
        self.screen = None
        self.rnstatus_screen = None
        self.rnstatus_instance = None
        self.logviewer_screen = None
    
        if not self.app.root.ids.screen_manager.has_screen("voice_screen"):
            self.screen = Builder.load_string(layout_voice_screen)
            self.screen.app = self.app
            self.screen.delegate = self
            self.app.root.ids.screen_manager.add_widget(self.screen)
        
        self.screen.ids.voice_scrollview.effect_cls = ScrollEffect
        info  = "Voice services UI"
        info += ""
        
        if self.app.theme_cls.theme_style == "Dark":
            info = "[color=#"+self.app.dark_theme_text_color+"]"+info+"[/color]"
        
        self.screen.ids.voice_info.text = info

layout_voice_screen = """
MDScreen:
    name: "voice_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Voice"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_any_action(self)],
                ]

        ScrollView:
            id: voice_scrollview

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(32), dp(28), dp(16)]

                # MDLabel:
                #     text: "Utilities & Tools"
                #     font_style: "H6"

                MDLabel:
                    id: voice_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(35), dp(0), dp(35)]

                    MDRectangleFlatIconButton:
                        id: rnstatus_button
                        icon: "wifi-check"
                        text: "Reticulum Status"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.delegate.rnstatus_action(self)
                        disabled: False                
"""
