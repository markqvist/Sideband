import time
import RNS

from kivy.metrics import dp,sp
from kivy.uix.label import MDLabel
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

Builder.load_string("""

""")