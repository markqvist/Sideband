'''
Facades
=======

Interface of all the features available.

'''

__all__ = ('Accelerometer', 'Audio', 'Barometer', 'Battery', 'Call', 'Camera',
           'Compass', 'Email', 'FileChooser', 'GPS', 'Gravity', 'Gyroscope',
           'IrBlaster', 'Light', 'Orientation', 'Notification', 'Proximity',
           'Sms', 'TTS', 'UniqueID', 'Vibrator', 'Wifi', 'Flash', 'CPU',
           'Temperature', 'Humidity', 'SpatialOrientation', 'Brightness',
           'Processors', 'StoragePath', 'Keystore', 'Bluetooth', 'Screenshot',
           'STT', 'DeviceName')

import RNS
if RNS.vendor.platformutils.is_android():
    from plyer.facades.accelerometer import Accelerometer
    from plyer.facades.audio import Audio
    from plyer.facades.barometer import Barometer
    from plyer.facades.battery import Battery
    from plyer.facades.call import Call
    from plyer.facades.camera import Camera
    from plyer.facades.compass import Compass
    from plyer.facades.email import Email
    from plyer.facades.filechooser import FileChooser
    from plyer.facades.flash import Flash
    from plyer.facades.gps import GPS
    from plyer.facades.gravity import Gravity
    from plyer.facades.gyroscope import Gyroscope
    from plyer.facades.irblaster import IrBlaster
    from plyer.facades.light import Light
    from plyer.facades.proximity import Proximity
    from plyer.facades.orientation import Orientation
    from plyer.facades.notification import Notification
    from plyer.facades.sms import Sms
    from plyer.facades.stt import STT
    from plyer.facades.tts import TTS
    from plyer.facades.uniqueid import UniqueID
    from plyer.facades.vibrator import Vibrator
    from plyer.facades.wifi import Wifi
    from plyer.facades.temperature import Temperature
    from plyer.facades.humidity import Humidity
    from plyer.facades.spatialorientation import SpatialOrientation
    from plyer.facades.brightness import Brightness
    from plyer.facades.keystore import Keystore
    from plyer.facades.storagepath import StoragePath
    from plyer.facades.bluetooth import Bluetooth
    from plyer.facades.processors import Processors
    from plyer.facades.cpu import CPU
    from plyer.facades.screenshot import Screenshot
    from plyer.facades.devicename import DeviceName
else:
    from sbapp.plyer.facades.accelerometer import Accelerometer
    from sbapp.plyer.facades.audio import Audio
    from sbapp.plyer.facades.barometer import Barometer
    from sbapp.plyer.facades.battery import Battery
    from sbapp.plyer.facades.call import Call
    from sbapp.plyer.facades.camera import Camera
    from sbapp.plyer.facades.compass import Compass
    from sbapp.plyer.facades.email import Email
    from sbapp.plyer.facades.filechooser import FileChooser
    from sbapp.plyer.facades.flash import Flash
    from sbapp.plyer.facades.gps import GPS
    from sbapp.plyer.facades.gravity import Gravity
    from sbapp.plyer.facades.gyroscope import Gyroscope
    from sbapp.plyer.facades.irblaster import IrBlaster
    from sbapp.plyer.facades.light import Light
    from sbapp.plyer.facades.proximity import Proximity
    from sbapp.plyer.facades.orientation import Orientation
    from sbapp.plyer.facades.notification import Notification
    from sbapp.plyer.facades.sms import Sms
    from sbapp.plyer.facades.stt import STT
    from sbapp.plyer.facades.tts import TTS
    from sbapp.plyer.facades.uniqueid import UniqueID
    from sbapp.plyer.facades.vibrator import Vibrator
    from sbapp.plyer.facades.wifi import Wifi
    from sbapp.plyer.facades.temperature import Temperature
    from sbapp.plyer.facades.humidity import Humidity
    from sbapp.plyer.facades.spatialorientation import SpatialOrientation
    from sbapp.plyer.facades.brightness import Brightness
    from sbapp.plyer.facades.keystore import Keystore
    from sbapp.plyer.facades.storagepath import StoragePath
    from sbapp.plyer.facades.bluetooth import Bluetooth
    from sbapp.plyer.facades.processors import Processors
    from sbapp.plyer.facades.cpu import CPU
    from sbapp.plyer.facades.screenshot import Screenshot
    from sbapp.plyer.facades.devicename import DeviceName
