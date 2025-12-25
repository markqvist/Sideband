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
from kivy.properties import StringProperty, BooleanProperty, OptionProperty, ColorProperty, Property
from kivymd.uix.list import MDList, IconLeftWidget, IconRightWidget, OneLineAvatarIconListItem
from kivymd.icon_definitions import md_icons
from kivymd.toast import toast
from kivy.properties import StringProperty, BooleanProperty
from kivy.effects.scroll import ScrollEffect

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import dark_theme_text_color
else:
    from .helpers import dark_theme_text_color

class Guide():
    def __init__(self, app):
        self.app = app
        self.screen = None

        if not self.app.root.ids.screen_manager.has_screen("guide_screen"):
            self.screen = Builder.load_string(layout_guide_screen)
            self.screen.app = self
            self.app.root.ids.screen_manager.add_widget(self.screen)

            def link_exec(sender=None, event=None):
                def lj(): webbrowser.open("https://unsigned.io/donate")
                threading.Thread(target=lj, daemon=True).start()

            guide_text1 = """
[size=18dp][b]Introduction[/b][/size][size=5dp]\n \n[/size]Welcome to [i]Sideband[/i], an LXMF client for Android, Linux, macOS and Windows. With Sideband, you can communicate with other people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, or anything else Reticulum supports.

This short guide will give you a basic introduction to the concepts that underpin Sideband and LXMF (which is the protocol that Sideband uses to communicate). If you are not already familiar with LXMF and Reticulum, it is probably a good idea to read this guide, since Sideband is very different from other messaging apps."""
            guide_text2 = """
[size=18dp][b]Communication Without Subjection[/b][/size][size=5dp]\n \n[/size]Sideband is completely free, permission-less, anonymous and infrastructure-less. Sideband uses the peer-to-peer and distributed messaging system LXMF. There is no sign-up, no service providers, no "end-user license agreements", no data theft and no surveillance. You own the system.

This also means that Sideband operates differently than what you might be used to. It does not need a connection to a server on the Internet to function, and you do not have an account anywhere."""
            
            guide_text3 = """
[size=18dp][b]Operating Principles[/b][/size][size=5dp]\n \n[/size]When Sideband is started on your device for the first time, it randomly generates a 512-bit Reticulum Identity Key. This cryptographic key is then used to create an LXMF address for your use, and in turn to secure any communication to your address. Any other endpoint in [i]any[/i] Reticulum network will be able to send data to your address, as long as there is [i]some sort of physical connection[/i] between your device and the remote endpoint. You can also move around to other Reticulum networks with this address, even ones that were never connected to the network the address was created on, or that didn't exist when the address was created.\n\nYour LXMF address is yours to keep and control for as long (or short) a time you need it, and you can always delete it and create a new one. You identity keys and corresponding addresses are never registered on or controlled by any external servers or services, and will never leave your device, unless you manually export them for backup."""
            
            guide_text10 = """
[size=18dp][b]Getting Connected[/b][/size][size=5dp]\n \n[/size]If you already have Reticulum connectivity set up on the device you are running Sideband on, no further configuration should be necessary, and Sideband will simply use the available Reticulum connectivity.\n\nIf you are running Sideband on a computer, you can configure interfaces in the Reticulum configuration file ([b]~/.reticulum/config[/b] by default). If you are running Sideband on an Android device, you can configure various interface types in the [b]Connectivity[/b] section. By default, only an [i]AutoInterface[/i] is enabled, which will connect you automatically with any other local devices on the same WiFi and/or Ethernet networks. This may or may not include Reticulum Transport Nodes, which can route your traffic to wider networks.\n\nYou can enable any or all of the other available interface types to gain wider connectivity. For more specific information on interface types, configuration options, and how to effectively build your own Reticulum networks, see the [b]Reticulum Manual[b]."""
        
            guide_text4 = """
[size=18dp][b]Becoming Reachable[/b][/size][size=5dp]\n \n[/size]To establish reachability for any Reticulum destination on a network, an [i]announce[/i] must be sent. By default, Sideband will announce automatically when necessary, but if you want to stay silent, automatic announces can be disabled in [b]Preferences[/b].\n\nTo send an announce manually, press the [i]Announce[/i] button in the [i]Conversations[/i] section of the program. When you send an announce, you make your LXMF address reachable for real-time messaging to the entire network you are connected to. Even in very large networks, you can expect global reachability for your address to be established in under a minute.

If you don't move to other places in the network, and keep connected through the same hubs or gateways, it is generally not necessary to send an announce more often than once every week. If you change your entry point to the network, you may want to send an announce, or you may just want to stay quiet."""

            guide_text5 = """
[size=18dp][b]Relax & Disconnect[/b][/size][size=5dp]\n \n[/size]If you are not connected to the network, it is still possible for other people to message you, as long as one or more [i]Propagation Nodes[/i] exist on the network. These nodes pick up and hold encrypted in-transit messages for offline users. Messages are always encrypted before leaving the originators device, and nobody else than the intended recipient can decrypt messages in transit.

The Propagation Nodes also distribute copies of messages between each other, such that even the failure of almost every node in the network will still allow users to sync their waiting messages. If all Propagation Nodes disappear or are destroyed, users can still communicate directly.\n\nReticulum and LXMF will degrade gracefully all the way down to single users communicating directly via long-range data radios. Anyone can start up new propagation nodes and integrate them into existing networks without permission or coordination. Even a small and cheap device like a Rasperry Pi can handle messages for millions of users. LXMF networks are designed to be quite resilient, as long as there are people using them."""

            guide_text6 = """
[size=18dp][b]Packets Find A Way[/b][/size][size=5dp]\n \n[/size]Connections in Reticulum networks can be wired or wireless, span many intermediary hops, run over fast links or ultra-low bandwidth radio, tunnel over the Invisible Internet (I2P), private networks, satellite connections, serial lines or anything else that Reticulum can carry data over.\n\nIn most cases it will not be possible to know what path packets takes in a Reticulum network, and apart from a destination hash, no transmitted packets carries any identifying characteristics. In Reticulum, [i]there is no source addresses[/i].\n\nAs long as you do not reveal any connecting details between your person and your LXMF address, you can remain anonymous. Sending messages to others does not reveal [i]your[/i] address to anyone else than the intended recipient."""

            guide_text7 = """
[size=18dp][b]Be Yourself, Be Unknown, Stay Free[/b][/size][size=5dp]\n \n[/size]Even with the above characteristics in mind, you [b]must remember[/b] that LXMF and Reticulum is not a technology that can guarantee anonymising connections that are already de-anonymised! If you use Sideband to connect to TCP Reticulum hubs over the clear Internet, from a network that can be tied to your personal identity, an adversary may learn that you are generating LXMF traffic.\n\nIf you want to avoid this, it is recommended to use I2P to connect to Reticulum hubs on the Internet. Or only connecting from within pure Reticulum networks, that take one or more hops to reach connections that span the Internet. This is a complex topic, with many more nuances than can be covered here. You are encouraged to ask on the various Reticulum discussion forums if you are in doubt.

If you use Reticulum and LXMF on hardware that does not carry any identifiers tied to you, it is possible to establish a completely free and identification-less communication system with Reticulum and LXMF clients."""
        
            guide_text8 = """
[size=18dp][b]Keyboard Shortcuts[/b][/size][size=5dp]\n \n[/size]To ease navigation and operation of the program, Sideband has keyboard shortcuts mapped to the most common actions. A reference is included below.

[b]Quick Actions[/b]
 - [b]Ctrl-W[/b] Go back
 - [b]Ctrl-Q[/b] Shut down Sideband
 - [b]Ctrl-R[/b] Start LXMF sync (from Conversations screen)
 - [b]Ctrl-N[/b] Create new conversation
 
 [b]Message Actions[/b]
 - [b]Ctrl-Shift-A[/b] add message attachment
 - [b]Ctrl-Shift-V[/b] add high-quality voice
 - [b]Ctrl-Shift-C[/b] add low-bandwidth voice
 - [b]Ctrl-Shift-I[/b] add medium-quality image
 - [b]Ctrl-Shift-F[/b] add file
 - [b]Ctrl-D[/b] or [b]Ctrl-S[/b] Send message

 [b]Voice & PTT Messages[/b]
 - [b]Space[/b] Start/stop recording
 - [b]Enter[/b] Save recording to message
 - With PTT enabled, hold [b]Space[/b] to talk

 [b]Voice Calls[/b]
 - [b]Ctrl-Space[/b] Answer incoming call
 - [b]Ctrl-.[/b] Reject incoming call
 - [b]Ctrl-.[/b] Hang up active call

 [b]Navigation[/b]
 - [b]Ctrl-[i]n[/i][/b] Go to conversation number [i]n[/i]
 - [b]Ctrl-R[/b] Go to Conversations
 - [b]Ctrl-O[/b] Go to Objects & Devices
 - [b]Ctrl-E[/b] Go to Voice
 - [b]Ctrl-L[/b] Go to Announce Stream
 - [b]Ctrl-M[/b] Go to Situation Map
 - [b]Ctrl-U[/b] Go to Utilities
 - [b]Ctrl-T[/b] Go to Telemetry configuration
 - [b]Ctrl-G[/b] Go to Guide
 - [b]Ctrl-Y[/b] Display own telemetry

[b]Map Controls[/b]
 - [b]Up[/b], [b]down[/b], [b]left[/b], [b]right[/b] Navigate
 - [b]W[/b], [b]A[/b], [b]S[/b], [b]D[/b] Navigate
 - [b]H[/b], [b]J[/b], [b]L[/b], [b]K[/b] Navigate
 - [b]E[/b] or [b]+[/b] Zoom in
 - [b]Q[/b] or [b]-[/b] Zoom out
 - Hold [b]Shift[/b] to navigate more coarsely
 - Hold [b]Alt[/b] to navigate more finely"""

            guide_text9 = """
[size=18dp][b]Please Support This Project[/b][/size][size=5dp]\n \n[/size]It took me more than eight years to design and build the entire ecosystem of software and hardware that makes this possible. If this project is valuable to you, please go to [u][ref=link]https://unsigned.io/donate[/ref][/u] to support the project with a donation. Every donation directly makes the entire Reticulum project possible.

Thank you very much for using Free Communications Systems.
"""
            info1 = guide_text1
            info2 = guide_text8
            info3 = guide_text2
            info4 = guide_text3
            info10 = guide_text10
            info5 = guide_text4
            info6 = guide_text5
            info7 = guide_text6
            info8 = guide_text7
            info9 = guide_text9

            if self.app.theme_cls.theme_style == "Dark":
                info1 = "[color=#"+dark_theme_text_color+"]"+info1+"[/color]"
                info2 = "[color=#"+dark_theme_text_color+"]"+info2+"[/color]"
                info3 = "[color=#"+dark_theme_text_color+"]"+info3+"[/color]"
                info4 = "[color=#"+dark_theme_text_color+"]"+info4+"[/color]"
                info5 = "[color=#"+dark_theme_text_color+"]"+info5+"[/color]"
                info6 = "[color=#"+dark_theme_text_color+"]"+info6+"[/color]"
                info7 = "[color=#"+dark_theme_text_color+"]"+info7+"[/color]"
                info8 = "[color=#"+dark_theme_text_color+"]"+info8+"[/color]"
                info9 = "[color=#"+dark_theme_text_color+"]"+info9+"[/color]"
                info10 = "[color=#"+dark_theme_text_color+"]"+info10+"[/color]"
            self.screen.ids.guide_info1.text = info1
            self.screen.ids.guide_info2.text = info2
            self.screen.ids.guide_info3.text = info3
            self.screen.ids.guide_info4.text = info4
            self.screen.ids.guide_info5.text = info5
            self.screen.ids.guide_info6.text = info6
            self.screen.ids.guide_info7.text = info7
            self.screen.ids.guide_info8.text = info8
            self.screen.ids.guide_info9.text = info9
            self.screen.ids.guide_info10.text = info10
            self.screen.ids.guide_info9.bind(on_ref_press=link_exec)
            self.screen.ids.guide_scrollview.effect_cls = ScrollEffect

layout_guide_screen = """
MDScreen:
    name: "guide_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Guide"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [ ['menu', lambda x: root.app.app.nav_drawer.set_state("open")] ]
            right_action_items:
                [ ['close', lambda x: root.app.app.close_guide_action(self)] ]

        ScrollView:
            id:guide_scrollview

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(35), dp(16), dp(35), dp(16)]

                MDLabel:
                    id: guide_info1
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info2
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info3
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info4
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info10
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info5
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info6
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info7
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info8
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    id: guide_info9
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]
"""