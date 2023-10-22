import time
import RNS

from kivy.metrics import dp,sp
from kivy.lang.builder import Builder

if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import ts_format
else:
    from .helpers import ts_format

class ObjectDetails():
    def __init__(self, app, object_hash = None):
        self.app = app
        self.widget = None
        self.object_hash = object_hash

        if not self.app.root.ids.screen_manager.has_screen("object_details_screen"):
            self.screen = Builder.load_string(layou_object_details)
            self.screen.app = self.app
            self.ids = self.screen.ids
            self.app.root.ids.screen_manager.add_widget(self.screen)

    def reload(self):
        self.clear_widget()
        self.update()

    def clear_widget(self):
        pass

    def update(self):
        us = time.time()
        self.update_widget()        
        RNS.log("Updated object details in "+RNS.prettytime(time.time()-us), RNS.LOG_DEBUG)

    def update_widget(self):
        if self.widget == None:
            self.widget = MDLabel(text=RNS.prettyhexrep(self.object_hash))

    def get_widget(self):
        return self.widget

layou_object_details = """
MDScreen:
    name: "object_details_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Details"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_map_action(self)],
                ]

        ScrollView:
            id: object_details_scrollview

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(48)
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    id: name_label
                    markup: True
                    text: "Object Name"
                    font_style: "H6"
                
                MDLabel:
                    id: test_label
                    markup: True
                    text: "Test"
                    font_style: "H6"
                
"""