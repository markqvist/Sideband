import time
import RNS

import base64
import threading
import RNS.vendor.umsgpack as msgpack
from kivy.metrics import dp,sp
from kivy.lang.builder import Builder
from kivy.core.clipboard import Clipboard
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy.effects.scroll import ScrollEffect
from kivy.clock import Clock
from kivy.uix.screenmanager import NoTransition, SlideTransition

TRANSITION_DURATION = 0.25
if RNS.vendor.platformutils.is_android():
    ll_ot = 0.55
    ll_ft = 0.275
else:
    ll_ot = 0.4
    ll_ft = 0.275

if RNS.vendor.platformutils.is_android():
    from ui.helpers import dark_theme_text_color
    from jnius import autoclass    
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
else:
    from .helpers import dark_theme_text_color


class Hardware():

    def __init__(self, app):
        self.app = app
        self.keys_screen = None
        self.hardware_rnode_ready = False
        self.hardware_modem_ready = False
        self.hardware_serial_ready = False

        self.no_transition = NoTransition()
        self.slide_transition = SlideTransition()

        if not self.app.hardware_ready:
            if not self.app.root.ids.screen_manager.has_screen("hardware_screen"):
                self.hardware_screen = Builder.load_string(layout_hardware_screen)
                self.hardware_screen.app = self
                self.app.root.ids.screen_manager.add_widget(self.hardware_screen)

            self.hardware_screen.ids.hardware_scrollview.effect_cls = ScrollEffect

            def con_hide_settings():
                self.app.widget_hide(self.hardware_screen.ids.hardware_rnode_button)
                self.app.widget_hide(self.hardware_screen.ids.hardware_modem_button)
                self.app.widget_hide(self.hardware_screen.ids.hardware_serial_button)

            if RNS.vendor.platformutils.get_platform() == "android":
                if not self.app.sideband.getpersistent("service.is_controlling_connectivity"):
                    info =  "Sideband is connected via a shared Reticulum instance running on this system.\n\n"
                    info += "To configure hardware parameters, edit the relevant configuration file for the instance."
                    self.hardware_screen.ids.hardware_info.text = info
                    con_hide_settings()

                else:
                    info =  "When using external hardware for communicating, you may configure various parameters, such as channel settings, modulation schemes, interface speeds and access parameters. You can set up these parameters per device type, and Sideband will apply the configuration when opening a device of that type.\n\n"
                    info += "Hardware configurations can also be exported or imported as [i]config motes[/i], which are self-contained plaintext strings that are easy to share with others. When importing a config mote, Sideband will automatically set all relevant parameters as specified within it.\n\n"
                    info += "For changes to hardware parameters to take effect, you must shut down and restart Sideband.\n"
                    self.hardware_screen.ids.hardware_info.text = info

            else:
                info = ""

                if self.app.sideband.reticulum.is_connected_to_shared_instance:
                    info =  "Sideband is connected via a shared Reticulum instance running on this system.\n\n"
                    info += "To configure hardware parameters, edit the configuration file located at:\n\n"
                    if not RNS.vendor.platformutils.is_windows(): info += str(RNS.Reticulum.configpath)
                    else:                                         info += str(RNS.Reticulum.configpath.replace("/", "\\"))
                else:
                    info =  "Sideband is currently running a standalone or master Reticulum instance on this system.\n\n"
                    info += "To configure hardware parameters, edit the configuration file located at:\n\n"
                    if not RNS.vendor.platformutils.is_windows(): info += str(RNS.Reticulum.configpath)
                    else:                                         info += str(RNS.Reticulum.configpath.replace("/", "\\"))

                self.hardware_screen.ids.hardware_info.text = info

                con_hide_settings()

        self.app.hardware_ready = True

    ## RNode hardware screen
    def hardware_rnode_action(self, sender=None, direction="left"):
        if self.hardware_rnode_ready:
            self.hardware_rnode_open(direction=direction)
        else:
            self.app.loader_action(direction=direction)
            def final(dt):
                self.hardware_rnode_init()
                def o(dt):
                    self.hardware_rnode_open(no_transition=True)
                Clock.schedule_once(o, ll_ot)
            Clock.schedule_once(final, ll_ft)

    def hardware_rnode_open(self, sender=None, direction="left", no_transition=False):
        if no_transition:
            self.app.root.ids.screen_manager.transition = self.no_transition
        else:
            self.app.root.ids.screen_manager.transition = self.slide_transition
            self.app.root.ids.screen_manager.transition.direction = direction

        self.app.root.ids.screen_manager.transition.direction = "left"
        self.app.root.ids.screen_manager.current = "hardware_rnode_screen"
        self.app.root.ids.nav_drawer.set_state("closed")
        self.app.sideband.setstate("app.displaying", self.app.root.ids.screen_manager.current)

        if no_transition:
            self.app.root.ids.screen_manager.transition = self.slide_transition

    def hardware_rnode_save(self):
        try: self.app.sideband.config["hw_rnode_frequency"] = int(float(self.hardware_rnode_screen.ids.hardware_rnode_frequency.text)*1000000)
        except: pass

        try: self.app.sideband.config["hw_rnode_bandwidth"] = int(float(self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.text)*1000)
        except: pass

        try: self.app.sideband.config["hw_rnode_tx_power"] = int(self.hardware_rnode_screen.ids.hardware_rnode_txpower.text)
        except: pass

        try: self.app.sideband.config["hw_rnode_spreading_factor"] = int(self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.text)
        except: pass
        
        try: self.app.sideband.config["hw_rnode_coding_rate"] = int(self.hardware_rnode_screen.ids.hardware_rnode_codingrate.text)
        except: pass
        
        try: self.app.sideband.config["hw_rnode_atl_short"] = float(self.hardware_rnode_screen.ids.hardware_rnode_atl_short.text)
        except: self.app.sideband.config["hw_rnode_atl_short"] = None

        try: self.app.sideband.config["hw_rnode_atl_long"] = float(self.hardware_rnode_screen.ids.hardware_rnode_atl_long.text)
        except: self.app.sideband.config["hw_rnode_atl_long"] = None
        
        if self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text == "": self.app.sideband.config["hw_rnode_beaconinterval"] = None
        else:
            try: self.app.sideband.config["hw_rnode_beaconinterval"] = int(self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text)
            except: pass

        if self.hardware_rnode_screen.ids.hardware_rnode_beacondata.text == "": self.app.sideband.config["hw_rnode_beacondata"] = None
        else: self.app.sideband.config["hw_rnode_beacondata"] = self.hardware_rnode_screen.ids.hardware_rnode_beacondata.text

        if self.hardware_rnode_screen.ids.hardware_rnode_bt_device.text == "": self.app.sideband.config["hw_rnode_bt_device"] = None
        else: self.app.sideband.config["hw_rnode_bt_device"] = self.hardware_rnode_screen.ids.hardware_rnode_bt_device.text

        if self.hardware_rnode_screen.ids.hardware_rnode_tcp_host.text == "": self.app.sideband.config["hw_rnode_tcp_host"] = None
        else: self.app.sideband.config["hw_rnode_tcp_host"] = self.hardware_rnode_screen.ids.hardware_rnode_tcp_host.text

        self.app.sideband.save_configuration()

    def hardware_rnode_scan_job(self):
        time.sleep(1.25)
        added_devices = []
        scan_timeout = time.time()+16
        def job(dt):
            self.hardware_rnode_screen.ids.hardware_rnode_bt_scan_button.disabled = True
            self.hardware_rnode_screen.ids.hardware_rnode_bt_scan_button.text = "Scanning..."
        Clock.schedule_once(job, 0.2)
        while time.time() < scan_timeout:
            RNS.log("Scanning...", RNS.LOG_DEBUG)
            for device_addr in self.app.discovered_bt_devices:
                if device_addr not in added_devices and not device_addr in self.app.bt_bonded_devices:
                    new_device = self.app.discovered_bt_devices[device_addr]
                    added_devices.append(device_addr)
                    RNS.log(f"Adding device: {new_device}")
                    def add_factory(add_device):
                        def add_job(dt):
                            pair_addr = add_device["address"]
                            btn_text = "Pair "+add_device["name"]
                            def run_pair(sender):
                                pair_result = self.hardware_rnode_pair_device_action(pair_addr)
                                if pair_result != "already_paired":
                                    def job(): self.hardware_rnode_pair_check_job(pair_addr, add_device["name"])
                                    threading.Thread(target=job, daemon=True).start()

                            device_button = MDRectangleFlatButton(text=btn_text, font_size=dp(16), padding=[dp(0), dp(14), dp(0), dp(14)], size_hint=[1.0, None])
                            device_button.bind(on_release=run_pair)
                            self.hardware_rnode_screen.ids.rnode_scan_results.add_widget(device_button)
                        return add_job
                    
                    Clock.schedule_once(add_factory(new_device), 0.1)

            time.sleep(2)

        def job(dt):
            self.hardware_rnode_screen.ids.hardware_rnode_bt_scan_button.disabled = False
            self.hardware_rnode_screen.ids.hardware_rnode_bt_scan_button.text = "Pair New Device"
        Clock.schedule_once(job, 0.2)

        if len(added_devices) == 0:
            def job(dt): toast("No unpaired RNodes discovered")
            Clock.schedule_once(job, 0.2)

    def hardware_rnode_pair_check_job(self, pair_addr, device_name):
        timeout = time.time()+45
        pairing_confirmed = False
        while not pairing_confirmed and time.time() < timeout:
            time.sleep(2)
            self.app.bluetooth_update_bonded_devices()
            if pair_addr in self.app.bt_bonded_devices:
                pairing_confirmed = True
                RNS.log(f"Pairing with {device_name} ({pair_addr}) successful", RNS.LOG_NOTICE)
                def job(dt=None): toast(f"Paired with {device_name}")
                Clock.schedule_once(job, 0.2)

    def hardware_rnode_pair_device_action(self, pair_addr):
        RNS.log(f"Pair action for {pair_addr}", RNS.LOG_DEBUG)
        self.app.stop_bluetooth_scan()
        if pair_addr in self.app.bt_bonded_devices:
            def job(dt): toast("Selected device already paired")
            Clock.schedule_once(job, 0.1)
            return "already_paired"

        else:
            BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
            if self.app.bt_adapter == None: self.app.bt_adapter = BluetoothAdapter.getDefaultAdapter()
            addr_bytes = bytes.fromhex(pair_addr.replace(":", ""))
            remote_device = self.app.bt_adapter.getRemoteDevice(addr_bytes)
            RNS.log(f"Remote device: {remote_device}", RNS.LOG_DEBUG)
            remote_device.createBond()

    def hardware_rnode_bt_scan_action(self, sender=None):
        self.app.discovered_bt_devices = {}
        rw = []
        for child in self.hardware_rnode_screen.ids.rnode_scan_results.children: rw.append(child)
        for w in rw: self.hardware_rnode_screen.ids.rnode_scan_results.remove_widget(w)
        
        Clock.schedule_once(self.app.bluetooth_scan_action, 0.5)

    def hardware_rnode_bt_on_action(self, sender=None):
        self.hardware_rnode_screen.ids.hardware_rnode_bt_pair_button.disabled = True
        self.hardware_rnode_screen.ids.hardware_rnode_bt_on_button.disabled = True
        self.hardware_rnode_screen.ids.hardware_rnode_bt_off_button.disabled = True
        def re_enable():
            time.sleep(2)
            while self.app.sideband.getstate("executing.bt_on"): time.sleep(1)
            self.hardware_rnode_screen.ids.hardware_rnode_bt_off_button.disabled = False
            self.hardware_rnode_screen.ids.hardware_rnode_bt_pair_button.disabled = False
            self.hardware_rnode_screen.ids.hardware_rnode_bt_on_button.disabled = False
        threading.Thread(target=re_enable, daemon=True).start()
        self.app.sideband.setstate("wants.bt_on", True)

    def hardware_rnode_bt_off_action(self, sender=None):
        self.hardware_rnode_screen.ids.hardware_rnode_bt_pair_button.disabled = True
        self.hardware_rnode_screen.ids.hardware_rnode_bt_on_button.disabled = True
        self.hardware_rnode_screen.ids.hardware_rnode_bt_off_button.disabled = True
        def re_enable():
            time.sleep(2)
            while self.app.sideband.getstate("executing.bt_off"): time.sleep(1)
            self.hardware_rnode_screen.ids.hardware_rnode_bt_off_button.disabled = False
            self.hardware_rnode_screen.ids.hardware_rnode_bt_pair_button.disabled = False
            self.hardware_rnode_screen.ids.hardware_rnode_bt_on_button.disabled = False
        threading.Thread(target=re_enable, daemon=True).start()
        self.app.sideband.setstate("wants.bt_off", True)

    def hardware_rnode_bt_pair_action(self, sender=None):
        self.hardware_rnode_screen.ids.hardware_rnode_bt_pair_button.disabled = True
        self.hardware_rnode_screen.ids.hardware_rnode_bt_on_button.disabled = True
        self.hardware_rnode_screen.ids.hardware_rnode_bt_off_button.disabled = True
        def re_enable():
            time.sleep(2)
            while self.app.sideband.getstate("executing.bt_pair"): time.sleep(1)
            self.hardware_rnode_screen.ids.hardware_rnode_bt_off_button.disabled = False
            self.hardware_rnode_screen.ids.hardware_rnode_bt_pair_button.disabled = False
            self.hardware_rnode_screen.ids.hardware_rnode_bt_on_button.disabled = False
        threading.Thread(target=re_enable, daemon=True).start()
        self.app.sideband.setstate("wants.bt_pair", True)

    def hardware_rnode_bt_toggle_action(self, sender=None, event=None):
        if sender.active:
            self.app.sideband.config["hw_rnode_bluetooth"] = True
            self.app.request_bluetooth_permissions()
        else:
            self.app.sideband.config["hw_rnode_bluetooth"] = False

        self.app.sideband.save_configuration()
   
    def hardware_rnode_ble_toggle_action(self, sender=None, event=None):
        if sender.active:
            self.app.sideband.config["hw_rnode_ble"] = True
            self.app.request_bluetooth_permissions()
        else:
            self.app.sideband.config["hw_rnode_ble"] = False

        self.app.sideband.save_configuration()
   
    def hardware_rnode_framebuffer_toggle_action(self, sender=None, event=None):
        if sender.active:
            self.app.sideband.config["hw_rnode_enable_framebuffer"] = True
        else:
            self.app.sideband.config["hw_rnode_enable_framebuffer"] = False

        self.app.sideband.save_configuration()
    
    def hardware_rnode_tcp_toggle_action(self, sender=None, event=None):
        if sender.active: self.app.sideband.config["hw_rnode_tcp"] = True
        else: self.app.sideband.config["hw_rnode_tcp"] = False

        self.app.sideband.save_configuration()
    
    def hardware_rnode_init(self, sender=None):
        if not self.hardware_rnode_ready:
            if not self.app.root.ids.screen_manager.has_screen("hardware_rnode_screen"):
                self.hardware_rnode_screen = Builder.load_string(layout_hardware_rnode_screen)
                self.hardware_rnode_screen.app = self
                self.app.root.ids.screen_manager.add_widget(self.hardware_rnode_screen)

            self.hardware_rnode_screen.ids.hardware_rnode_scrollview.effect_cls = ScrollEffect
            def save_connectivity(sender=None, event=None):
                if self.hardware_rnode_validate():
                    self.hardware_rnode_save()

            def focus_save(sender=None, event=None):
                if sender != None:
                    if not sender.focus:
                        save_connectivity(sender=sender)

            if self.app.sideband.config["hw_rnode_frequency"] != None:    t_freq = str(self.app.sideband.config["hw_rnode_frequency"]/1000000.0)
            else:                                                         t_freq = ""
            
            if self.app.sideband.config["hw_rnode_bandwidth"] != None:    t_bw = str(self.app.sideband.config["hw_rnode_bandwidth"]/1000.0)
            else:                                                         t_bw = str(62.5)
            
            if self.app.sideband.config["hw_rnode_tx_power"] != None:     t_p = str(self.app.sideband.config["hw_rnode_tx_power"])
            else:                                                         t_p = str(0)
            
            if self.app.sideband.config["hw_rnode_spreading_factor"] != None: t_sf = str(self.app.sideband.config["hw_rnode_spreading_factor"])
            else:                                                         t_sf = str(8)
            
            if self.app.sideband.config["hw_rnode_coding_rate"] != None:  t_cr = str(self.app.sideband.config["hw_rnode_coding_rate"])
            else:                                                         t_cr = str(6)

            if self.app.sideband.config["hw_rnode_beaconinterval"] != None: t_bi = str(self.app.sideband.config["hw_rnode_beaconinterval"])
            else:                                                         t_bi = ""
            
            if self.app.sideband.config["hw_rnode_beacondata"] != None:   t_bd = str(self.app.sideband.config["hw_rnode_beacondata"])
            else:                                                         t_bd = ""
            
            if self.app.sideband.config["hw_rnode_bt_device"] != None:    t_btd = str(self.app.sideband.config["hw_rnode_bt_device"])
            else:                                                         t_btd = ""
            
            if self.app.sideband.config["hw_rnode_tcp_host"] != None:     t_th = str(self.app.sideband.config["hw_rnode_tcp_host"])
            else:                                                         t_th = ""
            
            if self.app.sideband.config["hw_rnode_atl_short"] != None:    t_ats = str(self.app.sideband.config["hw_rnode_atl_short"])
            else:                                                         t_ats = ""
            
            if self.app.sideband.config["hw_rnode_atl_long"] != None:     t_atl = str(self.app.sideband.config["hw_rnode_atl_long"])
            else:                                                         t_atl = ""

            self.hardware_rnode_screen.ids.hardware_rnode_bluetooth.active = self.app.sideband.config["hw_rnode_bluetooth"]
            self.hardware_rnode_screen.ids.hardware_rnode_ble.active = self.app.sideband.config["hw_rnode_ble"]
            self.hardware_rnode_screen.ids.hardware_rnode_tcp.active = self.app.sideband.config["hw_rnode_tcp"]
            self.hardware_rnode_screen.ids.hardware_rnode_framebuffer.active = self.app.sideband.config["hw_rnode_enable_framebuffer"]
            self.hardware_rnode_screen.ids.hardware_rnode_frequency.text = t_freq
            self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.text = t_bw
            self.hardware_rnode_screen.ids.hardware_rnode_txpower.text = t_p
            self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.text = t_sf
            self.hardware_rnode_screen.ids.hardware_rnode_codingrate.text = t_cr
            self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text = t_bi
            self.hardware_rnode_screen.ids.hardware_rnode_beacondata.text = t_bd
            self.hardware_rnode_screen.ids.hardware_rnode_bt_device.text = t_btd
            self.hardware_rnode_screen.ids.hardware_rnode_tcp_host.text = t_th
            self.hardware_rnode_screen.ids.hardware_rnode_atl_short.text = t_ats
            self.hardware_rnode_screen.ids.hardware_rnode_atl_long.text = t_atl
            self.hardware_rnode_screen.ids.hardware_rnode_frequency.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_txpower.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_codingrate.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_beacondata.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_bt_device.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_tcp_host.bind(focus=focus_save)
            self.hardware_rnode_screen.ids.hardware_rnode_frequency.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_txpower.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_codingrate.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_beacondata.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_atl_short.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_atl_long.bind(on_text_validate=save_connectivity)
            self.hardware_rnode_screen.ids.hardware_rnode_bluetooth.bind(active=self.hardware_rnode_bt_toggle_action)
            self.hardware_rnode_screen.ids.hardware_rnode_ble.bind(active=self.hardware_rnode_ble_toggle_action)
            self.hardware_rnode_screen.ids.hardware_rnode_framebuffer.bind(active=self.hardware_rnode_framebuffer_toggle_action)
            self.hardware_rnode_screen.ids.hardware_rnode_tcp.bind(active=self.hardware_rnode_tcp_toggle_action)

            self.hardware_rnode_ready = True

    def hardware_rnode_validate(self, sender=None):
        valid = True        
        try:
            val = float(self.hardware_rnode_screen.ids.hardware_rnode_frequency.text)
            if not val > 0:
                raise ValueError("Invalid frequency")
            self.hardware_rnode_screen.ids.hardware_rnode_frequency.error = False
            self.hardware_rnode_screen.ids.hardware_rnode_frequency.text = str(val)
        except:
            self.hardware_rnode_screen.ids.hardware_rnode_frequency.error = True
            valid = False
        
        try:
            valid_vals = [7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125, 250, 500, 203.125, 406.25, 812.5, 1625]
            val = float(self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.text)
            if not val in valid_vals:
                raise ValueError("Invalid bandwidth")
            self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.error = False
            self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.text = str(val)
        except:
            self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.error = True
            valid = False
        
        try:
            val = int(self.hardware_rnode_screen.ids.hardware_rnode_txpower.text)
            if not val >= 0:
                raise ValueError("Invalid TX power")
            self.hardware_rnode_screen.ids.hardware_rnode_txpower.error = False
            self.hardware_rnode_screen.ids.hardware_rnode_txpower.text = str(val)
        except:
            self.hardware_rnode_screen.ids.hardware_rnode_txpower.error = True
            valid = False
        
        try:
            val = int(self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.text)
            if val < 7 or val > 12:
                raise ValueError("Invalid sf")
            self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.error = False
            self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.text = str(val)
        except:
            self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.error = True
            valid = False
        
        try:
            val = int(self.hardware_rnode_screen.ids.hardware_rnode_codingrate.text)
            if val < 5 or val > 8:
                raise ValueError("Invalid cr")
            self.hardware_rnode_screen.ids.hardware_rnode_codingrate.error = False
            self.hardware_rnode_screen.ids.hardware_rnode_codingrate.text = str(val)
        except:
            self.hardware_rnode_screen.ids.hardware_rnode_codingrate.error = True
            valid = False
        
        try:
            if self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text != "":
                val = int(self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text)
                if val < 10:
                    raise ValueError("Invalid beacon interval")
                self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text = str(val)

            self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.error = False
        except:
            self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text = ""
            valid = False
        
        return valid

    def hardware_rnode_import(self, sender=None):
        mote = None
        try:
            mote = Clipboard.paste()
        except Exception as e:
            yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
            dialog = MDDialog(
                title="Import Failed",
                text="Could not read data from your clipboard, please check your system permissions.",
                buttons=[ yes_button ],
                # elevation=0,
            )
            def dl_yes(s):
                dialog.dismiss()
            yes_button.bind(on_release=dl_yes)
            dialog.open()

        try:
            config = msgpack.unpackb(base64.b32decode(mote))
            self.hardware_rnode_screen.ids.hardware_rnode_frequency.text        = str(config["f"]/1000000.0)
            self.hardware_rnode_screen.ids.hardware_rnode_bandwidth.text        = str(config["b"]/1000.0)
            self.hardware_rnode_screen.ids.hardware_rnode_txpower.text          = str(config["t"])
            self.hardware_rnode_screen.ids.hardware_rnode_spreadingfactor.text  = str(config["s"])
            self.hardware_rnode_screen.ids.hardware_rnode_codingrate.text       = str(config["c"])
            
            if "n" in config and config["n"] != None:
                ifn = str(config["n"])
            else:
                ifn = ""
            if "p" in config and config["p"] != None:
                ifp = str(config["p"])
            else:
                ifp = ""

            if self.app.connectivity_screen != None:
                self.app.connectivity_screen.ids.connectivity_rnode_ifac_netname.text    = ifn
                self.app.connectivity_screen.ids.connectivity_rnode_ifac_passphrase.text = ifp
            
            self.app.sideband.config["connect_rnode_ifac_netname"]    = ifn
            self.app.sideband.config["connect_rnode_ifac_passphrase"] = ifp

            if config["i"] != None: ti = str(config["i"])
            else: ti = ""
            self.hardware_rnode_screen.ids.hardware_rnode_beaconinterval.text  = ti
            
            if config["d"] != None: td = str(config["d"])
            else: td = ""
            self.hardware_rnode_screen.ids.hardware_rnode_beacondata.text = td

            if self.hardware_rnode_validate():
                self.hardware_rnode_save()
                yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
                dialog = MDDialog(
                    title="Configuration Imported",
                    text="The config mote was imported and saved as your active configuration.",
                    buttons=[ yes_button ],
                    # elevation=0,
                )
                def dl_yes(s):
                    dialog.dismiss()
                yes_button.bind(on_release=dl_yes)
                dialog.open()
            else:
                raise ValueError("Invalid mote")

        except Exception as e:
            yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
            dialog = MDDialog(
                title="Import Failed",
                text="The read data did not contain a valid config mote. If any data was decoded, you may try to correct it by editing the relevant fields. The reported error was:\n\n"+str(e),
                buttons=[ yes_button ],
                # elevation=0,
            )
            def dl_yes(s):
                dialog.dismiss()
            yes_button.bind(on_release=dl_yes)
            dialog.open()

    def hardware_rnode_export(self, sender=None):
        mote = None
        try:
            mote = base64.b32encode(msgpack.packb({
                "f": self.app.sideband.config["hw_rnode_frequency"],
                "b": self.app.sideband.config["hw_rnode_bandwidth"],
                "t": self.app.sideband.config["hw_rnode_tx_power"],
                "s": self.app.sideband.config["hw_rnode_spreading_factor"],
                "c": self.app.sideband.config["hw_rnode_coding_rate"],
                "i": self.app.sideband.config["hw_rnode_beaconinterval"],
                "d": self.app.sideband.config["hw_rnode_beacondata"],
                "n": self.app.sideband.config["connect_rnode_ifac_netname"],
                "p": self.app.sideband.config["connect_rnode_ifac_passphrase"],
            }))
        except Exception as e:
            RNS.trace_exception(e)

        if mote != None:
            Clipboard.copy(mote)
            yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
            dialog = MDDialog(
                title="Configuration Exported",
                text="The config mote was created and copied to your clipboard.",
                buttons=[ yes_button ],
                # elevation=0,
            )
            def dl_yes(s):
                dialog.dismiss()
            yes_button.bind(on_release=dl_yes)
            dialog.open()
        else:
            yes_button = MDRectangleFlatButton(text="OK",font_size=dp(18))
            dialog = MDDialog(
                title="Export Failed",
                text="The config mote could not be created, please check your settings.",
                buttons=[ yes_button ],
                # elevation=0,
            )
            def dl_yes(s):
                dialog.dismiss()
            yes_button.bind(on_release=dl_yes)
            dialog.open()
    
    ## Modem hardware screen
    
    def hardware_modem_action(self, sender=None, direction="left"):
        if self.hardware_modem_ready:
            self.hardware_modem_open(direction=direction)
        else:
            self.app.loader_action(direction=direction)
            def final(dt):
                self.hardware_modem_init()
                def o(dt):
                    self.hardware_modem_open(no_transition=True)
                Clock.schedule_once(o, ll_ot)
            Clock.schedule_once(final, ll_ft)

    def hardware_modem_open(self, sender=None, direction="left", no_transition=False):
        if no_transition:
            self.app.root.ids.screen_manager.transition = self.no_transition
        else:
            self.app.root.ids.screen_manager.transition = self.slide_transition
            self.app.root.ids.screen_manager.transition.direction = direction

        self.hardware_modem_init()
        self.app.root.ids.screen_manager.transition.direction = "left"
        self.app.root.ids.screen_manager.current = "hardware_modem_screen"
        self.app.root.ids.nav_drawer.set_state("closed")
        self.app.sideband.setstate("app.displaying", self.app.root.ids.screen_manager.current)

        if no_transition:
            self.app.root.ids.screen_manager.transition = self.slide_transition

    def hardware_modem_init(self, sender=None):
        if not self.hardware_modem_ready:
            if not self.app.root.ids.screen_manager.has_screen("hardware_modem_screen"):
                self.hardware_modem_screen = Builder.load_string(layout_hardware_modem_screen)
                self.hardware_modem_screen.app = self
                self.app.root.ids.screen_manager.add_widget(self.hardware_modem_screen)

            self.hardware_modem_screen.ids.hardware_modem_scrollview.effect_cls = ScrollEffect
            def save_connectivity(sender=None, event=None):
                if self.hardware_modem_validate():
                    self.hardware_modem_save()

            def focus_save(sender=None, event=None):
                if sender != None:
                    if not sender.focus:
                        save_connectivity(sender=sender)

            if self.app.sideband.config["hw_modem_baudrate"] != None:
                t_b = str(self.app.sideband.config["hw_modem_baudrate"])
            else:
                t_b = ""

            if self.app.sideband.config["hw_modem_databits"] != None:
                t_db = str(self.app.sideband.config["hw_modem_databits"])
            else:
                t_db = ""

            if self.app.sideband.config["hw_modem_parity"] != None:
                t_p = str(self.app.sideband.config["hw_modem_parity"])
            else:
                t_p = ""
            
            if self.app.sideband.config["hw_modem_stopbits"] != None:
                t_sb = str(self.app.sideband.config["hw_modem_stopbits"])
            else:
                t_sb = ""
            
            if self.app.sideband.config["hw_modem_preamble"] != None:
                t_pa = str(self.app.sideband.config["hw_modem_preamble"])
            else:
                t_pa = ""
            
            if self.app.sideband.config["hw_modem_tail"] != None:
                t_t = str(self.app.sideband.config["hw_modem_tail"])
            else:
                t_t = ""
            
            if self.app.sideband.config["hw_modem_persistence"] != None:
                t_ps = str(self.app.sideband.config["hw_modem_persistence"])
            else:
                t_ps = ""

            if self.app.sideband.config["hw_modem_slottime"] != None:
                t_st = str(self.app.sideband.config["hw_modem_slottime"])
            else:
                t_st = ""

            if self.app.sideband.config["hw_modem_beaconinterval"] != None:
                t_bi = str(self.app.sideband.config["hw_modem_beaconinterval"])
            else:
                t_bi = ""
            if self.app.sideband.config["hw_modem_beacondata"] != None:
                t_bd = str(self.app.sideband.config["hw_modem_beacondata"])
            else:
                t_bd = ""
            
            self.hardware_modem_screen.ids.hardware_modem_baudrate.text = t_b
            self.hardware_modem_screen.ids.hardware_modem_databits.text = t_db
            self.hardware_modem_screen.ids.hardware_modem_parity.text = t_p
            self.hardware_modem_screen.ids.hardware_modem_stopbits.text = t_sb
            self.hardware_modem_screen.ids.hardware_modem_beaconinterval.text = t_bi
            self.hardware_modem_screen.ids.hardware_modem_beacondata.text = t_bd
            self.hardware_modem_screen.ids.hardware_modem_preamble.text = t_pa
            self.hardware_modem_screen.ids.hardware_modem_tail.text = t_t
            self.hardware_modem_screen.ids.hardware_modem_persistence.text = t_ps
            self.hardware_modem_screen.ids.hardware_modem_slottime.text = t_st
            self.hardware_modem_screen.ids.hardware_modem_baudrate.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_databits.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_parity.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_stopbits.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_beaconinterval.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_beacondata.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_preamble.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_tail.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_persistence.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_slottime.bind(focus=focus_save)
            self.hardware_modem_screen.ids.hardware_modem_baudrate.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_databits.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_parity.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_stopbits.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_beaconinterval.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_beacondata.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_preamble.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_tail.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_persistence.bind(on_text_validate=save_connectivity)
            self.hardware_modem_screen.ids.hardware_modem_slottime.bind(on_text_validate=save_connectivity)

            self.hardware_modem_ready = True
    
    def hardware_modem_save(self):
        self.app.sideband.config["hw_modem_baudrate"] = int(self.hardware_modem_screen.ids.hardware_modem_baudrate.text)
        self.app.sideband.config["hw_modem_databits"] = int(self.hardware_modem_screen.ids.hardware_modem_databits.text)
        self.app.sideband.config["hw_modem_parity"] = self.hardware_modem_screen.ids.hardware_modem_parity.text
        self.app.sideband.config["hw_modem_stopbits"] = int(self.hardware_modem_screen.ids.hardware_modem_stopbits.text)
        self.app.sideband.config["hw_modem_preamble"] = int(self.hardware_modem_screen.ids.hardware_modem_preamble.text)
        self.app.sideband.config["hw_modem_tail"] = int(self.hardware_modem_screen.ids.hardware_modem_tail.text)
        self.app.sideband.config["hw_modem_persistence"] = int(self.hardware_modem_screen.ids.hardware_modem_persistence.text)
        self.app.sideband.config["hw_modem_slottime"] = int(self.hardware_modem_screen.ids.hardware_modem_slottime.text)

        if self.hardware_modem_screen.ids.hardware_modem_beaconinterval.text == "":
            self.app.sideband.config["hw_modem_beaconinterval"] = None
        else:
            self.app.sideband.config["hw_modem_beaconinterval"] = int(self.hardware_modem_screen.ids.hardware_modem_beaconinterval.text)

        if self.hardware_modem_screen.ids.hardware_modem_beacondata.text == "":
            self.app.sideband.config["hw_modem_beacondata"] = None
        else:
            self.app.sideband.config["hw_modem_beacondata"] = self.hardware_modem_screen.ids.hardware_modem_beacondata.text

        self.app.sideband.save_configuration()

    def hardware_modem_validate(self, sender=None):
        valid = True        
        try:
            val = int(self.hardware_modem_screen.ids.hardware_modem_baudrate.text)
            if not val > 0:
                raise ValueError("Invalid baudrate")
            self.hardware_modem_screen.ids.hardware_modem_baudrate.error = False
            self.hardware_modem_screen.ids.hardware_modem_baudrate.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_baudrate.error = True
            valid = False
        
        try:
            val = int(self.hardware_modem_screen.ids.hardware_modem_databits.text)
            if not val > 0:
                raise ValueError("Invalid databits")
            self.hardware_modem_screen.ids.hardware_modem_databits.error = False
            self.hardware_modem_screen.ids.hardware_modem_databits.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_databits.error = True
            valid = False
        
        try:
            val = int(self.hardware_modem_screen.ids.hardware_modem_stopbits.text)
            if not val > 0:
                raise ValueError("Invalid stopbits")
            self.hardware_modem_screen.ids.hardware_modem_stopbits.error = False
            self.hardware_modem_screen.ids.hardware_modem_stopbits.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_stopbits.error = True
            valid = False
        
        try:
            val = int(self.hardware_modem_screen.ids.hardware_modem_preamble.text)
            if not (val >= 0 and val <= 1000):
                raise ValueError("Invalid preamble")
            self.hardware_modem_screen.ids.hardware_modem_preamble.error = False
            self.hardware_modem_screen.ids.hardware_modem_preamble.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_preamble.error = True
            valid = False
        
        try:
            val = int(self.hardware_modem_screen.ids.hardware_modem_tail.text)
            if not (val > 0 and val <= 500):
                raise ValueError("Invalid tail")
            self.hardware_modem_screen.ids.hardware_modem_tail.error = False
            self.hardware_modem_screen.ids.hardware_modem_tail.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_tail.error = True
            valid = False
        
        try:
            val = int(self.hardware_modem_screen.ids.hardware_modem_slottime.text)
            if not (val > 0 and val <= 500):
                raise ValueError("Invalid slottime")
            self.hardware_modem_screen.ids.hardware_modem_slottime.error = False
            self.hardware_modem_screen.ids.hardware_modem_slottime.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_slottime.error = True
            valid = False
        
        try:
            val = int(self.hardware_modem_screen.ids.hardware_modem_persistence.text)
            if not (val > 0 and val <= 255):
                raise ValueError("Invalid persistence")
            self.hardware_modem_screen.ids.hardware_modem_persistence.error = False
            self.hardware_modem_screen.ids.hardware_modem_persistence.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_persistence.error = True
            valid = False
        
        try:
            val = self.hardware_modem_screen.ids.hardware_modem_parity.text
            nval = val.lower()
            if nval in ["e", "ev", "eve", "even"]:
                val = "even"
            if nval in ["o", "od", "odd"]:
                val = "odd"
            if nval in ["n", "no", "non", "none", "not", "null", "off"]:
                val = "none"
            if not val in ["even", "odd", "none"]:
                raise ValueError("Invalid parity")
            self.hardware_modem_screen.ids.hardware_modem_parity.error = False
            self.hardware_modem_screen.ids.hardware_modem_parity.text = str(val)
        except:
            self.hardware_modem_screen.ids.hardware_modem_parity.error = True
            valid = False

        try:
            if self.hardware_modem_screen.ids.hardware_modem_beaconinterval.text != "":
                val = int(self.hardware_modem_screen.ids.hardware_modem_beaconinterval.text)
                if val < 10:
                    raise ValueError("Invalid bi")
                self.hardware_modem_screen.ids.hardware_modem_beaconinterval.text = str(val)

            self.hardware_modem_screen.ids.hardware_modem_beaconinterval.error = False
        except:
            self.hardware_modem_screen.ids.hardware_modem_beaconinterval.text = ""
            valid = False

        return valid
    
    ## Serial hardware screen
    def hardware_serial_action(self, sender=None, direction="left"):
        if self.hardware_serial_ready:
            self.hardware_serial_open(direction=direction)
        else:
            self.app.loader_action(direction=direction)
            def final(dt):
                self.hardware_serial_init()
                def o(dt):
                    self.hardware_serial_open(no_transition=True)
                Clock.schedule_once(o, ll_ot)
            Clock.schedule_once(final, ll_ft)

    def hardware_serial_open(self, sender=None, direction="left", no_transition=False):
        if no_transition:
            self.app.root.ids.screen_manager.transition = self.no_transition
        else:
            self.app.root.ids.screen_manager.transition = self.slide_transition
            self.app.root.ids.screen_manager.transition.direction = direction

        self.app.root.ids.screen_manager.transition.direction = "left"
        self.app.root.ids.screen_manager.current = "hardware_serial_screen"
        self.app.root.ids.nav_drawer.set_state("closed")
        self.app.sideband.setstate("app.displaying", self.app.root.ids.screen_manager.current)

        if no_transition:
            self.app.root.ids.screen_manager.transition = self.slide_transition

    def hardware_serial_init(self, sender=None):
        if not self.hardware_serial_ready:
            if not self.app.root.ids.screen_manager.has_screen("hardware_serial_screen"):
                self.hardware_serial_screen = Builder.load_string(layout_hardware_serial_screen)
                self.hardware_serial_screen.app = self
                self.app.root.ids.screen_manager.add_widget(self.hardware_serial_screen)

            self.hardware_serial_screen.ids.hardware_serial_scrollview.effect_cls = ScrollEffect
            def save_connectivity(sender=None, event=None):
                if self.hardware_serial_validate():
                    self.hardware_serial_save()

            def focus_save(sender=None, event=None):
                if sender != None:
                    if not sender.focus:
                        save_connectivity(sender=sender)

            if self.app.sideband.config["hw_serial_baudrate"] != None:
                t_b = str(self.app.sideband.config["hw_serial_baudrate"])
            else:
                t_b = ""

            if self.app.sideband.config["hw_serial_databits"] != None:
                t_db = str(self.app.sideband.config["hw_serial_databits"])
            else:
                t_db = ""

            if self.app.sideband.config["hw_serial_parity"] != None:
                t_p = str(self.app.sideband.config["hw_serial_parity"])
            else:
                t_p = ""
            
            if self.app.sideband.config["hw_serial_stopbits"] != None:
                t_sb = str(self.app.sideband.config["hw_serial_stopbits"])
            else:
                t_sb = ""
            
            self.hardware_serial_screen.ids.hardware_serial_baudrate.text = t_b
            self.hardware_serial_screen.ids.hardware_serial_databits.text = t_db
            self.hardware_serial_screen.ids.hardware_serial_parity.text = t_p
            self.hardware_serial_screen.ids.hardware_serial_stopbits.text = t_sb
            self.hardware_serial_screen.ids.hardware_serial_baudrate.bind(focus=focus_save)
            self.hardware_serial_screen.ids.hardware_serial_databits.bind(focus=focus_save)
            self.hardware_serial_screen.ids.hardware_serial_parity.bind(focus=focus_save)
            self.hardware_serial_screen.ids.hardware_serial_stopbits.bind(focus=focus_save)
            self.hardware_serial_screen.ids.hardware_serial_baudrate.bind(on_text_validate=save_connectivity)
            self.hardware_serial_screen.ids.hardware_serial_databits.bind(on_text_validate=save_connectivity)
            self.hardware_serial_screen.ids.hardware_serial_parity.bind(on_text_validate=save_connectivity)
            self.hardware_serial_screen.ids.hardware_serial_stopbits.bind(on_text_validate=save_connectivity)

            self.hardware_serial_ready = True

    def hardware_serial_validate(self, sender=None):
        valid = True        
        try:
            val = int(self.hardware_serial_screen.ids.hardware_serial_baudrate.text)
            if not val > 0:
                raise ValueError("Invalid baudrate")
            self.hardware_serial_screen.ids.hardware_serial_baudrate.error = False
            self.hardware_serial_screen.ids.hardware_serial_baudrate.text = str(val)
        except:
            self.hardware_serial_screen.ids.hardware_serial_baudrate.error = True
            valid = False
        
        try:
            val = int(self.hardware_serial_screen.ids.hardware_serial_databits.text)
            if not val > 0:
                raise ValueError("Invalid databits")
            self.hardware_serial_screen.ids.hardware_serial_databits.error = False
            self.hardware_serial_screen.ids.hardware_serial_databits.text = str(val)
        except:
            self.hardware_serial_screen.ids.hardware_serial_databits.error = True
            valid = False
        
        try:
            val = int(self.hardware_serial_screen.ids.hardware_serial_stopbits.text)
            if not val > 0:
                raise ValueError("Invalid stopbits")
            self.hardware_serial_screen.ids.hardware_serial_stopbits.error = False
            self.hardware_serial_screen.ids.hardware_serial_stopbits.text = str(val)
        except:
            self.hardware_serial_screen.ids.hardware_serial_stopbits.error = True
            valid = False
        
        try:
            val = self.hardware_serial_screen.ids.hardware_serial_parity.text
            nval = val.lower()
            if nval in ["e", "ev", "eve", "even"]:
                val = "even"
            if nval in ["o", "od", "odd"]:
                val = "odd"
            if nval in ["n", "no", "non", "none", "not", "null", "off"]:
                val = "none"
            if not val in ["even", "odd", "none"]:
                raise ValueError("Invalid parity")
            self.hardware_serial_screen.ids.hardware_serial_parity.error = False
            self.hardware_serial_screen.ids.hardware_serial_parity.text = str(val)
        except:
            self.hardware_serial_screen.ids.hardware_serial_parity.error = True
            valid = False

        return valid

    def hardware_serial_save(self):
        self.app.sideband.config["hw_serial_baudrate"] = int(self.hardware_serial_screen.ids.hardware_serial_baudrate.text)
        self.app.sideband.config["hw_serial_databits"] = int(self.hardware_serial_screen.ids.hardware_serial_databits.text)
        self.app.sideband.config["hw_serial_parity"] = self.hardware_serial_screen.ids.hardware_serial_parity.text
        self.app.sideband.config["hw_serial_stopbits"] = int(self.hardware_serial_screen.ids.hardware_serial_stopbits.text)

        self.app.sideband.save_configuration()

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
                [['menu', lambda x: root.app.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.app.close_hardware_action(self)],
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
                [['menu', lambda x: root.app.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.app.close_sub_hardware_action(self)],
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
                [['menu', lambda x: root.app.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.app.close_sub_hardware_action(self)],
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
                    padding: [dp(0), dp(0), dp(0), dp(48)]

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
                    text: "Radio Options\\n"
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
                    padding: [0,dp(14),dp(24),dp(0)]
                    height: dp(48)
                    
                    MDLabel:
                        text: "Control RNode Display"
                        font_style: "H6"

                    MDSwitch:
                        id: hardware_rnode_framebuffer
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDLabel:
                    text: "•"
                    font_style: "H6"
                    text_size: self.size
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: [0, dp(2+14), 0, dp(22+24)]

                MDLabel:
                    text: "WiFi & Ethernet Connection\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_rnode_info_wifi
                    markup: True
                    text: "If your device is hosting or connected to a WiFi network, you can connect it by entering its IP address or hostname below."
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,dp(12),dp(24),dp(0)]
                    height: dp(36)
                    
                    MDLabel:
                        text: "Connect using WiFi"
                        font_style: "H6"

                    MDSwitch:
                        id: hardware_rnode_tcp
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDBoxLayout:
                    orientation: "vertical"
                    # spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_rnode_tcp_host
                        hint_text: "RNode IP address or hostname"
                        text: ""
                        font_size: dp(24)

                MDLabel:
                    text: "•"
                    font_style: "H6"
                    text_size: self.size
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: [0, dp(2+14), 0, dp(22+24)]

                MDLabel:
                    text: "Bluetooth Connection\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_rnode_info
                    markup: True
                    text: "If you enable connection via Bluetooth, Sideband will attempt to connect to any available and paired RNodes over Bluetooth.\\n\\nIf your RNode uses BLE (ESP32-S3 and nRF devices) instead of classic Bluetooth, enable the [i]Device requires BLE[/i] option as well."
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

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

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    padding: [0,0,dp(24),dp(48)]
                    height: dp(86)
                    
                    MDLabel:
                        text: "Device requires BLE"
                        font_style: "H6"

                    MDSwitch:
                        id: hardware_rnode_ble
                        pos_hint: {"center_y": 0.3}
                        active: False

                MDLabel:
                    text: "Bluetooth Pairing\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_rnode_info
                    markup: True
                    text: "To put an RNode into pairing mode, hold down the multi-function user button for more than 5 seconds, and release it. The display will indicate pairing mode. If the in-app pairing does not find any devices, use the Bluetooth settings of your device to scan and pair.\\n"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(12)]

                    MDRectangleFlatIconButton:
                        id: hardware_rnode_bt_scan_button
                        icon: "bluetooth-connect"
                        text: "Pair New Device"
                        padding: [dp(0), dp(14), dp(0), dp(14)]
                        icon_size: dp(24)
                        font_size: dp(16)
                        size_hint: [1.0, None]
                        on_release: root.app.hardware_rnode_bt_scan_action(self)

                MDBoxLayout:
                    id: rnode_scan_results
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(12+24)]

                MDLabel:
                    text: "Preffered Bluetooth Device\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_rnode_info
                    markup: True
                    text: "Sideband will connect to the first available RNode that is paired. If you want to always use a specific RNode, you can enter its name here, for example \\"RNode A8EB\\"."
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: "24dp"
                    size_hint_y: None
                    height: self.minimum_height
                    # padding: [dp(0), dp(0), dp(0), dp(35)]

                    MDTextField:
                        id: hardware_rnode_bt_device
                        hint_text: "Preferred RNode Device Name"
                        text: ""
                        font_size: dp(24)

                MDLabel:
                    text: "•"
                    font_style: "H6"
                    text_size: self.size
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: [0, dp(2+14), 0, dp(22)]

                MDLabel:
                    text: "\\n\\nDevice Bluetooth Control\\n"
                    font_style: "H6"

                MDLabel:
                    id: hardware_rnode_info
                    markup: True
                    text: "\\n\\nIf your RNode does not have a physical pairing button, you can enable Bluetooth and put it into pairing mode by first connecting it via a USB cable, and using the buttons below. When plugging in the RNode over USB, you must grant Sideband permission to the USB device for this to work.\\n\\nYou can also change Bluetooth settings using the \\"rnodeconf\\" utility from a computer.\\n"
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
                [['menu', lambda x: root.app.app.nav_drawer.set_state("open")]]
            right_action_items:
                [
                ['close', lambda x: root.app.app.close_sub_hardware_action(self)],
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
