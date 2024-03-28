import RNS
import time
import threading

# This plugin requires the "gpsdclient" pip
# package to be installed on your system.
# Install it with: pip install gpsdclient
from gpsdclient import GPSDClient

class GpsdLocationPlugin(SidebandTelemetryPlugin):
    plugin_name = "gpsd_location"

    def __init__(self, sideband_core):
        self.connect_timeout = 5.0
        self.client = None
        self.client_connected = False
        self.should_run = False

        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.speed = None
        self.bearing = None
        self.accuracy = None
        self.last_update = None

        super().__init__(sideband_core)

    def start(self):
        RNS.log("Starting Linux GPSd Location provider plugin...")

        self.should_run = True
        update_thread = threading.Thread(target=self.update_job, daemon=True)
        update_thread.start()

        super().start()

    def stop(self):
        self.should_run = False
        super().stop()

    def update_job(self):
        while self.should_run:
            RNS.log("Connecting to local GPSd...", RNS.LOG_DEBUG)
            self.client_connected = False
            try:
                self.client = GPSDClient(timeout=self.connect_timeout)
                for result in self.client.dict_stream(convert_datetime=True, filter=["TPV"]):
                    if not self.client_connected:
                        RNS.log("Connected, streaming GPSd data", RNS.LOG_DEBUG)

                    self.client_connected = True
                    self.last_update = time.time()
                    self.latitude  = result.get("lat", None)
                    self.longitude = result.get("lon", None)
                    self.altitude  = result.get("altHAE", None)
                    self.speed     = result.get("speed", None)
                    self.bearing   = result.get("track", None)

                    epx = result.get("epx", None); epy = result.get("epy", None)
                    epv = result.get("epv", None)
                    if epx != None and epy != None and epv != None:
                        self.accuracy = max(epx, epy, epv)
                    else:
                        self.accuracy = None

            except Exception as e:
                RNS.log("Could not connect to local GPSd, retrying later", RNS.LOG_ERROR)

            time.sleep(5)

    def has_location(self):
        lat = self.latitude != None; lon = self.longitude != None
        alt = self.altitude != None; spd = self.speed != None
        brg = self.bearing != None; acc = self.accuracy != None
        return lat and lon and alt and spd and brg and acc

    def update_telemetry(self, telemeter):
        if self.is_running() and telemeter != None:
            if self.has_location():
                RNS.log("Updating location from gpsd", RNS.LOG_DEBUG)
                if not "location" in telemeter.sensors:
                    telemeter.synthesize("location")

                telemeter.sensors["location"].latitude   = self.latitude
                telemeter.sensors["location"].longitude  = self.longitude
                telemeter.sensors["location"].altitude   = self.altitude
                telemeter.sensors["location"].speed      = self.speed
                telemeter.sensors["location"].bearing    = self.bearing
                telemeter.sensors["location"].accuracy   = self.accuracy
                telemeter.sensors["location"].stale_time = 5
                telemeter.sensors["location"].set_update_time(self.last_update)
            
            else:
                RNS.log("No location from GPSd yet", RNS.LOG_DEBUG)


# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = GpsdLocationPlugin