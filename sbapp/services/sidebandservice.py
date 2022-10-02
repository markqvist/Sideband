import time
import RNS
from os import environ

from kivy.logger import Logger, LOG_LEVELS
# Logger.setLevel(LOG_LEVELS["debug"])
Logger.setLevel(LOG_LEVELS["error"])

if RNS.vendor.platformutils.get_platform() == "android":
    from jnius import autoclass, cast
    from android import python_act
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    Icon = autoclass("android.graphics.drawable.Icon")
    PendingIntent = autoclass('android.app.PendingIntent')
    AndroidString = autoclass('java.lang.String')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    
    from sideband.core import SidebandCore

else:
    from sbapp.sideband.core import SidebandCore

class SidebandService():
    def android_notification(self, title="", content="", ticker="", group=None, context_id=None):
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

    def __init__(self):
        self.argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
        self.app_dir = self.argument
        self.multicast_lock = None
        self.wake_lock = None
        self.should_run = False

        self.android_service = None
        self.app_context = None
        self.wifi_manager = None
        self.power_manager = None

        self.notification_service = None
        self.notification_channel = None
        self.notification_intent = None
        self.notification_small_icon = None

        if RNS.vendor.platformutils.get_platform() == "android":
            self.android_service = autoclass('org.kivy.android.PythonService').mService
            self.app_context = self.android_service.getApplication().getApplicationContext()
            self.wifi_manager = self.app_context.getSystemService(Context.WIFI_SERVICE)
            self.power_manager = self.app_context.getSystemService(Context.POWER_SERVICE)
            # The returned instance /\ is an android.net.wifi.WifiManager
        
        self.sideband = SidebandCore(self, is_service=True, android_app_dir=self.app_dir)
        self.sideband.service_context = self.android_service
        self.sideband.owner_service = self
        self.sideband.start()
        self.update_connectivity_type()
    
    def start(self):
        self.should_run = True
        self.take_locks()
        self.run()

    def stop(self):
        self.should_run = False

    def take_locks(self):
        if RNS.vendor.platformutils.get_platform() == "android":
            if self.multicast_lock == None:
                self.multicast_lock = self.wifi_manager.createMulticastLock("sideband_service")

            if not self.multicast_lock.isHeld():
                RNS.log("Taking multicast lock")
                self.multicast_lock.acquire()

            if self.wake_lock == None:
                self.wake_lock = self.power_manager.newWakeLock(self.power_manager.PARTIAL_WAKE_LOCK, "sideband_service")

            if not self.wake_lock.isHeld():
                RNS.log("Taking wake lock")
                self.wake_lock.acquire()

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

            if self.sideband.interface_local != None:
                np = len(self.sideband.interface_local.peers)
                if np == 1:
                    ws = "1 reachable peer"
                else:
                    ws = str(np)+" reachable peers"

            if self.sideband.interface_tcp != None:
                if self.sideband.interface_tcp.online:
                    ts = "Connected to "+str(self.sideband.interface_tcp.target_ip)+":"+str(self.sideband.interface_tcp.target_port)
                else:
                    ts = "Interface Down"

            if self.sideband.interface_i2p != None:
                if self.sideband.interface_i2p.online:
                    i2s = "Connected"
                else:
                    i2s = "Connecting to I2P"

            return "[size=22dp][b]Connectivity Status[/b][/size]\n\n[b]Local[/b]\n{ws}\n\n[b]TCP[/b]\n{ts}\n\n[b]I2P[/b]\n{i2s}".format(ws=ws, ts=ts, i2s=i2s)

    def run(self):
        while self.should_run:
            sleep_time = 1
            self.sideband.setstate("service.heartbeat", time.time())
            self.sideband.setstate("service.connectivity_status", self.get_connectivity_status())

            if self.sideband.getstate("wants.service_stop"):
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

        self.release_locks()

SidebandService().start()