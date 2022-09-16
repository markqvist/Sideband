'''
Android GPS
-----------
'''

from plyer.facades import GPS
from plyer.platforms.android import activity
from jnius import autoclass, java_method, PythonJavaClass

Looper = autoclass('android.os.Looper')
LocationManager = autoclass('android.location.LocationManager')
Context = autoclass('android.content.Context')


class _LocationListener(PythonJavaClass):
    __javainterfaces__ = ['android/location/LocationListener']

    def __init__(self, root):
        self.root = root
        super().__init__()

    @java_method('(Landroid/location/Location;)V')
    def onLocationChanged(self, location):
        self.root.on_location(
            lat=location.getLatitude(),
            lon=location.getLongitude(),
            speed=location.getSpeed(),
            bearing=location.getBearing(),
            altitude=location.getAltitude(),
            accuracy=location.getAccuracy())

    @java_method('(Ljava/lang/String;)V')
    def onProviderEnabled(self, status):
        if self.root.on_status:
            self.root.on_status('provider-enabled', status)

    @java_method('(Ljava/lang/String;)V')
    def onProviderDisabled(self, status):
        if self.root.on_status:
            self.root.on_status('provider-disabled', status)

    @java_method('(Ljava/lang/String;ILandroid/os/Bundle;)V')
    def onStatusChanged(self, provider, status, extras):
        if self.root.on_status:
            s_status = 'unknown'
            if status == 0x00:
                s_status = 'out-of-service'
            elif status == 0x01:
                s_status = 'temporarily-unavailable'
            elif status == 0x02:
                s_status = 'available'
            self.root.on_status('provider-status', '{}: {}'.format(
                provider, s_status))


class AndroidGPS(GPS):

    def _configure(self):
        if not hasattr(self, '_location_manager'):
            self._location_manager = activity.getSystemService(
                Context.LOCATION_SERVICE
            )
            self._location_listener = _LocationListener(self)

    def _start(self, **kwargs):
        min_time = kwargs.get('minTime')
        min_distance = kwargs.get('minDistance')
        providers = self._location_manager.getProviders(False).toArray()
        for provider in providers:
            self._location_manager.requestLocationUpdates(
                provider,
                min_time,  # minTime, in milliseconds
                min_distance,  # minDistance, in meters
                self._location_listener,
                Looper.getMainLooper())

    def _stop(self):
        self._location_manager.removeUpdates(self._location_listener)


def instance():
    return AndroidGPS()
