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
from kivymd.icon_definitions import md_icons
from kivy.properties import StringProperty, BooleanProperty
from kivy.effects.scroll import ScrollEffect
from kivy.clock import Clock
from sideband.sense import Telemeter
import threading


from datetime import datetime


if RNS.vendor.platformutils.get_platform() == "android":
    from ui.helpers import ts_format
else:
    from .helpers import ts_format

class Telemetry():
    def __init__(self, app):
        self.app = app
        self.screen = None
        self.sensors_screen = None
        self.icons_screen = None
        self.color_picker = None
    
        if not self.app.root.ids.screen_manager.has_screen("telemetry_screen"):
            self.screen = Builder.load_string(layout_telemetry_screen)
            self.screen.app = self.app
            self.screen.delegate = self
            self.app.root.ids.screen_manager.add_widget(self.screen)

        self.screen.ids.telemetry_collector.bind(focus=self.telemetry_save)
        if self.app.sideband.config["telemetry_collector"] == None:
            self.screen.ids.telemetry_collector.text = ""
        else:
            self.screen.ids.telemetry_collector.text = RNS.hexrep(self.app.sideband.config["telemetry_collector"], delimit=False)

        self.screen.ids.telemetry_icon_preview.icon_color  = self.app.sideband.config["telemetry_fg"]
        self.screen.ids.telemetry_icon_preview.md_bg_color = self.app.sideband.config["telemetry_bg"]
        self.screen.ids.telemetry_icon_preview.icon = self.app.sideband.config["telemetry_icon"]

        self.screen.ids.telemetry_enabled.active = self.app.sideband.config["telemetry_enabled"]
        self.screen.ids.telemetry_enabled.bind(active=self.telemetry_enabled_toggle)

        self.screen.ids.telemetry_send_to_trusted.active = self.app.sideband.config["telemetry_send_to_trusted"]
        self.screen.ids.telemetry_send_to_trusted.bind(active=self.telemetry_save)

        self.screen.ids.telemetry_display_trusted_only.active = self.app.sideband.config["telemetry_display_trusted_only"]
        self.screen.ids.telemetry_display_trusted_only.bind(active=self.telemetry_save)

        self.screen.ids.telemetry_receive_trusted_only.active = self.app.sideband.config["telemetry_receive_trusted_only"]
        self.screen.ids.telemetry_receive_trusted_only.bind(active=self.telemetry_save)

        self.screen.ids.telemetry_send_appearance.active = self.app.sideband.config["telemetry_send_appearance"]
        self.screen.ids.telemetry_send_appearance.bind(active=self.telemetry_save)

        self.screen.ids.telemetry_send_all_to_collector.active = self.app.sideband.config["telemetry_send_all_to_collector"]
        self.screen.ids.telemetry_send_all_to_collector.bind(active=self.telemetry_save)

        self.screen.ids.telemetry_scrollview.effect_cls = ScrollEffect
        info  = "\nSideband allows you to securely share telemetry, such as location and sensor data, with people, custom programs, machines or other system over LXMF. You have complete control over what kind of telemetry to send, and who you share it with.\n\nTelemetry data is never sent to, via or processed by any external services or servers, but is carried exclusively within encrypted LXMF messages over Reticulum, and only to the destinations you define.\n\nWhen telemetry is enabled, it is possible to embed telemetry data in normal messages on a per-peer basis. You can control this from the [b]Conversations[/b] list, by selecting the [b]Edit[/b] option for the relevant peer.\n\nYou can also define a [b]Telemetry Collector[/b], that Sideband can automatically send telemetry to on a periodic basis. By default, only your own telemetry will be sent to the collector, but by enabling the [b]Send all known to collector[/b] option, you can forward all known telemetry to the collector. This can also be used to aggregate telemetry from multiple different collectors, or create chains of transmission.\n"
        if self.app.theme_cls.theme_style == "Dark":
            info = "[color=#"+self.app.dark_theme_text_color+"]"+info+"[/color]"
        
        self.screen.ids.telemetry_info.text = info

        def send_interval_change(sender=None, event=None, save=True):
            slider_val = int(self.screen.ids.telemetry_send_interval.value)
            mseg = 72; hseg = 84
            if slider_val <= mseg:
                interval = slider_val*5*60
            elif slider_val > mseg and slider_val <= mseg+hseg:
                h = (slider_val-mseg)/2; mm = mseg*5*60
                interval = h*60*60+mm
            else:
                d = slider_val-hseg-mseg
                hm = (hseg/2)*60*60; mm = mseg*5*60
                interval = d*86400+hm+mm

            interval_text = RNS.prettytime(interval)
            if self.screen.ids.telemetry_send_to_collector.active:
                self.screen.ids.telemetry_send_to_collector_label.text = "Auto send to collector every "+interval_text
            else:
                self.screen.ids.telemetry_send_to_collector_label.text = "Auto send to collector"

            if save:
                self.app.sideband.config["telemetry_send_interval"] = interval
                self.app.sideband.save_configuration()

        def save_send_to_collector(sender=None, event=None, save=True):
            if self.screen.ids.telemetry_send_to_collector.active:
                self.widget_hide(self.screen.ids.send_syncslider_container, False)
            else:
                self.widget_hide(self.screen.ids.send_syncslider_container, True)

            if save:
                self.app.sideband.config["telemetry_send_to_collector"] = self.screen.ids.telemetry_send_to_collector.active
                self.app.sideband.save_configuration()

            send_interval_change(save=False)

        self.screen.ids.telemetry_send_to_collector.active = self.app.sideband.config["telemetry_send_to_collector"]
        self.screen.ids.telemetry_send_to_collector.bind(active=save_send_to_collector)
        save_send_to_collector(save=False)

        def send_interval_change_cb(sender=None, event=None):
            send_interval_change(sender=sender, event=event, save=False)
        self.screen.ids.telemetry_send_interval.bind(value=send_interval_change_cb)
        self.screen.ids.telemetry_send_interval.bind(on_touch_up=send_interval_change)
        self.screen.ids.telemetry_send_interval.value = self.interval_to_slider_val(self.app.sideband.config["telemetry_send_interval"])
        send_interval_change(save=False)

        def request_interval_change(sender=None, event=None, save=True):
            slider_val = int(self.screen.ids.telemetry_request_interval.value)
            mseg = 72; hseg = 84
            if slider_val <= mseg:
                interval = slider_val*5*60
            elif slider_val > mseg and slider_val <= mseg+hseg:
                h = (slider_val-mseg)/2; mm = mseg*5*60
                interval = h*60*60+mm
            else:
                d = slider_val-hseg-mseg
                hm = (hseg/2)*60*60; mm = mseg*5*60
                interval = d*86400+hm+mm

            interval_text = RNS.prettytime(interval)
            if self.screen.ids.telemetry_request_from_collector.active:
                self.screen.ids.telemetry_request_from_collector_label.text = "Auto request from collector every "+interval_text
            else:
                self.screen.ids.telemetry_request_from_collector_label.text = "Auto request from collector"

            if save:
                self.app.sideband.config["telemetry_request_interval"] = interval
                self.app.sideband.save_configuration()

        def save_request_from_collector(sender=None, event=None, save=True):
            if self.screen.ids.telemetry_request_from_collector.active:
                self.widget_hide(self.screen.ids.request_syncslider_container, False)
            else:
                self.widget_hide(self.screen.ids.request_syncslider_container, True)

            if save:
                self.app.sideband.config["telemetry_request_from_collector"] = self.screen.ids.telemetry_request_from_collector.active
                self.app.sideband.save_configuration()

            request_interval_change(save=False)

        self.screen.ids.telemetry_request_from_collector.active = self.app.sideband.config["telemetry_request_from_collector"]
        self.screen.ids.telemetry_request_from_collector.bind(active=save_request_from_collector)
        save_request_from_collector(save=False)

        def request_interval_change_cb(sender=None, event=None):
            request_interval_change(sender=sender, event=event, save=False)
        self.screen.ids.telemetry_request_interval.bind(value=request_interval_change_cb)
        self.screen.ids.telemetry_request_interval.bind(on_touch_up=request_interval_change)
        self.screen.ids.telemetry_request_interval.value = self.interval_to_slider_val(self.app.sideband.config["telemetry_request_interval"])
        request_interval_change(save=False)


    def interval_to_slider_val(self, interval):
        try:
            mseg = 72; hseg = 84; sv = 0
            mm = mseg*5*60; hm = hseg*60*30+mm

            if interval <= mm:
                sv = interval/60/5
            elif interval > mm and interval <= hm:
                half_hours = interval/(60*30)-(mm/(60*30))
                sv = mseg+half_hours
            else:
                days = (interval/86400)-((hseg*60*30)/84600)-(mm/86400)
                sv = 1+mseg+hseg+days
        except Exception as e:
            return 43200

        return sv

    def widget_hide(self, w, hide=True):
        if hasattr(w, "saved_attrs"):
            if not hide:
                w.height, w.size_hint_y, w.opacity, w.disabled = w.saved_attrs
                del w.saved_attrs
        elif hide:
            w.saved_attrs = w.height, w.size_hint_y, w.opacity, w.disabled
            w.height, w.size_hint_y, w.opacity, w.disabled = 0, None, 0, True

    def telemetry_enabled_toggle(self, sender=None, event=None):
        self.telemetry_save()
        if self.screen.ids.telemetry_enabled.active:
            self.app.sideband.run_telemetry()
        else:
            self.app.sideband.stop_telemetry()
    
    def telemetry_save(self, sender=None, event=None):
        run_telemetry_update = False
        if len(self.screen.ids.telemetry_collector.text) != 32:
            self.screen.ids.telemetry_collector.text = ""
            self.app.sideband.config["telemetry_collector"] = None
        else:
            try:
                self.app.sideband.config["telemetry_collector"] = bytes.fromhex(self.screen.ids.telemetry_collector.text)
            except:
                self.screen.ids.telemetry_collector.text = ""
                self.app.sideband.config["telemetry_collector"] = None

        self.app.sideband.config["telemetry_enabled"] = self.screen.ids.telemetry_enabled.active
        self.app.sideband.config["telemetry_send_to_collector"] = self.screen.ids.telemetry_send_to_collector.active
        self.app.sideband.config["telemetry_send_to_trusted"] = self.screen.ids.telemetry_send_to_trusted.active
        self.app.sideband.config["telemetry_display_trusted_only"] = self.screen.ids.telemetry_display_trusted_only.active
        self.app.sideband.config["telemetry_send_appearance"] = self.screen.ids.telemetry_send_appearance.active
        self.app.sideband.config["telemetry_receive_trusted_only"] = self.screen.ids.telemetry_receive_trusted_only.active
        self.app.sideband.config["telemetry_send_all_to_collector"] = self.screen.ids.telemetry_send_all_to_collector.active
        
        self.app.sideband.save_configuration()
        if run_telemetry_update:
            self.app.sideband.update_telemetry()
        else:
            self.app.sideband.setstate("app.flags.last_telemetry", time.time())

    def telemetry_copy(self, sender=None):
        Clipboard.copy(str(self.app.sideband.get_telemetry()))
        self.app.sideband.update_telemetry()

    def telemetry_fg_color(self, sender=None):
        if self.color_picker == None:
            self.color_picker = MDColorPicker(size_hint=(0.85, 0.85))
        
        self.color_picker.open()
        self.color_picker.bind(on_release=self.telemetry_fg_select)
        def job(sender=None):
            self.color_picker._rgb = self.app.sideband.config["telemetry_fg"][0:3]
            self.color_picker.ids.view_headline.on_tab_press()
        Clock.schedule_once(job, 0)
    
    def telemetry_fg_select(self, instance_color_picker: MDColorPicker, type_color: str, selected_color: Union[list, str]):
        s = selected_color; color = [s[0], s[1], s[2], 1]
        self.screen.ids.telemetry_icon_preview.icon_color = color
        self.app.sideband.config["telemetry_fg"] = color
        self.app.sideband.save_configuration()
        self.own_appearance_changed = True
        if hasattr(self, "color_picker") and self.color_picker != None:
            self.color_picker.dismiss()
            self.color_picker = None

    def telemetry_bg_color(self, sender=None):
        if self.color_picker == None:
            self.color_picker = MDColorPicker(size_hint=(0.85, 0.85))

        self.color_picker.open()
        self.color_picker.bind(on_release=self.telemetry_bg_select)
        def job(sender=None):
            self.color_picker._rgb = self.app.sideband.config["telemetry_bg"][0:3]
            self.color_picker.ids.view_headline.on_tab_press()
        Clock.schedule_once(job, 0)
    
    def telemetry_bg_select(self, instance_color_picker: MDColorPicker, type_color: str, selected_color: Union[list, str]):
        s = selected_color; color = [s[0], s[1], s[2], 1]
        self.screen.ids.telemetry_icon_preview.md_bg_color = color
        self.app.sideband.config["telemetry_bg"] = color
        self.app.sideband.save_configuration()
        self.own_appearance_changed = True
        if hasattr(self, "color_picker") and self.color_picker != None:
            self.color_picker.dismiss()
            self.color_picker = None


    ### Sensors Screen
    ######################################

    def sensors_init(self):
        if not self.app.root.ids.screen_manager.has_screen("sensors_screen"):
            self.sensors_screen = Builder.load_string(layout_sensors_screen)
            self.sensors_screen.app = self.app
            self.sensors_screen.delegate = self
            self.app.root.ids.screen_manager.add_widget(self.sensors_screen)

        info3 = "\nTo include a specific type of telemetry data while sending, it must be enabled below. Please note that some sensor types are not supported on all devices. Sideband will only be able to read a specific type of sensor if your device actually includes hardware for it.\n"
        if self.app.theme_cls.theme_style == "Dark":
            info3 = "[color=#"+self.app.dark_theme_text_color+"]"+info3+"[/color]"            
        self.sensors_screen.ids.telemetry_info3.text = info3
        self.sensors_screen.ids.sensors_scrollview.effect_cls = ScrollEffect

        try:
            lat = self.app.sideband.config["telemetry_s_fixed_latlon"][0]; lon = self.app.sideband.config["telemetry_s_fixed_latlon"][1]
        except:
            lat = 0.0; lon = 0.0

        self.sensors_screen.ids.telemetry_s_location.active = self.app.sideband.config["telemetry_s_location"]
        self.sensors_screen.ids.telemetry_s_location.bind(active=self.telemetry_location_toggle)
        self.sensors_screen.ids.telemetry_s_fixed_location.active = self.app.sideband.config["telemetry_s_fixed_location"]
        self.sensors_screen.ids.telemetry_s_fixed_location.bind(active=self.telemetry_location_toggle)
        self.sensors_screen.ids.telemetry_s_fixed_latlon.bind(focus=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_fixed_altitude.bind(focus=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_fixed_altitude.text = str(self.app.sideband.config["telemetry_s_fixed_altitude"])
        self.sensors_screen.ids.telemetry_s_fixed_latlon.text = f"{lat}, {lon}"
        self.sensors_screen.ids.telemetry_s_battery.active = self.app.sideband.config["telemetry_s_battery"]
        self.sensors_screen.ids.telemetry_s_battery.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_barometer.active = self.app.sideband.config["telemetry_s_pressure"]
        self.sensors_screen.ids.telemetry_s_barometer.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_temperature.active = self.app.sideband.config["telemetry_s_temperature"]
        self.sensors_screen.ids.telemetry_s_temperature.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_humidity.active = self.app.sideband.config["telemetry_s_humidity"]
        self.sensors_screen.ids.telemetry_s_humidity.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_compass.active = self.app.sideband.config["telemetry_s_magnetic_field"]
        self.sensors_screen.ids.telemetry_s_compass.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_light.active = self.app.sideband.config["telemetry_s_ambient_light"]
        self.sensors_screen.ids.telemetry_s_light.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_gravity.active = self.app.sideband.config["telemetry_s_gravity"]
        self.sensors_screen.ids.telemetry_s_gravity.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_gyroscope.active = self.app.sideband.config["telemetry_s_angular_velocity"]
        self.sensors_screen.ids.telemetry_s_gyroscope.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_accelerometer.active = self.app.sideband.config["telemetry_s_acceleration"]
        self.sensors_screen.ids.telemetry_s_accelerometer.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_proximity.active = self.app.sideband.config["telemetry_s_proximity"]
        self.sensors_screen.ids.telemetry_s_proximity.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_information.active = self.app.sideband.config["telemetry_s_information"]
        self.sensors_screen.ids.telemetry_s_information.bind(active=self.sensors_save)
        self.sensors_screen.ids.telemetry_s_information_text.text = str(self.app.sideband.config["telemetry_s_information_text"])
        self.sensors_screen.ids.telemetry_s_information_text.bind(focus=self.sensors_save)

    def sensors_action(self, sender=None):
        self.sensors_init()
        self.app.root.ids.screen_manager.transition.direction = "left"
        self.app.root.ids.screen_manager.current = "sensors_screen"
        self.app.root.ids.nav_drawer.set_state("closed")
        self.app.sideband.setstate("app.displaying", self.app.root.ids.screen_manager.current)

    def telemetry_location_toggle(self, sender=None, event=None):
        if sender == self.sensors_screen.ids.telemetry_s_location:
            if self.sensors_screen.ids.telemetry_s_location.active:
                self.sensors_screen.ids.telemetry_s_fixed_location.active = False
        if sender == self.sensors_screen.ids.telemetry_s_fixed_location:
            if self.sensors_screen.ids.telemetry_s_fixed_location.active:
                self.sensors_screen.ids.telemetry_s_location.active = False


        if self.sensors_screen.ids.telemetry_s_location.active:
            if RNS.vendor.platformutils.is_android():
                if not check_permission("android.permission.ACCESS_COARSE_LOCATION") or not check_permission("android.permission.ACCESS_FINE_LOCATION"):
                    RNS.log("Requesting location permission", RNS.LOG_DEBUG)
                    request_permissions(["android.permission.ACCESS_COARSE_LOCATION", "android.permission.ACCESS_FINE_LOCATION"])

        self.sensors_save()

    def sensors_save(self, sender=None, event=None):
        run_telemetry_update = False

        self.app.sideband.config["telemetry_s_location"] = self.sensors_screen.ids.telemetry_s_location.active
        self.app.sideband.config["telemetry_s_fixed_location"] = self.sensors_screen.ids.telemetry_s_fixed_location.active
        self.app.sideband.config["telemetry_s_battery"] = self.sensors_screen.ids.telemetry_s_battery.active
        self.app.sideband.config["telemetry_s_pressure"] = self.sensors_screen.ids.telemetry_s_barometer.active
        self.app.sideband.config["telemetry_s_temperature"] = self.sensors_screen.ids.telemetry_s_temperature.active
        self.app.sideband.config["telemetry_s_humidity"] = self.sensors_screen.ids.telemetry_s_humidity.active
        self.app.sideband.config["telemetry_s_magnetic_field"] = self.sensors_screen.ids.telemetry_s_compass.active
        self.app.sideband.config["telemetry_s_ambient_light"] = self.sensors_screen.ids.telemetry_s_light.active
        self.app.sideband.config["telemetry_s_gravity"] = self.sensors_screen.ids.telemetry_s_gravity.active
        self.app.sideband.config["telemetry_s_angular_velocity"] = self.sensors_screen.ids.telemetry_s_gyroscope.active
        self.app.sideband.config["telemetry_s_acceleration"] = self.sensors_screen.ids.telemetry_s_accelerometer.active
        self.app.sideband.config["telemetry_s_proximity"] = self.sensors_screen.ids.telemetry_s_proximity.active

        if self.app.sideband.config["telemetry_s_information"] != self.sensors_screen.ids.telemetry_s_information.active:
            self.app.sideband.config["telemetry_s_information"] = self.sensors_screen.ids.telemetry_s_information.active
            run_telemetry_update = True

        if self.app.sideband.config["telemetry_s_information_text"] != self.sensors_screen.ids.telemetry_s_information_text.text:
            self.app.sideband.config["telemetry_s_information_text"] = self.sensors_screen.ids.telemetry_s_information_text.text
            run_telemetry_update = True

        try:
            alt = float(self.sensors_screen.ids.telemetry_s_fixed_altitude.text.strip().replace(" ", ""))
            self.sensors_screen.ids.telemetry_s_fixed_altitude.text = str(alt)
            if self.app.sideband.config["telemetry_s_fixed_altitude"] != alt:
                self.app.sideband.config["telemetry_s_fixed_altitude"] = alt
                run_telemetry_update = True
        except:
            self.sensors_screen.ids.telemetry_s_fixed_altitude.text = str(self.app.sideband.config["telemetry_s_fixed_altitude"])

        try:
            s = self.sensors_screen.ids.telemetry_s_fixed_latlon.text
            l = s.strip().replace(" ","").split(",")
            lat = float(l[0]); lon = float(l[1])
            if self.app.sideband.config["telemetry_s_fixed_latlon"] != [lat, lon]:
                run_telemetry_update = True
            self.app.sideband.config["telemetry_s_fixed_latlon"] = [lat, lon]
            self.sensors_screen.ids.telemetry_s_fixed_latlon.text = f"{lat}, {lon}"
        except:
            try:
                lat = self.app.sideband.config["telemetry_s_fixed_latlon"][0]
                lon = self.app.sideband.config["telemetry_s_fixed_latlon"][1]
                self.sensors_screen.ids.telemetry_s_fixed_latlon.text = f"{lat}, {lon}"
            except:
                self.app.sideband.config["telemetry_s_fixed_latlon"] = [0.0, 0.0]
                self.sensors_screen.ids.telemetry_s_fixed_latlon.text = "0.0, 0.0"

        self.app.sideband.save_configuration()
        if run_telemetry_update:
            self.app.sideband.update_telemetry()
        else:
            self.app.sideband.setstate("app.flags.last_telemetry", time.time())


    ### Icons Screen
    ######################################

    def icons_action(self, sender=None):
        if not self.app.root.ids.screen_manager.has_screen("icons_screen"):
            self.icons_screen = Builder.load_string(layout_icons_screen)
            self.icons_screen.app = self.app
            self.icons_screen.delegate = self
            self.app.root.ids.screen_manager.add_widget(self.icons_screen)
            self.icons_filter()

        self.app.root.ids.screen_manager.transition.direction = "left"
        self.app.root.ids.screen_manager.current = "icons_screen"
        self.app.sideband.setstate("app.displaying", self.app.root.ids.screen_manager.current)
        
        # sf = self.icons_screen.ids.icons_search_field.text
        # self.icons_filter(sf, len(sf)>0)

    def telemetry_set_icon(self, text="", search=False):
        if text in md_icons.keys():
            self.screen.ids.telemetry_icon_preview.icon = text
        else:
            self.screen.ids.telemetry_icon_preview.icon = "alpha-p-circle-outline"

        self.app.sideband.config["telemetry_icon"] = self.screen.ids.telemetry_icon_preview.icon
        self.app.sideband.save_configuration()
        self.own_appearance_changed = True

    def icons_selected(self, selected=None):
        RNS.log("Selected: "+str(selected))
        if selected == None:
            selected = "alpha-p-circle-outline"
        self.telemetry_set_icon(selected)
        self.app.close_sub_telemetry_action()

    def icons_filter(self, text="", search=False):
        def add_icon_item(name_icon):
            def select_factory(x):
                def f():
                    self.icons_selected(x)
                return f

            self.icons_screen.ids.icons_rv.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "icon": name_icon,
                    "text": name_icon,
                    "callback": lambda x: x,
                    "on_release": select_factory(name_icon)
                }
            )

        self.icons_screen.ids.icons_rv.data = []
        for name_icon in md_icons.keys():
            if search:
                if text in name_icon:
                    add_icon_item(name_icon)
            else:
                add_icon_item(name_icon)


layout_telemetry_screen = """
MDScreen:
    name: "telemetry_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Telemetry"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_any_action(self)],
                ]

        ScrollView:
            id: telemetry_scrollview

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Telemetry Over LXMF"
                    font_style: "H6"

                MDLabel:
                    id: telemetry_info
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, dp(0), 0, dp(0)]

                    MDTextField:
                        id: telemetry_collector
                        max_text_length: 32
                        hint_text: "Telemetry Collector LXMF Address"
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    padding: [0,0,dp(24),0]
                    size_hint_y: None
                    height: dp(48)
                    
                    MDLabel:
                        id: telemetry_enabled_label
                        text: "Enable telemetry"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_enabled
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Only display from trusted"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_display_trusted_only
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Only receive from trusted"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_receive_trusted_only
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Send to all trusted peers"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_send_to_trusted
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Send display style to everyone"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_send_appearance
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        id: telemetry_send_all_to_collector_label
                        text: "Send all known to collector"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_send_all_to_collector
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        id: telemetry_send_to_collector_label
                        text: "Auto send to collector"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_send_to_collector
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    id: send_syncslider_container
                    orientation: "vertical"
                    size_hint_y: None
                    padding: [0,0,dp(0),0]
                    height: dp(68)

                    MDSlider
                        id: telemetry_send_interval
                        min: 1
                        max: 214
                        value: 150
                        sensitivity: "all"
                        hint: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        id: telemetry_request_from_collector_label
                        text: "Auto request from collector"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_request_from_collector
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    id: request_syncslider_container
                    orientation: "vertical"
                    size_hint_y: None
                    padding: [0,0,dp(0),0]
                    height: dp(68)

                    MDSlider
                        id: telemetry_request_interval
                        min: 1
                        max: 214
                        value: 150
                        sensitivity: "all"
                        hint: False

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(24)
                    size_hint_y: None
                    padding: [dp(0),dp(24),dp(0),dp(60)]
                    #height: dp(232)
                    height: self.minimum_height

                    MDRectangleFlatIconButton:
                        id: telemetry_sensors_button
                        icon: "sun-thermometer-outline"
                        text: "Configure Sensors"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.delegate.sensors_action(self)
                        disabled: False

                    MDRectangleFlatIconButton:
                        id: telemetry_own_button
                        icon: "database-eye-outline"
                        text: "Display Own Telemetry"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.map_display_own_telemetry(self)
                        disabled: False

                    MDRectangleFlatIconButton:
                        id: telemetry_copy_button
                        icon: "content-copy"
                        text: "Copy Telemetry Data To Clipboard"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.delegate.telemetry_copy(self)
                        disabled: False

                    MDRectangleFlatIconButton:
                        id: telemetry_send_update_button
                        icon: "upload-lock"
                        text: "Send Telemetry To Collector"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.telemetry_send_update(self)
                        disabled: False

                    MDRectangleFlatIconButton:
                        id: telemetry_request_button
                        icon: "arrow-down-bold-hexagon-outline"
                        text: "Request Telemetry From Collector"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.telemetry_request_action(self)
                        disabled: False

                MDLabel:
                    text: "Display Options"
                    font_style: "H6"

                MDLabel:
                    id: telemetry_info4
                    markup: True
                    text: "\\nYou can customise the display style of your telemetry data when viewed by others, by setting an icon and color options. This is usually used by clients to display your telemetry entry on a map or in lists and overviews. If left unset, the receiver will decide how to display the data.\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(112)
                    padding: [dp(0), dp(24), dp(0), dp(24)]
                    pos_hint: {"center_x": .5}

                    MDIconButton:
                        pos_hint: {"center_x": .5}
                        id: telemetry_icon_preview
                        icon: "account"
                        type: "large"
                        theme_icon_color: "Custom"
                        icon_color: [0, 0, 0, 1]
                        md_bg_color: [1, 1, 1, 1]
                        icon_size: dp(64)
                        size_hint_y: None
                        # width: dp(64)
                        height: dp(80)
                        on_release: root.delegate.icons_action(self)


                MDRectangleFlatIconButton:
                    id: telemetry_icons_button
                    icon: "list-box-outline"
                    text: "Select From Available Icons"
                    padding: [dp(0), dp(14), dp(0), dp(14)]
                    icon_size: dp(24)
                    font_size: dp(16)
                    size_hint: [1.0, None]
                    on_release: root.delegate.icons_action(self)
                    disabled: False

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    padding: [dp(0),dp(24),dp(0),dp(12)]
                    height: dp(74)

                    MDBoxLayout:
                        orientation: "horizontal"
                        #size_hint_y: None
                        spacing: dp(24)
                        # padding: [0,0,dp(24),dp(0)]
                        # height: dp(48)

                        MDRectangleFlatIconButton:
                            id: telemetry_icons_button
                            icon: "list-box-outline"
                            text: "Set Foreground Color"
                            padding: [dp(0), dp(14), dp(0), dp(14)]
                            icon_size: dp(24)
                            font_size: dp(16)
                            size_hint: [1.0, None]
                            on_release: root.delegate.telemetry_fg_color(self)
                            disabled: False

                        MDRectangleFlatIconButton:
                            id: telemetry_icons_button
                            icon: "list-box-outline"
                            text: "Set Background Color"
                            padding: [dp(0), dp(14), dp(0), dp(14)]
                            icon_size: dp(24)
                            font_size: dp(16)
                            size_hint: [1.0, None]
                            on_release: root.delegate.telemetry_bg_color(self)
                            disabled: False
"""

layout_sensors_screen = """
MDScreen:
    name: "sensors_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Sensors"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_telemetry_action(self)],
                ]

        ScrollView:
            id: sensors_scrollview

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(28), dp(48), dp(28), dp(16)]

                MDLabel:
                    text: "Sensor Types"
                    font_style: "H6"

                MDLabel:
                    id: telemetry_info3
                    markup: True
                    text: ""
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Location"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_location
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Battery State"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_battery
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Pressure"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_barometer
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Temperature"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_temperature
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Humidity"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_humidity
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Magnetic Field"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_compass
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Ambient Light"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_light
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Gravity"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_gravity
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Angular Velocity"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_gyroscope
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Acceleration"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_accelerometer
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Proximity"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_proximity
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Information"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_information
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    id: telemetry_information_fields
                    orientation: "horizontal"
                    size_hint_y: None
                    spacing: dp(16)
                    height: dp(64)
                    padding: [0, dp(0), 0, dp(0)]

                    MDTextField:
                        id: telemetry_s_information_text
                        size_hint: [1.0, None]
                        hint_text: "Custom information text"
                        max_text_length: 256
                        text: ""
                        font_size: dp(24)

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Fixed Location"
                        font_style: "H6"

                    MDSwitch:
                        id: telemetry_s_fixed_location
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    id: telemetry_fixed_location_fields
                    orientation: "horizontal"
                    size_hint_y: None
                    spacing: dp(16)
                    height: dp(64)
                    padding: [0, dp(0), 0, dp(0)]
                    # md_bg_color: [1,0,0,1]

                    MDTextField:
                        id: telemetry_s_fixed_latlon
                        size_hint: [0.618, None]
                        hint_text: "Latitude, longtitude"
                        text: ""
                        font_size: dp(24)

                    MDTextField:
                        id: telemetry_s_fixed_altitude
                        size_hint: [0.382, None]
                        hint_text: "Altitude"
                        text: ""
                        font_size: dp(24)

                MDLabel:
                    markup: True
                    text: "\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]
"""

layout_icons_screen = """
MDScreen:
    name: "icons_screen"
    
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Available Icons"
            anchor_title: "left"
            elevation: 0
            left_action_items:
                [['menu', lambda x: root.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.close_sub_telemetry_action(self)],
                ]

        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(20)

            MDBoxLayout:
                adaptive_height: True

                MDIconButton:
                    icon: 'magnify'

                MDTextField:
                    id: icons_search_field
                    hint_text: 'Search icon'
                    on_text: root.delegate.icons_filter(self.text, True)

            RecycleView:
                id: icons_rv
                key_viewclass: 'viewclass'
                key_size: 'height'

                RecycleBoxLayout:
                    padding: dp(10)
                    default_size: None, dp(48)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
"""