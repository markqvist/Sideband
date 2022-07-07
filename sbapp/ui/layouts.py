root_layout = """
MDNavigationLayout:

    ScreenManager:
        id: screen_manager

        MDScreen:
            name: "conversations_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Conversations"
                    elevation: 10
                    pos_hint: {"top": 1}
                    left_action_items:
                        [
                        ['menu', lambda x: nav_drawer.set_state("open")],
                        ]
                    right_action_items:
                        [
                        ['webhook', lambda x: root.ids.screen_manager.app.connectivity_status(self)],
                        ['access-point', lambda x: root.ids.screen_manager.app.announce_now_action(self)],
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
                    title: "Messages"
                    elevation: 10
                    pos_hint: {"top": 1}
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
                    orientation: "vertical"
                    id: no_keys_part
                    padding: [dp(28), dp(16), dp(16), dp(16)]
                    spacing: dp(24)
                    size_hint_y: None
                    height: self.minimum_height + dp(64)

                    MDLabel:
                        id: nokeys_text
                        text: ""

                    MDRectangleFlatIconButton:
                        icon: "key-wireless"
                        text: "Query Network For Keys"
                        # padding: [dp(16), dp(16), dp(16), dp(16)]
                        on_release: root.ids.screen_manager.app.key_query_action(self)
                    

                BoxLayout:
                    id: message_input_part
                    # orientation: "vertical"
                    padding: [dp(28), dp(16), dp(16), dp(16)]
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
                        icon: "transfer-up"
                        text: "Send"
                        # padding: [dp(16), dp(16), dp(16), dp(16)]
                        on_release: root.ids.screen_manager.app.message_send_action(self)
                        

        MDScreen:
            name: "broadcasts_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Local Broadcasts"
                    elevation: 10
                    pos_hint: {"top": 1}
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]

                ScrollView:
                    id: broadcasts_scrollview

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(64)

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
                    elevation: 10
                    pos_hint: {"top": 1}
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
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(16)

                        MDLabel:
                            text: ""
                            font_style: "H6"

                        MDLabel:
                            text: "Configuring Connectivity"
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
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                id: connectivity_local_label
                                text: "Connect via local WiFi/Ethernet"
                                font_style: "H6"

                            MDSwitch:
                                id: connectivity_use_local
                                active: False

                        MDLabel:
                            text: ""
                            font_size: dp(16)

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
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                id: connectivity_tcp_label
                                text: "Connect via TCP"
                                font_style: "H6"

                            MDSwitch:
                                id: connectivity_use_tcp
                                active: False


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
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                id: connectivity_i2p_label
                                text: "Connect via I2P"
                                font_style: "H6"

                            MDSwitch:
                                id: connectivity_use_i2p
                                active: False


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
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                id: connectivity_rnode_label
                                text: "Connect via RNode"
                                font_style: "H6"
                                disabled: True

                            MDSwitch:
                                id: connectivity_use_rnode
                                active: False
                                disabled: True

                        MDLabel:
                            id: rnode_support_info
                            markup: True
                            text: "[i]RNode support is in development[/i]"
                            size_hint_y: None
                            text_size: self.width, None
                            height: self.texture_size[1]

                        MDTextField:
                            id: connectivity_rnode_cid
                            hint_text: "RNode Pairing ID"
                            text: ""
                            font_size: dp(24)
                            disabled: True

        

        MDScreen:
            name: "guide_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Guide"
                    elevation: 10
                    pos_hint: {"top": 1}
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]

                ScrollView:
                    id:guide_scrollview

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(64)

                        MDLabel:
                            id: guide_info
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
                    elevation: 10
                    pos_hint: {"top": 1}
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]

                ScrollView:
                    id:information_scrollview

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(64)

                        MDLabel:
                            id: information_info
                            markup: True
                            text: ""
                            size_hint_y: None
                            text_size: self.width, None
                            height: self.texture_size[1]
        

        MDScreen:
            name: "map_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Local Area Map"
                    elevation: 10
                    pos_hint: {"top": 1}
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]

                ScrollView:
                    id:information_scrollview

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(64)

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
                    elevation: 10
                    pos_hint: {"top": 1}
                    left_action_items:
                        [['menu', lambda x: nav_drawer.set_state("open")]]

                ScrollView:
                    id:keys_scrollview

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(64)

                        MDLabel:
                            id: keys_info
                            markup: True
                            text: ""
                            size_hint_y: None
                            text_size: self.width, None
                            height: self.texture_size[1]
        

        MDScreen:
            name: "announces_screen"
            
            BoxLayout:
                orientation: "vertical"

                MDTopAppBar:
                    title: "Announce Stream"
                    elevation: 10
                    pos_hint: {"top": 1}
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
                    title: "Settings"
                    elevation: 10
                    pos_hint: {"top": 1}
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
                        spacing: "24dp"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(16)

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
                            id: settings_lxmf_address
                            hint_text: "Your LXMF Address"
                            text: ""
                            disabled: False
                            max_text_length: 32
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

                        MDBoxLayout:
                            orientation: "horizontal"
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                text: "Announce At App Startup"
                                font_style: "H6"

                            MDSwitch:
                                id: settings_start_announce
                                active: False

                        MDBoxLayout:
                            orientation: "horizontal"
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                text: "Deliver via LXMF Propagation Node by default"
                                font_style: "H6"

                            MDSwitch:
                                id: settings_lxmf_delivery_by_default
                                disabled: False
                                active: False

                        MDBoxLayout:
                            orientation: "horizontal"
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                text: "Limit each sync to 3 messages"
                                font_style: "H6"

                            MDSwitch:
                                id: settings_lxmf_sync_limit
                                disabled: False
                                active: False

                        MDBoxLayout:
                            orientation: "horizontal"
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                text: "Use Home Node as Broadcast Repeater"
                                font_style: "H6"

                            MDSwitch:
                                id: settings_home_node_as_broadcast_repeater
                                active: False
                                disabled: True

                        MDBoxLayout:
                            orientation: "horizontal"
                            # spacing: "24dp"
                            size_hint_y: None
                            height: dp(48)
                            
                            MDLabel:
                                text: "Send Telemetry to Home Node"
                                font_style: "H6"

                            MDSwitch:
                                id: settings_telemetry_to_home_node
                                disabled: True
                                active: False
        

    MDNavigationDrawer:
        id: nav_drawer

        ContentNavigationDrawer:
            ScrollView:
                DrawerList:
                    id: md_list
                    
                    MDList:
                        OneLineIconListItem:
                            text: "Conversations"
                            on_release: root.ids.screen_manager.app.conversations_action(self)
                        
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
                            text: "Connectivity"
                            on_release: root.ids.screen_manager.app.connectivity_action(self)
                            _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "wifi"
                                on_release: root.ids.screen_manager.app.connectivity_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Settings"
                            on_release: root.ids.screen_manager.app.settings_action(self)
                            _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "cog"
                                on_release: root.ids.screen_manager.app.settings_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Encryption Keys"
                            on_release: root.ids.screen_manager.app.keys_action(self)
                            _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "key-chain"
                                on_release: root.ids.screen_manager.app.keys_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Guide"
                            on_release: root.ids.screen_manager.app.guide_action(self)
                            _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "book-open"
                                on_release: root.ids.screen_manager.app.guide_action(self)

                                                       
                        OneLineIconListItem:
                            id: app_version_info
                            text: ""
                            on_release: root.ids.screen_manager.app.information_action(self)
                            _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "information"
                                on_release: root.ids.screen_manager.app.information_action(self)

                                                       
                        OneLineIconListItem:
                            text: "Shutdown"
                            on_release: root.ids.screen_manager.app.quit_action(self)
                            _no_ripple_effect: True
                        
                            IconLeftWidget:
                                icon: "power"
                                on_release: root.ids.screen_manager.app.quit_action(self)

<ListLXMessageCard>:
    padding: dp(8)
    size_hint: 1.0, None
    height: content_text.height + heading_text.height + dp(32)
    pos_hint: {"center_x": .5, "center_y": .5}

    MDRelativeLayout:
        size_hint: 1.0, None
        # size: root.size

        MDIconButton:
            id: msg_submenu
            icon: "dots-vertical"
            pos:
                root.width - (self.width + root.padding[0] + dp(4)), root.height - (self.height + root.padding[0] + dp(4))

        MDLabel:
            id: heading_text
            markup: True
            text: root.heading
            adaptive_size: True
            pos: 0, root.height - (self.height + root.padding[0] + dp(8))

        MDLabel:
            id: content_text
            text: root.text
            # adaptive_size: True
            size_hint_y: None
            text_size: self.width, None
            height: self.texture_size[1]

<MsgSync>
    orientation: "vertical"
    spacing: "24dp"
    size_hint_y: None
    height: self.minimum_height+dp(24)

    MDLabel:
        id: sync_status
        hint_text: "Name"
        text: "Initiating sync..."

    MDProgressBar:
        id: sync_progress
        value: 0

<ConvSettings>
    orientation: "vertical"
    spacing: "24dp"
    size_hint_y: None
    height: dp(148)

    MDTextField:
        id: name_field
        hint_text: "Name"
        text: root.disp_name
        font_size: dp(24)

    MDBoxLayout:
        orientation: "horizontal"
        # spacing: "24dp"
        size_hint_y: None
        height: dp(48)
        MDLabel:
            id: trusted_switch_label
            text: "Trusted"
            font_style: "H6"

        MDSwitch:
            id: trusted_switch
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
        height: dp(48)
        MDLabel:
            id: "trusted_switch_label"
            text: "Trusted"
            font_style: "H6"

        MDSwitch:
            id: n_trusted
            active: False
"""