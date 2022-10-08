__debug_build__ = False
__disable_shaders__ = True
__version__ = "0.2.2"
__variant__ = "beta"

import sys
import argparse
parser = argparse.ArgumentParser(description="Reticulum Network Stack Daemon")
parser.add_argument("-v", "--verbose", action='store_true', default=False, help="increase logging verbosity")
parser.add_argument("--version", action="version", version="sideband {version}".format(version=__version__))
args = parser.parse_args()
sys.argv = [sys.argv[0]]

import RNS
import LXMF
import time
import os
import plyer
import base64
import threading

from kivy.logger import Logger, LOG_LEVELS
if __debug_build__ or args.verbose:
    Logger.setLevel(LOG_LEVELS["debug"])
else:
    Logger.setLevel(LOG_LEVELS["error"])

if RNS.vendor.platformutils.get_platform() != "android":
    local = os.path.dirname(__file__)
    sys.path.append(local)

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.effects.scroll import ScrollEffect
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import FadeTransition, NoTransition
from kivy.effects.dampedscroll import DampedScrollEffect

if RNS.vendor.platformutils.get_platform() == "android":
    from sideband.core import SidebandCore

    from ui.layouts import root_layout
    from ui.conversations import Conversations, MsgSync, NewConv
    from ui.announces import Announces
    from ui.messages import Messages, ts_format
    from ui.helpers import ContentNavigationDrawer, DrawerList, IconListItem

    from jnius import cast
    from jnius import autoclass
    from android import mActivity
    from android.permissions import request_permissions, check_permission

    from kivymd.utils.set_bars_colors import set_bars_colors

else:
    from .sideband.core import SidebandCore

    from .ui.layouts import root_layout
    from .ui.conversations import Conversations, MsgSync, NewConv
    from .ui.announces import Announces
    from .ui.messages import Messages, ts_format
    from .ui.helpers import ContentNavigationDrawer, DrawerList, IconListItem

from kivy.metrics import dp, sp
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.color_definitions import colors

dark_theme_text_color = "ddd"

if RNS.vendor.platformutils.get_platform() == "android":
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

class SidebandApp(MDApp):
    STARTING = 0x00
    ACTIVE   = 0x01
    PAUSED   = 0x02
    STOPPING = 0x03

    PKGNAME  = "io.unsigned.sideband"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Sideband"
        self.app_state = SidebandApp.STARTING
        self.android_service = None
        self.app_dir = plyer.storagepath.get_application_dir()
        self.shaders_disabled = __disable_shaders__

        if RNS.vendor.platformutils.get_platform() == "android":
            self.sideband = SidebandCore(self, is_client=True, android_app_dir=self.app_dir, verbose=__debug_build__)
        else:
            self.sideband = SidebandCore(self, is_client=False, verbose=(args.verbose or __debug_build__))

        self.set_ui_theme()

        self.conversations_view = None
        self.sync_dialog = None
        self.settings_ready = False
        self.connectivity_ready = False

        Window.softinput_mode = "below_target"
        self.icon = self.sideband.asset_dir+"/icon.png"
        self.notification_icon = self.sideband.asset_dir+"/notification_icon.png"

    def start_core(self, dt):
        self.check_permissions()
        self.start_service()
        
        Clock.schedule_interval(self.jobs, 1)

        def dismiss_splash(dt):
            from android import loadingscreen
            loadingscreen.hide_loading_screen()

        if RNS.vendor.platformutils.get_platform() == "android":
            Clock.schedule_once(dismiss_splash, 0)

        self.sideband.setstate("app.loaded", True)
        self.sideband.setstate("app.running", True)
        self.sideband.setstate("app.foreground", True)

        if self.sideband.first_run:
            self.guide_action()
            def fp(delta_time):
                self.request_permissions()
            Clock.schedule_once(fp, 3)
        else:
            self.open_conversations()

        self.set_bars_colors()

        self.app_state = SidebandApp.ACTIVE
        
    def start_service(self):
        RNS.log("Launching platform-specific service for RNS and LXMF")
        if RNS.vendor.platformutils.get_platform() == "android":
            self.android_service = autoclass('io.unsigned.sideband.ServiceSidebandservice')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            argument = self.app_dir
            self.android_service.start(mActivity, argument)

            # Wait a little extra for user to react to permissions prompt
            if self.sideband.first_run:
                time.sleep(6)

            # Wait for service to become available
            while not self.sideband.service_available():
                time.sleep(0.20)

            # Start local core instance
            self.sideband.start()

        else:
            self.sideband.start()

        # Pre-load announce stream widgets
        self.init_announces_view()
        self.announces_view.update()


    #################################################
    # General helpers                               #
    #################################################

    def set_ui_theme(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.widget_style = "android"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Orange"

        if self.sideband.config["dark_ui"]:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

        self.update_ui_colors()

    def update_ui_colors(self):
        if self.sideband.config["dark_ui"]:
            self.color_reject = colors["DeepOrange"]["900"]
            self.color_accept = colors["LightGreen"]["700"]
        else:
            self.color_reject = colors["DeepOrange"]["800"]
            self.color_accept = colors["LightGreen"]["700"]

    def update_ui_theme(self):
        if self.sideband.config["dark_ui"]:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

        self.update_ui_colors()

        st = time.time()
        RNS.log("Recursing widgets...")
        for wid in self.root.ids:
            RNS.log("Found: "+str(wid)+str(self.root.ids[wid]))

    def set_bars_colors(self):
        if RNS.vendor.platformutils.get_platform() == "android":
            set_bars_colors(
                self.theme_cls.primary_color,  # status bar color
                [0,0,0,0],  # navigation bar color
                "Light",                       # icons color of status bar
            )

    def share_text(self, text):
        if RNS.vendor.platformutils.get_platform() == "android":
            Intent = autoclass('android.content.Intent')
            JString = autoclass('java.lang.String')

            shareIntent = Intent()
            shareIntent.setAction(Intent.ACTION_SEND)
            shareIntent.setType("text/plain")
            shareIntent.putExtra(Intent.EXTRA_TEXT, JString(text))

            mActivity.startActivity(shareIntent)

    def on_pause(self):
        RNS.log("App pausing...", RNS.LOG_DEBUG)
        self.sideband.setstate("app.running", True)
        self.sideband.setstate("app.foreground", False)
        self.app_state = SidebandApp.PAUSED
        self.sideband.should_persist_data()
        if self.conversations_view != None:
            self.root.ids.conversations_scrollview.effect_cls = ScrollEffect
            self.conversations_view.update()
            self.root.ids.conversations_scrollview.scroll = 1

        RNS.log("App paused", RNS.LOG_DEBUG)
        return True

    def on_resume(self):
        RNS.log("App resuming...", RNS.LOG_DEBUG)
        self.sideband.setstate("app.running", True)
        self.sideband.setstate("app.foreground", True)
        self.sideband.setstate("wants.clear_notifications", True)
        self.app_state = SidebandApp.ACTIVE
        if self.conversations_view != None:
            self.root.ids.conversations_scrollview.effect_cls = ScrollEffect
            self.conversations_view.update()
            self.root.ids.conversations_scrollview.scroll = 1
            
        else:
            RNS.log("Conversations view did not exist", RNS.LOG_DEBUG)

        RNS.log("App resumed...", RNS.LOG_DEBUG)

    def on_stop(self):
        RNS.log("App stopping...", RNS.LOG_DEBUG)
        self.sideband.setstate("app.running", False)
        self.sideband.setstate("app.foreground", False)
        self.app_state = SidebandApp.STOPPING
        RNS.log("App stopped", RNS.LOG_DEBUG)

    def is_in_foreground(self):
        if self.app_state == SidebandApp.ACTIVE:
            return True
        else:
            return False

    def check_permissions(self):
        if RNS.vendor.platformutils.get_platform() == "android":
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            Context = autoclass('android.content.Context')
            NotificationManager = autoclass('android.app.NotificationManager')
            notification_service = cast(NotificationManager, mActivity.getSystemService(Context.NOTIFICATION_SERVICE))

            if notification_service.areNotificationsEnabled():
                self.sideband.setpersistent("permissions.notifications", True)
            else:
                if check_permission("android.permission.POST_NOTIFICATIONS"):
                    RNS.log("Have notification permissions", RNS.LOG_DEBUG)
                    self.sideband.setpersistent("permissions.notifications", True)
                else:
                    RNS.log("Do not have notification permissions")
                    self.sideband.setpersistent("permissions.notifications", False)
        else:
            self.sideband.setpersistent("permissions.notifications", True)

    def request_permissions(self):
        self.request_notifications_permission()

    def request_notifications_permission(self):
        if RNS.vendor.platformutils.get_platform() == "android":
            if not check_permission("android.permission.POST_NOTIFICATIONS"):
                RNS.log("Requesting notification permission", RNS.LOG_DEBUG)
                request_permissions(["android.permission.POST_NOTIFICATIONS"])
            
        self.check_permissions()

    def build(self):
        FONT_PATH = self.sideband.asset_dir+"/fonts"
        if RNS.vendor.platformutils.is_darwin():
            self.icon = self.sideband.asset_dir+"/icon_macos_formed.png"
        else:
            self.icon = self.sideband.asset_dir+"/icon.png"

        self.announces_view = None

        screen = Builder.load_string(root_layout)

        return screen

    def jobs(self, delta_time):
        if self.root.ids.screen_manager.current == "messages_screen":
            self.messages_view.update()

            if not self.root.ids.messages_scrollview.dest_known:
                self.message_area_detect()

        elif self.root.ids.screen_manager.current == "conversations_screen":
            if self.sideband.getstate("app.flags.unread_conversations"):
                if self.conversations_view != None:
                    self.conversations_view.update()

            if self.sideband.getstate("app.flags.lxmf_sync_dialog_open") and self.sync_dialog != None:
                self.sync_dialog.ids.sync_progress.value = self.sideband.get_sync_progress()*100
                self.sync_dialog.ids.sync_status.text = self.sideband.get_sync_status()

                state = self.sideband.message_router.propagation_transfer_state
                if state > LXMF.LXMRouter.PR_IDLE and state < LXMF.LXMRouter.PR_COMPLETE:
                    self.widget_hide(self.sync_dialog.stop_button, False)
                else:
                    self.widget_hide(self.sync_dialog.stop_button, True)

        elif self.root.ids.screen_manager.current == "announces_screen":
            if self.sideband.getstate("app.flags.new_announces"):
                if self.announces_view != None:
                    self.announces_view.update()

        if self.sideband.getstate("app.flags.new_conversations"):
            if self.conversations_view != None:
                self.conversations_view.update()

    def on_start(self):
        self.last_exit_event = time.time()
        self.root.ids.screen_manager.transition.duration = 0.25
        self.root.ids.screen_manager.transition.bind(on_complete=self.screen_transition_complete)

        EventLoop.window.bind(on_keyboard=self.keyboard_event)
        EventLoop.window.bind(on_key_down=self.keydown_event)
        
        # This incredibly hacky hack circumvents a bug in SDL2
        # that prevents focus from being correctly released from
        # the software keyboard on Android. Without this the back
        # button/gesture does not work after the soft-keyboard has
        # appeared for the first time.
        if RNS.vendor.platformutils.get_platform() == "android":
            BIND_CLASSES = ["kivymd.uix.textfield.textfield.MDTextField",]
            
            for e in self.root.ids:
                te = self.root.ids[e]
                ts = str(te).split(" ")[0].replace("<", "")

                if ts in BIND_CLASSES:
                    te.bind(focus=self.android_focus_fix)
                #     RNS.log("Bound "+str(e)+" / "+ts)
                # else:
                #     RNS.log("Did not bind "+str(e)+" / "+ts)

                # RNS.log(str(e))

        self.root.ids.screen_manager.app = self
        self.root.ids.app_version_info.text = "Sideband v"+__version__+" "+__variant__
        self.root.ids.nav_scrollview.effect_cls = ScrollEffect
        Clock.schedule_once(self.start_core, 3.5)
    
    # Part of the focus hack fix
    def android_focus_fix(self, sender, val):
        if not val:
            @run_on_ui_thread
            def fix_back_button():
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                activity.onWindowFocusChanged(False)
                activity.onWindowFocusChanged(True)

            fix_back_button()


    def keydown_event(self, instance, keyboard, keycode, text, modifiers):
        if len(modifiers) > 0 and modifiers[0] == 'ctrl' and (text == "w" or text == "q"):
            self.quit_action(self)
        if len(modifiers) > 0 and modifiers[0] == 'ctrl' and (text == "s" or text == "d"):
            if self.root.ids.screen_manager.current == "messages_screen":
                self.message_send_action()
        if len(modifiers) > 0 and modifiers[0] == 'ctrl' and (text == "l"):
            self.announces_action(self)
        if len(modifiers) > 0 and modifiers[0] == 'ctrl' and (text == "r"):
            self.conversations_action(self)
        if len(modifiers) > 0 and modifiers[0] == 'ctrl' and (text == "g"):
            self.guide_action(self)
        if len(modifiers) > 0 and modifiers[0] == 'ctrl' and (text == "n"):
            if self.root.ids.screen_manager.current == "conversations_screen":
                if not hasattr(self, "dialog_open") or not self.dialog_open:
                    self.new_conversation_action(self)

            
    def keyboard_event(self, window, key, *largs):
        # Handle escape/back
        if key == 27:
            if self.root.ids.screen_manager.current == "conversations_screen":
                if time.time() - self.last_exit_event < 2:
                    self.quit_action(self)
                else:
                    self.last_exit_event = time.time()

            else:
                self.open_conversations(direction="right")

            return True

    def widget_hide(self, w, hide=True):
        if hasattr(w, "saved_attrs"):
            if not hide:
                w.height, w.size_hint_y, w.opacity, w.disabled = w.saved_attrs
                del w.saved_attrs
        elif hide:
            w.saved_attrs = w.height, w.size_hint_y, w.opacity, w.disabled
            w.height, w.size_hint_y, w.opacity, w.disabled = 0, None, 0, True

    def quit_action(self, sender):
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.should_persist_data()

        self.root.ids.screen_manager.transition = NoTransition()
        self.root.ids.screen_manager.current = "exit_screen"
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

        self.sideband.setstate("app.running", False)
        self.sideband.setstate("app.foreground", False)

        def final_exit(dt):
            RNS.log("Stopping service...")
            self.sideband.setstate("wants.service_stop", True)
            while self.sideband.service_available():
                time.sleep(0.2)
            RNS.log("Service stopped")
            
            RNS.exit()
            MDApp.get_running_app().stop()
            Window.close()

        Clock.schedule_once(final_exit, 0.5)

    def announce_now_action(self, sender=None):
        self.sideband.lxmf_announce()

        yes_button = MDFlatButton(
            text="OK",
        )

        dialog = MDDialog(
            text="An announce for your LXMF destination was sent on all available interfaces",
            buttons=[ yes_button ],
            # elevation=0,
        )
        def dl_yes(s):
            dialog.dismiss()
        
        yes_button.bind(on_release=dl_yes)
        dialog.open()


    #################################################
    # Screens                                       #
    #################################################

    ### Messages (conversation) screen
    ######################################
    def conversation_from_announce_action(self, context_dest):
        if self.sideband.has_conversation(context_dest):
            pass
        else:
            self.sideband.create_conversation(context_dest)
            self.sideband.setstate("app.flags.new_conversations", True)

        self.open_conversation(context_dest)


    def conversation_action(self, sender):
        self.open_conversation(sender.sb_uid)

    def open_conversation(self, context_dest):
        if self.sideband.config["propagation_by_default"]:
            self.outbound_mode_propagation = True
        else:
            self.outbound_mode_propagation = False

        self.root.ids.screen_manager.transition.direction = "left"
        self.messages_view = Messages(self, context_dest)

        self.root.ids.messages_scrollview.effect_cls = ScrollEffect
        for child in self.root.ids.messages_scrollview.children:
            self.root.ids.messages_scrollview.remove_widget(child)

        list_widget = self.messages_view.get_widget()

        self.root.ids.messages_scrollview.add_widget(list_widget)
        self.root.ids.messages_scrollview.scroll_y = 0.001

        self.root.ids.messages_toolbar.title = self.sideband.peer_display_name(context_dest)
        self.root.ids.messages_scrollview.active_conversation = context_dest
        self.sideband.setstate("app.active_conversation", context_dest)

        self.root.ids.nokeys_text.text = ""
        self.message_area_detect()
        self.update_message_widgets()
        self.root.ids.message_text.disabled = False


        self.root.ids.screen_manager.current = "messages_screen"
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)
    
        self.sideband.read_conversation(context_dest)
        self.sideband.setstate("app.flags.unread_conversations", True)

    def close_messages_action(self, sender=None):
        self.open_conversations(direction="right")

    def message_send_action(self, sender=None):
        if self.root.ids.message_text.text == "":
            return

        def cb(dt):
            self.message_send_dispatch(sender)
        Clock.schedule_once(cb, 0.20)

    def message_send_dispatch(self, sender=None):
        self.root.ids.message_send_button.disabled = True
        if self.root.ids.screen_manager.current == "messages_screen":
            if self.outbound_mode_propagation and self.sideband.message_router.get_outbound_propagation_node() == None:
                self.messages_view.send_error_dialog = MDDialog(
                    text="Error: Propagated delivery was requested, but no active LXMF propagation nodes were found. Cannot send message. Wait for a Propagation Node to announce on the network, or manually specify one in the settings.",
                    buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=self.messages_view.close_send_error_dialog
                        )
                    ],
                    # elevation=0,
                )
                self.messages_view.send_error_dialog.open()

            else:
                msg_content = self.root.ids.message_text.text
                context_dest = self.root.ids.messages_scrollview.active_conversation
                if self.sideband.send_message(msg_content, context_dest, self.outbound_mode_propagation):
                    self.root.ids.message_text.text = ""
                    
                    self.root.ids.messages_scrollview.scroll_y = 0
                    self.jobs(0)
                else:
                    self.messages_view.send_error_dialog = MDDialog(
                        text="Error: Could not send the message",
                        buttons=[
                            MDFlatButton(
                                text="OK",
                                theme_text_color="Custom",
                                text_color=self.theme_cls.primary_color,
                                on_release=self.messages_view.close_send_error_dialog
                            )
                        ],
                        # elevation=0,
                    )
                    self.messages_view.send_error_dialog.open()
        
        def cb(dt):
            self.root.ids.message_send_button.disabled = False
        Clock.schedule_once(cb, 0.5)


    def message_propagation_action(self, sender):
        if self.outbound_mode_propagation:
            self.outbound_mode_propagation = False
        else:
            self.outbound_mode_propagation = True
        self.update_message_widgets()

    def update_message_widgets(self):
        toolbar_items = self.root.ids.messages_toolbar.ids.right_actions.children
        mode_item = toolbar_items[1]

        if not self.outbound_mode_propagation:
            mode_item.icon = "lan-connect"
            self.root.ids.message_text.hint_text = "Write message for direct delivery"
        else:
            mode_item.icon = "upload-network"
            self.root.ids.message_text.hint_text = "Write message for propagation"
            # self.root.ids.message_text.hint_text = "Write message for delivery via propagation nodes"
    
    def key_query_action(self, sender):
        context_dest = self.root.ids.messages_scrollview.active_conversation
        if self.sideband.request_key(context_dest):
            keys_str = "Public key information for "+RNS.prettyhexrep(context_dest)+" was requested from the network. Waiting for request to be answered."
            self.root.ids.nokeys_text.text = keys_str
        else:
            keys_str = "Could not send request. Check your connectivity and addresses."
            self.root.ids.nokeys_text.text = keys_str

    def message_area_detect(self):
        context_dest = self.root.ids.messages_scrollview.active_conversation
        if self.sideband.is_known(context_dest):
            self.root.ids.messages_scrollview.dest_known = True
            self.widget_hide(self.root.ids.message_input_part, False)
            self.widget_hide(self.root.ids.no_keys_part, True)
        else:
            self.root.ids.messages_scrollview.dest_known = False
            if self.root.ids.nokeys_text.text == "":
                keys_str = "The crytographic keys for the destination address are unknown at this time. You can wait for an announce to arrive, or query the network for the necessary keys."
                self.root.ids.nokeys_text.text = keys_str
            self.widget_hide(self.root.ids.message_input_part, True)
            self.widget_hide(self.root.ids.no_keys_part, False)


    ### Conversations screen
    ######################################       
    def conversations_action(self, sender=None):
        self.open_conversations()

    def open_conversations(self, direction="left"):
        self.root.ids.screen_manager.transition.direction = direction
        self.root.ids.nav_drawer.set_state("closed")
        
        if not self.conversations_view:
            self.conversations_view = Conversations(self)

            for child in self.root.ids.conversations_scrollview.children:
                self.root.ids.conversations_scrollview.remove_widget(child)

            self.root.ids.conversations_scrollview.effect_cls = ScrollEffect
            self.root.ids.conversations_scrollview.add_widget(self.conversations_view.get_widget())

        self.root.ids.screen_manager.current = "conversations_screen"
        self.root.ids.messages_scrollview.active_conversation = None
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)
        self.sideband.setstate("wants.clear_notifications", True)

    def connectivity_status(self, sender):
        hs = dp(22)

        connectivity_status = ""
        if RNS.vendor.platformutils.get_platform() == "android":
            connectivity_status = self.sideband.getstate("service.connectivity_status")

        else:
            if self.sideband.reticulum.is_connected_to_shared_instance:
                connectivity_status = "[size=22dp][b]Connectivity Status[/b][/size]\n\nSideband is connected via a shared Reticulum instance running on this system. Use the rnstatus utility to obtain full connectivity info."
            else:
                connectivity_status = "[size=22dp][b]Connectivity Status[/b][/size]\n\nSideband is currently running a standalone or master Reticulum instance on this system. Use the rnstatus utility to obtain full connectivity info."

        yes_button = MDFlatButton(
            text="OK",
        )
        dialog = MDDialog(
            text=connectivity_status,
            buttons=[ yes_button ],
            # elevation=0,
        )
        def dl_yes(s):
            dialog.dismiss()
        
        yes_button.bind(on_release=dl_yes)
        dialog.open()

    def lxmf_sync_action(self, sender):
        if self.sideband.message_router.get_outbound_propagation_node() == None:
            yes_button = MDFlatButton(
                text="OK",
            )

            dialog = MDDialog(
                text="No active LXMF propagation nodes were found. Cannot fetch messages. Wait for a Propagation Node to announce on the network, or manually specify one in the settings.",
                buttons=[ yes_button ],
                # elevation=0,
            )
            def dl_yes(s):
                dialog.dismiss()
            
            yes_button.bind(on_release=dl_yes)
            dialog.open()
        else:
            if self.sideband.config["lxmf_sync_limit"]:
                sl = self.sideband.config["lxmf_sync_max"]
            else:
                sl = None

            self.sideband.setpersistent("lxmf.lastsync", time.time())
            self.sideband.setpersistent("lxmf.syncretrying", False)
            self.sideband.request_lxmf_sync(limit=sl)

            close_button = MDRectangleFlatButton(text="Close",font_size=sp(18))
            stop_button = MDRectangleFlatButton(text="Stop",font_size=sp(18), theme_text_color="Custom", line_color=self.color_reject, text_color=self.color_reject)
            dialog_content = MsgSync()
            dialog = MDDialog(
                title="LXMF Sync via "+RNS.prettyhexrep(self.sideband.message_router.get_outbound_propagation_node()),
                type="custom",
                content_cls=dialog_content,
                buttons=[ stop_button, close_button ],
                # elevation=0,
            )
            dialog.d_content = dialog_content
            def dl_close(s):                
                self.sideband.setstate("app.flags.lxmf_sync_dialog_open", False)
                dialog.dismiss()
                # self.sideband.cancel_lxmf_sync()

            def dl_stop(s):                
                # self.sideband.setstate("app.flags.lxmf_sync_dialog_open", False)
                # dialog.dismiss()
                self.sideband.cancel_lxmf_sync()
                def cb(dt):
                    self.widget_hide(self.sync_dialog.stop_button, True)
                Clock.schedule_once(cb, 0.25)

            close_button.bind(on_release=dl_close)
            stop_button.bind(on_release=dl_stop)
            self.sideband.setstate("app.flags.lxmf_sync_dialog_open", True)
            self.sync_dialog = dialog_content
            self.sync_dialog.stop_button = stop_button
            dialog.open()
            dialog_content.ids.sync_progress.value = self.sideband.get_sync_progress()*100
            dialog_content.ids.sync_status.text = self.sideband.get_sync_status()

    def new_conversation_action(self, sender=None):
        try:
            yes_button = MDFlatButton(
                text="OK",
                font_size=dp(20),
            )

            cancel_button = MDRectangleFlatButton(text="Cancel",font_size=sp(18))
            create_button = MDRectangleFlatButton(text="Create",font_size=sp(18), theme_text_color="Custom", line_color=self.color_accept, text_color=self.color_accept)
            
            dialog_content = NewConv()
            dialog = MDDialog(
                title="New Conversation",
                type="custom",
                content_cls=dialog_content,
                buttons=[ create_button, cancel_button ],
                # elevation=0,
            )
            dialog.d_content = dialog_content
            def dl_yes(s):
                new_result = False
                try:
                    n_address = dialog.d_content.ids["n_address_field"].text
                    n_name = dialog.d_content.ids["n_name_field"].text
                    n_trusted = dialog.d_content.ids["n_trusted"].active
                    new_result = self.sideband.new_conversation(n_address, n_name, n_trusted)

                except Exception as e:
                    RNS.log("Error while creating conversation: "+str(e), RNS.LOG_ERROR)

                if new_result:
                    dialog.d_content.ids["n_address_field"].error = False
                    dialog.dismiss()
                    if self.conversations_view != None:
                        self.conversations_view.update()
                else:
                    dialog.d_content.ids["n_address_field"].error = True
                    # dialog.d_content.ids["n_error_field"].text = "Could not create conversation. Check your input."

            def dl_no(s):
                dialog.dismiss()

            def dl_ds(s):
                self.dialog_open = False

            create_button.bind(on_release=dl_yes)
            cancel_button.bind(on_release=dl_no)

            dialog.bind(on_dismiss=dl_ds)
            dialog.open()
            self.dialog_open = True

        except Exception as e:
            RNS.log("Error while creating new conversation dialog: "+str(e), RNS.LOG_ERROR)

    ### Information/version screen
    ######################################
    def information_action(self, sender=None):
        def link_exec(sender=None, event=None):
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        info = "This is Sideband v"+__version__+" "+__variant__+", on RNS v"+RNS.__version__+"\n\nHumbly build using the following open components:\n\n - [b]Reticulum[/b] (MIT License)\n - [b]LXMF[/b] (MIT License)\n - [b]KivyMD[/b] (MIT License)\n - [b]Kivy[/b] (MIT License)\n - [b]Python[/b] (PSF License)"+"\n\nGo to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project.\n\nThe Sideband app is Copyright (c) 2022 Mark Qvist / unsigned.io\n\nPermission is granted to freely share and distribute binary copies of Sideband v"+__version__+" "+__variant__+", so long as no payment or compensation is charged for said distribution or sharing.\n\nIf you were charged or paid anything for this copy of Sideband, please report it to [b]license@unsigned.io[/b].\n\nTHIS IS EXPERIMENTAL SOFTWARE - USE AT YOUR OWN RISK AND RESPONSIBILITY"
        self.root.ids.information_info.text = info
        self.root.ids.information_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "information_screen"
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

    def close_information_action(self, sender=None):
        self.open_conversations(direction="right")


    ### Settings screen
    ######################################
    def settings_action(self, sender=None):
        self.root.ids.screen_manager.transition.direction = "left"

        self.settings_init()

        self.root.ids.screen_manager.current = "settings_screen"
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

    def settings_init(self, sender=None):
        if not self.settings_ready:
            def save_disp_name(sender=None, event=None):
                in_name = self.root.ids.settings_display_name.text
                if in_name == "":
                    new_name = "Anonymous Peer"
                else:
                    new_name = in_name

                self.sideband.config["display_name"] = new_name
                self.sideband.save_configuration()

            def save_prop_addr(sender=None, event=None):
                in_addr = self.root.ids.settings_propagation_node_address.text

                new_addr = None
                if in_addr == "":
                    new_addr = None
                    self.root.ids.settings_propagation_node_address.error = False
                else:
                    if len(in_addr) != RNS.Reticulum.TRUNCATED_HASHLENGTH//8*2:
                        new_addr = None
                    else:
                        try:
                            new_addr = bytes.fromhex(in_addr)
                        except Exception as e:
                            new_addr = None

                    if new_addr == None:
                        self.root.ids.settings_propagation_node_address.error = True
                    else:
                        self.root.ids.settings_propagation_node_address.error = False


                self.sideband.config["lxmf_propagation_node"] = new_addr
                self.sideband.set_active_propagation_node(self.sideband.config["lxmf_propagation_node"])

            def save_dark_ui(sender=None, event=None):
                self.sideband.config["dark_ui"] = self.root.ids.settings_dark_ui.active
                self.sideband.save_configuration()
                self.update_ui_theme()

            def save_notifications_on(sender=None, event=None):
                self.sideband.config["notifications_on"] = self.root.ids.settings_notifications_on.active
                self.sideband.save_configuration()

            def save_start_announce(sender=None, event=None):
                self.sideband.config["start_announce"] = self.root.ids.settings_start_announce.active
                self.sideband.save_configuration()

            def save_lxmf_delivery_by_default(sender=None, event=None):
                self.sideband.config["propagation_by_default"] = self.root.ids.settings_lxmf_delivery_by_default.active
                self.sideband.save_configuration()

            def save_lxmf_sync_limit(sender=None, event=None):
                self.sideband.config["lxmf_sync_limit"] = self.root.ids.settings_lxmf_sync_limit.active
                self.sideband.save_configuration()

            def save_lxmf_periodic_sync(sender=None, event=None, save=True):
                if self.root.ids.settings_lxmf_periodic_sync.active:
                    self.widget_hide(self.root.ids.lxmf_syncslider_container, False)
                else:
                    self.widget_hide(self.root.ids.lxmf_syncslider_container, True)

                if save:
                    self.sideband.config["lxmf_periodic_sync"] = self.root.ids.settings_lxmf_periodic_sync.active
                    self.sideband.save_configuration()

            def sync_interval_change(sender=None, event=None, save=True):
                interval = (self.root.ids.settings_lxmf_sync_interval.value//300)*300
                interval_text = RNS.prettytime(interval)
                pre = self.root.ids.settings_lxmf_sync_periodic.text
                self.root.ids.settings_lxmf_sync_periodic.text = "Auto sync every "+interval_text
                if save:
                    self.sideband.config["lxmf_sync_interval"] = interval
                    self.sideband.save_configuration()

            self.root.ids.settings_lxmf_address.text = RNS.hexrep(self.sideband.lxmf_destination.hash, delimit=False)

            self.root.ids.settings_display_name.text = self.sideband.config["display_name"]
            self.root.ids.settings_display_name.bind(on_text_validate=save_disp_name)
            self.root.ids.settings_display_name.bind(focus=save_disp_name)

            if self.sideband.config["lxmf_propagation_node"] == None:
                prop_node_addr = ""
            else:
                prop_node_addr = RNS.hexrep(self.sideband.config["lxmf_propagation_node"], delimit=False)

            self.root.ids.settings_propagation_node_address.text = prop_node_addr
            self.root.ids.settings_propagation_node_address.bind(on_text_validate=save_prop_addr)
            self.root.ids.settings_propagation_node_address.bind(focus=save_prop_addr)

            self.root.ids.settings_notifications_on.active = self.sideband.config["notifications_on"]
            self.root.ids.settings_notifications_on.bind(active=save_notifications_on)

            self.root.ids.settings_dark_ui.active = self.sideband.config["dark_ui"]
            self.root.ids.settings_dark_ui.bind(active=save_dark_ui)

            self.root.ids.settings_start_announce.active = self.sideband.config["start_announce"]
            self.root.ids.settings_start_announce.bind(active=save_start_announce)

            self.root.ids.settings_lxmf_delivery_by_default.active = self.sideband.config["propagation_by_default"]
            self.root.ids.settings_lxmf_delivery_by_default.bind(active=save_lxmf_delivery_by_default)

            self.root.ids.settings_lxmf_periodic_sync.active = self.sideband.config["lxmf_periodic_sync"]
            self.root.ids.settings_lxmf_periodic_sync.bind(active=save_lxmf_periodic_sync)
            save_lxmf_periodic_sync(save=False)

            def sync_interval_change_cb(sender=None, event=None):
                sync_interval_change(sender=sender, event=event, save=False)
            self.root.ids.settings_lxmf_sync_interval.bind(value=sync_interval_change_cb)
            self.root.ids.settings_lxmf_sync_interval.bind(on_touch_up=sync_interval_change)
            self.root.ids.settings_lxmf_sync_interval.value = self.sideband.config["lxmf_sync_interval"]
            sync_interval_change(save=False)


            if self.sideband.config["lxmf_sync_limit"] == None or self.sideband.config["lxmf_sync_limit"] == False:
                sync_limit = False
            else:
                sync_limit = True

            self.root.ids.settings_lxmf_sync_limit.active = sync_limit
            self.root.ids.settings_lxmf_sync_limit.bind(active=save_lxmf_sync_limit)
            self.settings_ready = True

    def close_settings_action(self, sender=None):
        self.open_conversations(direction="right")


    ### Connectivity screen
    ######################################
    def connectivity_action(self, sender=None):
        self.connectivity_init()
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "connectivity_screen"
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

    def connectivity_init(self, sender=None):
        if not self.connectivity_ready:
            def con_hide_settings():
                self.widget_hide(self.root.ids.connectivity_use_local)
                self.widget_hide(self.root.ids.connectivity_local_groupid)
                self.widget_hide(self.root.ids.connectivity_local_ifac_netname)
                self.widget_hide(self.root.ids.connectivity_local_ifac_passphrase)
                self.widget_hide(self.root.ids.connectivity_use_tcp)
                self.widget_hide(self.root.ids.connectivity_tcp_host)
                self.widget_hide(self.root.ids.connectivity_tcp_port)
                self.widget_hide(self.root.ids.connectivity_tcp_ifac_netname)
                self.widget_hide(self.root.ids.connectivity_tcp_ifac_passphrase)
                self.widget_hide(self.root.ids.connectivity_use_i2p)
                self.widget_hide(self.root.ids.connectivity_i2p_b32)
                self.widget_hide(self.root.ids.connectivity_i2p_ifac_netname)
                self.widget_hide(self.root.ids.connectivity_i2p_ifac_passphrase)
                self.widget_hide(self.root.ids.connectivity_tcp_label)
                self.widget_hide(self.root.ids.connectivity_local_label)
                self.widget_hide(self.root.ids.connectivity_i2p_label)
                self.widget_hide(self.root.ids.connectivity_rnode_label)
                self.widget_hide(self.root.ids.connectivity_use_rnode)
                self.widget_hide(self.root.ids.connectivity_rnode_cid)
                self.widget_hide(self.root.ids.connectivity_modem_label)
                self.widget_hide(self.root.ids.connectivity_use_modem)
                self.widget_hide(self.root.ids.connectivity_modem_fields)
                self.widget_hide(self.root.ids.connectivity_bluetooth_label)
                self.widget_hide(self.root.ids.connectivity_use_bluetooth)
                self.widget_hide(self.root.ids.connectivity_bluetooth_fields)
                self.widget_hide(self.root.ids.connectivity_transport_label)
                self.widget_hide(self.root.ids.connectivity_enable_transport)
                # self.widget_hide(self.root.ids.rnode_support_info)

            def con_collapse_local(collapse=True):
                self.widget_hide(self.root.ids.connectivity_local_fields, collapse)
                
            def con_collapse_tcp(collapse=True):
                self.widget_hide(self.root.ids.connectivity_tcp_fields, collapse)
                
            def con_collapse_i2p(collapse=True):
                self.widget_hide(self.root.ids.connectivity_i2p_fields, collapse)
                
            def con_collapse_bluetooth(collapse=True):
                self.widget_hide(self.root.ids.connectivity_bluetooth_fields, collapse)
                
            def con_collapse_rnode(collapse=True):
                self.widget_hide(self.root.ids.connectivity_rnode_fields, collapse)
                
            def con_collapse_modem(collapse=True):
                self.widget_hide(self.root.ids.connectivity_modem_fields, collapse)
                
            def save_connectivity(sender=None, event=None):
                self.sideband.config["connect_local"] = self.root.ids.connectivity_use_local.active
                self.sideband.config["connect_local_groupid"] = self.root.ids.connectivity_local_groupid.text
                self.sideband.config["connect_local_ifac_netname"] = self.root.ids.connectivity_local_ifac_netname.text
                self.sideband.config["connect_local_ifac_passphrase"] = self.root.ids.connectivity_local_ifac_passphrase.text
                self.sideband.config["connect_tcp"] = self.root.ids.connectivity_use_tcp.active
                self.sideband.config["connect_tcp_host"] = self.root.ids.connectivity_tcp_host.text
                self.sideband.config["connect_tcp_port"] = self.root.ids.connectivity_tcp_port.text
                self.sideband.config["connect_tcp_ifac_netname"] = self.root.ids.connectivity_tcp_ifac_netname.text
                self.sideband.config["connect_tcp_ifac_passphrase"] = self.root.ids.connectivity_tcp_ifac_passphrase.text
                self.sideband.config["connect_i2p"] = self.root.ids.connectivity_use_i2p.active
                self.sideband.config["connect_i2p_b32"] = self.root.ids.connectivity_i2p_b32.text
                self.sideband.config["connect_i2p_ifac_netname"] = self.root.ids.connectivity_i2p_ifac_netname.text
                self.sideband.config["connect_i2p_ifac_passphrase"] = self.root.ids.connectivity_i2p_ifac_passphrase.text

                con_collapse_local(collapse=not self.root.ids.connectivity_use_local.active)
                con_collapse_tcp(collapse=not self.root.ids.connectivity_use_tcp.active)
                con_collapse_i2p(collapse=not self.root.ids.connectivity_use_i2p.active)
                con_collapse_rnode(collapse=not self.root.ids.connectivity_use_rnode.active)
                con_collapse_bluetooth(collapse=not self.root.ids.connectivity_use_bluetooth.active)
                con_collapse_modem(collapse=not self.root.ids.connectivity_use_modem.active)

                self.sideband.save_configuration()

            if RNS.vendor.platformutils.get_platform() == "android":
                if not self.sideband.getpersistent("service.is_controlling_connectivity"):
                    info =  "Sideband is connected via a shared Reticulum instance running on this system.\n\n"
                    info += "To configure connectivity, edit the relevant configuration file for the instance."
                    self.root.ids.connectivity_info.text = info
                    con_hide_settings()

                else:
                    info =  "By default, Sideband will try to discover and connect to any available Reticulum networks via active WiFi and/or Ethernet interfaces. If any Reticulum Transport Instances are found, Sideband will use these to connect to wider Reticulum networks. You can disable this behaviour if you don't want it.\n\n"
                    info += "You can also connect to a network via a remote or local Reticulum instance using TCP or I2P. [b]Please Note![/b] Connecting via I2P requires that you already have I2P running on your device, and that the SAM API is enabled.\n\n"
                    info += "For changes to connectivity to take effect, you must shut down and restart Sideband.\n"
                    self.root.ids.connectivity_info.text = info

                    self.root.ids.connectivity_use_local.active = self.sideband.config["connect_local"]
                    con_collapse_local(collapse=not self.root.ids.connectivity_use_local.active)
                    self.root.ids.connectivity_local_groupid.text = self.sideband.config["connect_local_groupid"]
                    self.root.ids.connectivity_local_ifac_netname.text = self.sideband.config["connect_local_ifac_netname"]
                    self.root.ids.connectivity_local_ifac_passphrase.text = self.sideband.config["connect_local_ifac_passphrase"]

                    self.root.ids.connectivity_use_tcp.active = self.sideband.config["connect_tcp"]
                    con_collapse_tcp(collapse=not self.root.ids.connectivity_use_tcp.active)
                    self.root.ids.connectivity_tcp_host.text = self.sideband.config["connect_tcp_host"]
                    self.root.ids.connectivity_tcp_port.text = self.sideband.config["connect_tcp_port"]
                    self.root.ids.connectivity_tcp_ifac_netname.text = self.sideband.config["connect_tcp_ifac_netname"]
                    self.root.ids.connectivity_tcp_ifac_passphrase.text = self.sideband.config["connect_tcp_ifac_passphrase"]

                    self.root.ids.connectivity_use_i2p.active = self.sideband.config["connect_i2p"]
                    con_collapse_i2p(collapse=not self.root.ids.connectivity_use_i2p.active)
                    self.root.ids.connectivity_i2p_b32.text = self.sideband.config["connect_i2p_b32"]
                    self.root.ids.connectivity_i2p_ifac_netname.text = self.sideband.config["connect_i2p_ifac_netname"]
                    self.root.ids.connectivity_i2p_ifac_passphrase.text = self.sideband.config["connect_i2p_ifac_passphrase"]

                    self.root.ids.connectivity_use_rnode.active = False
                    con_collapse_rnode(collapse=not self.root.ids.connectivity_use_rnode.active)

                    self.root.ids.connectivity_use_bluetooth.active = False
                    con_collapse_bluetooth(collapse=not self.root.ids.connectivity_use_bluetooth.active)

                    self.root.ids.connectivity_use_modem.active = False
                    con_collapse_modem(collapse=not self.root.ids.connectivity_use_modem.active)

                    self.root.ids.connectivity_use_local.bind(active=save_connectivity)
                    self.root.ids.connectivity_local_groupid.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_local_ifac_netname.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_local_ifac_passphrase.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_use_tcp.bind(active=save_connectivity)
                    self.root.ids.connectivity_tcp_host.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_tcp_port.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_tcp_ifac_netname.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_tcp_ifac_passphrase.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_use_i2p.bind(active=save_connectivity)
                    self.root.ids.connectivity_i2p_b32.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_i2p_ifac_netname.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_i2p_ifac_passphrase.bind(on_text_validate=save_connectivity)
                    self.root.ids.connectivity_use_rnode.bind(active=save_connectivity)
                    self.root.ids.connectivity_use_bluetooth.bind(active=save_connectivity)

            else:
                info = ""

                if self.sideband.reticulum.is_connected_to_shared_instance:
                    info =  "Sideband is connected via a shared Reticulum instance running on this system.\n\n"
                    info += "To get connectivity status, use the rnstatus utility.\n\n"
                    info += "To configure connectivity, edit the configuration file located at:\n\n"
                    info += str(RNS.Reticulum.configpath)
                else:
                    info =  "Sideband is currently running a standalone or master Reticulum instance on this system.\n\n"
                    info += "To get connectivity status, use the rnstatus utility.\n\n"
                    info += "To configure connectivity, edit the configuration file located at:\n\n"
                    info += str(RNS.Reticulum.configpath)

                self.root.ids.connectivity_info.text = info

                con_hide_settings()

        self.connectivity_ready = True

    def close_connectivity_action(self, sender=None):
        self.open_conversations(direction="right")

    ### Announce Stream screen
    ######################################
    def init_announces_view(self, sender=None):
        if not self.announces_view:
            self.announces_view = Announces(self)
            self.sideband.setstate("app.flags.new_announces", True)

            for child in self.root.ids.announces_scrollview.children:
                self.root.ids.announces_scrollview.remove_widget(child)

            self.root.ids.announces_scrollview.effect_cls = ScrollEffect
            self.root.ids.announces_scrollview.add_widget(self.announces_view.get_widget())

    def announces_action(self, sender=None):
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.nav_drawer.set_state("closed")
        
        if self.sideband.getstate("app.flags.new_announces"):
            self.init_announces_view()
            self.announces_view.update()

        self.root.ids.screen_manager.current = "announces_screen"
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

    def close_announces_action(self, sender=None):
        self.open_conversations(direction="right")

    def announce_filter_action(self, sender=None):
        pass

    def screen_transition_complete(self, sender):
        if self.root.ids.screen_manager.current == "announces_screen":
            pass
        if self.root.ids.screen_manager.current == "conversations_screen":
            pass

    ### Keys screen
    ######################################
    def keys_action(self, sender=None):
        # def link_exec(sender=None, event=None):
        #     import webbrowser
        #     webbrowser.open("https://unsigned.io/sideband")
        # self.root.ids.keys_info.bind(on_ref_press=link_exec)

        info = "Your primary encryption keys are stored in a Reticulum Identity within the Sideband app. If you want to backup this Identity for later use on this or another device, you can export it as a plain text blob, with the key data encoded in Base32 format. This will allow you to restore your address in Sideband or other LXMF clients at a later point.\n\n[b]Warning![/b] Anyone that gets access to the key data will be able to control your LXMF address, impersonate you, and read your messages. In is [b]extremely important[/b] that you keep the Identity data secure if you export it.\n\nBefore displaying or exporting your Identity data, make sure that no machine or person in your vicinity is able to see, copy or record your device screen or similar."

        if not RNS.vendor.platformutils.get_platform() == "android":
            self.widget_hide(self.root.ids.keys_share)

        self.root.ids.keys_info.text = info
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "keys_screen"
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

    def close_keys_action(self, sender=None):
        self.open_conversations(direction="right")

    def identity_display_action(self, sender=None):
        yes_button = MDFlatButton(
            text="OK",
        )

        dialog = MDDialog(
            text="Your Identity key, in base32 format is as follows:\n\n[b]"+str(base64.b32encode(self.sideband.identity.get_private_key()).decode("utf-8"))+"[/b]",
            buttons=[ yes_button ],
            # elevation=0,
        )
        def dl_yes(s):
            dialog.dismiss()
        
        yes_button.bind(on_release=dl_yes)
        dialog.open()

    def identity_copy_action(self, sender=None):
        c_yes_button = MDFlatButton(text="Yes, copy my key")
        c_no_button = MDFlatButton(text="No, go back")
        c_dialog = MDDialog(text="[b]Caution![/b]\n\nYour Identity key will be copied to the system clipboard. Take extreme care that no untrusted app steals your key by reading the clipboard data. Clear the system clipboard immediately after pasting your key where you need it.\n\nAre you sure that you wish to proceed?", buttons=[ c_no_button, c_yes_button ])
        def c_dl_no(s):
            c_dialog.dismiss()
        def c_dl_yes(s):
            c_dialog.dismiss()
            yes_button = MDFlatButton(text="OK")
            dialog = MDDialog(text="Your Identity key was copied to the system clipboard", buttons=[ yes_button ])
            def dl_yes(s):
                dialog.dismiss()
            yes_button.bind(on_release=dl_yes)

            Clipboard.copy(str(base64.b32encode(self.sideband.identity.get_private_key()).decode("utf-8")))
            dialog.open()
        
        c_yes_button.bind(on_release=c_dl_yes)
        c_no_button.bind(on_release=c_dl_no)

        c_dialog.open()

    def identity_share_action(self, sender=None):
        if RNS.vendor.platformutils.get_platform() == "android":
            self.share_text(str(base64.b32encode(self.sideband.identity.get_private_key()).decode("utf-8")))

    def identity_restore_action(self, sender=None):
        c_yes_button = MDFlatButton(text="Yes, import the key")
        c_no_button = MDFlatButton(text="No, go back")
        c_dialog = MDDialog(text="[b]Caution![/b]\n\nYou are about to import a new Identity key into Sideband. The currently active key will be irreversibly destroyed, and you will loose your LXMF address if you have not already backed up your current Identity key.\n\nAre you sure that you wish to import the key?", buttons=[ c_no_button, c_yes_button ])
        def c_dl_no(s):
            c_dialog.dismiss()
        def c_dl_yes(s):
            c_dialog.dismiss()
            b32_text = self.root.ids.key_restore_text.text
        
            try:
                key_bytes = base64.b32decode(b32_text)
                new_id = RNS.Identity.from_bytes(key_bytes)

                if new_id != None:
                    new_id.to_file(self.sideband.identity_path)

                yes_button = MDFlatButton(text="OK")
                dialog = MDDialog(text="[b]The provided Identity key data was imported[/b]\n\nThe app will now exit. Please restart Sideband to use the new Identity.", buttons=[ yes_button ])
                def dl_yes(s):
                    dialog.dismiss()
                    self.quit_action(sender=self)
                yes_button.bind(on_release=dl_yes)
                dialog.open()

            except Exception as e:
                yes_button = MDFlatButton(text="OK")
                dialog = MDDialog(text="[b]The provided Identity key data was not valid[/b]\n\nThe error reported by Reticulum was:\n\n[i]"+str(e)+"[/i]\n\nNo Identity was imported into Sideband.", buttons=[ yes_button ])
                def dl_yes(s):
                    dialog.dismiss()
                yes_button.bind(on_release=dl_yes)
                dialog.open()
            
        
        c_yes_button.bind(on_release=c_dl_yes)
        c_no_button.bind(on_release=c_dl_no)

        c_dialog.open()


    ### Guide screen
    ######################################
    def close_guide_action(self, sender=None):
        self.open_conversations(direction="right")
    
    def guide_action(self, sender=None):
        def link_exec(sender=None, event=None):
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        guide_text1 = """
[size=18dp][b]Introduction[/b][/size][size=5dp]\n \n[/size]Welcome to [i]Sideband[/i], an LXMF client for Android, Linux and macOS. With Sideband, you can communicate with other people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, or anything else Reticulum supports.

This short guide will give you a basic introduction to the concepts that underpin Sideband and LXMF (which is the protocol that Sideband uses to communicate). If you are not already familiar with LXMF and Reticulum, it is probably a good idea to read this guide, since Sideband is very different from other messaging apps."""
        guide_text2 = """
[size=18dp][b]Communication Without Subjection[/b][/size][size=5dp]\n \n[/size]Sideband is completely free, permission-less, anonymous and infrastructure-less. Sideband uses the peer-to-peer and distributed messaging system LXMF. There is no sign-up, no service providers, no "end-user license agreements", no data theft and no surveillance. You own the system.

This also means that Sideband operates differently than what you might be used to. It does not need a connection to a server on the Internet to function, and you do not have an account anywhere."""
        
        guide_text3 = """
[size=18dp][b]Operating Principles[/b][/size][size=5dp]\n \n[/size]When Sideband is started on your device for the first time, it randomly generates a set of cryptographic keys. These keys are then used to create an LXMF address for your use. Any other endpoint in [i]any[/i] Reticulum network will be able to send data to this address, as long as there is [i]some sort of physical connection[/i] between your device and the remote endpoint. You can also move around to other Reticulum networks with this address, even ones that were never connected to the network the address was created on, or that didn't exist when the address was created. The address is yours to keep and control for as long (or short) a time you need it, and you can always delete it and create a new one."""
        
        guide_text4 = """
[size=18dp][b]Becoming Reachable[/b][/size][size=5dp]\n \n[/size]To establish reachability for any Reticulum address on a network, an [i]announce[/i] must be sent. Sideband does not do this automatically by default, but can be configured to do so every time the program starts. To send an announce manually, press the [i]Announce[/i] button in the [i]Conversations[/i] section of the program. When you send an announce, you make your LXMF address reachable for real-time messaging to the entire network you are connected to. Even in very large networks, you can expect global reachability for your address to be established in under a minute.

If you don't move to other places in the network, and keep connected through the same hubs or gateways, it is generally not necessary to send an announce more often than once every week. If you change your entry point to the network, you may want to send an announce, or you may just want to stay quiet."""

        guide_text5 = """
[size=18dp][b]Relax & Disconnect[/b][/size][size=5dp]\n \n[/size]If you are not connected to the network, it is still possible for other people to message you, as long as one or more [i]Propagation Nodes[/i] exist on the network. These nodes pick up and hold encrypted in-transit messages for offline users. Messages are always encrypted before leaving the originators device, and nobody else than the intended recipient can decrypt messages in transit.

The Propagation Nodes also distribute copies of messages between each other, such that even the failure of almost every node in the network will still allow users to sync their waiting messages. If all Propagation Nodes disappear or are destroyed, users can still communicate directly. Reticulum and LXMF will degrade gracefully all the way down to single users communicating directly via long-range data radios. Anyone can start up new propagation nodes and integrate them into existing networks without permission or coordination. Even a small and cheap device like a Rasperry Pi can handle messages for millions of users. LXMF networks are designed to be quite resilient, as long as there are people using them."""

        guide_text6 = """
[size=18dp][b]Packets Find A Way[/b][/size][size=5dp]\n \n[/size]Connections in Reticulum networks can be wired or wireless, span many intermediary hops, run over fast links or ultra-low bandwidth radio, tunnel over the Invisible Internet (I2P), private networks, satellite connections, serial lines or anything else that Reticulum can carry data over. In most cases it will not be possible to know what path data takes in a Reticulum network, and no transmitted packets carries any identifying characteristics, apart from a destination address. There is no source addresses in Reticulum. As long as you do not reveal any connecting details between your person and your LXMF address, you can remain anonymous. Sending messages to others does not reveal [i]your[/i] address to anyone else than the intended recipient."""

        guide_text7 = """
[size=18dp][b]Be Yourself, Be Unknown, Stay Free[/b][/size][size=5dp]\n \n[/size]Even with the above characteristics in mind, you [b]must remember[/b] that LXMF and Reticulum is not a technology that can guarantee anonymising connections that are already de-anonymised! If you use Sideband to connect to TCP Reticulum hubs over the clear Internet, from a network that can be tied to your personal identity, an adversary may learn that you are generating LXMF traffic. If you want to avoid this, it is recommended to use I2P to connect to Reticulum hubs on the Internet. Or only connecting from within pure Reticulum networks, that take one or more hops to reach connections that span the Internet. This is a complex topic, with many more nuances than can not be covered here. You are encouraged to ask on the various Reticulum discussion forums if you are in doubt.

If you use Reticulum and LXMF on hardware that does not carry any identifiers tied to you, it is possible to establish a completely free and anonymous communication system with Reticulum and LXMF clients."""
        
        guide_text8 = """
[size=18dp][b]Keyboard Shortcuts[/b][/size][size=5dp]\n \n[/size] - Ctrl+Q or Ctrl-W Shut down Sideband
 - Ctrl-D or Ctrl-S Send message
 - Ctrl-R Show Conversations
 - Ctrl-L Show Announce Stream
 - Ctrl-N New conversation
 - Ctrl-G Show guide"""
        
        guide_text9 = """
[size=18dp][b]Sow Seeds Of Freedom[/b][/size][size=5dp]\n \n[/size]It took me more than six years to design and built the entire ecosystem of software and hardware that makes this possible. If this project is valuable to you, please go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project with a donation. Every donation directly makes the entire Reticulum project possible.

Thank you very much for using Free Communications Systems.
"""
        info1 = guide_text1
        info2 = guide_text2
        info3 = guide_text3
        info4 = guide_text4
        info5 = guide_text5
        info6 = guide_text6
        info7 = guide_text7
        info8 = guide_text8
        info9 = guide_text9

        if self.theme_cls.theme_style == "Dark":
            info1 = "[color=#"+dark_theme_text_color+"]"+info1+"[/color]"
            info2 = "[color=#"+dark_theme_text_color+"]"+info2+"[/color]"
            info3 = "[color=#"+dark_theme_text_color+"]"+info3+"[/color]"
            info4 = "[color=#"+dark_theme_text_color+"]"+info4+"[/color]"
            info5 = "[color=#"+dark_theme_text_color+"]"+info5+"[/color]"
            info6 = "[color=#"+dark_theme_text_color+"]"+info6+"[/color]"
            info7 = "[color=#"+dark_theme_text_color+"]"+info7+"[/color]"
            info8 = "[color=#"+dark_theme_text_color+"]"+info8+"[/color]"
            info9 = "[color=#"+dark_theme_text_color+"]"+info9+"[/color]"
        self.root.ids.guide_info1.text = info1
        self.root.ids.guide_info2.text = info2
        self.root.ids.guide_info3.text = info3
        self.root.ids.guide_info4.text = info4
        self.root.ids.guide_info5.text = info5
        self.root.ids.guide_info6.text = info6
        self.root.ids.guide_info7.text = info7
        self.root.ids.guide_info8.text = info8
        self.root.ids.guide_info9.text = info9
        self.root.ids.guide_info9.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "guide_screen"
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)


    #################################################
    # Unimplemented Screens                         #
    #################################################

    def map_action(self, sender=None):
        def link_exec(sender=None, event=None):
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        info = "The [b]Local Area[/b] feature is not yet implemented in Sideband.\n\nWant it faster? Go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project."
        if self.theme_cls.theme_style == "Dark":
            info = "[color=#"+dark_theme_text_color+"]"+info+"[/color]"
        self.root.ids.map_info.text = info
        self.root.ids.map_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "map_screen"
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

    def broadcasts_action(self, sender=None):
        def link_exec(sender=None, event=None):
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        info = "The [b]Local Broadcasts[/b] feature will allow you to send and listen for local broadcast transmissions on connected radio, LoRa and WiFi interfaces.\n\n[b]Local Broadcasts[/b] makes it easy to establish public information exchange with anyone in direct radio range, or even with large areas far away using the [i]Remote Broadcast Repeater[/i] feature.\n\nThese features are not yet implemented in Sideband.\n\nWant it faster? Go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project."
        if self.theme_cls.theme_style == "Dark":
            info = "[color=#"+dark_theme_text_color+"]"+info+"[/color]"
        self.root.ids.broadcasts_info.text = info
        self.root.ids.broadcasts_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "broadcasts_screen"
        self.root.ids.nav_drawer.set_state("closed")
        self.sideband.setstate("app.displaying", self.root.ids.screen_manager.current)

    

def run():
    SidebandApp().run()

if __name__ == "__main__":
    run()