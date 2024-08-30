__debug_build__ = False

import sys
import time
import RNS
from os import environ

from kivy.logger import Logger, LOG_LEVELS

if __debug_build__:
    Logger.setLevel(LOG_LEVELS["debug"])
else:
    Logger.setLevel(LOG_LEVELS["error"])

if RNS.vendor.platformutils.get_platform() == "android":
    from jnius import autoclass, cast

    # Squelch excessive method signature logging
    import jnius.reflect
    class redirect_log():
        def isEnabledFor(self, arg):
            return False
        def debug(self, arg):
            pass
    def mod(method, name, signature):
        pass
    jnius.reflect.log_method = mod
    jnius.reflect.log = redirect_log()
    ############################################

    from android import python_act
    android_api_version = autoclass('android.os.Build$VERSION').SDK_INT
            
    Intent = autoclass('android.content.Intent')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    Icon = autoclass("android.graphics.drawable.Icon")
    PendingIntent = autoclass('android.app.PendingIntent')
    AndroidString = autoclass('java.lang.String')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')

    if android_api_version >= 26:
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        NotificationChannel = autoclass('android.app.NotificationChannel')

    from usb4a import usb
    from usbserial4a import serial4a
    from sideband.core import SidebandCore

else:
    from sbapp.sideband.core import SidebandCore

class SidebandService():
    usb_device_filter = {
        0x0403: [0x6001, 0x6010, 0x6011, 0x6014, 0x6015], # FTDI
        0x10C4: [0xea60, 0xea70, 0xea71], # SiLabs
        0x067B: [0x2303, 0x23a3, 0x23b3, 0x23c3, 0x23d3, 0x23e3, 0x23f3], # Prolific
        0x1a86: [0x5523, 0x7523, 0x55D4], # Qinheng
        0x0483: [0x5740], # ST CDC
        0x2E8A: [0x0005, 0x000A], # Raspberry Pi Pico
        0x239A: [0x8029], # Adafruit (RAK4631)
        0x303A: [0x1001], # ESP-32S3
    }
    
    def android_notification(self, title="", content="", ticker="", group=None, context_id=None):
        if android_api_version < 26:
            return
        else:
            package_name = "io.unsigned.sideband"

            if not self.notification_service:
                self.notification_service = cast(NotificationManager, self.app_context.getSystemService(
                    Context.NOTIFICATION_SERVICE
                ))

            channel_id = package_name
            group_id = ""
            if group != None:
                channel_id += "."+str(group)
                group_id += str(group)
            if context_id != None:
                channel_id += "."+str(context_id)
                group_id += "."+str(context_id)

            if not title or title == "":
                channel_name = "Sideband"
            else:
                channel_name = title

            self.notification_channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_DEFAULT)
            self.notification_channel.enableVibration(True)
            self.notification_channel.setShowBadge(True)
            self.notification_service.createNotificationChannel(self.notification_channel)

            notification = NotificationBuilder(self.app_context, channel_id)
            notification.setContentTitle(title)
            notification.setContentText(AndroidString(content))
            
            # if group != None:
            #     notification.setGroup(group_id)

            if not self.notification_small_icon:
                path = self.sideband.notification_icon
                bitmap = BitmapFactory.decodeFile(path)
                self.notification_small_icon = Icon.createWithBitmap(bitmap)

            notification.setSmallIcon(self.notification_small_icon)

            # large_icon_path = self.sideband.icon
            # bitmap_icon = BitmapFactory.decodeFile(large_icon_path)
            # notification.setLargeIcon(bitmap_icon)

            if not self.notification_intent:
                notification_intent = Intent(self.app_context, python_act)
                notification_intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
                notification_intent.setAction(Intent.ACTION_MAIN)
                notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
                self.notification_intent = PendingIntent.getActivity(self.app_context, 0, notification_intent, 0)

            notification.setContentIntent(self.notification_intent)
            notification.setAutoCancel(True)

            built_notification = notification.build()
            self.notification_service.notify(0, built_notification)

    def check_permission(self, permission):
        if RNS.vendor.platformutils.is_android():
            try:
                result = self.android_service.checkSelfPermission("android.permission."+permission)
                if result == 0:
                    return True

            except Exception as e:
                RNS.log("Error while checking permission: "+str(e), RNS.LOG_ERROR)
            
            return False
        
        else:
            return False

    def background_location_allowed(self):
        if not RNS.vendor.platformutils.is_android():
            return False

        perms = ["ACCESS_FINE_LOCATION","ACCESS_COARSE_LOCATION","ACCESS_BACKGROUND_LOCATION"]
        for perm in perms:
            if not self.check_permission(perm):
                return False

        return True

    def android_location_callback(self, **kwargs):
        self._raw_gps = kwargs
        self._last_gps_update = time.time()

    def should_update_location(self):
        if self.sideband.config["telemetry_enabled"] and self.sideband.config["telemetry_s_location"] and self.background_location_allowed():
            return True
        else:
            return False

    def update_location_provider(self):
        if RNS.vendor.platformutils.is_android():
            if self.should_update_location():
                if not self._gps_started:
                    RNS.log("Starting service location provider", RNS.LOG_DEBUG)
                    
                    if self.gps == None:
                        from plyer import gps
                        self.gps = gps

                    self.gps.configure(on_location=self.android_location_callback)
                    self.gps.start(minTime=self._gps_stale_time, minDistance=self._gps_min_distance)
                    self._gps_started = True

            else:
                if self._gps_started:
                    RNS.log("Stopping service location provider", RNS.LOG_DEBUG)
                    if self.gps != None:
                        self.gps.stop()
                    self._gps_started = False
                    self._raw_gps = None

    def get_location(self):
        return self._last_gps_update, self._raw_gps

    def __init__(self):
        self.argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
        self.app_dir = self.argument
        self.multicast_lock = None
        self.wake_lock = None
        self.should_run = False
        self.gps = None
        self._gps_started = False
        self._gps_stale_time = 300-1
        self._gps_min_distance = 3
        self._raw_gps = None

        self.android_service = None
        self.app_context = None
        self.wifi_manager = None
        self.power_manager = None
        self.usb_devices = []
        self.usb_device_filter = SidebandService.usb_device_filter

        self.notification_service = None
        self.notification_channel = None
        self.notification_intent = None
        self.notification_small_icon = None

        if RNS.vendor.platformutils.is_android():
            self.android_service = autoclass('org.kivy.android.PythonService').mService
            self.app_context = self.android_service.getApplication().getApplicationContext()
            
            try:
                self.wifi_manager = self.app_context.getSystemService(Context.WIFI_SERVICE)
            except Exception as e:
                self.wifi_manager = None
                RNS.log("Could not acquire Android WiFi Manager! Keeping WiFi-based interfaces up will be unavailable.", RNS.LOG_ERROR)
                RNS.log("The contained exception was: "+str(e), RNS.LOG_ERROR)

            try:
                self.power_manager = self.app_context.getSystemService(Context.POWER_SERVICE)
            except Exception as e:
                self.power_manager = None
                RNS.log("Could not acquire Android Power Manager! Taking wakelocks and keeping the CPU running will be unavailable.", RNS.LOG_ERROR)
                RNS.log("The contained exception was: "+str(e), RNS.LOG_ERROR)

            self.discover_usb_devices()
        
        self.sideband = SidebandCore(self, is_service=True, android_app_dir=self.app_dir, verbose=__debug_build__, owner_service=self, service_context=self.android_service)

        if self.sideband.config["debug"]:
            Logger.setLevel(LOG_LEVELS["debug"])

        self.sideband.start()
        self.update_connectivity_type()
        
        if RNS.vendor.platformutils.is_android():
            RNS.log("Discovered USB devices: "+str(self.usb_devices), RNS.LOG_EXTREME)
            self.update_location_provider()


    def discover_usb_devices(self):
        self.usb_devices = []
        RNS.log("Discovering attached USB devices...", RNS.LOG_EXTREME)
        try:
            devices = usb.get_usb_device_list()
            for device in devices:
                device_entry = {
                    "port": device.getDeviceName(),
                    "vid": device.getVendorId(),
                    "pid": device.getProductId(),
                    "manufacturer": device.getManufacturerName(),
                    "productname": device.getProductName(),
                }
                if device_entry["vid"] in self.usb_device_filter:
                    if device_entry["pid"] in self.usb_device_filter[device_entry["vid"]]:
                        self.usb_devices.append(device_entry)

        except Exception as e:
            RNS.log("Could not list USB devices. The contained exception was: "+str(e), RNS.LOG_ERROR)
    
    def start(self):
        self.should_run = True
        self.take_locks()
        self.run()

    def stop(self):
        self.should_run = False

    def take_locks(self, force_multicast=False):
        if RNS.vendor.platformutils.get_platform() == "android":
            if self.multicast_lock == None or force_multicast:
                if self.wifi_manager != None:
                    RNS.log("Creating multicast lock", RNS.LOG_DEBUG)
                    self.multicast_lock = self.wifi_manager.createMulticastLock("sideband_service")

            if self.multicast_lock != None:
                if not self.multicast_lock.isHeld():
                    RNS.log("Taking multicast lock", RNS.LOG_DEBUG)
                    self.multicast_lock.acquire()
                else:
                    RNS.log("Multicast lock already held", RNS.LOG_DEBUG)

            if self.wake_lock == None:
                if self.power_manager != None:
                    RNS.log("Creating wake lock", RNS.LOG_DEBUG)
                    self.wake_lock = self.power_manager.newWakeLock(self.power_manager.PARTIAL_WAKE_LOCK, "sideband_service")

            if self.wake_lock != None:
                if not self.wake_lock.isHeld():
                    RNS.log("Taking wake lock", RNS.LOG_DEBUG)
                    self.wake_lock.acquire()
                else:
                    RNS.log("Wake lock already held", RNS.LOG_DEBUG)

    def release_locks(self):
        if RNS.vendor.platformutils.get_platform() == "android":
            if not self.multicast_lock == None and self.multicast_lock.isHeld():
                RNS.log("Releasing multicast lock")
                self.multicast_lock.release()

            if not self.wake_lock == None and self.wake_lock.isHeld():
                RNS.log("Releasing wake lock")
                self.wake_lock.release()

    def update_connectivity_type(self):
        if self.sideband.reticulum.is_connected_to_shared_instance:
            is_controlling = False
        else:
            is_controlling = True

        self.sideband.setpersistent("service.is_controlling_connectivity", is_controlling)
    
    def get_connectivity_status(self):
        if self.sideband.reticulum.is_connected_to_shared_instance:
            return "[size=22dp][b]Connectivity Status[/b][/size]\n\nSideband is connected via a shared Reticulum instance running on this system. Use the rnstatus utility to obtain full connectivity info."
        else:
            ws = "Disabled"
            ts = "Disabled"
            i2s = "Disabled"

            # stat = "[size=22dp][b]Connectivity Status[/b][/size]\n\n"
            stat = ""

            if self.sideband.interface_local != None:
                netdevs = self.sideband.interface_local.adopted_interfaces
                if len(netdevs) > 0:
                    ds = "Using "
                    for netdev in netdevs:
                        ds += "[i]"+str(netdev)+"[/i], "
                    ds = ds[:-2]
                else:
                    ds = "No usable network devices"

                np = len(self.sideband.interface_local.peers)
                if np == 1:
                    ws = "1 reachable peer"
                else:
                    ws = str(np)+" reachable peers"

                stat += "[b]Local[/b]\n{ds}\n{ws}\n\n".format(ds=ds, ws=ws)

            if self.sideband.interface_rnode != None:
                if self.sideband.interface_rnode.online:
                    rs = "On-air at "+str(self.sideband.interface_rnode.bitrate_kbps)+" Kbps"
                else:
                    rs = "Interface Down"

                stat += "[b]RNode[/b]\n{rs}\n\n".format(rs=rs)

            if self.sideband.interface_modem != None:
                if self.sideband.interface_modem.online:
                    rm = "Connected"
                else:
                    rm = "Interface Down"

                stat += "[b]Radio Modem[/b]\n{rm}\n\n".format(rm=rm)

            if self.sideband.interface_serial != None:
                if self.sideband.interface_serial.online:
                    rs = "Running at "+RNS.prettysize(self.sideband.interface_serial.bitrate/8, suffix="b")+"ps"
                else:
                    rs = "Interface Down"

                stat += "[b]Serial Port[/b]\n{rs}\n\n".format(rs=rs)

            if self.sideband.interface_tcp != None:
                if self.sideband.interface_tcp.online:
                    ts = "Connected to "+str(self.sideband.interface_tcp.target_ip)+":"+str(self.sideband.interface_tcp.target_port)
                else:
                    ts = "Interface Down"

                stat += "[b]TCP[/b]\n{ts}\n\n".format(ts=ts)

            if self.sideband.interface_i2p != None:
                i2s = "Unknown"
                if hasattr(self.sideband.interface_i2p, "i2p_tunnel_state") and self.sideband.interface_i2p.i2p_tunnel_state != None:
                    if self.sideband.interface_i2p.i2p_tunnel_state == RNS.Interfaces.I2PInterface.I2PInterfacePeer.TUNNEL_STATE_INIT:
                        i2s = "Tunnel Connecting"
                    elif self.sideband.interface_i2p.i2p_tunnel_state == RNS.Interfaces.I2PInterface.I2PInterfacePeer.TUNNEL_STATE_ACTIVE:
                        i2s = "Tunnel Active"
                    elif self.sideband.interface_i2p.i2p_tunnel_state == RNS.Interfaces.I2PInterface.I2PInterfacePeer.TUNNEL_STATE_STALE:
                        i2s = "Tunnel Unresponsive"
                else:
                    if self.sideband.interface_i2p.online:
                        i2s = "Connected"
                    else:
                        i2s = "Connecting to I2P"

                stat += "[b]I2P[/b]\n{i2s}\n\n".format(i2s=i2s)

            total_rxb = 0
            total_txb = 0

            if self.sideband.interface_local != None:
                total_rxb += self.sideband.interface_local.rxb
                total_txb += self.sideband.interface_local.txb
            
            if self.sideband.interface_rnode != None:
                total_rxb += self.sideband.interface_rnode.rxb
                total_txb += self.sideband.interface_rnode.txb
            
            if self.sideband.interface_modem != None:
                total_rxb += self.sideband.interface_modem.rxb
                total_txb += self.sideband.interface_modem.txb
            
            if self.sideband.interface_serial != None:
                total_rxb += self.sideband.interface_serial.rxb
                total_txb += self.sideband.interface_serial.txb
            
            if self.sideband.interface_tcp != None:
                total_rxb += self.sideband.interface_tcp.rxb
                total_txb += self.sideband.interface_tcp.txb
            
            if self.sideband.interface_i2p != None:
                total_rxb += self.sideband.interface_i2p.rxb
                total_txb += self.sideband.interface_i2p.txb

            if RNS.Reticulum.transport_enabled():
                stat += "[b]Transport Instance[/b]\nRouting Traffic\n\n"

            stat += "[b]Traffic[/b]\nIn: {inb}\nOut: {outb}\n\n".format(inb=RNS.prettysize(total_rxb), outb=RNS.prettysize(total_txb))

            if stat.endswith("\n\n"):
                stat = stat[:-2]

            return stat

    def run(self):
        while self.should_run:
            sleep_time = 1
            self.sideband.setstate("service.heartbeat", time.time())
            self.sideband.setstate("service.connectivity_status", self.get_connectivity_status())

            if self.sideband.getstate("wants.service_stop"):
                self.sideband.service_stopped = True
                self.should_run = False
                sleep_time = 0

            if self.sideband.getstate("wants.clear_notifications"):
                self.sideband.setstate("wants.clear_notifications", False)
                if self.notification_service != None:
                    self.notification_service.cancelAll()

            if self.sideband.getstate("wants.settings_reload"):
                self.sideband.setstate("wants.settings_reload", False)
                self.sideband.reload_configuration()

            time.sleep(sleep_time)

        self.sideband.cleanup()
        self.release_locks()

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    if exc_type == SystemExit:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    import traceback
    exc_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    RNS.log(f"An unhandled {str(exc_type)} exception occurred: {str(exc_value)}", RNS.LOG_ERROR)
    RNS.log(exc_text, RNS.LOG_ERROR)

sys.excepthook = handle_exception
SidebandService().start()
