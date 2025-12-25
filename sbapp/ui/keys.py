import time
import RNS

import base64
import threading
from kivy.metrics import dp,sp
from kivy.lang.builder import Builder
from kivy.core.clipboard import Clipboard
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy.effects.scroll import ScrollEffect

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import dark_theme_text_color
else:
    from .helpers import dark_theme_text_color

class Keys():
    def __init__(self, app):
        self.app = app
        self.keys_screen = None

        if not self.app.root.ids.screen_manager.has_screen("keys_screen"):
            self.keys_screen = Builder.load_string(layout_keys_screen)
            self.keys_screen.app = self
            self.app.root.ids.screen_manager.add_widget(self.keys_screen)
            self.app.bind_clipboard_actions(self.keys_screen.ids)

            self.keys_screen.ids.keys_scrollview.effect_cls = ScrollEffect
            info1 = "[size=18dp][b]Encryption Keys[/b][/size][size=5dp]\n \n[/size]Your primary encryption keys are stored in a Reticulum Identity within the Sideband app. If you want to backup this Identity for later use on this or another device, you can export it as a plain text blob, with the key data encoded in Base32 format. This will allow you to restore your address in Sideband or other LXMF clients at a later point.\n\n[b]Warning![/b] Anyone that gets access to the key data will be able to control your LXMF address, impersonate you, and read your messages. It is [b]extremely important[/b] that you keep the Identity data secure if you export it.\n\nBefore displaying or exporting your Identity data, make sure that no machine or person in your vicinity is able to see, copy or record your device screen or similar."
            info2 = "[size=18dp][b]Backup & Restore[/b][/size][size=5dp]\n \n[/size]You can backup your entire Sideband profile for import on a computer or other device. The exported backup archive will be saved in the downloads folder of your device. Please note that the exported archive contains all your messages, data and encryption keys. Take extreme care to keep this archive secure."

            if not RNS.vendor.platformutils.get_platform() == "android":
                self.app.widget_hide(self.keys_screen.ids.keys_share)

            self.keys_screen.ids.keys_info.text = info1
            self.keys_screen.ids.backup_info.text = info2


    def _profile_backup_job(self):
        import tarfile
        import plyer
        from .helpers import file_ts_format
        from kivy.clock import Clock
        output_path = plyer.storagepath.get_downloads_dir()
        time_str = time.strftime(file_ts_format, time.localtime(time.time()))
        target_file = f"{output_path}/sideband_backup_{time_str}.tar.gz"
        tar = tarfile.open(target_file, "w:gz")
        tar.add(f"{self.app.sideband.app_dir}/app_storage", arcname="Sideband Backup")
        tar.close()
        
        def job(dt):
            self.keys_screen.ids.keys_backup.disabled = False
            toast("Backup done")
            ok_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
            dialog = MDDialog(text=f"Backup has been saved to {target_file}",
                              buttons=[ok_button])
            def dl_yes(s): dialog.dismiss()
            
            ok_button.bind(on_release=dl_yes)
            dialog.open()

        Clock.schedule_once(job, 0.3)

    def profile_backup_action(self, sender=None):
        self.keys_screen.ids.keys_backup.disabled = True
        toast("Creating backup...")
        threading.Thread(target=self._profile_backup_job, daemon=True).start()

    def identity_display_action(self, sender=None):
        yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))

        dialog = MDDialog(
            text="Your Identity key, in base32 format is as follows:\n\n[b]"+str(base64.b32encode(self.app.sideband.identity.get_private_key()).decode("utf-8"))+"[/b]",
            buttons=[ yes_button ],
            # elevation=0,
        )
        def dl_yes(s):
            dialog.dismiss()
        
        yes_button.bind(on_release=dl_yes)
        dialog.open()

    def identity_copy_action(self, sender=None):
        c_yes_button = MDRectangleFlatButton(text="Yes",font_size=dp(18), theme_text_color="Custom", line_color=self.app.color_reject, text_color=self.app.color_reject)
        c_no_button = MDRectangleFlatButton(text="No, go back",font_size=dp(18))
        c_dialog = MDDialog(text="[b]Caution![/b]\n\nYour Identity key will be copied to the system clipboard. Take extreme care that no untrusted app steals your key by reading the clipboard data. Clear the system clipboard immediately after pasting your key where you need it.\n\nAre you sure that you wish to proceed?", buttons=[ c_no_button, c_yes_button ])
        def c_dl_no(s):
            c_dialog.dismiss()
        def c_dl_yes(s):
            c_dialog.dismiss()
            yes_button = MDRectangleFlatButton(text="OK")
            dialog = MDDialog(text="Your Identity key was copied to the system clipboard", buttons=[ yes_button ])
            def dl_yes(s):
                dialog.dismiss()
            yes_button.bind(on_release=dl_yes)

            Clipboard.copy(str(base64.b32encode(self.app.sideband.identity.get_private_key()).decode("utf-8")))
            dialog.open()
        
        c_yes_button.bind(on_release=c_dl_yes)
        c_no_button.bind(on_release=c_dl_no)

        c_dialog.open()

    def identity_share_action(self, sender=None):
        if RNS.vendor.platformutils.get_platform() == "android":
            self.share_text(str(base64.b32encode(self.app.sideband.identity.get_private_key()).decode("utf-8")))

    def identity_restore_action(self, sender=None):
        c_yes_button = MDRectangleFlatButton(text="Yes",font_size=dp(18), theme_text_color="Custom", line_color=self.app.color_reject, text_color=self.app.color_reject)
        c_no_button = MDRectangleFlatButton(text="No, go back",font_size=dp(18))
        c_dialog = MDDialog(text="[b]Caution![/b]\n\nYou are about to import a new Identity key into Sideband. The currently active key will be irreversibly destroyed, and you will loose your LXMF address if you have not already backed up your current Identity key.\n\nAre you sure that you wish to import the key?", buttons=[ c_no_button, c_yes_button ])
        def c_dl_no(s):
            c_dialog.dismiss()
        def c_dl_yes(s):
            c_dialog.dismiss()
            b32_text = self.keys_screen.ids.key_restore_text.text
        
            try:
                key_bytes = base64.b32decode(b32_text)
                new_id = RNS.Identity.from_bytes(key_bytes)

                if new_id != None:
                    new_id.to_file(self.app.sideband.identity_path)

                yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                dialog = MDDialog(text="[b]The provided Identity key data was imported[/b]\n\nThe app will now exit. Please restart Sideband to use the new Identity.", buttons=[ yes_button ])
                def dl_yes(s):
                    dialog.dismiss()
                    self.app.quit_action(sender=self)
                yes_button.bind(on_release=dl_yes)
                dialog.open()

            except Exception as e:
                yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                dialog = MDDialog(text="[b]The provided Identity key data was not valid[/b]\n\nThe error reported by Reticulum was:\n\n[i]"+str(e)+"[/i]\n\nNo Identity was imported into Sideband.", buttons=[ yes_button ])
                def dl_yes(s):
                    dialog.dismiss()
                yes_button.bind(on_release=dl_yes)
                dialog.open()
            
        
        c_yes_button.bind(on_release=c_dl_yes)
        c_no_button.bind(on_release=c_dl_no)

        c_dialog.open()


layout_keys_screen = """
MDScreen:
    name: "keys_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Backup & Keys"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_keys_action(self)],
                ]

        ScrollView:
            id:keys_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "24dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(35), dp(35), dp(35), dp(35)]


                MDLabel:
                    id: backup_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDRectangleFlatIconButton:
                    id: keys_backup
                    icon: "home-export-outline"
                    text: "Backup Sideband Profile"
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.app.profile_backup_action(self)

                MDRectangleFlatIconButton:
                    id: keys_restore
                    icon: "home-import-outline"
                    text: "Restore Sideband Profile"
                    disabled: True
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.app.profile_backup_action(self)

                MDLabel:
                    id: keys_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDRectangleFlatIconButton:
                    id: keys_display
                    icon: "eye"
                    text: "Display Identity Key"
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.app.identity_display_action(self)

                MDRectangleFlatIconButton:
                    id: keys_copy
                    icon: "file-key"
                    text: "Copy Key To Clipboard"
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.app.identity_copy_action(self)

                MDRectangleFlatIconButton:
                    id: keys_share
                    icon: "upload-lock"
                    text: "Send Key To Other App"
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.app.identity_share_action(self)

                MDBoxLayout:
                    orientation: "vertical"
                    # spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(12), dp(0), dp(0)]

                    MDTextField:
                        id: key_restore_text
                        hint_text: "Enter base32 key for import"
                        mode: "rectangle"
                        # size_hint: [1.0, None]
                        pos_hint: {"center_x": .5}

                MDRectangleFlatIconButton:
                    id: keys_restore
                    icon: "download-lock"
                    text: "Restore Identity From Key"
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.app.identity_restore_action(self)
"""