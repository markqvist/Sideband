root_layout = """
#: import NoTransition kivy.uix.screenmanager.NoTransition
#: import SlideTransition kivy.uix.screenmanager.SlideTransition

MDNavigationLayout:
    md_bg_color: app.theme_cls.bg_darkest

    ScreenManager:
        id: screen_manager
        transition: SlideTransition()
        # transition: NoTransition()

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


        MDScreen:
            name: "conversations_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Conversations"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [
                        ['menu', lambda x: nav_drawer.set_state("open")],
                        ]
                    right_action_items:
                        [
                        ['access-point', lambda x: root.ids.screen_manager.app.announce_now_action(self)],
                        ['webhook', lambda x: root.ids.screen_manager.app.connectivity_status(self)],
                        ['qrcode', lambda x: root.ids.screen_manager.app.ingest_lxm_action(self)],
                        ['email-sync', lambda x: root.ids.screen_manager.app.lxmf_sync_action(self)],
                        ['account-plus', lambda x: root.ids.screen_manager.app.new_conversation_action(self)],
                        ]

                ScrollView:
                    id: conversations_scrollview


        MDScreen:
            name: "messages_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    id: messages_toolbar
                    anchor_title: "left"
                    title: "Messages"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['lan-connect', lambda x: root.ids.screen_manager.app.message_propagation_action(self)],
                        ['close', lambda x: root.ids.screen_manager.app.close_messages_action(self)],
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
                        on_release: root.ids.screen_manager.app.key_query_action(self)
                    

                BoxLayout:
                    id: message_input_part
                    padding: [dp(16), dp(0), dp(16), dp(16)]
                    spacing: dp(24)
                    size_hint_y: None
                    height: self.minimum_height

                    MDTextField:
                        id: message_text
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
                        on_release: root.ids.screen_manager.app.message_send_action(self)
                        

        MDScreen:
            name: "broadcasts_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Local Broadcasts"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_any_action(self)],
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
        

        MDScreen:
            name: "connectivity_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Connectivity"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_connectivity_action(self)],
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

        
        MDScreen:
            name: "guide_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Guide"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_guide_action(self)],
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
        

        MDScreen:
            name: "information_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "App & Version Information"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_information_action(self)],
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

        MDScreen:
            name: "map_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Local Area Map"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_any_action(self)],
                        ]

                ScrollView:
                    id:map_scrollview

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: [dp(35), dp(35), dp(35), dp(35)]


                        MDLabel:
                            id: map_info
                            markup: True
                            text: ""
                            size_hint_y: None
                            text_size: self.width, None
                            height: self.texture_size[1]
        

        MDScreen:
            name: "keys_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Encryption Keys"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_keys_action(self)],
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
                            on_release: root.ids.screen_manager.app.identity_display_action(self)

                        MDRectangleFlatIconButton:
                            id: keys_copy
                            icon: "file-key"
                            text: "Copy Key To Clipboard"
                            padding: [dp(0), dp(14), dp(0), dp(14)]
                            icon_size: dp(24)
                            font_size: dp(16)
                            size_hint: [1.0, None]
                            on_release: root.ids.screen_manager.app.identity_copy_action(self)

                        MDRectangleFlatIconButton:
                            id: keys_share
                            icon: "upload-lock"
                            text: "Send Key To Other App"
                            padding: [dp(0), dp(14), dp(0), dp(14)]
                            icon_size: dp(24)
                            font_size: dp(16)
                            size_hint: [1.0, None]
                            on_release: root.ids.screen_manager.app.identity_share_action(self)

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
                            on_release: root.ids.screen_manager.app.identity_restore_action(self)
        

        MDScreen:
            name: "announces_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Announce Stream"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_settings_action(self)],
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
        

        MDScreen:
            name: "settings_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Preferences"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_settings_action(self)],
                        ]

                ScrollView:
                    id: settings_scrollview

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: 0
                        size_hint_y: None
                        height: self.minimum_height
                        padding: [0, 0, 0, 0]

                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: "16dp"
                            size_hint_y: None
                            height: self.minimum_height
                            padding: [dp(28), dp(16), dp(28), dp(16)]
                            

                            MDLabel:
                                text: ""
                                font_style: "H6"

                            MDLabel:
                                text: "User Options"
                                font_style: "H6"

                            MDTextField:
                                id: settings_display_name
                                hint_text: "Display Name"
                                text: ""
                                max_text_length: 128
                                font_size: dp(24)

                            MDTextField:
                                id: settings_propagation_node_address
                                hint_text: "LXMF Propagation Node"
                                disabled: False
                                text: ""
                                max_text_length: 32
                                font_size: dp(24)

                            MDTextField:
                                id: settings_home_node_address
                                hint_text: "Nomad Network Home Node"
                                disabled: False
                                text: ""
                                max_text_length: 32
                                font_size: dp(24)

                            MDTextField:
                                id: settings_print_command
                                hint_text: "Print Command"
                                disabled: False
                                text: ""
                                max_text_length: 32
                                font_size: dp(24)

                            MDLabel:
                                text: ""
                                font_style: "H6"

                            MDLabel:
                                text: "Address & Identity"
                                font_style: "H6"

                            MDTextField:
                                id: settings_lxmf_address
                                hint_text: "Your LXMF Address"
                                text: ""
                                disabled: False
                                max_text_length: 32
                                font_size: dp(24)

                            MDTextField:
                                id: settings_identity_hash
                                hint_text: "Your Identity Hash"
                                text: ""
                                disabled: False
                                max_text_length: 32
                                font_size: dp(24)


                        MDBoxLayout:
                            orientation: "vertical"
                            # spacing: "24dp"
                            size_hint_y: None
                            height: self.minimum_height
                            padding: [dp(28), dp(16), dp(28), dp(16)]

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
                                    text: "Dark Mode UI"
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
                                    min: 300
                                    max: 172800
                                    value: 43200
                                    id: settings_lxmf_sync_interval
                                    sensitivity: "all"
                                    hint: False

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
                                padding: [0,0,dp(24),dp(0)]
                                height: dp(48)
                                
                                MDLabel:
                                    text: "Send Telemetry to Home Node"
                                    font_style: "H6"

                                MDSwitch:
                                    id: settings_telemetry_to_home_node
                                    pos_hint: {"center_y": 0.3}
                                    disabled: True
                                    active: False

                            MDBoxLayout:
                                orientation: "horizontal"
                                size_hint_y: None
                                padding: [0,0,dp(24),dp(0)]
                                height: dp(48)
                                
                                MDLabel:
                                    text: "Debug Logging"
                                    font_style: "H6"

                                MDSwitch:
                                    id: settings_debug
                                    pos_hint: {"center_y": 0.3}
                                    disabled: False
                                    active: False

        MDScreen:
            name: "hardware_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Hardware"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_hardware_action(self)],
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
                                on_release: root.ids.screen_manager.app.hardware_rnode_action(self)

                            MDRectangleFlatIconButton:
                                id: hardware_modem_button
                                icon: "router-wireless"
                                text: "Radio Modem"
                                padding: [dp(0), dp(14), dp(0), dp(14)]
                                icon_size: dp(24)
                                font_size: dp(16)
                                size_hint: [1.0, None]
                                on_release: root.ids.screen_manager.app.hardware_modem_action(self)
                                disabled: False

                            MDRectangleFlatIconButton:
                                id: hardware_serial_button
                                icon: "cable-data"
                                text: "Serial Port"
                                padding: [dp(0), dp(14), dp(0), dp(14)]
                                icon_size: dp(24)
                                font_size: dp(16)
                                size_hint: [1.0, None]
                                on_release: root.ids.screen_manager.app.hardware_serial_action(self)
                                disabled: False

        MDScreen:
            name: "hardware_rnode_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "RNode"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_sub_hardware_action(self)],
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
                                on_release: root.ids.screen_manager.app.hardware_rnode_export(self)

                            MDRectangleFlatIconButton:
                                id: rnode_mote_import
                                icon: "download"
                                text: "Import"
                                padding: [dp(0), dp(14), dp(0), dp(14)]
                                icon_size: dp(24)
                                font_size: dp(16)
                                size_hint: [1.0, None]
                                on_release: root.ids.screen_manager.app.hardware_rnode_import(self)

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
                                on_release: root.ids.screen_manager.app.hardware_rnode_bt_on_action(self)

                            MDRectangleFlatIconButton:
                                id: hardware_rnode_bt_off_button
                                icon: "bluetooth-off"
                                text: "Disable Bluetooth"
                                padding: [dp(0), dp(14), dp(0), dp(14)]
                                icon_size: dp(24)
                                font_size: dp(16)
                                size_hint: [1.0, None]
                                on_release: root.ids.screen_manager.app.hardware_rnode_bt_off_action(self)
                                disabled: False

                            MDRectangleFlatIconButton:
                                id: hardware_rnode_bt_pair_button
                                icon: "link-variant"
                                text: "Start Pairing Mode"
                                padding: [dp(0), dp(14), dp(0), dp(14)]
                                icon_size: dp(24)
                                font_size: dp(16)
                                size_hint: [1.0, None]
                                on_release: root.ids.screen_manager.app.hardware_rnode_bt_pair_action(self)
                                disabled: False

                            MDTextField:
                                id: hardware_rnode_bt_device
                                hint_text: "Preferred RNode Device Name"
                                text: ""
                                font_size: dp(24)

        MDScreen:
            name: "hardware_modem_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Radio Modem"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_sub_hardware_action(self)],
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

        MDScreen:
            name: "hardware_serial_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Serial Port"
                    anchor_title: "left"
                    elevation: 2
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]
                    right_action_items:
                        [
                        ['close', lambda x: root.ids.screen_manager.app.close_sub_hardware_action(self)],
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

                        # MDBoxLayout:
                        #     orientation: "horizontal"
                        #     spacing: "24dp"
                        #     size_hint_y: None
                        #     height: self.minimum_height
                        #     padding: [dp(0), dp(0), dp(0), dp(35)]

                        #     MDRectangleFlatIconButton:
                        #         id: serial_mote_export
                        #         icon: "upload"
                        #         text: "Export"
                        #         padding: [dp(0), dp(14), dp(0), dp(14)]
                        #         icon_size: dp(24)
                        #         font_size: dp(16)
                        #         size_hint: [1.0, None]
                        #         on_release: root.ids.screen_manager.app.hardware_serial_export(self)

                        #     MDRectangleFlatIconButton:
                        #         id: serial_mote_import
                        #         icon: "download"
                        #         text: "Import"
                        #         padding: [dp(0), dp(14), dp(0), dp(14)]
                        #         icon_size: dp(24)
                        #         font_size: dp(16)
                        #         size_hint: [1.0, None]
                        #         on_release: root.ids.screen_manager.app.hardware_serial_import(self)

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
                                icon: "email"
                                on_release: root.ids.screen_manager.app.conversations_action(self)
                                

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
                            text: "Local Area Map"
                            on_release: root.ids.screen_manager.app.map_action(self)
                        
                            IconLeftWidget:
                                icon: "map"
                                on_release: root.ids.screen_manager.app.map_action(self)

                                                       
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
                            text: "Guide"
                            on_release: root.ids.screen_manager.app.guide_action(self)
                        
                            IconLeftWidget:
                                icon: "book-open"
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

<ListLXMessageCard>:
    style: "outlined"
    elevation: 2
    padding: dp(8)
    radius: [dp(4), dp(4), dp(4), dp(4)]
    size_hint: 1.0, None
    height: content_text.height + heading_text.height + dp(32)
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

        MDLabel:
            id: content_text
            text: root.text
            # adaptive_size: True
            size_hint_y: None
            text_size: self.width, None
            # theme_text_color: 'Custom'
            # text_color: rgba(255,255,255,216)
            height: self.texture_size[1]

<MsgSync>
    orientation: "vertical"
    spacing: "24dp"
    size_hint_y: None
    padding: [0, 0, 0, dp(16)]
    height: self.minimum_height+dp(24)

    MDProgressBar:
        id: sync_progress
        value: 0

    MDLabel:
        id: sync_status
        hint_text: "Name"
        text: "Initiating sync..."

<ConvSettings>
    orientation: "vertical"
    spacing: "16dp"
    size_hint_y: None
    padding: [0, 0, 0, dp(8)]
    height: self.minimum_height

    MDTextField:
        id: dest_field
        hint_text: "Address"
        text: root.context_dest
        # disabled: True
        font_size: dp(18)

    MDTextField:
        id: name_field
        hint_text: "Name"
        text: root.disp_name
        font_size: dp(18)

    MDBoxLayout:
        orientation: "horizontal"
        # spacing: "24dp"
        size_hint_y: None
        padding: [0,0,dp(8),0]
        height: dp(48)
        MDLabel:
            id: trusted_switch_label
            text: "Trusted"
            font_style: "H6"

        MDSwitch:
            id: trusted_switch
            pos_hint: {"center_y": 0.43}
            active: root.trusted

<NewConv>
    orientation: "vertical"
    spacing: "24dp"
    size_hint_y: None
    height: dp(250)

    MDTextField:
        id: n_address_field
        max_text_length: 32
        hint_text: "Address"
        helper_text: "Error, check your input"
        helper_text_mode: "on_error"
        text: ""
        font_size: dp(24)

    MDTextField:
        id: n_name_field
        hint_text: "Name"
        text: ""
        font_size: dp(24)

    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        padding: [0,0,dp(8),dp(24)]
        height: dp(48)
        MDLabel:
            id: "trusted_switch_label"
            text: "Trusted"
            font_style: "H6"

        MDSwitch:
            id: n_trusted
            pos_hint: {"center_y": 0.3}
            active: False
"""