from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList, IconLeftWidget, IconRightWidget
from kivy.properties import StringProperty

ts_format = "%Y-%m-%d %H:%M:%S"
file_ts_format = "%Y_%m_%d_%H_%M_%S"

def mdc(color, hue=None):
    if hue == None:
        hue = "400"
    return get_color_from_hex(colors[color][hue])

color_received = "LightGreen"
color_delivered = "Blue"
color_paper = "Indigo"
color_propagated = "Indigo"
color_failed = "Red"
color_unknown = "Gray"
intensity_msgs_dark = "800"
intensity_msgs_light = "500"

class ContentNavigationDrawer(Screen):
    pass

class DrawerList(ThemableBehavior, MDList):
    pass

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

