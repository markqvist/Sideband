import time
import RNS

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.list import MDList, IconLeftWidget, IconRightWidget, OneLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from ui.helpers import ts_format

class Announces():
    def __init__(self, app):
        self.app = app
        self.context_dests = []
        self.added_item_dests = []
        self.list = None
        self.update()

    def reload(self):
        self.clear_list()
        self.update()

    def clear_list(self):
        if self.list != None:
            self.list.clear_widgets()

        self.context_dests = []
        self.added_item_dests = []

    def update(self):
        self.clear_list()
        self.announces = self.app.sideband.list_announces()
        self.update_widget()

        self.app.flag_new_announces = False

    def update_widget(self):
        if self.list == None:
            self.list = MDList()
            
        for announce in self.announces:
            context_dest = announce["dest"]
            ts = announce["time"]
            a_data = announce["data"]

            if not context_dest in self.added_item_dests:
                if self.app.sideband.is_trusted(context_dest):
                    trust_icon = "account-check"
                else:
                    trust_icon = "account-question"

                def gen_info(ts, dest, name):
                    def x(sender):
                        yes_button = MDFlatButton(
                            text="OK",
                        )
                        
                        dialog = MDDialog(
                            text="Announce Received: "+ts+"\nAnnounced Name: "+name+"\nLXMF Address: "+RNS.prettyhexrep(dest),
                            buttons=[ yes_button ],
                        )
                        def dl_yes(s):
                            dialog.dismiss()

                        yes_button.bind(on_release=dl_yes)
                        item.dmenu.dismiss()
                        dialog.open()
                    return x

                time_string = time.strftime(ts_format, time.localtime(ts))
                disp_name = self.app.sideband.peer_display_name(context_dest)
                iconl = IconLeftWidget(icon=trust_icon)
                item = OneLineAvatarIconListItem(text=time_string+": "+disp_name, on_release=gen_info(time_string, context_dest, a_data))
                item.add_widget(iconl)
                item.sb_uid = context_dest

                def gen_del(dest, item):
                    def x():
                        yes_button = MDFlatButton(
                            text="Yes",
                        )
                        no_button = MDFlatButton(
                            text="No",
                        )
                        dialog = MDDialog(
                            text="Delete announce?",
                            buttons=[ yes_button, no_button ],
                        )
                        def dl_yes(s):
                            dialog.dismiss()
                            self.app.sideband.delete_announce(dest)
                            self.reload()
                        def dl_no(s):
                            dialog.dismiss()

                        yes_button.bind(on_release=dl_yes)
                        no_button.bind(on_release=dl_no)
                        item.dmenu.dismiss()
                        dialog.open()
                    return x

                def gen_conv(dest, item):
                    def x():
                        item.dmenu.dismiss()
                        self.app.conversation_from_announce_action(dest)
                    return x

                dm_items = [
                    {
                        "viewclass": "OneLineListItem",
                        "text": "Converse",
                        "height": dp(40),
                        "on_release": gen_conv(context_dest, item)
                    },
                    # {
                    #     "text": "Delete Announce",
                    #     "viewclass": "OneLineListItem",
                    #     "height": dp(64),
                    #     "on_release": gen_del(context_dest, item)
                    # }
                ]

                item.iconr = IconRightWidget(icon="dots-vertical");
                
                item.dmenu = MDDropdownMenu(
                    caller=item.iconr,
                    items=dm_items,
                    position="center",
                    width_mult=4,
                )

                def callback_factory(ref):
                    def x(sender):
                        ref.dmenu.open()
                    return x

                item.iconr.bind(on_release=callback_factory(item))

                item.add_widget(item.iconr)
                
                self.added_item_dests.append(context_dest)
                self.list.add_widget(item)

    def get_widget(self):
        return self.list