import time
import RNS
from os import environ

from kivy.logger import Logger, LOG_LEVELS
# TODO: Reset
Logger.setLevel(LOG_LEVELS["debug"])
# Logger.setLevel(LOG_LEVELS["error"])

if RNS.vendor.platformutils.get_platform() == "android":
    from jnius import autoclass, cast
    Context = autoclass('android.content.Context')
    from sideband.core import SidebandCore

else:
    from sbapp.sideband.core import SidebandCore

class AppProxy():
    def __init__(self):
        pass

class SidebandService():

    def __init__(self):
        self.argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
        self.app_dir = self.argument
        self.multicast_lock = None
        self.wake_lock = None
        self.should_run = False

        self.app_proxy = AppProxy()

        self.android_service = None
        self.app_context = None
        self.wifi_manager = None

        if RNS.vendor.platformutils.get_platform() == "android":
            self.android_service = autoclass('org.kivy.android.PythonService').mService
            self.app_context = self.android_service.getApplication().getApplicationContext()
            self.wifi_manager = self.app_context.getSystemService(Context.WIFI_SERVICE)
            # The returned instance is an android.net.wifi.WifiManager
        
        # TODO: Remove?
        RNS.log("Sideband background service created, starting core...", RNS.LOG_DEBUG)
        self.sideband = SidebandCore(self.app_proxy, is_service=True, android_app_dir=self.app_dir)
        self.sideband.start()
    
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
                RNS.log("Took lock")
        

    def release_locks():
        if RNS.vendor.platformutils.get_platform() == "android":
            if not self.multicast_lock == None and self.multicast_lock.isHeld():
                self.multicast_lock.release()

    def run(self):
        while self.should_run:
            time.sleep(1)

        self.release_locks()

sbs = SidebandService()
sbs.start()

# TODO: Remove
print("SBS: Service thread done")
RNS.log("Service thread done")