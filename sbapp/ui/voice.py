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
        self.settings_screen = None
        self.dial_target = None
        self.ui_updater = None
        self.path_requesting = None
    
        if not self.app.root.ids.screen_manager.has_screen("voice_screen"):
            self.screen = Builder.load_string(layout_voice_screen)
            self.screen.app = self.app
            self.screen.delegate = self
            self.app.root.ids.screen_manager.add_widget(self.screen)
        
        self.screen.ids.voice_scrollview.effect_cls = ScrollEffect
        # info  = "Voice services UI"
        # info += ""
        
        # if self.app.theme_cls.theme_style == "Dark":
        #     info = "[color=#"+self.app.dark_theme_text_color+"]"+info+"[/color]"
        
        # self.screen.ids.voice_info.text = info

    def update_call_status(self, dt=None):
        if self.app.root.ids.screen_manager.current == "voice_screen":
            if self.ui_updater == None: self.ui_updater = Clock.schedule_interval(self.update_call_status, 0.5)
        else:
            if self.ui_updater:
                self.ui_updater.cancel()
                self.ui_updater = None

        db = self.screen.ids.dial_button
        ih = self.screen.ids.identity_hash
        if self.app.sideband.voice_running:
            telephone = self.app.sideband.telephone
            if self.path_requesting:
                db.disabled = True
                ih.disabled = True

            else:
                if telephone.is_available:
                    ih.disabled = False
                    self.target_input_action(ih)
                else:
                    ih.disabled = True

                if telephone.is_in_call or telephone.call_is_connecting:
                    ih.disabled = True
                    db.disabled = False
                    db.text = "Hang up"
                    db.icon = "phone-hangup"

                elif telephone.is_ringing:
                    ih.disabled = True
                    db.disabled = False
                    db.text = "Answer"
                    db.icon = "phone-ring"
                    if telephone.caller: ih.text = RNS.hexrep(telephone.caller.hash, delimit=False)

        else:
            db.disabled = True; db.text = "Voice calls disabled"
            ih.disabled = True

    def target_valid(self):
        if self.app.sideband.voice_running:
            db = self.screen.ids.dial_button
            db.disabled = False; db.text = "Call"
            db.icon = "phone-outgoing"

    def target_invalid(self):
        if self.app.sideband.voice_running:
            db = self.screen.ids.dial_button
            db.disabled = True; db.text = "Call"
            db.icon = "phone-outgoing"

    def target_input_action(self, sender):
        if sender:
            target_hash = sender.text
            if len(target_hash) == RNS.Reticulum.TRUNCATED_HASHLENGTH//8*2:
                try:
                    identity_hash = bytes.fromhex(target_hash)
                    self.dial_target = identity_hash
                    self.target_valid()

                except Exception as e: self.target_invalid()
            else: self.target_invalid()

    def request_path(self, destination_hash):
        if not self.path_requesting:
            self.app.sideband.telephone.set_busy(True)
            toast("Requesting path...")
            self.screen.ids.dial_button.disabled = True
            self.path_requesting = destination_hash
            RNS.Transport.request_path(destination_hash)
            threading.Thread(target=self._path_wait_job, daemon=True).start()
        
        else:
            toast("Waiting for path request answer...")

    def _path_wait_job(self):
        timeout = time.time()+self.app.sideband.telephone.PATH_TIME
        while not RNS.Transport.has_path(self.path_requesting) and time.time() < timeout:
            time.sleep(0.25)

        self.app.sideband.telephone.set_busy(False)
        if RNS.Transport.has_path(self.path_requesting):
            RNS.log(f"Calling {RNS.prettyhexrep(self.dial_target)}...", RNS.LOG_DEBUG)
            self.app.sideband.telephone.dial(self.dial_target)
            Clock.schedule_once(self.update_call_status, 0.1)

        else:
            Clock.schedule_once(self._path_request_failed, 0.05)
            Clock.schedule_once(self.update_call_status, 0.1)

        self.path_requesting = None
        self.update_call_status()

    def _path_request_failed(self, dt):
        toast("Path request timed out")

    def dial_action(self, sender=None):
        if self.app.sideband.voice_running:
            if self.app.sideband.telephone.is_available:

                destination_hash = RNS.Destination.hash_from_name_and_identity("lxst.telephony", self.dial_target)
                if not RNS.Transport.has_path(destination_hash):
                    self.request_path(destination_hash)

                else:
                    RNS.log(f"Calling {RNS.prettyhexrep(self.dial_target)}...", RNS.LOG_DEBUG)
                    self.app.sideband.telephone.dial(self.dial_target)
                    self.update_call_status()

            elif self.app.sideband.telephone.is_in_call or self.app.sideband.telephone.call_is_connecting:
                RNS.log(f"Hanging up", RNS.LOG_DEBUG)
                self.app.sideband.telephone.hangup()
                self.update_call_status()

            elif self.app.sideband.telephone.is_ringing:
                RNS.log(f"Answering", RNS.LOG_DEBUG)
                self.app.sideband.telephone.answer()
                self.update_call_status()

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

                MDBoxLayout:
                    orientation: "vertical"
                    # spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(12), dp(0), dp(0)]

                    MDTextField:
                        id: identity_hash
                        hint_text: "Identity hash"
                        mode: "rectangle"
                        # size_hint: [1.0, None]
                        pos_hint: {"center_x": .5}
                        max_text_length: 32
                        on_text: root.delegate.target_input_action(self)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(35), dp(0), dp(35)]

                    MDRectangleFlatIconButton:
                        id: dial_button
                        icon: "phone-outgoing"
                        text: "Call"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.delegate.dial_action(self)
                        disabled: True
"""
