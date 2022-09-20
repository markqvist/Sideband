import time
import RNS
from sideband.core import SidebandCore
from os import environ
from jnius import autoclass, cast

Context = autoclass('android.content.Context')

class sidebandservice():

    def __init__(self):
        self.argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
        self.multicast_lock = None
        self.wake_lock = None

        self.service = autoclass('org.kivy.android.PythonService').mService
        self.app_context = self.service.getApplication().getApplicationContext()
        self.wifi_manager = self.app_context.getSystemService(Context.WIFI_SERVICE)
        # The returned instance is an android.net.wifi.WifiManager
        
        print("Sideband Service created")
        self.take_locks()
        self.run()

    def take_locks(self):
        if self.multicast_lock == None:
            self.multicast_lock = self.wifi_manager.createMulticastLock("sideband_service")

        if not self.multicast_lock.isHeld():
            RNS.log("Taking multicast lock")
            self.multicast_lock.acquire()
            RNS.log("Took lock")
        

    def release_locks():
        if not self.multicast_lock == None and self.multicast_lock.isHeld():
            self.multicast_lock.release()

    def run(self):
        while True:
            print("Service ping")
            time.sleep(5)

sbs = sidebandservice()