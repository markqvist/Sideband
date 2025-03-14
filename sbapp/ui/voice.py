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
from kivymd.uix.button import MDRectangleFlatIconButton
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
        self.output_devices = []
        self.input_devices = []
        self.listed_output_devices = []
        self.listed_input_devices = []
        self.listed_ringer_devices = []
    
        if not self.app.root.ids.screen_manager.has_screen("voice_screen"):
            self.screen = Builder.load_string(layout_voice_screen)
            self.screen.app = self.app
            self.screen.delegate = self
            self.app.root.ids.screen_manager.add_widget(self.screen)
        
        self.screen.ids.voice_scrollview.effect_cls = ScrollEffect

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


    ### settings screen
    ######################################

    def settings_action(self, sender=None):
        if not self.app.root.ids.screen_manager.has_screen("voice_settings_screen"):
            self.voice_settings_screen = Builder.load_string(layout_voice_settings_screen)
            self.voice_settings_screen.app = self.app
            self.voice_settings_screen.delegate = self
            self.app.root.ids.screen_manager.add_widget(self.voice_settings_screen)

        self.app.root.ids.screen_manager.transition.direction = "left"
        self.app.root.ids.screen_manager.current = "voice_settings_screen"
        self.voice_settings_screen.ids.voice_settings_scrollview.effect_cls = ScrollEffect
        self.app.sideband.setstate("app.displaying", self.app.root.ids.screen_manager.current)
        
        self.update_settings_screen()

    def update_devices(self):
        import LXST
        self.output_devices = []; self.input_devices = []
        for device in LXST.Sources.Backend().soundcard.all_speakers():  self.output_devices.append(device.name)
        for device in LXST.Sinks.Backend().soundcard.all_microphones(): self.input_devices.append(device.name)
        if self.app.sideband.config["voice_output"] != None:
            if not self.app.sideband.config["voice_output"] in self.output_devices: self.output_devices.append(self.app.sideband.config["voice_output"])
        if self.app.sideband.config["voice_input"] != None:
            if not self.app.sideband.config["voice_input"] in self.input_devices: self.input_devices.append(self.app.sideband.config["voice_input"])
        if self.app.sideband.config["voice_ringer"] != None:
            if not self.app.sideband.config["voice_ringer"] in self.output_devices: self.output_devices.append(self.app.sideband.config["voice_ringer"])

    def update_settings_screen(self, sender=None):
        self.voice_settings_screen.ids.voice_trusted_only.active = self.app.sideband.config["voice_trusted_only"]
        self.voice_settings_screen.ids.voice_trusted_only.bind(active=self.settings_save_action)

        bp = 6; ml = 45; fs = 16; ics = 14
        self.update_devices()

        # Output devices
        if not "system_default" in self.listed_output_devices:
            default_output_button = MDRectangleFlatIconButton(text="System Default", font_size=dp(fs), icon_size=dp(ics), on_release=self.output_device_action)
            default_output_button.device = None; default_output_button.size_hint = [1.0, None]
            if self.app.sideband.config["voice_output"] == None: default_output_button.icon = "check"
            self.voice_settings_screen.ids.output_devices.add_widget(default_output_button)
            self.listed_output_devices.append("system_default")

        for device in self.output_devices:
            if not device in self.listed_output_devices:
                label = device if len(device) < ml else device[:ml-3]+"..."
                device_button = MDRectangleFlatIconButton(text=label, font_size=dp(fs), icon_size=dp(ics), on_release=self.output_device_action)
                device_button.padding = [dp(bp), dp(bp), dp(bp), dp(bp)]; device_button.size_hint = [1.0, None]
                if self.app.sideband.config["voice_output"] == device: device_button.icon = "check"
                device_button.device = device
                self.voice_settings_screen.ids.output_devices.add_widget(device_button)
                self.listed_output_devices.append(device)

        # Input devices
        if not "system_default" in self.listed_input_devices:
            default_input_button = MDRectangleFlatIconButton(text="System Default", font_size=dp(fs), icon_size=dp(ics), on_release=self.input_device_action)
            default_input_button.device = None; default_input_button.size_hint = [1.0, None]
            if self.app.sideband.config["voice_output"] == None: default_input_button.icon = "check"
            self.voice_settings_screen.ids.input_devices.add_widget(default_input_button)
            self.listed_input_devices.append("system_default")

        for device in self.input_devices:
            if not device in self.listed_input_devices:
                label = device if len(device) < ml else device[:ml-3]+"..."
                device_button = MDRectangleFlatIconButton(text=label, font_size=dp(fs), icon_size=dp(ics), on_release=self.input_device_action)
                device_button.padding = [dp(bp), dp(bp), dp(bp), dp(bp)]; device_button.size_hint = [1.0, None]
                if self.app.sideband.config["voice_input"] == device: device_button.icon = "check"
                device_button.device = device
                self.voice_settings_screen.ids.input_devices.add_widget(device_button)
                self.listed_input_devices.append(device)

        # Ringer devices
        if not "system_default" in self.listed_ringer_devices:
            default_ringer_button = MDRectangleFlatIconButton(text="System Default", font_size=dp(fs), icon_size=dp(ics), on_release=self.ringer_device_action)
            default_ringer_button.device = None; default_ringer_button.size_hint = [1.0, None]
            if self.app.sideband.config["voice_ringer"] == None: default_ringer_button.icon = "check"
            self.voice_settings_screen.ids.ringer_devices.add_widget(default_ringer_button)
            self.listed_ringer_devices.append("system_default")

        for device in self.output_devices:
            if not device in self.listed_ringer_devices:
                label = device if len(device) < ml else device[:ml-3]+"..."
                device_button = MDRectangleFlatIconButton(text=label, font_size=dp(fs), icon_size=dp(ics), on_release=self.ringer_device_action)
                device_button.padding = [dp(bp), dp(bp), dp(bp), dp(bp)]; device_button.size_hint = [1.0, None]
                if self.app.sideband.config["voice_ringer"] == device: device_button.icon = "check"
                device_button.device = device
                self.voice_settings_screen.ids.ringer_devices.add_widget(device_button)
                self.listed_ringer_devices.append(device)

    def settings_save_action(self, sender=None, event=None):
        self.app.sideband.config["voice_trusted_only"] = self.voice_settings_screen.ids.voice_trusted_only.active
        self.app.sideband.save_configuration()

    def output_device_action(self, sender=None):
        self.app.sideband.config["voice_output"] = sender.device
        self.app.sideband.save_configuration()
        for w in self.voice_settings_screen.ids.output_devices.children: w.icon = ""
        sender.icon = "check"
        if self.app.sideband.telephone:
            self.app.sideband.telephone.set_speaker(self.app.sideband.config["voice_output"])

    def input_device_action(self, sender=None):
        self.app.sideband.config["voice_input"] = sender.device
        self.app.sideband.save_configuration()
        for w in self.voice_settings_screen.ids.input_devices.children: w.icon = ""
        sender.icon = "check"
        if self.app.sideband.telephone:
            self.app.sideband.telephone.set_microphone(self.app.sideband.config["voice_input"])

    def ringer_device_action(self, sender=None):
        self.app.sideband.config["voice_ringer"] = sender.device
        self.app.sideband.save_configuration()
        for w in self.voice_settings_screen.ids.ringer_devices.children: w.icon = ""
        sender.icon = "check"
        if self.app.sideband.telephone:
            self.app.sideband.telephone.set_ringer(self.app.sideband.config["voice_ringer"])


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
                ['wrench-cog', lambda x: root.delegate.settings_action(self)],
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

layout_voice_settings_screen = """
MDScreen:
    name: "voice_settings_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: top_bar
            title: "Voice Configuration"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_voice_action(self)],
                ]

        MDScrollView:
            id: voice_settings_scrollview
            size_hint_x: 1
            size_hint_y: None
            size: [root.width, root.height-root.ids.top_bar.height]
            do_scroll_x: False
            do_scroll_y: True

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Call Handling"
                    font_style: "H6"
                    height: self.texture_size[1]
                    padding: [dp(0), dp(0), dp(0), dp(12)]

                MDLabel:
                    id: voice_settings_info
                    markup: True
                    text: "You can block calls from all other callers than contacts marked as trusted, by enabling the following option."
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]
                    padding: [dp(0), dp(16), dp(0), dp(16)]

                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(48)
                    
                    MDLabel:
                        text: "Block non-trusted callers"
                        font_style: "H6"

                    MDSwitch:
                        id: voice_trusted_only
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDLabel:
                    text: "Audio Devices"
                    font_style: "H6"
                    padding: [dp(0), dp(96), dp(0), dp(12)]

                MDLabel:
                    id: voice_settings_info
                    markup: True
                    text: "You can configure which audio devices Sideband will use for voice calls, by selecting either the system default device, or specific audio devices available."
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]
                    padding: [dp(0), dp(64), dp(0), dp(32)]

                MDLabel:
                    text: "[b]Output[/b]"
                    font_size: dp(18)
                    markup: True

                MDBoxLayout:
                    id: output_devices
                    orientation: "vertical"
                    spacing: "12dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(24), dp(0), dp(48)]

                    # MDRectangleFlatIconButton:
                    #     id: output_default_button
                    #     text: "System Default"
                    #     padding: [dp(0), dp(14), dp(0), dp(14)]
                    #     icon_size: dp(24)
                    #     font_size: dp(16)
                    #     size_hint: [1.0, None]
                    #     on_release: root.delegate.output_device_action(self)
                    #     disabled: False

                MDLabel:
                    text: "[b]Input[/b]"
                    font_size: dp(18)
                    markup: True

                MDBoxLayout:
                    id: input_devices
                    orientation: "vertical"
                    spacing: "12dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(24), dp(0), dp(48)]

                MDLabel:
                    text: "[b]Ringer[/b]"
                    font_size: dp(18)
                    markup: True

                MDBoxLayout:
                    id: ringer_devices
                    orientation: "vertical"
                    spacing: "12dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(24), dp(0), dp(48)]

"""