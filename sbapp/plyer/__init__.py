'''
Plyer
=====

'''

__all__ = (
    'accelerometer', 'audio', 'barometer', 'battery', 'bluetooth',
    'brightness', 'call', 'camera', 'compass', 'cpu', 'email', 'filechooser',
    'flash', 'gps', 'gravity', 'gyroscope', 'humidity', 'irblaster',
    'keystore', 'light', 'notification', 'orientation', 'processors',
    'proximity', 'screenshot', 'sms', 'spatialorientation', 'storagepath',
    'stt', 'temperature', 'tts', 'uniqueid', 'vibrator', 'wifi', 'devicename'
)

__version__ = '2.1.0.dev0'


from plyer import facades
from plyer.utils import Proxy

#: Accelerometer proxy to :class:`plyer.facades.Accelerometer`
accelerometer = Proxy('accelerometer', facades.Accelerometer)

#: Keyring proxy to :class::`plyer.facades.Keystore`
keystore = Proxy('keystore', facades.Keystore)

#: Audio proxy to :class:`plyer.facades.Audio`
audio = Proxy('audio', facades.Audio)

#: Barometer proxy to :class:`plyer.facades.Barometer`
barometer = Proxy('barometer', facades.Barometer)

#: Battery proxy to :class:`plyer.facades.Battery`
battery = Proxy('battery', facades.Battery)

#: Call proxy to  :class `plyer.facades.Call`
call = Proxy('call', facades.Call)

#: Compass proxy to :class:`plyer.facades.Compass`
compass = Proxy('compass', facades.Compass)

#: Camera proxy to :class:`plyer.facades.Camera`
camera = Proxy('camera', facades.Camera)

#: Email proxy to :class:`plyer.facades.Email`
email = Proxy('email', facades.Email)

#: FileChooser proxy to :class:`plyer.facades.FileChooser`
filechooser = Proxy('filechooser', facades.FileChooser)

#: GPS proxy to :class:`plyer.facades.GPS`
gps = Proxy('gps', facades.GPS)

#: Gravity proxy to :class:`plyer.facades.Gravity`
gravity = Proxy('gravity', facades.Gravity)

#: Gyroscope proxy to :class:`plyer.facades.Gyroscope`
gyroscope = Proxy('gyroscope', facades.Gyroscope)

#: IrBlaster proxy to :class:`plyer.facades.IrBlaster`
irblaster = Proxy('irblaster', facades.IrBlaster)

#: Light proxy to :class:`plyer.facades.Light`
light = Proxy('light', facades.Light)

#: Orientation proxy to :class:`plyer.facades.Orientation`
orientation = Proxy('orientation', facades.Orientation)

#: Notification proxy to :class:`plyer.facades.Notification`
notification = Proxy('notification', facades.Notification)

#: Proximity proxy to :class:`plyer.facades.Proximity`
proximity = Proxy('proximity', facades.Proximity)

#: Sms proxy to :class:`plyer.facades.Sms`
sms = Proxy('sms', facades.Sms)

#: Speech proxy to :class:`plyer.facades.STT`
stt = Proxy('stt', facades.STT)

#: TTS proxy to :class:`plyer.facades.TTS`
tts = Proxy('tts', facades.TTS)

#: UniqueID proxy to :class:`plyer.facades.UniqueID`
uniqueid = Proxy('uniqueid', facades.UniqueID)

#: Vibrator proxy to :class:`plyer.facades.Vibrator`
vibrator = Proxy('vibrator', facades.Vibrator)

#: Flash proxy to :class:`plyer.facades.Flash`
flash = Proxy('flash', facades.Flash)

#: Wifi proxy to :class:`plyer.facades.Wifi`
wifi = Proxy('wifi', facades.Wifi)

#: Temperature proxy to :class:`plyer.facades.Temperature`
temperature = Proxy('temperature', facades.Temperature)

#: Humidity proxy to :class:`plyer.facades.Humidity`
humidity = Proxy('humidity', facades.Humidity)
#: SpatialOrientation proxy to :class:`plyer.facades.SpatialOrientation`
spatialorientation = Proxy('spatialorientation', facades.SpatialOrientation)

#: Brightness proxy to :class:`plyer.facades.Brightness`
brightness = Proxy('brightness', facades.Brightness)

#: StoragePath proxy to :class:`plyer.facades.StoragePath`
storagepath = Proxy('storagepath', facades.StoragePath)

#: Bluetooth proxy to :class:`plyer.facades.Bluetooth`
bluetooth = Proxy('bluetooth', facades.Bluetooth)

#: Processors proxy to :class:`plyer.facades.Processors`
processors = Proxy('processors', facades.Processors)

#: Processors proxy to :class:`plyer.facades.CPU`
cpu = Proxy('cpu', facades.CPU)

#: Screenshot proxy to :class:`plyer.facades.Screenshot`
screenshot = Proxy('screenshot', facades.Screenshot)

#: devicename proxy to :class:`plyer.facades.DeviceName`
devicename = Proxy('devicename', facades.DeviceName)
