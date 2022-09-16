'''
iOS GPS
-----------
'''

from pyobjus import autoclass, protocol
from pyobjus.dylib_manager import load_framework
from plyer.facades import GPS

load_framework('/System/Library/Frameworks/CoreLocation.framework')
CLLocationManager = autoclass('CLLocationManager')


class IosGPS(GPS):
    def _configure(self):
        if not hasattr(self, '_location_manager'):
            self._location_manager = CLLocationManager.alloc().init()

    def _start(self, **kwargs):
        self._location_manager.delegate = self

        self._location_manager.requestWhenInUseAuthorization()
        # NSLocationWhenInUseUsageDescription key must exist in Info.plist
        # file. When the authorization prompt is displayed your app goes
        # into pause mode and if your app doesn't support background mode
        # it will crash.
        self._location_manager.startUpdatingLocation()

    def _stop(self):
        self._location_manager.stopUpdatingLocation()

    @protocol('CLLocationManagerDelegate')
    def locationManager_didChangeAuthorizationStatus_(self, manager, status):
        if self.on_status:
            s_status = ''
            provider_status = ''
            provider = 'standard-ios-provider'
            if status == 0:
                provider_status = 'provider-disabled'
                s_status = 'notDetermined'
            elif status == 1:
                provider_status = 'provider-enabled'
                s_status = 'restricted'
            elif status == 2:
                provider_status = 'provider-disabled'
                s_status = 'denied'
            elif status == 3:
                provider_status = 'provider-enabled'
                s_status = 'authorizedAlways'
            elif status == 4:
                provider_status = 'provider-enabled'
                s_status = 'authorizedWhenInUse'
            self.on_status(provider_status, '{}: {}'.format(
                provider, s_status))

    @protocol('CLLocationManagerDelegate')
    def locationManager_didUpdateLocations_(self, manager, locations):
        location = manager.location

        description = location.description.UTF8String()
        split_description = description.split('<')[-1].split('>')[0].split(',')

        lat, lon = [float(coord) for coord in split_description]
        acc = float(description.split(' +/- ')[-1].split('m ')[0])

        speed = location.speed
        altitude = location.altitude
        course = location.course

        self.on_location(
            lat=lat,
            lon=lon,
            speed=speed,
            bearing=course,
            altitude=altitude,
            accuracy=acc)


def instance():
    return IosGPS()
