from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList, IconLeftWidget, IconRightWidget
from kivy.properties import StringProperty

ts_format = "%Y-%m-%d %H:%M:%S"

def mdc(color, hue=None):
    if hue == None:
        hue = "400"
    return get_color_from_hex(colors[color][hue])

color_received = "Green"
color_delivered = "Indigo"
color_propagated = "Blue"
color_failed = "Red"
color_unknown = "Gray"
intensity_msgs = "600"

class ContentNavigationDrawer(Screen):
    pass

class DrawerList(ThemableBehavior, MDList):
    pass

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

