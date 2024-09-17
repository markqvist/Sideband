import time
import RNS
import LXMF

from kivy.metrics import dp,sp
from kivy.core.clipboard import Clipboard
from kivy.core.image import Image as CoreImage
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
# from kivymd.uix.behaviors import RoundedRectangularElevationBehavior, FakeRectangularElevationBehavior
from kivymd.uix.behaviors import CommonElevationBehavior
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.utils import escape_markup

from kivymd.uix.button import MDRectangleFlatButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import multilingual_markup
else:
    from .helpers import multilingual_markup

import io
import os
import subprocess
import shlex

from kivy.graphics.opengl import glGetIntegerv, GL_MAX_TEXTURE_SIZE

if RNS.vendor.platformutils.get_platform() == "android":
    import plyer
    from sideband.sense import Telemeter, Commands
    from ui.helpers import ts_format, file_ts_format, mdc
    from ui.helpers import color_playing, color_received, color_delivered, color_propagated, color_paper, color_failed, color_unknown, intensity_msgs_dark, intensity_msgs_light, intensity_play_dark, intensity_play_light
else:
    import sbapp.plyer as plyer
    from sbapp.sideband.sense import Telemeter, Commands
    from .helpers import ts_format, file_ts_format, mdc
    from .helpers import color_playing, color_received, color_delivered, color_propagated, color_paper, color_failed, color_unknown, intensity_msgs_dark, intensity_msgs_light, intensity_play_dark, intensity_play_light

if RNS.vendor.platformutils.is_darwin():
    from PIL import Image as PilImage

from kivy.lang.builder import Builder
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

class DialogItem(OneLineIconListItem):
    divider = None
    icon = StringProperty()

class ListLXMessageCard(MDCard):
# class ListLXMessageCard(MDCard, FakeRectangularElevationBehavior):
    text = StringProperty()
    heading = StringProperty()

class Messages():
    def __init__(self, app, context_dest):
        self.app = app
        self.context_dest = context_dest
        self.source_dest = context_dest
        self.is_trusted = self.app.sideband.is_trusted(self.context_dest)
        self.ptt_enabled = self.app.sideband.ptt_enabled(self.context_dest)

        self.screen = self.app.root.ids.screen_manager.get_screen("messages_screen")
        self.ids = self.screen.ids

        self.max_texture_size = glGetIntegerv(GL_MAX_TEXTURE_SIZE)[0]
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
        self.details_dialog = None
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

    def message_details_dialog(self, lxm_hash):
        ss = int(dp(16))
        ms = int(dp(14))
        
        msg = self.app.sideband.message(lxm_hash)
        if msg:
            close_button = MDRectangleFlatButton(text="Close", font_size=dp(18))
            # d_items = [ ]
            # d_items.append(DialogItem(IconLeftWidget(icon="postage-stamp"), text="[size="+str(ss)+"]Stamp[/size]"))

            d_text = ""

            if "lxm" in msg and msg["lxm"] != None:
                size_str = RNS.prettysize(msg["lxm"].packed_size)
                d_text += f"[size={ss}][b]Message size[/b] {size_str}[/size]\n"

                if msg["lxm"].signature_validated:
                    d_text += f"[size={ss}][b]Signature[/b] validated successfully[/size]\n"
                else:
                    d_text += f"[size={ss}][b]Signature[/b] is invalid[/size]\n"

            ratchet_method = ""
            if "method" in msg:
                if msg["method"] == LXMF.LXMessage.UNKNOWN:
                    d_text += f"[size={ss}][b]Delivered[/b] via unknown method[/size]\n"
                if msg["method"] == LXMF.LXMessage.OPPORTUNISTIC:
                    ratchet_method = "with ratchet"
                    d_text += f"[size={ss}][b]Delivered[/b] opportunistically[/size]\n"
                if msg["method"] == LXMF.LXMessage.DIRECT:
                    ratchet_method = "by link"
                    d_text += f"[size={ss}][b]Delivered[/b] over direct link[/size]\n"
                if msg["method"] == LXMF.LXMessage.PROPAGATED:
                    ratchet_method = "with ratchet"
                    d_text += f"[size={ss}][b]Delivered[/b] to propagation network[/size]\n"

            if msg["extras"] != None and "ratchet_id" in msg["extras"]:
                r_str = RNS.prettyhexrep(msg["extras"]["ratchet_id"])
                d_text += f"[size={ss}][b]Encrypted[/b] {ratchet_method} {r_str}[/size]\n"
            else:
                if msg["method"] == LXMF.LXMessage.OPPORTUNISTIC or msg["method"] == LXMF.LXMessage.PROPAGATED:
                    d_text += f"[size={ss}][b]Encrypted[/b] with destination identity key[/size]\n"
                else:
                    d_text += f"[size={ss}][b]Encryption[/b] status unknown[/size]\n"
            
            if msg["extras"] != None and "stamp_checked" in msg["extras"]:
                valid_str = " is not valid"
                if msg["extras"]["stamp_valid"] == True:
                    valid_str = " is valid"
                sv = msg["extras"]["stamp_value"]
                if sv == None:
                    if "stamp_raw" in msg["extras"]:
                        sv_str = ""
                        valid_str = "is not valid"
                    else:
                        sv_str = ""
                        valid_str = "was not included in the message"
                elif sv > 255:
                    sv_str = "generated from ticket"
                else:
                    sv_str = f"with value {sv}"

                if msg["extras"]["stamp_checked"] == True:
                    d_text += f"[size={ss}][b]Stamp[/b] {sv_str}{valid_str}[/size]\n"

                else:
                    sv = msg["extras"]["stamp_value"]
                    if sv == None:
                        pass
                    elif sv > 255:
                        d_text += f"[size={ss}][b]Stamp[/b] generated from ticket[/size]\n"
                    else:
                        d_text += f"[size={ss}][b]Value[/b] of stamp is {sv}[/size]\n"

                # Stamp details
                if "stamp_raw" in msg["extras"] and type(msg["extras"]["stamp_raw"]) == bytes:
                    sstr = RNS.hexrep(msg["extras"]["stamp_raw"])
                    sstr1 = RNS.hexrep(msg["extras"]["stamp_raw"][:16])
                    sstr2 = RNS.hexrep(msg["extras"]["stamp_raw"][16:])
                    d_text += f"[size={ss}]\n[b]Raw stamp[/b]\n[/size][size={ms}][font=RobotoMono-Regular]{sstr1}\n{sstr2}[/font][/size]\n"

            self.details_dialog = MDDialog(
                title="Message Details",
                type="simple",
                text=d_text,
                # items=d_items,
                buttons=[ close_button ],
                width_offset=dp(32),
            )

            close_button.bind(on_release=self.details_dialog.dismiss)
            self.details_dialog.open()

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

        if RNS.vendor.platformutils.is_darwin() or RNS.vendor.platformutils.is_windows():
            self.hide_widget(self.ids.message_ptt, True)
        else:
            if self.ptt_enabled:
                self.hide_widget(self.ids.message_ptt, False)
            else:
                self.hide_widget(self.ids.message_ptt, True)

        c_ts = time.time()
        if len(self.new_messages) > 0:
            self.update_widget()

        if (len(self.added_item_hashes) < self.db_message_count) and not self.load_more_button in self.list.children:
            self.list.add_widget(self.load_more_button, len(self.list.children))

        if self.app.sideband.config["dark_ui"]:
            intensity_msgs = intensity_msgs_dark
            intensity_play = intensity_play_dark
        else:
            intensity_msgs = intensity_msgs_light
            intensity_play = intensity_play_light

        for w in self.widgets:
            m = w.m
            if self.app.sideband.config["dark_ui"]:
                w.line_color = (1.0, 1.0, 1.0, 0.25)
            else:
                w.line_color = (1.0, 1.0, 1.0, 0.5)

            if m["state"] == LXMF.LXMessage.SENDING or m["state"] == LXMF.LXMessage.OUTBOUND or m["state"] == LXMF.LXMessage.SENT:
                msg = self.app.sideband.message(m["hash"])

                if msg != None:
                    delivery_syms = ""
                    # if msg["extras"] != None and "ratchet_id" in m["extras"]:
                    #     delivery_syms += " ⚙️"
                    if msg["method"] == LXMF.LXMessage.OPPORTUNISTIC:
                        delivery_syms += " 📨"
                    if msg["method"] == LXMF.LXMessage.DIRECT:
                        delivery_syms += " 🔗"
                    if msg["method"] == LXMF.LXMessage.PROPAGATED:
                        delivery_syms += " 📦"
                    delivery_syms = multilingual_markup(delivery_syms.encode("utf-8")).decode("utf-8")

                    if msg["state"] == LXMF.LXMessage.OUTBOUND or msg["state"] == LXMF.LXMessage.SENDING or msg["state"] == LXMF.LXMessage.SENT:
                        w.md_bg_color = msg_color = mdc(color_unknown, intensity_msgs)
                        txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                        titlestr = ""
                        prgstr = ""
                        sphrase = "Sending"
                        prg = self.app.sideband.get_lxm_progress(msg["hash"])
                        if prg != None:
                            prgstr = ", "+str(round(prg*100, 1))+"% done"
                            if prg <= 0.00:
                                stamp_cost = self.app.sideband.get_lxm_stamp_cost(msg["hash"])
                                if stamp_cost:
                                    sphrase = f"Generating stamp with cost {stamp_cost}"
                                    prgstr = ""
                                else:
                                    sphrase = "Waiting for path"
                            elif prg <= 0.01:
                                sphrase = "Waiting for path"
                            elif prg <= 0.03:
                                sphrase = "Establishing link"
                            elif prg <= 0.05:
                                sphrase = "Link established"
                            elif prg >= 0.05:
                                sphrase = "Sending"
                            
                        if msg["title"]:
                            titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                        w.heading = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] "+sphrase+prgstr+"                          "
                        if w.has_audio:
                            alstr = RNS.prettysize(w.audio_size)
                            w.heading += f"\n[b]Audio Message[/b] ({alstr})"
                        m["state"] = msg["state"]


                    if msg["state"] == LXMF.LXMessage.DELIVERED:
                        w.md_bg_color = msg_color = mdc(color_delivered, intensity_msgs)
                        txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                        titlestr = ""
                        if msg["title"]:
                            titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                        w.heading = titlestr+"[b]Sent[/b] "+txstr+delivery_syms+"\n[b]State[/b] Delivered"
                        if w.has_audio:
                            alstr = RNS.prettysize(w.audio_size)
                            w.heading += f"\n[b]Audio Message[/b] ({alstr})"
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
                        w.heading = titlestr+"[b]Sent[/b] "+txstr+delivery_syms+"\n[b]State[/b] On Propagation Net"
                        if w.has_audio:
                            alstr = RNS.prettysize(w.audio_size)
                            w.heading += f"\n[b]Audio Message[/b] ({alstr})"
                        m["state"] = msg["state"]

                    if msg["state"] == LXMF.LXMessage.FAILED:
                        w.md_bg_color = msg_color = mdc(color_failed, intensity_msgs)
                        txstr = time.strftime(ts_format, time.localtime(msg["sent"]))
                        titlestr = ""
                        if msg["title"]:
                            titlestr = "[b]Title[/b] "+msg["title"].decode("utf-8")+"\n"
                        w.heading = titlestr+"[b]Sent[/b] "+txstr+"\n[b]State[/b] Failed"
                        m["state"] = msg["state"]
                        if w.has_audio:
                            alstr = RNS.prettysize(w.audio_size)
                            w.heading += f"\n[b]Audio Message[/b] ({alstr})"
                        w.dmenu.items.append(w.dmenu.retry_item)


    def hide_widget(self, wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

    def update_widget(self):
        if self.app.sideband.config["dark_ui"]:
            intensity_msgs = intensity_msgs_dark
            intensity_play = intensity_play_dark
            mt_color = [1.0, 1.0, 1.0, 0.8]
        else:
            intensity_msgs = intensity_msgs_light
            intensity_play = intensity_play_light
            mt_color = [1.0, 1.0, 1.0, 0.95]

        self.ids.message_text.font_name = self.app.input_font

        if self.loading_earlier_messages:
            self.new_messages.reverse()

        for m in self.new_messages:
            if not m["hash"] in self.added_item_hashes:
                try:
                    if not self.is_trusted:
                        message_input = str( escape_markup(m["content"].decode("utf-8")) ).encode("utf-8")
                    else:
                        message_input = m["content"]
                except Exception as e:
                    RNS.log(f"Message content could not be decoded: {e}", RNS.LOG_DEBUG)
                    message_input = b""

                if message_input.strip() == b"":
                    if not ("lxm" in m and m["lxm"] != None and m["lxm"].fields != None and LXMF.FIELD_COMMANDS in m["lxm"].fields):
                        message_input = "[i]This message contains no text content[/i]".encode("utf-8")

                message_markup = multilingual_markup(message_input)

                txstr = time.strftime(ts_format, time.localtime(m["sent"]))
                rxstr = time.strftime(ts_format, time.localtime(m["received"]))
                titlestr = ""
                extra_content = ""
                extra_telemetry = {}
                telemeter = None
                image_field = None
                audio_field = None
                has_image = False
                has_audio = False
                attachments_field = None
                has_attachment = False
                force_markup = False
                signature_valid = False
                stamp_valid = False
                stamp_value = None

                delivery_syms = ""
                # if m["extras"] != None and "ratchet_id" in m["extras"]:
                #     delivery_syms += " ⚙️"
                if m["method"] == LXMF.LXMessage.OPPORTUNISTIC:
                    delivery_syms += " 📨"
                if m["method"] == LXMF.LXMessage.DIRECT:
                    delivery_syms += " 🔗"
                if m["method"] == LXMF.LXMessage.PROPAGATED:
                    delivery_syms += " 📦"
                delivery_syms = multilingual_markup(delivery_syms.encode("utf-8")).decode("utf-8")

                if "lxm" in m and m["lxm"] != None and m["lxm"].signature_validated:
                    signature_valid = True

                if "extras" in m and m["extras"] != None and "packed_telemetry" in m["extras"]:
                    try:
                        telemeter = Telemeter.from_packed(m["extras"]["packed_telemetry"])
                    except Exception as e:
                        pass

                if "extras" in m and m["extras"] != None and "stamp_checked" in m["extras"] and m["extras"]["stamp_checked"] == True:
                    stamp_valid = m["extras"]["stamp_valid"]
                    stamp_value = m["extras"]["stamp_value"]

                if "lxm" in m and m["lxm"] != None and m["lxm"].fields != None and LXMF.FIELD_COMMANDS in m["lxm"].fields:
                    try:
                        commands = m["lxm"].fields[LXMF.FIELD_COMMANDS]
                        for command in commands:
                            if Commands.ECHO in command:
                                extra_content = "[font=RobotoMono-Regular]> echo "+command[Commands.ECHO].decode("utf-8")+"[/font]\n"
                            if Commands.PING in command:
                                extra_content = "[font=RobotoMono-Regular]> ping[/font]\n"
                            if Commands.SIGNAL_REPORT in command:
                                extra_content = "[font=RobotoMono-Regular]> sig[/font]\n"
                            if Commands.PLUGIN_COMMAND in command:
                                cmd_content = command[Commands.PLUGIN_COMMAND]
                                extra_content = "[font=RobotoMono-Regular]> "+str(cmd_content)+"[/font]\n"
                        extra_content = extra_content[:-1]
                        force_markup = True
                    except Exception as e:
                        RNS.log("Error while generating command display: "+str(e), RNS.LOG_ERROR)

                if telemeter == None and "lxm" in m and m["lxm"] and m["lxm"].fields != None and LXMF.FIELD_TELEMETRY in m["lxm"].fields:
                    try:
                        packed_telemetry = m["lxm"].fields[LXMF.FIELD_TELEMETRY]
                        telemeter = Telemeter.from_packed(packed_telemetry)
                    except Exception as e:
                        pass

                if "lxm" in m and m["lxm"] and m["lxm"].fields != None and LXMF.FIELD_IMAGE in m["lxm"].fields:
                    try:
                        image_field = m["lxm"].fields[LXMF.FIELD_IMAGE]
                        has_image = True
                    except Exception as e:
                        pass

                if "lxm" in m and m["lxm"] and m["lxm"].fields != None and LXMF.FIELD_AUDIO in m["lxm"].fields:
                    try:
                        audio_field = m["lxm"].fields[LXMF.FIELD_AUDIO]
                        has_audio = True
                    except Exception as e:
                        pass

                if "lxm" in m and m["lxm"] and m["lxm"].fields != None and LXMF.FIELD_FILE_ATTACHMENTS in m["lxm"].fields:
                    if len(m["lxm"].fields[LXMF.FIELD_FILE_ATTACHMENTS]) > 0:
                        try:
                            attachments_field = m["lxm"].fields[LXMF.FIELD_FILE_ATTACHMENTS]
                            has_attachment = True
                        except Exception as e:
                            pass

                rcvd_d_str = ""
                
                trcvd = telemeter.read("received") if telemeter else None
                if trcvd and "distance" in trcvd:
                    d = trcvd["distance"]
                    if "euclidian" in d:
                        edst = d["euclidian"]
                        if edst != None:
                            rcvd_d_str = "\n[b]Distance[/b] "+RNS.prettydistance(edst)
                    elif "geodesic" in d:
                        gdst = d["geodesic"]
                        if gdst != None:
                            rcvd_d_str = "\n[b]Distance[/b] "+RNS.prettydistance(gdst) + " (geodesic)"

                phy_stats_str = ""
                if "extras" in m and m["extras"] != None:
                    phy_stats = m["extras"]
                    if "q" in phy_stats:
                        try:
                            lq = round(float(phy_stats["q"]), 1)
                            phy_stats_str += "[b]Link Quality[/b] "+str(lq)+"% "
                            extra_telemetry["quality"] = lq
                        except:
                            pass
                    if "rssi" in phy_stats:
                        try:
                            lr = round(float(phy_stats["rssi"]), 1)
                            phy_stats_str += "[b]RSSI[/b] "+str(lr)+"dBm "
                            extra_telemetry["rssi"] = lr
                        except:
                            pass
                    if "snr" in phy_stats:
                        try:
                            ls = round(float(phy_stats["snr"]), 1)
                            phy_stats_str += "[b]SNR[/b] "+str(ls)+"dB "
                            extra_telemetry["snr"] = ls
                        except:
                            pass

                if m["title"]:
                    titlestr = "[b]Title[/b] "+m["title"].decode("utf-8")+"\n"

                if m["source"] == self.app.sideband.lxmf_destination.hash:
                    if m["state"] == LXMF.LXMessage.DELIVERED:
                        msg_color = mdc(color_delivered, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+delivery_syms+"\n[b]State[/b] Delivered"

                    elif m["method"] == LXMF.LXMessage.PROPAGATED and m["state"] == LXMF.LXMessage.SENT:
                        msg_color = mdc(color_propagated, intensity_msgs)
                        heading_str = titlestr+"[b]Sent[/b] "+txstr+delivery_syms+"\n[b]State[/b] On Propagation Net"

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
                    heading_str = titlestr
                    if phy_stats_str != "" and self.app.sideband.config["advanced_stats"]:
                        heading_str += phy_stats_str+"\n"
                    # TODO: Remove
                    # if stamp_valid:
                    #     txstr += f" [b]Stamp[/b] value is {stamp_value} "

                    heading_str += "[b]Sent[/b] "+txstr+delivery_syms
                    heading_str += "\n[b]Received[/b] "+rxstr

                    if rcvd_d_str != "":
                        heading_str += rcvd_d_str

                pre_content = ""
                if not signature_valid:
                    identity_known = False
                    if RNS.Identity.recall(m["hash"]) != None:
                        identity_known = True

                    if identity_known == True:
                        pre_content += "[b]Warning![/b] The signature for this message could not be validated. [b]This message is likely to be fake[/b].\n\n"
                        force_markup = True

                if has_attachment:
                    heading_str += "\n[b]Attachments[/b] "
                    for attachment in attachments_field:
                        heading_str += str(attachment[0])+", "
                    heading_str = heading_str[:-2]

                if has_audio:
                    alstr = RNS.prettysize(len(audio_field[1]))
                    heading_str += f"\n[b]Audio Message[/b] ({alstr})"

                item = ListLXMessageCard(
                    text=pre_content+message_markup.decode("utf-8")+extra_content,
                    heading=heading_str,
                    md_bg_color=msg_color,
                )
                item.lsource = m["source"]
                item.has_audio = False

                if has_attachment:
                    item.attachments_field = attachments_field

                if has_audio:
                    def play_audio(sender):
                        self.app.play_audio_field(sender.audio_field)
                        stored_color = sender.md_bg_color
                        if sender.lsource == self.app.sideband.lxmf_destination.hash:
                            sender.md_bg_color = mdc(color_delivered, intensity_play)
                        else:
                            sender.md_bg_color = mdc(color_received, intensity_play)

                        def cb(dt):
                            sender.md_bg_color = stored_color
                        Clock.schedule_once(cb, 0.25)

                    item.has_audio = True
                    item.audio_size = len(audio_field[1])
                    item.audio_field = audio_field
                    item.bind(on_release=play_audio)

                if image_field != None:
                    item.has_image = True
                    item.image_field = image_field
                    img = item.ids.message_image
                    img.source = ""

                    # Convert to PNG format on OSX, since support
                    # for webp seems rather flaky.
                    if RNS.vendor.platformutils.is_darwin():
                        im = PilImage.open(io.BytesIO(image_field[1]))
                        buf = io.BytesIO()
                        im.save(buf, format="png")
                        image_field[1] = buf.getvalue()
                        image_field[0] = "png"

                    img.texture = CoreImage(io.BytesIO(image_field[1]), ext=image_field[0]).texture
                    img.reload()

                else:
                    item.has_image = False

                def check_textures(w, val):
                    try:
                        if w.texture_size[0] > 360 and w.texture_size[1] >= self.max_texture_size:
                            w.text = "[i]The content of this message is too large to display in the message stream. You can copy the message content into another program by using the context menu of this message, and selecting [b]Copy[/b].[/i]"

                        if w.owner.has_image:
                            img = w.owner.ids.message_image
                            img.size_hint_x = 1
                            img.size_hint_y = None
                            img_w = w.owner.size[0]
                            img_ratio = img.texture_size[0] / img.texture_size[1]
                            img.size = (img_w,img_w/img_ratio)
                            img.fit_mode = "contain"

                    except Exception as e:
                        RNS.log("An error occurred while scaling message display textures:", RNS.LOG_ERROR)
                        RNS.trace_exception(e)

                item.ids.content_text.owner = item
                item.ids.content_text.bind(texture_size=check_textures)

                if not RNS.vendor.platformutils.is_android():
                    item.radius = dp(5)

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

                def gen_retry(mhash, mcontent, item):
                    def x():
                        self.app.messages_view.ids.message_text.text = mcontent.decode("utf-8")
                        self.app.sideband.delete_message(mhash)
                        self.app.message_send_action()
                        item.dmenu.dismiss()
                        def cb(dt):
                            self.reload()
                        Clock.schedule_once(cb, 0.2)

                    return x

                def gen_details(mhash, item):
                    def x():
                        item.dmenu.dismiss()
                        def cb(dt):
                            self.message_details_dialog(mhash)
                        Clock.schedule_once(cb, 0.2)

                    return x

                def gen_copy(msg, item):
                    def x():
                        Clipboard.copy(msg)
                        item.dmenu.dismiss()

                    return x

                def gen_save_image(item):
                    if RNS.vendor.platformutils.is_android():
                        def x():
                            image_field = item.image_field
                            extension = str(image_field[0]).replace(".", "")
                            filename = time.strftime("LXM_%Y_%m_%d_%H_%M_%S", time.localtime(time.time()))+"."+str(extension)
                            
                            self.app.share_image(image_field[1], filename)
                            item.dmenu.dismiss()
                        return x

                    else:
                        def x():
                            image_field = item.image_field
                            try:
                                extension = str(image_field[0]).replace(".", "")
                                filename = time.strftime("LXM_%Y_%m_%d_%H_%M_%S", time.localtime(time.time()))+"."+str(extension)
                                if RNS.vendor.platformutils.is_darwin():
                                    save_path = str(plyer.storagepath.get_downloads_dir()+filename).replace("file://", "")
                                else:
                                    save_path = plyer.storagepath.get_downloads_dir()+"/"+filename

                                with open(save_path, "wb") as save_file:
                                    save_file.write(image_field[1])

                                item.dmenu.dismiss()

                                ok_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                                dialog = MDDialog(
                                    title="Image Saved",
                                    text="The image has been saved to: "+save_path+"",
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
                                    text="Could not save the image:\n\n"+save_path+"\n\n"+str(e),
                                    buttons=[ ok_button ],
                                    # elevation=0,
                                )
                                def dl_ok(s):
                                    dialog.dismiss()
                                
                                ok_button.bind(on_release=dl_ok)
                                dialog.open()

                            item.dmenu.dismiss()

                        return x

                def gen_save_attachment(item):
                    def x():
                        attachments_field = item.attachments_field
                        if isinstance(attachments_field, list):
                            try:
                                if RNS.vendor.platformutils.is_darwin():
                                    output_path = str(plyer.storagepath.get_downloads_dir()).replace("file://", "")
                                else:
                                    output_path = plyer.storagepath.get_downloads_dir()+"/"

                                if len(attachments_field) == 1:
                                    saved_text = "The attached file has been saved to: "+output_path
                                    saved_title = "Attachment Saved"
                                else:
                                    saved_text = "The attached files have been saved to: "+output_path
                                    saved_title = "Attachment Saved"

                                for attachment in attachments_field:
                                    filename = str(attachment[0]).replace("../", "").replace("..\\", "")
                                    if RNS.vendor.platformutils.is_darwin():
                                        save_path = str(plyer.storagepath.get_downloads_dir()+filename).replace("file://", "")
                                    else:
                                        save_path = plyer.storagepath.get_downloads_dir()+"/"+filename

                                    name_counter = 1
                                    pre_count = save_path
                                    while os.path.exists(save_path):
                                        save_path = str(pre_count)+"."+str(name_counter)
                                        name_counter += 1

                                    saved_text = "The attached file has been saved to: "+save_path

                                    with open(save_path, "wb") as save_file:
                                        save_file.write(attachment[1])

                                item.dmenu.dismiss()

                                ok_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                                dialog = MDDialog(
                                    title=saved_title,
                                    text=saved_text,
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
                                    text="Could not save the attachment:\n\n"+save_path+"\n\n"+str(e),
                                    buttons=[ ok_button ],
                                    # elevation=0,
                                )
                                def dl_ok(s):
                                    dialog.dismiss()
                                
                                ok_button.bind(on_release=dl_ok)
                                dialog.open()

                            item.dmenu.dismiss()

                    return x

                def gen_copy_telemetry(telemeter, extra_telemetry, item):
                    def x():
                        try:
                            telemeter
                            if extra_telemetry and len(extra_telemetry) != 0:
                                physical_link = extra_telemetry
                                telemeter.synthesize("physical_link")
                                if "rssi" in physical_link: telemeter.sensors["physical_link"].rssi = physical_link["rssi"]
                                if "snr" in physical_link: telemeter.sensors["physical_link"].snr = physical_link["snr"]
                                if "quality" in physical_link: telemeter.sensors["physical_link"].q = physical_link["quality"]
                                telemeter.sensors["physical_link"].update_data()
                            
                            tlm = telemeter.read_all()
                            Clipboard.copy(str(tlm))
                            item.dmenu.dismiss()
                        except Exception as e:
                            RNS.log("An error occurred while decoding telemetry. The contained exception was: "+str(e), RNS.LOG_ERROR)
                            Clipboard.copy("Could not decode telemetry")

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

                retry_item = {
                    "viewclass": "OneLineListItem",
                    "text": "Retry",
                    "height": dp(40),
                    "on_release": gen_retry(m["hash"], m["content"], item)
                }

                details_item = {
                    "viewclass": "OneLineListItem",
                    "text": "Details",
                    "height": dp(40),
                    "on_release": gen_details(m["hash"], item)
                }

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
                                "on_release": gen_copy(message_input.decode("utf-8"), item)
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
                                "on_release": gen_copy(message_input.decode("utf-8"), item)
                            },
                            {
                                "text": "Delete",
                                "viewclass": "OneLineListItem",
                                "height": dp(40),
                                "on_release": gen_del(m["hash"], item)
                            }
                        ]

                else:
                    if m["state"] == LXMF.LXMessage.FAILED:
                        dm_items = [
                            retry_item,
                            {
                                "viewclass": "OneLineListItem",
                                "text": "Copy",
                                "height": dp(40),
                                "on_release": gen_copy(message_input.decode("utf-8"), item)
                            },
                            {
                                "text": "Delete",
                                "viewclass": "OneLineListItem",
                                "height": dp(40),
                                "on_release": gen_del(m["hash"], item)
                            }
                        ]
                    else:
                        if telemeter != None:
                            dm_items = [
                                details_item,
                                {
                                    "viewclass": "OneLineListItem",
                                    "text": "Copy",
                                    "height": dp(40),
                                    "on_release": gen_copy(message_input.decode("utf-8"), item)
                                },
                                {
                                    "viewclass": "OneLineListItem",
                                    "text": "Copy telemetry",
                                    "height": dp(40),
                                    "on_release": gen_copy_telemetry(telemeter, extra_telemetry, item)
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
                                details_item,
                                {
                                    "viewclass": "OneLineListItem",
                                    "text": "Copy",
                                    "height": dp(40),
                                    "on_release": gen_copy(message_input.decode("utf-8"), item)
                                },
                                {
                                    "text": "Delete",
                                    "viewclass": "OneLineListItem",
                                    "height": dp(40),
                                    "on_release": gen_del(m["hash"], item)
                                }
                            ]
                        if has_image:
                            extra_item = {
                                "viewclass": "OneLineListItem",
                                "text": "Save image",
                                "height": dp(40),
                                "on_release": gen_save_image(item)
                            }
                            dm_items.append(extra_item)
                        if has_attachment:
                            extra_item = {
                                "viewclass": "OneLineListItem",
                                "text": "Save attachment",
                                "height": dp(40),
                                "on_release": gen_save_attachment(item)
                            }
                            dm_items.append(extra_item)

                item.dmenu = MDDropdownMenu(
                    caller=item.ids.msg_submenu,
                    items=dm_items,
                    position="auto",
                    width=dp(256),
                    elevation=0,
                    radius=dp(3),
                )
                item.dmenu.md_bg_color = self.app.color_hover
                item.dmenu.retry_item = retry_item

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

messages_screen_kv = """
MDScreen:
    name: "messages_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: messages_toolbar
            anchor_title: "left"
            title: "Messages"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")],]
            right_action_items:
                [
                ['attachment-plus', lambda x: root.app.message_attachment_action(self)],
                ['map-marker-path', lambda x: root.app.peer_show_telemetry_action(self)],
                ['map-search', lambda x: root.app.peer_show_location_action(self)],
                ['lan-connect', lambda x: root.app.message_propagation_action(self)],
                ['close', lambda x: root.app.close_settings_action(self)],
                ]

        ScrollView:
            id: messages_scrollview
            do_scroll_x: False
            do_scroll_y: True

        BoxLayout:
            id: no_keys_part
            orientation: "vertical"
            padding: [dp(16), dp(0), dp(16), dp(16)]
            spacing: dp(24)
            size_hint_y: None
            height: self.minimum_height + dp(64)

            MDLabel:
                id: nokeys_text
                text: ""

            MDRectangleFlatIconButton:
                icon: "key-wireless"
                text: "Query Network For Keys"
                on_release: root.app.key_query_action(self)

        BoxLayout:
            id: message_ptt
            padding: [dp(16), dp(8), dp(16), dp(8)]
            spacing: dp(24)
            size_hint_y: None
            height: self.minimum_height

            MDRectangleFlatIconButton:
                id: message_ptt_button
                icon: "microphone"
                text: "PTT"
                size_hint_x: 1.0
                padding: [dp(10), dp(13), dp(10), dp(14)]
                icon_size: dp(24)
                font_size: dp(16)
                on_press: root.app.message_ptt_down_action(self)
                on_release: root.app.message_ptt_up_action(self)
                _no_ripple_effect: True
                background_normal: ""
                background_down: ""            

        BoxLayout:
            id: message_input_part
            padding: [dp(16), dp(0), dp(16), dp(16)]
            spacing: dp(24)
            size_hint_y: None
            height: self.minimum_height

            MDTextField:
                id: message_text
                keyboard_suggestions: True
                multiline: True
                hint_text: "Write message"
                mode: "rectangle"
                max_height: dp(100)

            MDRectangleFlatIconButton:
                id: message_send_button
                icon: "transfer-up"
                text: "Send"
                padding: [dp(10), dp(13), dp(10), dp(14)]
                icon_size: dp(24)
                font_size: dp(16)
                on_release: root.app.message_send_action(self)
"""

Builder.load_string("""
<ListLXMessageCard>:
    style: "outlined"
    padding: dp(8)
    radius: dp(4)
    size_hint: 1.0, None
    height: content_text.height + heading_text.height + message_image.size[1] + dp(32)
    pos_hint: {"center_x": .5, "center_y": .5}

    MDRelativeLayout:
        size_hint: 1.0, None
        theme_text_color: "ContrastParentBackground"

        MDIconButton:
            id: msg_submenu
            icon: "dots-vertical"
            # theme_text_color: 'Custom'
            # text_color: rgba(255,255,255,216)
            pos:
                root.width - (self.width + root.padding[0] + dp(4)), root.height - (self.height + root.padding[0] + dp(4))

        MDLabel:
            id: heading_text
            markup: True
            text: root.heading
            adaptive_size: True
            # theme_text_color: 'Custom'
            # text_color: rgba(255,255,255,100)
            pos: 0, root.height - (self.height + root.padding[0] + dp(8))

        Image:
            id: message_image
            size_hint_x: 0
            size_hint_y: 0
            pos: 0, root.height - (self.height + root.padding[0] + dp(8)) - heading_text.height - dp(8)

        MDLabel:
            id: content_text
            text: root.text
            markup: True
            size_hint_y: None
            text_size: self.width, None
            height: self.texture_size[1]

<CustomOneLineIconListItem>
    IconLeftWidget:
        icon: root.icon
""")
