# Windows Location Provider plugin example, provided by @haplo-dev

import RNS
import time
import threading
import asyncio
from winsdk.windows.devices import geolocation

class WindowsLocationPlugin(SidebandTelemetryPlugin):
    plugin_name = "windows_location"

    def __init__(self, sideband_core):
        self.update_interval = 5.0
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
        RNS.log("Starting Windows Location provider plugin...")

        self.should_run = True
        update_thread = threading.Thread(target=self.update_job, daemon=True)
        update_thread.start()

        super().start()

    def stop(self):
        self.should_run = False
        super().stop()

    def update_job(self):
        while self.should_run:
            RNS.log("Updating location from Windows Geolocation...", RNS.LOG_DEBUG)
            try:
                asyncio.run(self.get_location())
            except Exception as e:
                RNS.log(f"Error getting location: {str(e)}", RNS.LOG_ERROR)

            time.sleep(self.update_interval)

    async def get_location(self):
        geolocator = geolocation.Geolocator()
        position = await geolocator.get_geoposition_async()

        self.last_update = time.time()
        self.latitude = position.coordinate.latitude
        self.longitude = position.coordinate.longitude
        self.altitude = position.coordinate.altitude
        self.accuracy = position.coordinate.accuracy

        # Note: Windows Geolocation doesn't provide speed and bearing directly
        # You might need to calculate these from successive position updates
        self.speed = None
        self.bearing = None

    def has_location(self):
        return all([self.latitude, self.longitude, self.altitude, self.accuracy]) is not None

    def update_telemetry(self, telemeter):
        if self.is_running() and telemeter is not None:
            if self.has_location():
                RNS.log("Updating location from Windows Geolocation", RNS.LOG_DEBUG)
                if "location" not in telemeter.sensors:
                    telemeter.synthesize("location")

                telemeter.sensors["location"].latitude = self.latitude
                telemeter.sensors["location"].longitude = self.longitude
                telemeter.sensors["location"].altitude = self.altitude
                telemeter.sensors["location"].speed = self.speed
                telemeter.sensors["location"].bearing = self.bearing
                telemeter.sensors["location"].accuracy = self.accuracy
                telemeter.sensors["location"].stale_time = 5
                telemeter.sensors["location"].set_update_time(self.last_update)
            
            else:
                RNS.log("No location from Windows Geolocation yet", RNS.LOG_DEBUG)

# Finally, tell Sideband what class in this
# file is the actual plugin class.
plugin_class = WindowsLocationPlugin