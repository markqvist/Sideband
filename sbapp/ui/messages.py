import time
import RNS
import LXMF

from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import ts_format, mdc
    from ui.helpers import color_received, color_delivered, color_propagated, color_failed, color_unknown, intensity_msgs
else:
    from .helpers import ts_format, mdc
    from .helpers import color_received, color_delivered, color_propagated, color_failed, color_unknown, intensity_msgs

class ListLXMessageCard(MDCard, RoundedRectangularElevationBehavior):
    text = StringProperty()
    heading = StringProperty()

class Messages():
    def __init__(self, app, context_dest):
        self.app = app
        self.context_dest = context_dest
        self.messages = []
        self.added_item_hashes = []
        self.latest_message_timestamp = None
        self.list = None
        self.widgets = []
        self.send_error_dialog = None
        self.update()

    def reload(self):
        if self.list != None:
            self.list.clear_widgets()

        self.messages = []
        self.added_item_hashes = []
        self.latest_message_timestamp = None
        self.widgets = []

        self.update()

    def update(self):
        self.messages = self.app.sideband.list_messages(self.context_dest, self.latest_message_timestamp)
        if self.list == None:
            layout = GridLayout(cols=1, spacing=16, padding=16, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))
            self.list = layout

        if len(self.messages) > 0:
            self.update_widget()

        for w in self.widgets:
            m = w.m
            if m["state"] == LXMF.LXMessage.SENDING or m["state"] == LXMF.LXMessage.OUTBOUND:
                msg = self.app.sideband.message(m["hash"])
                if msg["state"] == LXMF.LXMessage.DELIVERED:
                    w.md_bg_color = msg_color = mdc(color_delivered, intensity_msgs)
                    txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                    titlestr = ""
                    if msg["title"]:
                        titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                    w.heading = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] Delivered"
                    m["state"] = msg["state"]

                if msg["method"] == LXMF.LXMessage.PROPAGATED and msg["state"] == LXMF.LXMessage.SENT:
                    w.md_bg_color = msg_color = mdc(color_propagated, intensity_msgs)
                    txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                    titlestr = ""
                    if msg["title"]:
                        titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                    w.heading = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] On Propagation Net"
                    m["state"] = msg["state"]

                if msg["state"] == LXMF.LXMessage.FAILED:
                    w.md_bg_color = msg_color = mdc(color_failed, intensity_msgs)
                    txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                    titlestr = ""
                    if msg["title"]:
                        titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                    w.heading = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] Failed"
                    m["state"] = msg["state"]


    def update_widget(self):
        for m in self.messages:
            if not m["hash"] in self.added_item_hashes:
                txstr = time.strftime(ts_format, time.localtime(m["sent"]))
                rxstr = time.strftime(ts_format, time.localtime(m["received"]))
                titlestr = ""

                if m["title"]:
                    titlestr = "[b]Title[/b] "+m["title"].decode("utf-8")+"\n"

                if m["source"] == self.app.sideband.lxmf_destination.hash:
                    if m["state"] == LXMF.LXMessage.DELIVERED:
                        msg_color = mdc(color_delivered, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] Delivered"

                    elif m["method"] == LXMF.LXMessage.PROPAGATED and m["state"] == LXMF.LXMessage.SENT:
                        msg_color = mdc(color_propagated, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] On Propagation Net"

                    elif m["state"] == LXMF.LXMessage.FAILED:
                        msg_color = mdc(color_failed, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] Failed"

                    elif m["state"] == LXMF.LXMessage.OUTBOUND or m["state"] == LXMF.LXMessage.SENDING:
                        msg_color = mdc(color_unknown, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] Sending                          "

                    else:
                        msg_color = mdc(color_unknown, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+" [b]State[/b] Unknown"

                else:
                    msg_color = mdc("Green", intensity_msgs)
                    heading_str = titlestr+"[b]Sent[/b] "+txstr+"\n[b]Received[/b] "+rxstr

                item = ListLXMessageCard(
                    text=m["content"].decode("utf-8"),
                    heading=heading_str,
                    md_bg_color=msg_color,
                )
                item.sb_uid = m["hash"]
                item.m = m

                def gen_del(mhash, item):
                    def x():
                        yes_button = MDFlatButton(
                            text="Yes",
                        )
                        no_button = MDFlatButton(
                            text="No",
                        )
                        dialog = MDDialog(
                            text="Delete message?",
                            buttons=[ yes_button, no_button ],
                        )
                        def dl_yes(s):
                            dialog.dismiss()
                            self.app.sideband.delete_message(mhash)
                            self.reload()
                        def dl_no(s):
                            dialog.dismiss()

                        yes_button.bind(on_release=dl_yes)
                        no_button.bind(on_release=dl_no)
                        item.dmenu.dismiss()
                        dialog.open()
                    return x

                def gen_copy(msg, item):
                    def x():
                        Clipboard.copy(msg)
                        RNS.log(str(item))
                        item.dmenu.dismiss()

                    return x

                dm_items = [
                    {
                        "viewclass": "OneLineListItem",
                        "text": "Copy",
                        "height": dp(40),
                        "on_release": gen_copy(m["content"].decode("utf-8"), item)
                    },
                    {
                        "text": "Delete",
                        "viewclass": "OneLineListItem",
                        "height": dp(40),
                        "on_release": gen_del(m["hash"], item)
                    }
                ]

                item.dmenu = MDDropdownMenu(
                    caller=item.ids.msg_submenu,
                    items=dm_items,
                    position="center",
                    width_mult=4,
                )

                def callback_factory(ref):
                    def x(sender):
                        ref.dmenu.open()
                    return x

                # Bind menu open
                item.ids.msg_submenu.bind(on_release=callback_factory(item))

                self.added_item_hashes.append(m["hash"])
                self.widgets.append(item)
                self.list.add_widget(item)

                if self.latest_message_timestamp == None or m["received"] > self.latest_message_timestamp:
                    self.latest_message_timestamp = m["received"]

    def get_widget(self):
        return self.list

    def close_send_error_dialog(self, sender=None):
        if self.send_error_dialog:
            self.send_error_dialog.dismiss()