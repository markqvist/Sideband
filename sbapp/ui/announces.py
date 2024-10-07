import time
import RNS

from kivy.metrics import dp,sp
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.list import MDList, IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog

from kivy.lang.builder import Builder

from kivy.utils import escape_markup
if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import multilingual_markup
else:
    from .helpers import multilingual_markup

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import ts_format
else:
    from .helpers import ts_format

class Announces():
    def __init__(self, app):
        self.app = app
        self.context_dests = []
        self.added_item_dests = []
        self.list = None

        if not self.app.root.ids.screen_manager.has_screen("announces_screen"):
            self.screen = Builder.load_string(layout_announces_screen)
            self.screen.app = self.app
            self.ids = self.screen.ids
            self.app.root.ids.screen_manager.add_widget(self.screen)

        self.fetch_announces()
        self.list = MDList()
        # self.update()

    def fetch_announces(self):
        self.announces = self.app.sideband.list_announces()

    def reload(self):
        self.clear_list()
        self.update()

    def clear_list(self):
        if self.list != None:
            self.list.clear_widgets()

        self.context_dests = []
        self.added_item_dests = []

    def update(self):
        us = time.time()
        self.fetch_announces()
        self.update_widget()
        self.app.sideband.setstate("app.flags.new_announces", False)
        RNS.log(f"Updated announce stream widgets in {RNS.prettytime(time.time() - us)}", RNS.LOG_DEBUG)

    def update_widget(self):
        if self.list == None:
            self.list = MDList()

        remove_widgets = []
        for item in self.list.children:
            if not item.sb_uid in (a["dest"] for a in self.announces):
                remove_widgets.append(item)

            else:
                for announce in self.announces:
                    if announce["dest"] == item.sb_uid:
                        if announce["time"] > item.ts:
                            remove_widgets.append(item)
                            break

        for item in remove_widgets:
            if item.sb_uid in self.added_item_dests:
                self.added_item_dests.remove(item.sb_uid)
            self.list.remove_widget(item)

        for announce in self.announces:
            context_dest = announce["dest"]
            ts = announce["time"]
            a_name = announce["name"]
            a_cost = announce["cost"]
            dest_type = announce["type"]

            if not context_dest in self.added_item_dests:
                if self.app.sideband.is_trusted(context_dest):
                    trust_icon = "account-check"
                else:
                    trust_icon = "account-question"

                def gen_info(ts, dest, name, cost, dtype):
                    name = multilingual_markup(escape_markup(str(name)).encode("utf-8")).decode("utf-8")
                    cost = str(cost)
                    def x(sender):
                        yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                        if dtype == "lxmf.delivery":
                            ad_text = f"[size=22dp]LXMF Peer[/size]\n\n[b]Received[/b] {ts}\n[b]Address[/b] {RNS.prettyhexrep(dest)}\n[b]Name[/b] {name}\n[b]Stamp Cost[/b] {cost}"

                        if dtype == "lxmf.propagation":
                            ad_text = f"[size=22dp]LXMF Propagation Node[/size]\n\n[b]Received[/b] {ts}\n[b]Address[/b] {RNS.prettyhexrep(dest)}"

                        dialog = MDDialog(
                            text=ad_text,
                            buttons=[ yes_button ],
                            # elevation=0,
                        )
                        def dl_yes(s):
                            dialog.dismiss()

                        yes_button.bind(on_release=dl_yes)
                        item.dmenu.dismiss()
                        dialog.open()
                    return x

                time_string = time.strftime(ts_format, time.localtime(ts))

                if dest_type == "lxmf.delivery":
                    disp_name = multilingual_markup(escape_markup(str(self.app.sideband.peer_display_name(context_dest))).encode("utf-8")).decode("utf-8")
                    iconl = IconLeftWidget(icon=trust_icon)

                elif dest_type == "lxmf.propagation":
                    disp_name = f"Propagation Node {RNS.prettyhexrep(context_dest)}"
                    iconl = IconLeftWidget(icon="upload-network")

                else:
                    disp_name = "Unknown Announce"
                    iconl = IconLeftWidget(icon="progress-question")

                item = TwoLineAvatarIconListItem(text=time_string, secondary_text=disp_name, on_release=gen_info(time_string, context_dest, a_name, a_cost, dest_type))
                item.add_widget(iconl)
                item.sb_uid = context_dest
                item.ts = ts

                def gen_del(dest, item):
                    def x():
                        yes_button = MDRectangleFlatButton(text="Yes",font_size=dp(18), theme_text_color="Custom", line_color=self.app.color_reject, text_color=self.app.color_reject)
                        no_button = MDRectangleFlatButton(text="No",font_size=dp(18))
                        dialog = MDDialog(
                            title="Delete announce?",
                            buttons=[ yes_button, no_button ],
                            padding=[0,0,dp(32),0]
                            # elevation=0,
                        )
                        def dl_yes(s):
                            dialog.dismiss()
                            def cb(dt):
                                self.app.sideband.delete_announce(dest)
                                self.update()
                            Clock.schedule_once(cb, 0.2)
                        def dl_no(s):
                            dialog.dismiss()

                        yes_button.bind(on_release=dl_yes)
                        no_button.bind(on_release=dl_no)
                        item.dmenu.dismiss()
                        dialog.open()
                    return x

                def gen_conv(dest, item):
                    def x():
                        item.dmenu.dismiss()
                        self.app.conversation_from_announce_action(dest)
                    return x

                def gen_copy_addr(dest, item):
                    def x():
                        Clipboard.copy(RNS.hexrep(dest, delimit=False))
                        item.dmenu.dismiss()
                    return x

                def gen_set_node(dest, item):
                    def x():
                        item.dmenu.dismiss()
                        self.app.sideband.set_active_propagation_node(dest)
                        self.app.sideband.config["lxmf_propagation_node"] = dest
                        self.app.sideband.save_configuration()
                    return x

                if dest_type == "lxmf.delivery":
                    dm_items = [
                        {
                            "viewclass": "OneLineListItem",
                            "text": "Converse",
                            "height": dp(40),
                            "on_release": gen_conv(context_dest, item)
                        },
                        {
                            "viewclass": "OneLineListItem",
                            "text": "Copy address",
                            "height": dp(40),
                            "on_release": gen_copy_addr(context_dest, item)
                        },
                        {
                            "text": "Delete Announce",
                            "viewclass": "OneLineListItem",
                            "height": dp(40),
                            "on_release": gen_del(context_dest, item)
                        }
                    ]

                elif dest_type == "lxmf.propagation":
                    dm_items = [
                        {
                            "viewclass": "OneLineListItem",
                            "text": "Use this Propagation Node",
                            "height": dp(40),
                            "on_release": gen_set_node(context_dest, item)
                        },
                        {
                            "viewclass": "OneLineListItem",
                            "text": "Copy address",
                            "height": dp(40),
                            "on_release": gen_copy_addr(context_dest, item)
                        },
                        {
                            "text": "Delete Announce",
                            "viewclass": "OneLineListItem",
                            "height": dp(40),
                            "on_release": gen_del(context_dest, item)
                        }
                    ]

                else:
                    dm_items = []

                item.iconr = IconRightWidget(icon="dots-vertical");

                item.dmenu = MDDropdownMenu(
                    caller=item.iconr,
                    items=dm_items,
                    position="auto",
                    width=dp(256),
                    elevation=0,
                    radius=dp(3),
                )
                item.dmenu.md_bg_color = self.app.color_hover

                def callback_factory(ref):
                    def x(sender):
                        ref.dmenu.open()
                    return x

                item.iconr.bind(on_release=callback_factory(item))
                item.add_widget(item.iconr)

                self.added_item_dests.append(context_dest)
                self.list.add_widget(item, index=len(self.list.children))

    def get_widget(self):
        return self.list

layout_announces_screen = """
MDScreen:
    name: "announces_screen"

    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Announce Stream"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_settings_action(self)],
                ]
            #    [['eye-off', lambda x: root.ids.screen_manager.app.announce_filter_action(self)]]

        ScrollView:
            id: announces_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "24dp"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(64)

                MDLabel:
                    id: announces_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]
"""
