import time
import RNS
import LXMF

from kivy.metrics import dp,sp
from kivy.core.clipboard import Clipboard
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
# from kivymd.uix.behaviors import RoundedRectangularElevationBehavior, FakeRectangularElevationBehavior
from kivymd.uix.behaviors import CommonElevationBehavior
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from kivymd.uix.button import MDRectangleFlatButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog

import os
import plyer
import subprocess
import shlex

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import ts_format, file_ts_format, mdc
    from ui.helpers import color_received, color_delivered, color_propagated, color_paper, color_failed, color_unknown, intensity_msgs_dark, intensity_msgs_light
else:
    from .helpers import ts_format, file_ts_format, mdc
    from .helpers import color_received, color_delivered, color_propagated, color_paper, color_failed, color_unknown, intensity_msgs_dark, intensity_msgs_light

class ListLXMessageCard(MDCard):
# class ListLXMessageCard(MDCard, FakeRectangularElevationBehavior):
    text = StringProperty()
    heading = StringProperty()

class Messages():
    def __init__(self, app, context_dest):
        self.app = app
        self.context_dest = context_dest
        self.new_messages = []
        self.added_item_hashes = []
        self.added_messages = 0
        self.latest_message_timestamp = None
        self.earliest_message_timestamp = time.time()
        self.loading_earlier_messages = False
        self.list = None
        self.widgets = []
        self.send_error_dialog = None
        self.load_more_button = None
        self.update()

    def reload(self):
        if self.list != None:
            self.list.clear_widgets()

        self.new_messages = []
        self.added_item_hashes = []
        self.added_messages = 0
        self.latest_message_timestamp = None
        self.widgets = []

        self.update()

    def load_more(self, dt):
        for new_message in self.app.sideband.list_messages(self.context_dest, before=self.earliest_message_timestamp,limit=5):
            self.new_messages.append(new_message)

        if len(self.new_messages) > 0:
            self.loading_earlier_messages = True
            self.list.remove_widget(self.load_more_button)

    def update(self, limit=8):
        for new_message in self.app.sideband.list_messages(self.context_dest, after=self.latest_message_timestamp,limit=limit):
            self.new_messages.append(new_message)

        self.db_message_count = self.app.sideband.count_messages(self.context_dest)

        if self.load_more_button == None:
            self.load_more_button = MDRectangleFlatIconButton(
                icon="message-text-clock-outline",
                text="Load earlier messages",
                font_size=dp(18),
                theme_text_color="Custom",
                size_hint=[1.0, None],
            )
            def lmcb(sender):
                Clock.schedule_once(self.load_more, 0.15)

            self.load_more_button.bind(on_release=lmcb)

        if self.list == None:
            layout = GridLayout(cols=1, spacing=dp(16), padding=dp(16), size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))
            self.list = layout

        c_ts = time.time()
        if len(self.new_messages) > 0:
            self.update_widget()

        if (len(self.added_item_hashes) < self.db_message_count) and not self.load_more_button in self.list.children:
            self.list.add_widget(self.load_more_button, len(self.list.children))

        if self.app.sideband.config["dark_ui"]:
            intensity_msgs = intensity_msgs_dark
        else:
            intensity_msgs = intensity_msgs_light

        for w in self.widgets:
            m = w.m
            if self.app.sideband.config["dark_ui"]:
                w.line_color = (1.0, 1.0, 1.0, 0.25)
            else:
                w.line_color = (1.0, 1.0, 1.0, 0.5)

            if m["state"] == LXMF.LXMessage.SENDING or m["state"] == LXMF.LXMessage.OUTBOUND:
                msg = self.app.sideband.message(m["hash"])
                if msg["state"] == LXMF.LXMessage.DELIVERED:
                    w.md_bg_color = msg_color = mdc(color_delivered, intensity_msgs)
                    txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                    titlestr = ""
                    if msg["title"]:
                        titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                    w.heading = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Delivered"
                    m["state"] = msg["state"]

                if msg["method"] == LXMF.LXMessage.PAPER:
                    w.md_bg_color = msg_color = mdc(color_paper, intensity_msgs)
                    txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                    titlestr = ""
                    if msg["title"]:
                        titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                    w.heading = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Paper Message"
                    m["state"] = msg["state"]

                if msg["method"] == LXMF.LXMessage.PROPAGATED and msg["state"] == LXMF.LXMessage.SENT:
                    w.md_bg_color = msg_color = mdc(color_propagated, intensity_msgs)
                    txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                    titlestr = ""
                    if msg["title"]:
                        titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                    w.heading = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] On Propagation Net"
                    m["state"] = msg["state"]

                if msg["state"] == LXMF.LXMessage.FAILED:
                    w.md_bg_color = msg_color = mdc(color_failed, intensity_msgs)
                    txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                    titlestr = ""
                    if msg["title"]:
                        titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                    w.heading = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Failed"
                    m["state"] = msg["state"]


    def update_widget(self):
        if self.app.sideband.config["dark_ui"]:
            intensity_msgs = intensity_msgs_dark
            mt_color = [1.0, 1.0, 1.0, 0.8]
        else:
            intensity_msgs = intensity_msgs_light
            mt_color = [1.0, 1.0, 1.0, 0.95]

        if self.loading_earlier_messages:
            self.new_messages.reverse()

        for m in self.new_messages:
            if not m["hash"] in self.added_item_hashes:
                txstr = time.strftime(ts_format, time.localtime(m["sent"]))
                rxstr = time.strftime(ts_format, time.localtime(m["received"]))
                titlestr = ""

                if m["title"]:
                    titlestr = "[b]Title[/b] "+m["title"].decode("utf-8")+"\n"

                if m["source"] == self.app.sideband.lxmf_destination.hash:
                    if m["state"] == LXMF.LXMessage.DELIVERED:
                        msg_color = mdc(color_delivered, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Delivered"

                    elif m["method"] == LXMF.LXMessage.PROPAGATED and m["state"] == LXMF.LXMessage.SENT:
                        msg_color = mdc(color_propagated, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] On Propagation Net"

                    elif m["method"] == LXMF.LXMessage.PAPER:
                        msg_color = mdc(color_paper, intensity_msgs)
                        heading_str = titlestr+"[b]Created[/b] "+txstr+"\n[b]State[/b] Paper Message"

                    elif m["state"] == LXMF.LXMessage.FAILED:
                        msg_color = mdc(color_failed, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Failed"

                    elif m["state"] == LXMF.LXMessage.OUTBOUND or m["state"] == LXMF.LXMessage.SENDING:
                        msg_color = mdc(color_unknown, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Sending                          "

                    else:
                        msg_color = mdc(color_unknown, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Unknown"

                else:
                    msg_color = mdc(color_received, intensity_msgs)
                    heading_str = titlestr+"[b]Sent[/b] "+txstr+"\n[b]Received[/b] "+rxstr

                item = ListLXMessageCard(
                    text=m["content"].decode("utf-8"),
                    heading=heading_str,
                    md_bg_color=msg_color,
                )
                item.sb_uid = m["hash"]
                item.m = m
                item.ids.heading_text.theme_text_color = "Custom"
                item.ids.heading_text.text_color = mt_color
                item.ids.content_text.theme_text_color = "Custom"
                item.ids.content_text.text_color = mt_color
                item.ids.msg_submenu.theme_text_color = "Custom"
                item.ids.msg_submenu.text_color = mt_color

                def gen_del(mhash, item):
                    def x():
                        yes_button = MDRectangleFlatButton(text="Yes",font_size=dp(18), theme_text_color="Custom", line_color=self.app.color_reject, text_color=self.app.color_reject)
                        no_button = MDRectangleFlatButton(text="No",font_size=dp(18))
                        dialog = MDDialog(
                            title="Delete message?",
                            buttons=[ yes_button, no_button ],
                            # elevation=0,
                        )
                        def dl_yes(s):
                            dialog.dismiss()
                            self.app.sideband.delete_message(mhash)

                            def cb(dt):
                                self.reload()
                            Clock.schedule_once(cb, 0.2)

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
                        item.dmenu.dismiss()

                    return x

                def gen_copy_lxm_uri(lxm, item):
                    def x():
                        Clipboard.copy(lxm.as_uri())
                        item.dmenu.dismiss()

                    return x

                def gen_save_qr(lxm, item):
                    if RNS.vendor.platformutils.is_android():
                        def x():
                            qr_image = lxm.as_qr()
                            hash_str = RNS.hexrep(lxm.hash[-2:], delimit=False)
                            filename = "Paper_Message_"+time.strftime(file_ts_format, time.localtime(m["sent"]))+"_"+hash_str+".png"
                            # filename = "Paper_Message.png"
                            self.app.share_image(qr_image, filename)
                            item.dmenu.dismiss()
                        return x

                    else:
                        def x():
                            try:
                                qr_image = lxm.as_qr()
                                hash_str = RNS.hexrep(lxm.hash[-2:], delimit=False)
                                filename = "Paper_Message_"+time.strftime(file_ts_format, time.localtime(m["sent"]))+"_"+hash_str+".png"
                                if RNS.vendor.platformutils.is_darwin():
                                    save_path = str(plyer.storagepath.get_downloads_dir()+filename).replace("file://", "")
                                else:
                                    save_path = plyer.storagepath.get_downloads_dir()+"/"+filename

                                qr_image.save(save_path)
                                item.dmenu.dismiss()

                                ok_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                                dialog = MDDialog(
                                    title="QR Code Saved",
                                    text="The paper message has been saved to: "+save_path+"",
                                    buttons=[ ok_button ],
                                    # elevation=0,
                                )
                                def dl_ok(s):
                                    dialog.dismiss()
                                
                                ok_button.bind(on_release=dl_ok)
                                dialog.open()

                            except Exception as e:
                                item.dmenu.dismiss()
                                ok_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                                dialog = MDDialog(
                                    title="Error",
                                    text="Could not save the paper message QR-code to:\n\n"+save_path+"\n\n"+str(e),
                                    buttons=[ ok_button ],
                                    # elevation=0,
                                )
                                def dl_ok(s):
                                    dialog.dismiss()
                                
                                ok_button.bind(on_release=dl_ok)
                                dialog.open()

                        return x

                def gen_print_qr(lxm, item):
                    if RNS.vendor.platformutils.is_android():
                        def x():
                            item.dmenu.dismiss()
                        return x
                    
                    else:
                        def x():
                            try:
                                qr_image = lxm.as_qr()
                                qr_tmp_path = self.app.sideband.tmp_dir+"/"+str(RNS.hexrep(lxm.hash, delimit=False))
                                qr_image.save(qr_tmp_path)

                                print_command = self.app.sideband.config["print_command"]+" "+qr_tmp_path
                                return_code = subprocess.call(shlex.split(print_command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                                os.unlink(qr_tmp_path)

                                item.dmenu.dismiss()

                            except Exception as e:
                                item.dmenu.dismiss()
                                ok_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                                dialog = MDDialog(
                                    title="Error",
                                    text="Could not print the paper message QR-code.\n\n"+str(e),
                                    buttons=[ ok_button ],
                                    # elevation=0,
                                )
                                def dl_ok(s):
                                    dialog.dismiss()
                                
                                ok_button.bind(on_release=dl_ok)
                                dialog.open()

                        return x

                if m["method"] == LXMF.LXMessage.PAPER:
                    if RNS.vendor.platformutils.is_android():
                        qr_save_text = "Share QR Code"
                        dm_items = [
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Share QR Code",
                                "height": dp(40),
                                "on_release": gen_save_qr(m["lxm"], item)
                            },
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Copy LXM URI",
                                "height": dp(40),
                                "on_release": gen_copy_lxm_uri(m["lxm"], item)
                            },
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Copy message text",
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

                    else:
                        dm_items = [
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Print QR Code",
                                "height": dp(40),
                                "on_release": gen_print_qr(m["lxm"], item)
                            },
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Save QR Code",
                                "height": dp(40),
                                "on_release": gen_save_qr(m["lxm"], item)
                            },
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Copy LXM URI",
                                "height": dp(40),
                                "on_release": gen_copy_lxm_uri(m["lxm"], item)
                            },
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Copy message text",
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

                else:
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
                    elevation=1,
                    radius=dp(3),
                    opening_transition="linear",
                    opening_time=0.0,
                )

                def callback_factory(ref):
                    def x(sender):
                        ref.dmenu.open()
                    return x

                # Bind menu open
                item.ids.msg_submenu.bind(on_release=callback_factory(item))

                if self.loading_earlier_messages:
                    insert_pos = len(self.list.children)
                else:
                    insert_pos = 0

                self.added_item_hashes.append(m["hash"])
                self.widgets.append(item)
                self.list.add_widget(item, insert_pos)

                if self.latest_message_timestamp == None or m["received"] > self.latest_message_timestamp:
                    self.latest_message_timestamp = m["received"]

                if self.earliest_message_timestamp == None or m["received"] < self.earliest_message_timestamp:
                    self.earliest_message_timestamp = m["received"]

        self.added_messages += len(self.new_messages)
        self.new_messages = []

    def get_widget(self):
        return self.list

    def close_send_error_dialog(self, sender=None):
        if self.send_error_dialog:
            self.send_error_dialog.dismiss()