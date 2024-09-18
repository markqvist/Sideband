root_layout = """
#: import NoTransition kivy.uix.screenmanager.NoTransition
#: import SlideTransition kivy.uix.screenmanager.SlideTransition
#:import images_path kivymd.images_path

MDNavigationLayout:
    md_bg_color: app.theme_cls.bg_darkest

    ScreenManager:
        id: screen_manager
        transition: SlideTransition()

        MDScreen:
            name: "starting_screen"
                 
            AnchorLayout:
                padding: [dp(0), dp(72), dp(0), dp(0)]
                anchor_x: "center"
                anchor_y: "center"

                BoxLayout:
                    spacing: dp(36)
                    orientation: 'vertical'
                    size_hint_y: None

                    MDLabel:
                        id: connecting_info
                        halign: "center"
                        text: "Please Wait"
                        font_size: "32dp"

                    MDIconButton:
                        pos_hint: {"center_x": .5, "center_y": .5}
                        icon: "transit-connection-variant"
                        icon_size: "92dp"

                    MDLabel:
                        id: connecting_status
                        halign: "center"
                        text: "Substantiating Reticulum"
                        font_size: "32dp"

    MDNavigationDrawer:
        id: nav_drawer
        radius: (0, dp(8), dp(8), 0)

        ContentNavigationDrawer:
            ScrollView:
                id: nav_scrollview
                DrawerList:
                    id: md_list
                    
                    MDList:
                        OneLineIconListItem:
                            text: "Conversations"
                            on_release: root.ids.screen_manager.app.conversations_action(self)
                            # _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "comment-text-multiple"
                                on_release: root.ids.screen_manager.app.conversations_action(self)
                                

                        OneLineIconListItem:
                            text: "Objects & Devices"
                            on_release: root.ids.screen_manager.app.objects_action(self)
                            # _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "devices"
                                on_release: root.ids.screen_manager.app.objects_action(self)
                                

                        OneLineIconListItem:
                            text: "Situation Map"
                            on_release: root.ids.screen_manager.app.map_action(self)
                        
                            IconLeftWidget:
                                icon: "map"
                                on_release: root.ids.screen_manager.app.map_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Announce Stream"
                            on_release: root.ids.screen_manager.app.announces_action(self)
                        
                            IconLeftWidget:
                                icon: "account-voice"
                                on_release: root.ids.screen_manager.app.announces_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Local Broadcasts"
                            on_release: root.ids.screen_manager.app.broadcasts_action(self)
                        
                            IconLeftWidget:
                                icon: "radio-tower"
                                on_release: root.ids.screen_manager.app.broadcasts_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Telemetry"
                            on_release: root.ids.screen_manager.app.telemetry_action(self)
                        
                            IconLeftWidget:
                                icon: "map-marker-path"
                                on_release: root.ids.screen_manager.app.telemetry_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Preferences"
                            on_release: root.ids.screen_manager.app.settings_action(self)
                        
                            IconLeftWidget:
                                icon: "cog"
                                on_release: root.ids.screen_manager.app.settings_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Connectivity"
                            on_release: root.ids.screen_manager.app.connectivity_action(self)
                        
                            IconLeftWidget:
                                icon: "wifi"
                                on_release: root.ids.screen_manager.app.connectivity_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Hardware"
                            on_release: root.ids.screen_manager.app.hardware_action(self)
                        
                            IconLeftWidget:
                                icon: "router-wireless"
                                on_release: root.ids.screen_manager.app.hardware_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Encryption Keys"
                            on_release: root.ids.screen_manager.app.keys_action(self)
                        
                            IconLeftWidget:
                                icon: "key-chain"
                                on_release: root.ids.screen_manager.app.keys_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Plugins"
                            on_release: root.ids.screen_manager.app.plugins_action(self)
                        
                            IconLeftWidget:
                                icon: "google-circles-extended"
                                on_release: root.ids.screen_manager.app.keys_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Guide"
                            on_release: root.ids.screen_manager.app.guide_action(self)
                        
                            IconLeftWidget:
                                icon: "book-open"
                                on_release: root.ids.screen_manager.app.guide_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Repository"
                            on_release: root.ids.screen_manager.app.repository_action(self)
                        
                            IconLeftWidget:
                                icon: "book-multiple"
                                on_release: root.ids.screen_manager.app.guide_action(self)

                                                       
                        OneLineIconListItem:
                            id: app_version_info
                            text: ""
                            on_release: root.ids.screen_manager.app.information_action(self)
                        
                            IconLeftWidget:
                                icon: "information"
                                on_release: root.ids.screen_manager.app.information_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Shutdown"
                            on_release: root.ids.screen_manager.app.quit_action(self)
                        
                            IconLeftWidget:
                                icon: "power"
                                on_release: root.ids.screen_manager.app.quit_action(self)

"""

layout_broadcasts_screen = """
MDScreen:
    name: "broadcasts_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Local Broadcasts"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_any_action(self)],
                ]

        ScrollView:
            id: broadcasts_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "24dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(35), dp(35), dp(35), dp(35)]

                MDLabel:
                    id: broadcasts_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]
"""

layout_exit_screen = """
MDScreen:
    name: "exit_screen"
         
    AnchorLayout:
        padding: [dp(0), dp(72), dp(0), dp(0)]
        anchor_x: "center"
        anchor_y: "center"

        BoxLayout:
            spacing: dp(36)
            orientation: 'vertical'
            size_hint_y: None

            MDLabel:
                id: exiting_info
                halign: "center"
                text: "Please Wait"
                font_size: "32dp"

            MDIconButton:
                pos_hint: {"center_x": .5, "center_y": .5}
                icon: "waves"
                icon_size: "92dp"

            MDLabel:
                id: exiting_status
                halign: "center"
                text: "Dissolving Reticulum"
                font_size: "32dp"
"""

layout_loader_screen = """
MDScreen:
    name: "loader_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: ""
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', None ]]
            right_action_items:
                [
                ]

        AnchorLayout:
            padding: [dp(0), dp(72), dp(0), dp(0)]
            anchor_x: "center"
            anchor_y: "center"

            BoxLayout:
                spacing: dp(36)
                orientation: 'vertical'
                size_hint_y: None

                MDIconButton:
                    pos_hint: {"center_x": .5, "center_y": .5}
                    icon: "dots-horizontal"
                    icon_size: "64dp"
"""

layout_connectivity_screen = """
MDScreen:
    name: "connectivity_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Connectivity"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_connectivity_action(self)],
                ]

        ScrollView:
            id: connectivity_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "10dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Configuring Connectivity\\n"
                    font_style: "H6"

                MDLabel:
                    id: connectivity_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(24)
                    
                    MDLabel:
                        id: connectivity_local_label
                        text: "Connect via local WiFi/Ethernet"
                        font_style: "H6"

                    MDSwitch:
                        id: connectivity_use_local
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    id: connectivity_local_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    MDTextField:
                        id: connectivity_local_groupid
                        hint_text: "Optional WiFi/Ethernet Group ID"
                        text: ""
                        max_text_length: 128
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_local_ifac_netname
                        hint_text: "Optional IFAC network name"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_local_ifac_passphrase
                        hint_text: "Optional IFAC passphrase"
                        text: ""
                        font_size: dp(24)


                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(24)
                    
                    MDLabel:
                        id: connectivity_tcp_label
                        text: "Connect via TCP"
                        font_style: "H6"

                    MDSwitch:
                        id: connectivity_use_tcp
                        pos_hint: {"center_y": 0.3}
                        active: False


                MDBoxLayout:
                    id: connectivity_tcp_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    MDTextField:
                        id: connectivity_tcp_host
                        hint_text: "TCP Host"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_tcp_port
                        hint_text: "TCP Port"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_tcp_ifac_netname
                        hint_text: "Optional IFAC network name"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_tcp_ifac_passphrase
                        hint_text: "Optional IFAC passphrase"
                        text: ""
                        font_size: dp(24)


                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(24)
                    
                    MDLabel:
                        id: connectivity_i2p_label
                        text: "Connect via I2P"
                        font_style: "H6"

                    MDSwitch:
                        id: connectivity_use_i2p
                        pos_hint: {"center_y": 0.3}
                        active: False


                MDBoxLayout:
                    id: connectivity_i2p_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    MDTextField:
                        id: connectivity_i2p_b32
                        hint_text: "I2P B32"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_i2p_ifac_netname
                        hint_text: "Optional IFAC network name"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_i2p_ifac_passphrase
                        hint_text: "Optional IFAC passphrase"
                        text: ""
                        font_size: dp(24)


                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(24)
                    
                    MDLabel:
                        id: connectivity_rnode_label
                        text: "Connect via RNode"
                        font_style: "H6"
                        disabled: False

                    MDSwitch:
                        id: connectivity_use_rnode
                        active: False
                        pos_hint: {"center_y": 0.3}
                        disabled: False

                MDBoxLayout:
                    id: connectivity_rnode_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    MDTextField:
                        id: connectivity_rnode_ifac_netname
                        hint_text: "Optional IFAC network name"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_rnode_ifac_passphrase
                        hint_text: "Optional IFAC passphrase"
                        text: ""
                        font_size: dp(24)


                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(24)
                    
                    MDLabel:
                        id: connectivity_modem_label
                        text: "Connect via Radio Modem"
                        font_style: "H6"
                        disabled: False

                    MDSwitch:
                        id: connectivity_use_modem
                        active: False
                        pos_hint: {"center_y": 0.3}
                        disabled: False

                MDBoxLayout:
                    id: connectivity_modem_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    MDTextField:
                        id: connectivity_modem_ifac_netname
                        hint_text: "Optional IFAC network name"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_modem_ifac_passphrase
                        hint_text: "Optional IFAC passphrase"
                        text: ""
                        font_size: dp(24)


                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(24)
                    
                    MDLabel:
                        id: connectivity_serial_label
                        text: "Connect via Serial Port"
                        font_style: "H6"
                        disabled: False

                    MDSwitch:
                        id: connectivity_use_serial
                        active: False
                        pos_hint: {"center_y": 0.3}
                        disabled: False

                MDBoxLayout:
                    id: connectivity_serial_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    MDTextField:
                        id: connectivity_serial_ifac_netname
                        hint_text: "Optional IFAC network name"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: connectivity_serial_ifac_passphrase
                        hint_text: "Optional IFAC passphrase"
                        text: ""
                        font_size: dp(24)


                # MDBoxLayout:
                #     orientation: "horizontal"
                #     padding: [0,0,dp(24),0]
                #     size_hint_y: None
                #     height: dp(24)
                    
                #     MDLabel:
                #         id: connectivity_bluetooth_label
                #         text: "Connect via Bluetooth"
                #         font_style: "H6"
                #         disabled: True

                #     MDSwitch:
                #         id: connectivity_use_bluetooth
                #         active: False
                #         pos_hint: {"center_y": 0.3}
                #         disabled: True

                # MDBoxLayout:
                #     id: connectivity_bluetooth_fields
                #     orientation: "vertical"
                #     size_hint_y: None
                #     height: self.minimum_height
                #     padding: [0, 0, 0, dp(32)]

                #     MDTextField:
                #         id: connectivity_bluetooth_cid
                #         hint_text: "Bluetooth Pairing ID"
                #         text: ""
                #         font_size: dp(24)
                #         # disabled: True

                MDLabel:
                    text: "Shared Instance Access\\n"
                    id: connectivity_shared_access_label
                    font_style: "H5"

                MDLabel:
                    id: connectivity_shared_access
                    markup: True
                    text: "The Reticulum instance launched by Sideband will be available for other programs on this system. By default, this grants connectivity to other local Reticulum-based programs, but no access to management, interface status and path information.\\n\\nIf you want to allow full functionality and ability to manage the running instance, you will need to configure other programs to use the correct RPC key for this instance.\\n\\nThis can be very useful for using other tools related to Reticulum, for example via command-line programs running in Termux. To do this, use the button below to copy the RPC key configuration line, and paste it into the Reticulum configuration file within the Termux environment, or other program.\\n\\nPlease note! [b]It is not necessary[/b] to enable Reticulum Transport for this to work!\\n\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    id: connectivity_shared_access_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    MDRectangleFlatIconButton:
                        id: rpc_keys_copy
                        icon: "file-key"
                        text: "Copy RPC Config To Clipboard"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.rpc_copy_action(self)

                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(24)
                    
                    MDLabel:
                        id: connectivity_transport_label
                        text: "Enable Reticulum Transport"
                        font_style: "H6"
                        # disabled: True

                    MDSwitch:
                        id: connectivity_enable_transport
                        active: False
                        pos_hint: {"center_y": 0.3}
                        # disabled: True

                MDLabel:
                    id: connectivity_transport_info
                    markup: True
                    text: "Enabling Reticulum Transport will allow this device to route traffic between all enabled interfaces.\\n\\nFor general usage, this option should not be enabled, but it can be useful in situations where you want to share connectivity from one device to many others. An example of this could be sharing connectivity from a radio interface to other people on your local WiFi network.\\n\\nWhen enabled, you will be able to configure the interface mode for all interfaces configured on this device. For more information on this topic, refer to the Reticulum Manual."
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    id: connectivity_transport_fields
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, 0, 0, dp(32)]

                    # MDLabel:
                    #     id: connectivity_modes_info
                    #     markup: True
                    #     text: "With Transport enabled, you can configure the interface modes for any enabled interfaces. Changing interface modes affects how Reticulum processes traffic and announces. For more information, refer to the Reticulum Manual."
                    #     size_hint_y: None
                    #     text_size: self.width, None
                    #     height: self.texture_size[1]

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: [dp(0), dp(12), dp(0), dp(12)]

                        MDTextField:
                            id: connectivity_local_ifmode
                            hint_text: "Local Interface Mode"
                            text: ""
                            font_size: dp(24)

                        MDTextField:
                            id: connectivity_tcp_ifmode
                            hint_text: "TCP Interface Mode"
                            text: ""
                            font_size: dp(24)

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: [dp(0), dp(12), dp(0), dp(12)]

                        MDTextField:
                            id: connectivity_i2p_ifmode
                            hint_text: "I2P Mode"
                            text: ""
                            font_size: dp(24)

                        MDTextField:
                            id: connectivity_rnode_ifmode
                            hint_text: "RNode Mode"
                            text: ""
                            font_size: dp(24)

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: [dp(0), dp(12), dp(0), dp(12)]

                        MDTextField:
                            id: connectivity_modem_ifmode
                            hint_text: "Modem Mode"
                            text: ""
                            font_size: dp(24)

                        MDTextField:
                            id: connectivity_serial_ifmode
                            hint_text: "Serial Mode"
                            text: ""
                            font_size: dp(24)

                    # MDTextField:
                    #     id: connectivity_bluetooth_ifmode
                    #     hint_text: "Bluetooth Mode"
                    #     text: ""
                    #     font_size: dp(24)
"""

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
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_guide_action(self)],
                ]

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

layout_information_screen = """
MDScreen:
    name: "information_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "App & Version Information"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_information_action(self)],
                ]

        ScrollView:
            id:information_scrollview

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(35)
                padding: [dp(35), dp(32), dp(35), dp(16)]

                MDLabel:
                    id: information_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    size_hint_x: None
                    height: dp(256)
                    width: dp(256)
                    spacing: dp(0)
                    padding: [dp(0), dp(0), dp(0), dp(0)]
                    pos_hint: {"center_x": .5, "center_y": .5}

                    MDIcon:
                        pos_hint: {"center_x": .5, "center_y": .5}
                        id: information_logo
                        font_size: "256dp"
                        width: dp(256)
                        height: dp(256)
"""

layout_map_settings_screen = """
MDScreen:
    name: "map_settings_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Map Configuration"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_map_action(self)],
                ]

        ScrollView:
            id: map_settings_scrollview

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Configure Map"
                    font_style: "H6"

                MDLabel:
                    id: map_config_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    markup: True
                    text: "\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(48)
                    
                    MDLabel:
                        text: "Use online map sources"
                        font_style: "H6"

                    MDSwitch:
                        id: map_use_online
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(48)
                    
                    MDLabel:
                        text: "Use offline map source"
                        font_style: "H6"

                    MDSwitch:
                        id: map_use_offline
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(48)
                    
                    MDLabel:
                        id: map_storage_external_label
                        text: "Use external storage path"
                        font_style: "H6"

                    MDSwitch:
                        id: map_storage_external
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    spacing: dp(24)
                    height: self.minimum_height
                    padding: [0, dp(24), 0, 0]

                    MDRectangleFlatIconButton:
                        id: map_select_button
                        icon: "list-box-outline"
                        text: "Select MBTiles Map"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.map_select_file_action(self)
                        disabled: False

                    MDRectangleFlatIconButton:
                        id: map_cache_button
                        icon: "map-clock-outline"
                        text: "Clear map cache"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.map_clear_cache(self)
                        disabled: False
"""

layout_map_screen = """
MDScreen:
    name: "map_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Map"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                #['format-list-bulleted-type', lambda x: root.app.map_object_list(self)], # Object List
                ['arrow-down-bold-hexagon-outline', lambda x: root.app.telemetry_request_action(self)], # Download telemetry
                ['upload-lock', lambda x: root.app.telemetry_send_update(self)], # Send telemetry update
                ['layers', lambda x: root.app.map_layers_action(self)],
                ['wrench-cog', lambda x: root.app.map_settings_action(self)],
                ['crosshairs-gps', lambda x: root.app.map_own_location_action(self)],
                ['close', lambda x: root.app.close_any_action(self)],
                ]

        MDBoxLayout:
            id: map_layout
"""

layout_keys_screen = """
MDScreen:
    name: "keys_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Encryption Keys"
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

layout_plugins_screen = """
MDScreen:
    name: "plugins_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Plugins & Services"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_plugins_action(self)],
                ]

        ScrollView:
            id:plugins_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "24dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(35), dp(35), dp(35), dp(35)]

                MDLabel:
                    padding: [0,dp(0),dp(0),dp(0)]
                    text: "Plugin Settings"
                    id: plugins_active_heading
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: plugins_info1
                    markup: True
                    text: ""
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(26),dp(0)]
                    height: dp(24)
                    
                    MDLabel:
                        text: "Enable Plugins"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_service_plugins_enabled
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(26),dp(0)]
                    height: dp(24)
                    
                    MDLabel:
                        text: "Enable Command Plugins"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_command_plugins_enabled
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDRectangleFlatIconButton:
                    id: plugins_display
                    icon: "folder-cog-outline"
                    text: "Select Plugins Directory"
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.app.plugins_select_directory_action(self)

                MDLabel:
                    id: plugins_info2
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    padding: [0,dp(14),dp(0),dp(0)]
                    text: "Active Plugins"
                    id: plugins_active_heading
                    font_style: "H6"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: plugins_loaded
                    markup: True
                    text: ""
                    size_hint_y: None
                    height: self.texture_size[1]
"""

layout_settings_screen = """
MDScreen:
    name: "settings_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: settings_top_bar
            title: "Preferences"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_settings_action(self)],
                ]

        MDScrollView:
            id: settings_scrollview
            size_hint_x: 1
            size_hint_y: None
            size: [root.width, root.height-root.ids.settings_top_bar.height]
            do_scroll_x: False
            do_scroll_y: True

            MDGridLayout:
                cols: 1
                padding: [dp(28), dp(28), dp(28), dp(28)]
                size_hint_y: None
                height: self.minimum_height

                MDLabel:
                    text: "User Options"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: settings_info1
                    markup: True
                    text: ""
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, dp(24), 0, dp(24)]

                    MDTextField:
                        id: settings_display_name
                        hint_text: "Display Name"
                        text: ""
                        max_text_length: 128
                        font_size: dp(24)

                    MDTextField:
                        id: settings_propagation_node_address
                        hint_text: "LXMF Propagation Node"
                        text: ""
                        max_text_length: 32
                        font_size: dp(24)
                        height: dp(64)

                    MDTextField:
                        id: settings_print_command
                        hint_text: "Print Command"
                        text: ""
                        font_size: dp(24)
                        height: dp(64)

                MDLabel:
                    text: "•"
                    font_style: "H6"
                    text_size: self.size
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: [0, dp(2), 0, dp(22)]

                MDLabel:
                    text: "Address & Identity"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: settings_info2
                    markup: True
                    text: "\\nYour address and identity hashes are derived from your primary identity keys, and are therefore not editable, but these fields can be used to view and copy the hashes. If you want a new LXMF address, create or import a new primary identity.\\n"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, dp(0), 0, dp(24)]

                    MDTextField:
                        id: settings_lxmf_address
                        hint_text: "Your LXMF Address"
                        text: ""
                        max_text_length: 32
                        font_size: dp(24)
                        height: dp(64)

                    MDTextField:
                        id: settings_identity_hash
                        hint_text: "Your Identity Hash"
                        text: ""
                        max_text_length: 32
                        font_size: dp(24)
                        height: dp(64)

                MDLabel:
                    text: "•"
                    font_style: "H6"
                    text_size: self.size
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: [0, dp(2), 0, dp(22)]

                MDLabel:
                    text: "Appearance"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: settings_info3
                    markup: True
                    text: "\\nThis section lets you configure the appearance of the application to suit your preferences, such as themes and what levels of information to display. When user icons are enabled, the contact list will display icons other users have configured in their [b]Telemetry[/b] settings.\\n"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Notifications"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_notifications_on
                        pos_hint: {"center_y": 0.3}
                        active: True

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Dark Mode"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_dark_ui
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "E-Ink Mode"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_eink_mode
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Show user icons in conversation list"
                        font_style: "H6"

                    MDSwitch:
                        id: display_style_in_contact_list
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Only show user icons from trusted"
                        font_style: "H6"

                    MDSwitch:
                        id: display_style_from_trusted_only
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Advanced Metrics"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_advanced_statistics
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDLabel:
                    text: "•"
                    font_style: "H6"
                    text_size: self.size
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: [0, dp(22), 0, dp(2)]

                MDLabel:
                    text: "\\nBehaviour"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: settings_info3
                    markup: True
                    text: "\\nThis section configures various automated actions and default behaviours. Sync intervals can be configured, and you can control what kind of peers can send you messages.\\n"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Announce Automatically"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_start_announce
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Try propagation on direct delivery failure"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lxmf_try_propagation_on_fail
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Send via Propagation Node by default"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lxmf_delivery_by_default
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Ignore unknown senders"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lxmf_ignore_unknown
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Limit incoming messages to 1MB"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lxm_limit_1mb
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Limit each sync to 3 messages"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lxmf_sync_limit
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        id: settings_lxmf_sync_periodic
                        text: "Sync with Propagation Node periodically"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lxmf_periodic_sync
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    id: lxmf_syncslider_container
                    orientation: "vertical"
                    size_hint_y: None
                    padding: [0,0,dp(0),0]
                    height: dp(68)

                    MDSlider
                        min: 1
                        max: 214
                        value: 150
                        id: settings_lxmf_sync_interval
                        sensitivity: "all"
                        hint: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        id: settings_lxmf_require_stamps_label
                        text: "Require stamps for incoming"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lxmf_require_stamps
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    id: lxmf_costslider_container
                    orientation: "vertical"
                    size_hint_y: None
                    padding: [0,0,dp(0),0]
                    height: dp(68)

                    MDSlider
                        min: 1
                        max: 32
                        value: 8
                        id: settings_lxmf_require_stamps_cost
                        sensitivity: "all"
                        hint: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Ignore messages with invalid stamps"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_ignore_invalid_stamps
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Use Home Node as Broadcast Repeater"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_home_node_as_broadcast_repeater
                        pos_hint: {"center_y": 0.3}
                        active: False
                        disabled: True

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(24)]
                    height: dp(48+24)
                    
                    MDLabel:
                        text: "Debug Logging"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_debug
                        pos_hint: {"center_y": 0.3}
                        disabled: False
                        active: False

                MDLabel:
                    text: "•"
                    font_style: "H6"
                    text_size: self.size
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: [0, dp(0), 0, dp(30)]

                MDLabel:
                    text: "Input Options & Localisation"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    id: settings_info_lang
                    markup: True
                    text: ""
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Latin, Greek, Cyrillic"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lang_default
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Chinese"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lang_chinese
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Japanese"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lang_japanese
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Korean"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lang_korean
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Devanagari"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lang_devangari
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Hebrew (incomplete)"
                        font_style: "H6"

                    MDSwitch:
                        id: settings_lang_hebrew
                        pos_hint: {"center_y": 0.3}
                        active: False

                # MDBoxLayout:
                #     orientation: "horizontal"
                #     size_hint_y: None
                #     padding: [0,0,dp(24),dp(0)]
                #     height: dp(48)
                    
                #     MDLabel:
                #         text: "Allow Predictive Text"
                #         font_style: "H6"

                #     MDSwitch:
                #         id: settings_allow_predictive_text
                #         pos_hint: {"center_y": 0.3}
                #         active: False

                # MDBoxLayout:
                #     orientation: "vertical"
                #     size_hint_y: None
                #     height: self.minimum_height
                #     padding: [0, dp(24), 0, dp(24)]

                #     MDRectangleFlatIconButton:
                #         id: hardware_rnode_button
                #         icon: "translate"
                #         text: "Input Languages"
                #         padding: [dp(0), dp(14), dp(0), dp(14)]
                #         icon_size: dp(24)
                #         font_size: dp(16)
                #         size_hint: [1.0, None]
                #         on_release: root.app.input_languages_action(self)

"""

layout_repository_screen = """
MDScreen:
    name: "repository_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Share Software & Guides"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_repository_action(self)],
                ]

        ScrollView:
            id: repository_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Repository Server\\n"
                    font_style: "H6"

                MDLabel:
                    id: repository_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]


                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(35), dp(0), dp(35)]

                    MDRectangleFlatIconButton:
                        id: repository_enable_button
                        icon: "wifi"
                        text: "Start Repository Server"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.repository_start_action(self)

                    MDRectangleFlatIconButton:
                        id: repository_disable_button
                        icon: "wifi-off"
                        text: "Stop Repository Server"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.repository_stop_action(self)
                        disabled: True

                    MDRectangleFlatIconButton:
                        id: repository_download_button
                        icon: "download-multiple"
                        text: "Update Contents"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.repository_download_action(self)
                        disabled: False

                    MDLabel:
                        id: repository_update
                        markup: True
                        text: ""
                        size_hint_y: None
                        text_size: self.width, None
                        height: self.texture_size[1]
"""

layout_hardware_screen = """
MDScreen:
    name: "hardware_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Hardware"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_hardware_action(self)],
                ]

        ScrollView:
            id: hardware_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Configure Hardware Parameters\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]


                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(35), dp(0), dp(35)]

                    MDRectangleFlatIconButton:
                        id: hardware_rnode_button
                        icon: "radio-handheld"
                        text: "RNode"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_rnode_action(self)

                    MDRectangleFlatIconButton:
                        id: hardware_modem_button
                        icon: "router-wireless"
                        text: "Radio Modem"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_modem_action(self)
                        disabled: False

                    MDRectangleFlatIconButton:
                        id: hardware_serial_button
                        icon: "cable-data"
                        text: "Serial Port"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_serial_action(self)
                        disabled: False
"""

layout_hardware_modem_screen = """
MDScreen:
    name: "hardware_modem_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Radio Modem"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_hardware_action(self)],
                ]

        ScrollView:
            id: hardware_modem_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Modem Hardware Parameters\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_modem_info
                    markup: True
                    text: "To communicate using a Radio Modem, you will need to specify the following parameters. Serial port parameters must be set to match those of the modem. CSMA parameters can be left at their default values in most cases.\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    text: "Port Options"
                    font_style: "H6"

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_modem_baudrate
                        hint_text: "Baud Rate"
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(24)]

                    MDTextField:
                        id: hardware_modem_databits
                        hint_text: "Data Bits"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_modem_parity
                        hint_text: "Parity"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_modem_stopbits
                        hint_text: "Stop Bits"
                        text: ""
                        font_size: dp(24)

                MDLabel:
                    text: "CSMA Parameters"
                    font_style: "H6"

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(0)]

                    MDTextField:
                        id: hardware_modem_preamble
                        hint_text: "Preamble (ms)"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_modem_tail
                        hint_text: "TX Tail (ms)"
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(24)]

                    MDTextField:
                        id: hardware_modem_persistence
                        hint_text: "Persistence (1-255)"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_modem_slottime
                        hint_text: "Slot Time (ms)"
                        text: ""
                        font_size: dp(24)

                MDLabel:
                    text: "Optional Settings"
                    font_style: "H6"

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_modem_beaconinterval
                        hint_text: "Beacon Interval (seconds)"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_modem_beacondata
                        hint_text: "Beacon Data"
                        text: ""
                        font_size: dp(24)
"""

layout_hardware_rnode_screen = """
MDScreen:
    name: "hardware_rnode_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "RNode"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_hardware_action(self)],
                ]

        ScrollView:
            id: hardware_rnode_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "RNode Hardware Parameters\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_rnode_info
                    markup: True
                    text: "To communicate using an RNode, you will need to specify the following parameters. For two or more RNodes to be able to communicate, all parameters must match, except for the [i]Coding Rate[/i] and [i]TX Power[/i] parameter, which can vary between devices.\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDRectangleFlatIconButton:
                        id: rnode_mote_export
                        icon: "upload"
                        text: "Export"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_rnode_export(self)

                    MDRectangleFlatIconButton:
                        id: rnode_mote_import
                        icon: "download"
                        text: "Import"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_rnode_import(self)

                MDLabel:
                    text: "Radio Options"
                    font_style: "H6"

                # MDTextField:
                #     id: hardware_rnode_modulation
                #     hint_text: "Modulation"
                #     text: "LoRa"
                #     disabled: True
                #     font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_rnode_frequency
                        hint_text: "Frequency (MHz)"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_rnode_bandwidth
                        hint_text: "Bandwidth (KHz)"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_rnode_txpower
                        hint_text: "TX Power (dBm)"
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(24)]

                    MDTextField:
                        id: hardware_rnode_spreadingfactor
                        hint_text: "Spreading Factor"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_rnode_codingrate
                        hint_text: "Coding Rate"
                        text: ""
                        font_size: dp(24)

                MDLabel:
                    text: "Optional Settings"
                    font_style: "H6"

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_rnode_beaconinterval
                        hint_text: "Beacon Interval (seconds)"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_rnode_beacondata
                        hint_text: "Beacon Data"
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_rnode_atl_short
                        hint_text: "Airime Limit % (15s)"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_rnode_atl_long
                        hint_text: "Airime Limit % (1h)"
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Control RNode Display"
                        font_style: "H6"

                    MDSwitch:
                        id: hardware_rnode_framebuffer
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Connect using Bluetooth"
                        font_style: "H6"

                    MDSwitch:
                        id: hardware_rnode_bluetooth
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDLabel:
                    id: hardware_rnode_info
                    markup: True
                    text: "If you enable connection via Bluetooth, Sideband will attempt to connect to any available and paired RNodes over Bluetooth.\\n\\nYou must first pair the RNode with your device for this to work. If your RNode does not have a physical pairing button, you can enable Bluetooth and put it into pairing mode by first connecting it via a USB cable, and using the buttons below. When plugging in the RNode over USB, you must grant Sideband permission to the USB device for this to work.\\n\\nYou can also change Bluetooth settings using the \\"rnodeconf\\" utility from a computer.\\n\\nBy default, Sideband will connect to the first available RNode that is paired. If you want to always use a specific RNode, you can enter its name in the Preferred RNode Device Name field below, for example \\"RNode A8EB\\".\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDRectangleFlatIconButton:
                        id: hardware_rnode_bt_on_button
                        icon: "bluetooth"
                        text: "Enable Bluetooth"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_rnode_bt_on_action(self)

                    MDRectangleFlatIconButton:
                        id: hardware_rnode_bt_off_button
                        icon: "bluetooth-off"
                        text: "Disable Bluetooth"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_rnode_bt_off_action(self)
                        disabled: False

                    MDRectangleFlatIconButton:
                        id: hardware_rnode_bt_pair_button
                        icon: "link-variant"
                        text: "Start Pairing Mode"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_rnode_bt_pair_action(self)
                        disabled: False

                    MDTextField:
                        id: hardware_rnode_bt_device
                        hint_text: "Preferred RNode Device Name"
                        text: ""
                        font_size: dp(24)
"""

layout_hardware_serial_screen = """
MDScreen:
    name: "hardware_serial_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Serial Port"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_hardware_action(self)],
                ]

        ScrollView:
            id: hardware_serial_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Serial Hardware Parameters\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_serial_info
                    markup: True
                    text: "To communicate using a serial port, you will need to specify the following parameters. If communicating directly to another Reticulum instance over serial, the parameters must match the other device.\\n\\nIf you are using a serial-connected device to pass on data to other Reticulum instances, it should be configured to pass data transparently to the desired endpoints.\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDLabel:
                    text: "Port Options"
                    font_style: "H6"

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_serial_baudrate
                        hint_text: "Baud Rate"
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(24)]

                    MDTextField:
                        id: hardware_serial_databits
                        hint_text: "Data Bits"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_serial_parity
                        hint_text: "Parity"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: hardware_serial_stopbits
                        hint_text: "Stop Bits"
                        text: ""
                        font_size: dp(24)
"""
