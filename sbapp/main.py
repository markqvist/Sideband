import RNS
import LXMF
import time
import sys
import os

from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["error"])

if RNS.vendor.platformutils.get_platform() != "android":
    local = os.path.dirname(__file__)
    sys.path.append(local)

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.lang.builder import Builder

if RNS.vendor.platformutils.get_platform() == "android":
    from sideband.core import SidebandCore

    from ui.layouts import root_layout
    from ui.conversations import Conversations, MsgSync, NewConv
    from ui.announces import Announces
    from ui.messages import Messages, ts_format
    from ui.helpers import ContentNavigationDrawer, DrawerList, IconListItem

else:
    from .sideband.core import SidebandCore

    from .ui.layouts import root_layout
    from .ui.conversations import Conversations, MsgSync, NewConv
    from .ui.announces import Announces
    from .ui.messages import Messages, ts_format
    from .ui.helpers import ContentNavigationDrawer, DrawerList, IconListItem

from kivy.metrics import dp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

__version__ = "0.1.8"
__variant__ = "beta"

if RNS.vendor.platformutils.get_platform() == "android":
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

class SidebandApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Sideband"

        self.sideband = SidebandCore(self)
        self.conversations_view = None

        self.flag_new_conversations = False
        self.flag_unread_conversations = False
        self.flag_new_announces = False
        self.lxmf_sync_dialog_open = False
        self.sync_dialog = None


        Window.softinput_mode = "below_target"
        self.icon = self.sideband.asset_dir+"/images/icon.png"

    #################################################
    # General helpers                               #
    #################################################

    def build(self):
        FONT_PATH = self.sideband.asset_dir+"/fonts"
        # self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        # self.theme_cls.theme_style = "Light"
        screen = Builder.load_string(root_layout)

        return screen

    def jobs(self, delta_time):
        if self.root.ids.screen_manager.current == "messages_screen":
            self.messages_view.update()

            if not self.root.ids.messages_scrollview.dest_known:
                self.message_area_detect()

        elif self.root.ids.screen_manager.current == "conversations_screen":
            if self.flag_new_conversations:
                RNS.log("Updating because of new conversations flag")
                if self.conversations_view != None:
                    self.conversations_view.update()

            if self.flag_unread_conversations:
                RNS.log("Updating because of unread messages flag")
                if self.conversations_view != None:
                    self.conversations_view.update()

            if self.lxmf_sync_dialog_open and self.sync_dialog != None:
                self.sync_dialog.ids.sync_progress.value = self.sideband.get_sync_progress()*100
                self.sync_dialog.ids.sync_status.text = self.sideband.get_sync_status()

        elif self.root.ids.screen_manager.current == "announces_screen":
            if self.flag_new_announces:
                RNS.log("Updating because of new announces flag")
                if self.announces_view != None:
                    self.announces_view.update()

    def on_start(self):        
        self.last_exit_event = time.time()
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
        self.open_conversations()

        Clock.schedule_interval(self.jobs, 1)
    
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
        RNS.exit()
        RNS.log("RNS shutdown complete")
        MDApp.get_running_app().stop()
        Window.close()

    def announce_now_action(self, sender=None):
        self.sideband.lxmf_announce()

        yes_button = MDFlatButton(
            text="OK",
        )

        dialog = MDDialog(
            text="An announce for your LXMF destination was sent on all available interfaces",
            buttons=[ yes_button ],
        )
        def dl_yes(s):
            dialog.dismiss()
        
        yes_button.bind(on_release=dl_yes)
        dialog.open()

    def conversation_update(self, context_dest):
        pass
        # if self.root.ids.messages_scrollview.active_conversation == context_dest:
        #     self.messages_view.update_widget()
        # else:
        #     RNS.log("Not updating since context_dest does not match active")


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

        for child in self.root.ids.messages_scrollview.children:
            self.root.ids.messages_scrollview.remove_widget(child)

        list_widget = self.messages_view.get_widget()

        self.root.ids.messages_scrollview.add_widget(list_widget)
        self.root.ids.messages_scrollview.scroll_y = 0
        self.root.ids.messages_toolbar.title = self.sideband.peer_display_name(context_dest)
        self.root.ids.messages_scrollview.active_conversation = context_dest

        self.root.ids.nokeys_text.text = ""
        self.message_area_detect()
        self.update_message_widgets()

        self.root.ids.screen_manager.current = "messages_screen"
        
        self.sideband.read_conversation(context_dest)

    def close_messages_action(self, sender=None):
        self.open_conversations(direction="right")

    def message_send_action(self, sender=None):
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
                )
                self.messages_view.send_error_dialog.open()

            else:
                msg_content = self.root.ids.message_text.text
                context_dest = self.root.ids.messages_scrollview.active_conversation
                if self.sideband.send_message(msg_content, context_dest, self.outbound_mode_propagation):
                    self.root.ids.message_text.text = ""
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
                    )
                    self.messages_view.send_error_dialog.open()

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
        self.conversations_view = Conversations(self)

        for child in self.root.ids.conversations_scrollview.children:
            self.root.ids.conversations_scrollview.remove_widget(child)

        self.root.ids.conversations_scrollview.add_widget(self.conversations_view.get_widget())

        self.root.ids.screen_manager.current = "conversations_screen"
        self.root.ids.messages_scrollview.active_conversation = None

    def connectivity_status(self, sender):
        hs = dp(22)
        connectivity_status = ""
        if RNS.vendor.platformutils.get_platform() == "android":
            if self.sideband.reticulum.is_connected_to_shared_instance:
                connectivity_status = "[size=22dp][b]Connectivity Status[/b][/size]\n\nSideband is connected via a shared Reticulum instance running on this system. Use the rnstatus utility to obtain full connectivity info."

            else:
                ws = "Disabled"
                ts = "Disabled"
                i2s = "Disabled"

                if self.sideband.interface_local != None:
                    np = len(self.sideband.interface_local.peers)
                    if np == 1:
                        ws = "1 reachable peer"
                    else:
                        ws = str(np)+" reachable peers"

                if self.sideband.interface_tcp != None:
                    if self.sideband.interface_tcp.online:
                        ts = "Connected to "+str(self.sideband.interface_tcp.target_ip)+":"+str(self.sideband.interface_tcp.target_port)
                    else:
                        ts = "Interface Down"

                if self.sideband.interface_i2p != None:
                    if self.sideband.interface_i2p.online:
                        i2s = "Connected"
                    else:
                        i2s = "Connecting to I2P"

                connectivity_status = "[size=22dp][b]Connectivity Status[/b][/size]\n\n[b]Local[/b]\n{ws}\n\n[b]TCP[/b]\n{ts}\n\n[b]I2P[/b]\n{i2s}".format(ws=ws, ts=ts, i2s=i2s)

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

            self.sideband.request_lxmf_sync(limit=sl)

            close_button = MDFlatButton(text="Close", font_size=dp(20))
            # stop_button = MDFlatButton(text="Stop", font_size=dp(20))
            dialog_content = MsgSync()
            dialog = MDDialog(
                title="LXMF Sync via "+RNS.prettyhexrep(self.sideband.message_router.get_outbound_propagation_node()),
                type="custom",
                content_cls=dialog_content,
                buttons=[ close_button ],
            )
            dialog.d_content = dialog_content
            def dl_close(s):                
                self.lxmf_sync_dialog_open = False
                dialog.dismiss()
                self.sideband.cancel_lxmf_sync()

            # def dl_stop(s):         
            #     self.lxmf_sync_dialog_open = False
            #     dialog.dismiss()
            #     self.sideband.cancel_lxmf_sync()

            close_button.bind(on_release=dl_close)
            # stop_button.bind(on_release=dl_stop)
            self.lxmf_sync_dialog_open = True
            self.sync_dialog = dialog_content
            dialog.open()
            dialog_content.ids.sync_progress.value = self.sideband.get_sync_progress()*100
            dialog_content.ids.sync_status.text = self.sideband.get_sync_status()

    def new_conversation_action(self, sender=None):
        try:
            yes_button = MDFlatButton(
                text="OK",
                font_size=dp(20),
            )
            no_button = MDFlatButton(
                text="Cancel",
                font_size=dp(20),
            )
            dialog_content = NewConv()
            dialog = MDDialog(
                title="New Conversation",
                type="custom",
                content_cls=dialog_content,
                buttons=[ yes_button, no_button ],
            )
            dialog.d_content = dialog_content
            def dl_yes(s):
                new_result = False
                try:
                    n_address = dialog.d_content.ids["n_address_field"].text
                    n_name = dialog.d_content.ids["n_name_field"].text
                    n_trusted = dialog.d_content.ids["n_trusted"].active
                    RNS.log("Create conversation "+str(n_address)+"/"+str(n_name)+"/"+str(n_trusted))
                    new_result = self.sideband.new_conversation(n_address, n_name, n_trusted)

                except Exception as e:
                    RNS.log("Error while creating conversation: "+str(e), RNS.LOG_ERROR)

                if new_result:
                    dialog.d_content.ids["n_address_field"].error = False
                    dialog.dismiss()
                    self.open_conversations()
                else:
                    dialog.d_content.ids["n_address_field"].error = True
                    # dialog.d_content.ids["n_error_field"].text = "Could not create conversation. Check your input."

            def dl_no(s):
                dialog.dismiss()

            def dl_ds(s):
                self.dialog_open = False

            yes_button.bind(on_release=dl_yes)
            no_button.bind(on_release=dl_no)

            dialog.bind(on_dismiss=dl_ds)
            dialog.open()
            self.dialog_open = True

        except Exception as e:
            RNS.log("Error while creating new conversation dialog: "+str(e), RNS.LOG_ERROR)

    ### Information/version screen
    ######################################
    def information_action(self, sender=None):
        def link_exec(sender=None, event=None):
            RNS.log("Click")
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        info = "This is Sideband v"+__version__+" "+__variant__+", on RNS v"+RNS.__version__+"\n\nHumbly build using the following open components:\n\n - [b]Reticulum[/b] (MIT License)\n - [b]LXMF[/b] (MIT License)\n - [b]KivyMD[/b] (MIT License)\n - [b]Kivy[/b] (MIT License)\n - [b]Python[/b] (PSF License)"+"\n\nGo to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project.\n\nThe Sideband app is Copyright (c) 2022 Mark Qvist / unsigned.io\n\nPermission is granted to freely share and distribute binary copies of Sideband v"+__version__+" "+__variant__+", so long as no payment or compensation is charged for said distribution or sharing.\n\nIf you were charged or paid anything for this copy of Sideband, please report it to [b]license@unsigned.io[/b].\n\nTHIS IS EXPERIMENTAL SOFTWARE - USE AT YOUR OWN RISK AND RESPONSIBILITY"
        self.root.ids.information_info.text = info
        self.root.ids.information_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "information_screen"
        self.root.ids.nav_drawer.set_state("closed")

    ### Prepare Settings screen
    def settings_action(self, sender=None):
        self.root.ids.screen_manager.transition.direction = "left"

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

        def save_start_announce(sender=None, event=None):
            RNS.log("Save announce")
            self.sideband.config["start_announce"] = self.root.ids.settings_start_announce.active
            self.sideband.save_configuration()

        def save_lxmf_delivery_by_default(sender=None, event=None):
            RNS.log("Save propagation")
            self.sideband.config["propagation_by_default"] = self.root.ids.settings_lxmf_delivery_by_default.active
            self.sideband.save_configuration()

        def save_lxmf_sync_limit(sender=None, event=None):
            RNS.log("Save propagation")
            self.sideband.config["lxmf_sync_limit"] = self.root.ids.settings_lxmf_sync_limit.active
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

        self.root.ids.settings_start_announce.active = self.sideband.config["start_announce"]
        self.root.ids.settings_start_announce.bind(active=save_start_announce)

        self.root.ids.settings_lxmf_delivery_by_default.active = self.sideband.config["propagation_by_default"]
        self.root.ids.settings_lxmf_delivery_by_default.bind(active=save_lxmf_delivery_by_default)

        if self.sideband.config["lxmf_sync_limit"] == None or self.sideband.config["lxmf_sync_limit"] == False:
            sync_limit = False
        else:
            sync_limit = True

        self.root.ids.settings_lxmf_sync_limit.active = sync_limit
        self.root.ids.settings_lxmf_sync_limit.bind(active=save_lxmf_sync_limit)

        self.root.ids.screen_manager.current = "settings_screen"
        self.root.ids.nav_drawer.set_state("closed")

    def close_settings_action(self, sender=None):
        self.open_conversations(direction="right")


    ### Connectivity screen
    ######################################
    def connectivity_action(self, sender=None):
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
            self.widget_hide(self.root.ids.rnode_support_info)

        def save_connectivity(sender=None, event=None):
            RNS.log("Save connectivity")
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
            self.sideband.save_configuration()

        if RNS.vendor.platformutils.get_platform() == "android":
            if self.sideband.reticulum.is_connected_to_shared_instance:
                info =  "Sideband is connected via a shared Reticulum instance running on this system.\n\n"
                info += "To configure connectivity, edit the relevant configuration file for the instance."
                self.root.ids.connectivity_info.text = info
                con_hide_settings()

            else:
                info =  "By default, Sideband will try to discover and connect to any available Reticulum networks via active WiFi and/or Ethernet interfaces. If any Reticulum Transport Instances are found, Sideband will use these to connect to wider Reticulum networks. You can disable this behaviour if you don't want it.\n\n"
                info += "You can also connect to a network via a remote or local Reticulum instance using TCP or I2P. [b]Please Note![/b] Connecting via I2P requires that you already have I2P running on your device, and that the SAM API is enabled.\n\n"
                info += "For changes to connectivity to take effect, you must shut down and restart Sideband."
                self.root.ids.connectivity_info.text = info

                self.root.ids.connectivity_use_local.active = self.sideband.config["connect_local"]
                self.root.ids.connectivity_local_groupid.text = self.sideband.config["connect_local_groupid"]
                self.root.ids.connectivity_local_ifac_netname.text = self.sideband.config["connect_local_ifac_netname"]
                self.root.ids.connectivity_local_ifac_passphrase.text = self.sideband.config["connect_local_ifac_passphrase"]

                self.root.ids.connectivity_use_tcp.active = self.sideband.config["connect_tcp"]
                self.root.ids.connectivity_tcp_host.text = self.sideband.config["connect_tcp_host"]
                self.root.ids.connectivity_tcp_port.text = self.sideband.config["connect_tcp_port"]
                self.root.ids.connectivity_tcp_ifac_netname.text = self.sideband.config["connect_tcp_ifac_netname"]
                self.root.ids.connectivity_tcp_ifac_passphrase.text = self.sideband.config["connect_tcp_ifac_passphrase"]

                self.root.ids.connectivity_use_i2p.active = self.sideband.config["connect_i2p"]
                self.root.ids.connectivity_i2p_b32.text = self.sideband.config["connect_i2p_b32"]
                self.root.ids.connectivity_i2p_ifac_netname.text = self.sideband.config["connect_i2p_ifac_netname"]
                self.root.ids.connectivity_i2p_ifac_passphrase.text = self.sideband.config["connect_i2p_ifac_passphrase"]

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

        else:
            info = ""

            if self.sideband.reticulum.is_connected_to_shared_instance:
                info =  "Sideband is connected via a shared Reticulum instance running on this system.\n\n"
                info += "To configure connectivity, edit the configuration file located at:\n\n"
                info += str(RNS.Reticulum.configpath)
            else:
                info =  "Sideband is currently running a standalone or master Reticulum instance on this system.\n\n"
                info += "To configure connectivity, edit the configuration file located at:\n\n"
                info += str(RNS.Reticulum.configpath)

            self.root.ids.connectivity_info.text = info

            con_hide_settings()

        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "connectivity_screen"
        self.root.ids.nav_drawer.set_state("closed")


    def close_connectivity_action(self, sender=None):
        self.open_conversations(direction="right")

    ### Announce Stream screen
    ######################################
    def announces_action(self, sender=None):
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.nav_drawer.set_state("closed")
        self.announces_view = Announces(self)


        # info = "The [b]Announce Stream[/b] feature is not yet implemented in Sideband.\n\nWant it faster? Go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project."
        # self.root.ids.announces_info.text = info
        # self.root.ids.announces_info.bind(on_ref_press=link_exec)

        for child in self.root.ids.announces_scrollview.children:
            self.root.ids.announces_scrollview.remove_widget(child)

        self.root.ids.announces_scrollview.add_widget(self.announces_view.get_widget())

        self.root.ids.screen_manager.current = "announces_screen"

    def announce_filter_action(self, sender=None):
        pass


    #################################################
    # Unimplemented Screens                         #
    #################################################

    def keys_action(self, sender=None):
        def link_exec(sender=None, event=None):
            RNS.log("Click")
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        info = "The [b]Encryption Keys[/b] import and export feature is not yet implemented in Sideband. In this section of the program, you will be able to export, import and back up your RNS identities, and to link Sideband with your Nomad Network identity, for fetching messages from it on the go.\n\nWant it faster? Go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project."
        self.root.ids.keys_info.text = info
        self.root.ids.keys_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "keys_screen"
        self.root.ids.nav_drawer.set_state("closed")

    def map_action(self, sender=None):
        def link_exec(sender=None, event=None):
            RNS.log("Click")
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        info = "The [b]Local Area[/b] feature is not yet implemented in Sideband.\n\nWant it faster? Go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project."
        self.root.ids.map_info.text = info
        self.root.ids.map_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "map_screen"
        self.root.ids.nav_drawer.set_state("closed")

    def broadcasts_action(self, sender=None):
        def link_exec(sender=None, event=None):
            RNS.log("Click")
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        info = "The [b]Local Broadcasts[/b] feature will allow you to send and listen for local broadcast transmissions on connected radio, LoRa and WiFi interfaces.\n\n[b]Local Broadcasts[/b] makes it easy to establish public information exchange with anyone in direct radio range, or even with large areas far away using the [i]Remote Broadcast Repeater[/i] feature.\n\nThese features are not yet implemented in Sideband.\n\nWant it faster? Go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project."
        self.root.ids.broadcasts_info.text = info
        self.root.ids.broadcasts_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "broadcasts_screen"
        self.root.ids.nav_drawer.set_state("closed")

    def guide_action(self, sender=None):
        def link_exec(sender=None, event=None):
            RNS.log("Click")
            import webbrowser
            webbrowser.open("https://unsigned.io/sideband")

        guide_text = """
Welcome to [b]Sideband[/b], an LXMF client for Android, Linux and macOS. With Sideband, you can communicate with other people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, or anything else Reticulum supports.

This short guide will give you a basic introduction to the concepts that underpin Sideband and LXMF (the protocol that Sideband uses to communicate). If you are not already familiar with LXMF and Reticulum, it is probably a good idea to read this guide, since Sideband is very different from other messaging apps.

Sideband is completely free, permission-less, anonymous and infrastructure-less. Sideband uses the peer-to-peer and distributed messaging system LXMF. There is no sign-up, no service providers, no "end-user license agreements", no data theft and no surveillance. You own the system.

This also means that Sideband operates differently than what you might be used to. It does not need a connection to a server on the Internet to function, and you do not have an account anywhere.

When Sideband is started on your device for the first time, it randomly generates a set of cryptographic keys. These keys are then used to create an LXMF address for your use. Any other endpoint in [i]any[/i] Reticulum network will be able to send data to this address, as long as there is [i]some sort of physical connection[/i] between your device and the remote endpoint. You can also move around to other Reticulum networks with this address, even ones that were never connected to the network the address was created on, or that didn't exist when the address was created. The address is yours to keep and control for as long (or short) a time you need it, and you can always delete it and create a new one.

To establish reachability for any Reticulum address on a network, an [i]announce[/i] must be sent. Sideband does not do this automatically by default, but can be configured to do so every time the program starts. To send an announce manually, press the [i]Announce[/i] button in the [i]Conversations[/i] section of the program. When you send an announce, you make your LXMF address reachable for real-time messaging to the entire network you are connected to. Even in very large networks, you can expect global reachability for your address to be established in under a minute.

If you don't move to other places in the network, and keep connected through the same hubs or gateways, it is generally not necessary to send an announce more often than once every week. If you change your entry point to the network, you may want to send an announce, or you may just want to stay quiet.

If you are not connected to the network, it is still possible for other people to message you, as long as one or more [i]Propagation Nodes[/i] exist on the network. These nodes pick up and hold encrypted in-transit messages for offline users. Messages are always encrypted before leaving the originators device, and nobody else than the intended recipient can decrypt messages in transit.

The Propagation Nodes also distribute copies of messages between each other, such that even the failure of almost every node in the network will still allow users to sync their waiting messages. If all Propagation Nodes disappear or are destroyed, users can still communicate directly. Reticulum and LXMF will degrade gracefully all the way down to single users communicating directly via long-range data radios. Anyone can start up new propagation nodes and integrate them into existing networks without permission or coordination. Even a small and cheap device like a Rasperry Pi can handle messages for millions of users. LXMF networks are designed to be quite resilient, as long as there are people using them.

Connections in Reticulum networks can be wired or wireless, span many intermediary hops, run over fast links or ultra-low bandwidth radio, tunnel over the Invisible Internet (I2P), private networks, satellite connections, serial lines or anything else that Reticulum can carry data over. In most cases it will not be possible to know what path data takes in a Reticulum network, and no transmitted data carries any identifying characteristics, apart from a destination address. There is no source addresses in Reticulum. As long as you do not establish a link between you personal identity and your LXMF address through some other method, you can remain anonymous. Sending messages to others does not reveal [i]your[/i] address.

That being said, you [b]must remember[/b] that LXMF and Reticulum is not a technology that can guarantee anonymising connections that are already de-anonymised! If you use Sideband to connect to TCP Reticulum hubs over the clear Internet, from a network that can be tied to your personal identity, an adversary may learn that you are generating LXMF traffic. If you want to avoid this, it is recommended to use I2P to connect to Reticulum hubs on the Internet. Or only connecting from within pure Reticulum networks, that take one or more hops to reach connections that span the Internet. This is a complex topic, with many more nuances than can not be covered here. You are encouraged to ask on the various Reticulum discussion forums if you are in doubt.

If you use Reticulum and LXMF on hardware that does not carry any identifiers tied to you, it is possible to establish a completely free and anonymous communication system with Reticulum and LXMF clients.

It took me more than six years to design and built the entire ecosystem of software and hardware that makes this possible. If this project is valuable to you, please go to [u][ref=link]https://unsigned.io/sideband[/ref][/u] to support the project with a donation. Every donation directly makes the entire Reticulum project possible.

Thank you very much for using Free Communications Systems.
"""
        info = guide_text
        self.root.ids.guide_info.text = info
        self.root.ids.guide_info.bind(on_ref_press=link_exec)
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = "guide_screen"
        self.root.ids.nav_drawer.set_state("closed")

def run():
    SidebandApp().run()

if __name__ == "__main__":
    run()